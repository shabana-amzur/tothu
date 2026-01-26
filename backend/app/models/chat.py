"""
Pydantic models for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ChatMessage(BaseModel):
    """Single chat message"""
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Request payload for chat endpoint"""
    message: str = Field(..., description="User's message", min_length=1)
    conversation_history: List[ChatMessage] = Field(
        default=[],
        description="Previous messages for context"
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Optional session ID to group related chats"
    )
    thread_id: Optional[int] = Field(
        default=None,
        description="Optional thread ID to associate message with a thread"
    )
    use_agent: bool = Field(
        default=False,
        description="Use agent mode with tools (calculator, text utilities)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "What is artificial intelligence?",
                "conversation_history": [
                    {
                        "role": "user",
                        "content": "Hello!",
                        "timestamp": "2026-01-15T10:00:00Z"
                    },
                    {
                        "role": "assistant",
                        "content": "Hello! How can I help you today?",
                        "timestamp": "2026-01-15T10:00:01Z"
                    }
                ]
            }
        }


class ChatResponse(BaseModel):
    """Response payload for chat endpoint"""
    message: str = Field(..., description="AI assistant's response")
    timestamp: datetime = Field(default_factory=datetime.now)
    model: str = Field(default="gemini-1.5-pro")
    thread_id: Optional[int] = Field(default=None, description="Thread ID")
    image_url: Optional[str] = Field(default=None, description="Generated image URL if applicable")
    is_image: Optional[bool] = Field(default=False, description="Whether this response includes an image")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Artificial Intelligence (AI) is...",
                "timestamp": "2026-01-15T10:00:02Z",
                "model": "gemini-1.5-pro"
            }
        }


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
