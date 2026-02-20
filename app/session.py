"""
ConversationSession: in-memory representation of a single chat session.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Optional


class ConversationSession:
    """Represents a single conversation session with its message history."""

    def __init__(self, session_id: str = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.messages: List[Dict] = []
        self.created_at = datetime.now()
        self.title = "New Chat"
        self.last_updated = datetime.now()

    def add_message(self, role: str, content: str):
        """Append a message and auto-generate title from the first user message."""
        self.messages.append({"role": role, "content": content})
        self.last_updated = datetime.now()

        if role == "user" and self.title == "New Chat" and content.strip():
            self.title = content[:50] + "..." if len(content) > 50 else content

    def get_chat_history(self) -> List[Dict]:
        return self.messages

    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "title": self.title,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "message_count": len(self.messages),
        }