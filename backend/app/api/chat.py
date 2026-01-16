"""
Chat API Routes
Handles all chat-related endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import Dict, List
import logging

from ..models.chat import ChatRequest, ChatResponse, ErrorResponse
from ..services.chat_service import get_chat_service
from ..database import get_db
from ..models.database import User, ChatHistory, ChatThread
from ..utils.auth import get_current_active_user
from ..api.threads import generate_thread_title

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        500: {"model": ErrorResponse},
        400: {"model": ErrorResponse}
    },
    summary="Send a chat message",
    description="Send a message to the AI assistant and receive a response"
)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> ChatResponse:
    """
    Chat endpoint - sends user message to Gemini and returns AI response
    Requires authentication and saves chat history to database
    
    **Request Body:**
    - message: User's message (required)
    - conversation_history: List of previous messages (optional)
    - thread_id: Thread ID to associate message with (optional)
    
    **Returns:**
    - AI assistant's response with timestamp and model info
    """
    try:
        logger.info(f"User {current_user.email} sent message with length: {len(request.message)}")
        
        # Handle thread creation or retrieval
        thread_id = request.thread_id
        is_new_thread = False
        
        if thread_id is None:
            # Create a new thread
            new_thread = ChatThread(user_id=current_user.id, title="New Conversation")
            db.add(new_thread)
            db.commit()
            db.refresh(new_thread)
            thread_id = new_thread.id
            is_new_thread = True
            logger.info(f"Created new thread {thread_id} for user {current_user.email}")
        else:
            # Verify thread belongs to user
            thread = db.query(ChatThread).filter(
                ChatThread.id == thread_id,
                ChatThread.user_id == current_user.id
            ).first()
            if not thread:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Thread not found"
                )
        
        # Get last 5 conversation pairs from this thread for conversation memory
        # Each ChatHistory record contains one user message and one AI response
        recent_messages = db.query(ChatHistory).filter(
            ChatHistory.thread_id == thread_id
        ).order_by(ChatHistory.created_at.desc()).limit(5).all()
        
        # Build conversation history (reverse to chronological order)
        # This will include up to 5 previous user messages and 5 previous AI responses
        history = []
        for msg in reversed(recent_messages):
            history.append({"role": "user", "content": msg.message})
            history.append({"role": "assistant", "content": msg.response})
        
        logger.info(f"Retrieved {len(recent_messages)} previous conversation pairs for thread {thread_id}")
        
        # Get chat service
        chat_service = get_chat_service()
        
        # Check if user has documents and should use RAG
        from app.services.rag_service import get_rag_service
        rag_service = get_rag_service()
        use_rag = rag_service.should_use_rag(current_user.id)
        
        if use_rag:
            logger.info(f"Using RAG for user {current_user.email}")
        
        # Get response from Gemini (with RAG if available)
        result = await chat_service.get_chat_response(
            user_message=request.message,
            conversation_history=history,
            user_id=current_user.id,
            use_rag=use_rag
        )
        
        # Save chat history to database with thread_id
        try:
            chat_record = ChatHistory(
                user_id=current_user.id,
                thread_id=thread_id,
                message=request.message,
                response=result["message"],
                model=result["model"],
                session_id=request.session_id
            )
            db.add(chat_record)
            db.commit()
            logger.info(f"Chat history saved for user {current_user.email} in thread {thread_id}")
        except Exception as db_error:
            logger.error(f"Failed to save chat history: {str(db_error)}")
            db.rollback()
            # Continue even if saving fails
        
        # Auto-generate/update thread title based on latest conversation
        try:
            # Generate title from the current conversation context
            title = await generate_thread_title(request.message)
            db.query(ChatThread).filter(ChatThread.id == thread_id).update({"title": title})
            db.commit()
            logger.info(f"{'Generated' if is_new_thread else 'Updated'} title '{title}' for thread {thread_id}")
        except Exception as title_error:
            logger.error(f"Failed to generate thread title: {str(title_error)}")
        
        # Return response
        return ChatResponse(
            message=result["message"],
            model=result["model"],
            thread_id=thread_id
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat request: {str(e)}"
        )


@router.get(
    "/chat/model-info",
    summary="Get model information",
    description="Get information about the current AI model configuration"
)
async def get_model_info() -> Dict[str, str]:
    """Get information about the current Gemini model"""
    try:
        chat_service = get_chat_service()
        return chat_service.get_model_info()
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/chat/history",
    summary="Get chat history",
    description="Get chat history for the current user"
)
async def get_chat_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    session_id: str = None
):
    """Get chat history for the current user"""
    try:
        query = db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id)
        
        if session_id:
            query = query.filter(ChatHistory.session_id == session_id)
        
        chat_history = query.order_by(ChatHistory.created_at.desc()).limit(limit).all()
        
        return {
            "history": [
                {
                    "id": chat.id,
                    "message": chat.message,
                    "response": chat.response,
                    "model": chat.model,
                    "session_id": chat.session_id,
                    "created_at": chat.created_at
                }
                for chat in chat_history
            ]
        }
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chat history"
        )

