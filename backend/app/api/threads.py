"""
Chat Thread API Endpoints
Handles thread creation, listing, updating, and deletion
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import logging

from app.database import get_db
from app.models.database import User, ChatThread, ChatHistory
from app.models.thread import ThreadCreate, ThreadUpdate, ThreadResponse, ThreadWithMessages
from app.utils.auth import get_current_user
from app.services.chat_service import get_chat_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/threads", tags=["threads"])


async def generate_thread_title(first_message: str) -> str:
    """Generate a title for a thread based on the first message"""
    try:
        chat_service = get_chat_service()
        
        # Use AI to generate a concise title
        prompt = f"Based on this user message: '{first_message[:100]}', generate a short descriptive title (max 5 words) that describes what the conversation is about. Use natural language like 'Poem on Cat' or 'Python Tutorial' rather than 'Cat Poem Request' or 'Tutorial Request'. Just respond with the title, nothing else."
        
        from langchain.schema import HumanMessage
        result = await chat_service.llm.ainvoke([HumanMessage(content=prompt)])
        
        title = result.content.strip().strip('"').strip("'")
        # Limit to 50 characters
        return title[:50] if len(title) > 50 else title
    except Exception as e:
        logger.error(f"Error generating title: {str(e)}")
        # Fallback: use first few words of message
        words = first_message.split()[:5]
        return " ".join(words) + ("..." if len(first_message.split()) > 5 else "")


@router.post("/", response_model=ThreadResponse, status_code=status.HTTP_201_CREATED)
async def create_thread(
    thread_data: ThreadCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new chat thread"""
    try:
        # If no title provided, use a default
        title = thread_data.title or "New Chat"
        
        new_thread = ChatThread(
            user_id=current_user.id,
            title=title
        )
        
        db.add(new_thread)
        db.commit()
        db.refresh(new_thread)
        
        logger.info(f"Thread created: {new_thread.id} by user {current_user.email}")
        
        return ThreadResponse(
            id=new_thread.id,
            title=new_thread.title,
            created_at=new_thread.created_at,
            updated_at=new_thread.updated_at,
            message_count=0
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating thread: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create thread"
        )


@router.get("/", response_model=List[ThreadResponse])
async def list_threads(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of user's chat threads"""
    try:
        # Get threads with message count
        threads = db.query(
            ChatThread,
            func.count(ChatHistory.id).label('message_count')
        ).outerjoin(ChatHistory).filter(
            ChatThread.user_id == current_user.id
        ).group_by(ChatThread.id).order_by(
            ChatThread.updated_at.desc()
        ).all()
        
        return [
            ThreadResponse(
                id=thread.id,
                title=thread.title,
                created_at=thread.created_at,
                updated_at=thread.updated_at,
                message_count=count
            )
            for thread, count in threads
        ]
        
    except Exception as e:
        logger.error(f"Error listing threads: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list threads"
        )


@router.get("/{thread_id}", response_model=ThreadWithMessages)
async def get_thread(
    thread_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific thread with its messages"""
    try:
        thread = db.query(ChatThread).filter(
            ChatThread.id == thread_id,
            ChatThread.user_id == current_user.id
        ).first()
        
        if not thread:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thread not found"
            )
        
        # Get messages for this thread
        messages = db.query(ChatHistory).filter(
            ChatHistory.thread_id == thread_id
        ).order_by(ChatHistory.created_at).all()
        
        message_list = []
        for msg in messages:
            # Add user message
            message_list.append({
                "id": msg.id,
                "message": msg.message,
                "response": msg.response,
                "created_at": msg.created_at.isoformat()
            })
        
        return ThreadWithMessages(
            id=thread.id,
            title=thread.title,
            created_at=thread.created_at,
            updated_at=thread.updated_at,
            messages=message_list
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting thread: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get thread"
        )


@router.put("/{thread_id}", response_model=ThreadResponse)
async def update_thread(
    thread_id: int,
    thread_data: ThreadUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a thread's title"""
    try:
        thread = db.query(ChatThread).filter(
            ChatThread.id == thread_id,
            ChatThread.user_id == current_user.id
        ).first()
        
        if not thread:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thread not found"
            )
        
        thread.title = thread_data.title
        db.commit()
        db.refresh(thread)
        
        # Get message count
        message_count = db.query(ChatHistory).filter(
            ChatHistory.thread_id == thread_id
        ).count()
        
        logger.info(f"Thread {thread_id} updated by user {current_user.email}")
        
        return ThreadResponse(
            id=thread.id,
            title=thread.title,
            created_at=thread.created_at,
            updated_at=thread.updated_at,
            message_count=message_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating thread: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update thread"
        )


@router.delete("/{thread_id}")
async def delete_thread(
    thread_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a thread and all its messages"""
    try:
        thread = db.query(ChatThread).filter(
            ChatThread.id == thread_id,
            ChatThread.user_id == current_user.id
        ).first()
        
        if not thread:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thread not found"
            )
        
        db.delete(thread)
        db.commit()
        
        logger.info(f"Thread {thread_id} deleted by user {current_user.email}")
        
        return {"message": "Thread deleted successfully", "thread_id": thread_id}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting thread: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete thread"
        )
