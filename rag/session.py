"""In-memory representation of a single chat session."""

from datetime import datetime
from typing import Dict, List
import uuid


class ConversationSession:
    """Represent a chat session and its message history."""

    def __init__(self, session_id: str = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.messages: List[Dict] = []
        self.created_at = datetime.now()
        self.title = "New Chat"
        self.last_updated = datetime.now()

    def add_message(self, role: str, content: str):
        """Append a message and derive a title from the first user message."""
        self.messages.append({"role": role, "content": content})
        self.last_updated = datetime.now()

        if role == "user" and self.title == "New Chat" and content.strip():
            self.title = content[:50] + "..." if len(content) > 50 else content

    def get_chat_history(self) -> List[Dict]:
        return self.messages
