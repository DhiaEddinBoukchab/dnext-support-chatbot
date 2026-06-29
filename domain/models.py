"""Domain models used by the FastAPI runtime."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class UserStatus(Enum):
    """User account status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"


@dataclass
class User:
    """Persisted chatbot user."""

    email: str
    full_name: str
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    status: UserStatus = UserStatus.ACTIVE
    user_id: Optional[int] = None
    total_queries: int = 0


@dataclass
class Conversation:
    """Persisted chat exchange."""

    user_id: int
    message: str
    response: str
    timestamp: datetime = field(default_factory=datetime.now)
    conversation_id: Optional[int] = None
    session_id: Optional[str] = None
    conversation_type: str = "TECHNICAL"
    response_time_ms: Optional[int] = None
    attachments: Optional[str] = None


@dataclass
class RetrievalTrace:
    """Persisted retrieval trace for technical conversations."""

    conversation_id: int
    query_input: str
    retrieved_chunks: str
    final_answer: str
    num_chunks_retrieved: int
    timestamp: datetime = field(default_factory=datetime.now)
    retrieval_trace_id: Optional[int] = None
