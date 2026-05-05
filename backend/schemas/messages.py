"""Request and response schemas for chat endpoint"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatRequest(BaseModel):
    """Schema for chat request"""
    message: str = Field(..., min_length=1, description="User message text")
    session_id: Optional[str] = Field(None, description="Session ID for conversation persistence")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "What does my dashboard cover?",
                "session_id": "session_abc123"
            }
        }


class ChatResponse(BaseModel):
    """Schema for chat response metadata"""
    session_id: str
    conversation_type: str
    chunks_retrieved: int
    response_time_ms: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_abc123",
                "conversation_type": "TECHNICAL",
                "chunks_retrieved": 3,
                "response_time_ms": 1200
            }
        }


class StreamingMessage(BaseModel):
    """Schema for streaming SSE messages"""
    type: str = Field(..., description="Message type: 'response' or 'metadata'")
    content: Optional[str] = Field(None, description="Response content (for type='response')")
    data: Optional[dict] = Field(None, description="Metadata (for type='metadata')")
    
    class Config:
        json_schema_extra = {
            "example_response": {
                "type": "response",
                "content": "I can help you with that question..."
            },
            "example_metadata": {
                "type": "metadata",
                "data": {
                    "chunks_retrieved": 3,
                    "response_time_ms": 1200
                }
            }
        }


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    error: str
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "bad_request",
                "message": "Message text is required"
            }
        }
