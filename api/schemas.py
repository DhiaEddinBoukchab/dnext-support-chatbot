from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=100)


class UserResponse(BaseModel):
    user_id: int
    email: EmailStr
    full_name: str
    status: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user: UserResponse


class ChatRequest(BaseModel):
    query: str = Field(min_length=1)
    session_id: Optional[str] = None


class RetrievedChunk(BaseModel):
    document: str
    section: str
    distance: Optional[float] = None
    text: str


class ChatResponse(BaseModel):
    session_id: str
    conversation_type: str
    answer: str
    chunks_retrieved: int
    retrieved_chunks: List[RetrievedChunk]
    response_time_ms: int


class SessionSummary(BaseModel):
    session_id: str
    title: str
    last_updated: str


class SessionMessage(BaseModel):
    role: str
    content: str


class SessionHistoryResponse(BaseModel):
    session_id: str
    messages: List[SessionMessage]


class ReindexResponse(BaseModel):
    success: bool
    message: str


class HealthResponse(BaseModel):
    status: str
    providers: dict
    docs_folder: str
    timestamp: datetime
