"""
Chat API Routes
Handles all chat-related endpoints
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict
import logging

from ..models.chat import ChatRequest, ChatResponse, ErrorResponse
from ..services.chat_service import get_chat_service

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
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Chat endpoint - sends user message to Gemini and returns AI response
    
    **Request Body:**
    - message: User's message (required)
    - conversation_history: List of previous messages (optional)
    
    **Returns:**
    - AI assistant's response with timestamp and model info
    """
    try:
        logger.info(f"Received chat request with message length: {len(request.message)}")
        
        # Get chat service
        chat_service = get_chat_service()
        
        # Convert Pydantic models to dicts for service layer
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.conversation_history
        ]
        
        # Get response from Gemini
        result = await chat_service.get_chat_response(
            user_message=request.message,
            conversation_history=history
        )
        
        # Return response
        return ChatResponse(
            message=result["message"],
            model=result["model"]
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
