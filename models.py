"""
Database models for user management and conversation tracking
Following Single Responsibility Principle - each model has one clear purpose
"""

from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field
from enum import Enum
import sqlite3
import json


class UserStatus(Enum):
    """User account status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"


@dataclass
class User:
    """User model - SRP: Represents a single user entity"""
    email: str
    full_name: str
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    status: UserStatus = UserStatus.ACTIVE
    user_id: Optional[int] = None
    total_queries: int = 0
    
    def to_dict(self) -> dict:
        """Convert user to dictionary"""
        return {
            'user_id': self.user_id,
            'email': self.email,
            'full_name': self.full_name,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'status': self.status.value,
            'total_queries': self.total_queries
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Create user from dictionary"""
        return cls(
            email=data['email'],
            full_name=data['full_name'],
            created_at=datetime.fromisoformat(data['created_at']),
            last_login=datetime.fromisoformat(data['last_login']) if data['last_login'] else None,
            status=UserStatus(data['status']),
            user_id=data.get('user_id'),
            total_queries=data.get('total_queries', 0)
        )


@dataclass
class Conversation:
    """Conversation model - SRP: Represents a single conversation"""
    user_id: int
    message: str
    response: str
    timestamp: datetime = field(default_factory=datetime.now)
    conversation_id: Optional[int] = None
    conversation_type: str = "TECHNICAL"  # TECHNICAL or CASUAL
    response_time_ms: Optional[int] = None
    # JSON-encoded list of attachment metadata dictionaries, e.g.
    # [{"type": "image", "path": "uploads/...", "original_name": "file.png"}, ...]
    attachments: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert conversation to dictionary"""
        return {
            'conversation_id': self.conversation_id,
            'user_id': self.user_id,
            'message': self.message,
            'response': self.response,
            'timestamp': self.timestamp.isoformat(),
            'conversation_type': self.conversation_type,
            'response_time_ms': self.response_time_ms,
            'attachments': self.attachments,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Conversation':
        """Create conversation from dictionary"""
        return cls(
            user_id=data['user_id'],
            message=data['message'],
            response=data['response'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            conversation_id=data.get('conversation_id'),
            conversation_type=data.get('conversation_type', 'TECHNICAL'),
            response_time_ms=data.get('response_time_ms'),
            attachments=data.get('attachments'),
        )


@dataclass
class AdminUser:
    """Admin user model - SRP: Represents admin credentials"""
    username: str
    password_hash: str
    created_at: datetime = field(default_factory=datetime.now)
    admin_id: Optional[int] = None
    
    def to_dict(self) -> dict:
        """Convert admin to dictionary"""
        return {
            'admin_id': self.admin_id,
            'username': self.username,
            'created_at': self.created_at.isoformat()
        }