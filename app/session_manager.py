"""
Session manager: create, restore, and list conversation sessions.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from app.session import ConversationSession

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages in-memory sessions and syncs with the database."""

    def __init__(self, db):
        self.db = db
        # user_id -> {session_id -> ConversationSession}
        self._sessions: Dict[int, Dict[str, ConversationSession]] = {}

    # ── Create / retrieve ────────────────────────────────────────────────────

    def get_or_create(self, user_id: int, session_id: str = None) -> ConversationSession:
        """Return an existing session or create a fresh one."""
        if user_id not in self._sessions:
            self._sessions[user_id] = {}

        if session_id and session_id in self._sessions[user_id]:
            return self._sessions[user_id][session_id]

        session = ConversationSession(session_id)
        self._sessions[user_id][session.session_id] = session
        logger.info(f"Created session {session.session_id} for user {user_id}")
        return session

    def restore_from_db(self, user_id: int, session_id: str) -> ConversationSession:
        """
        Rebuild a session from all DB rows that share the same session_id.
        Re-uses the in-memory session if already loaded.
        """
        if user_id not in self._sessions:
            self._sessions[user_id] = {}

        if session_id in self._sessions[user_id]:
            return self._sessions[user_id][session_id]

        rows = self.db.get_conversations_by_session(user_id, session_id)
        session = ConversationSession(session_id)

        for row in rows:
            session.messages.append({"role": "user",      "content": row.message})
            session.messages.append({"role": "assistant", "content": row.response})

        if rows:
            first_msg = rows[0].message
            session.title = first_msg[:50] + "..." if len(first_msg) > 50 else first_msg
            session.last_updated = rows[-1].timestamp

        self._sessions[user_id][session_id] = session
        logger.info(f"Restored session {session_id} ({len(rows)} exchanges) for user {user_id}")
        return session

    def clear_user(self, user_id: int):
        """Remove all in-memory sessions for a user (called on logout)."""
        self._sessions.pop(user_id, None)

    # ── Sidebar data ─────────────────────────────────────────────────────────

    def get_sidebar_choices(self, user_id: int) -> List[Tuple[str, str]]:
        """
        Return (title, session_id) pairs for the sidebar, one per session.
        Merges in-memory sessions with persisted DB sessions, newest first.
        """
        # In-memory sessions that have at least one message
        in_memory: Dict[str, ConversationSession] = {}
        for sid, sess in self._sessions.get(user_id, {}).items():
            if sess.messages:
                in_memory[sid] = sess

        # DB sessions
        db_sessions = self.db.get_session_summaries(user_id)

        merged: Dict[str, Dict] = {}

        for row in db_sessions:
            first_msg = row["first_message"]
            merged[row["session_id"]] = {
                "session_id": row["session_id"],
                "title": first_msg[:50] + "..." if len(first_msg) > 50 else first_msg,
                "last_updated": row["last_updated"],
            }

        # In-memory sessions are fresher — overlay them
        for sid, sess in in_memory.items():
            if sess.title != "New Chat":
                last_upd = (
                    sess.last_updated.isoformat()
                    if isinstance(sess.last_updated, datetime)
                    else sess.last_updated
                )
                merged[sid] = {
                    "session_id": sid,
                    "title": sess.title,
                    "last_updated": last_upd,
                }

        sorted_sessions = sorted(merged.values(), key=lambda x: x["last_updated"], reverse=True)
        return [(s["title"], s["session_id"]) for s in sorted_sessions]