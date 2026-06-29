"""Restore and cache chat sessions in memory."""

import logging
from typing import Dict

from rag.session import ConversationSession


logger = logging.getLogger(__name__)


class SessionManager:
    """Manage in-memory sessions and rebuild them from the database when needed."""

    def __init__(self, db):
        self.db = db
        self._sessions: Dict[int, Dict[str, ConversationSession]] = {}

    def get_or_create(self, user_id: int, session_id: str = None) -> ConversationSession:
        """Return an existing session or create a new one."""
        if user_id not in self._sessions:
            self._sessions[user_id] = {}

        if session_id and session_id in self._sessions[user_id]:
            return self._sessions[user_id][session_id]

        session = ConversationSession(session_id)
        self._sessions[user_id][session.session_id] = session
        logger.info(f"Created session {session.session_id} for user {user_id}")
        return session

    def restore_from_db(self, user_id: int, session_id: str) -> ConversationSession:
        """Rebuild one session from persisted conversation rows."""
        if user_id not in self._sessions:
            self._sessions[user_id] = {}

        if session_id in self._sessions[user_id]:
            return self._sessions[user_id][session_id]

        rows = self.db.get_conversations_by_session(user_id, session_id)
        session = ConversationSession(session_id)

        for row in rows:
            session.messages.append({"role": "user", "content": row.message})
            session.messages.append({"role": "assistant", "content": row.response})

        if rows:
            first_message = rows[0].message
            session.title = first_message[:50] + "..." if len(first_message) > 50 else first_message
            session.last_updated = rows[-1].timestamp

        self._sessions[user_id][session_id] = session
        logger.info(f"Restored session {session_id} ({len(rows)} exchanges) for user {user_id}")
        return session
