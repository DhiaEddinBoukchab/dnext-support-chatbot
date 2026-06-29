"""SQLite repository used by the FastAPI service."""

from datetime import datetime
import logging
from pathlib import Path
import sqlite3
from typing import List, Optional

from domain.models import Conversation, RetrievalTrace, User, UserStatus


logger = logging.getLogger(__name__)


class DatabaseRepository:
    """Persist users, sessions, conversations, and retrieval traces."""

    def __init__(self, db_path: str = "./runtime_data/chatbot_api.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_database(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    last_login TIMESTAMP,
                    status TEXT NOT NULL DEFAULT 'active',
                    total_queries INTEGER DEFAULT 0
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_id TEXT,
                    message TEXT NOT NULL,
                    response TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    conversation_type TEXT DEFAULT 'TECHNICAL',
                    response_time_ms INTEGER,
                    attachments TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS retrieval_traces (
                    retrieval_trace_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER NOT NULL,
                    query_input TEXT NOT NULL,
                    retrieved_chunks TEXT NOT NULL,
                    final_answer TEXT NOT NULL,
                    num_chunks_retrieved INTEGER NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (conversation_id) ON DELETE CASCADE
                )
                """
            )

            cursor.execute("PRAGMA table_info(conversations)")
            existing_columns = {row["name"] for row in cursor.fetchall()}
            if "attachments" not in existing_columns:
                cursor.execute("ALTER TABLE conversations ADD COLUMN attachments TEXT")
            if "session_id" not in existing_columns:
                cursor.execute("ALTER TABLE conversations ADD COLUMN session_id TEXT")

            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_retrieval_traces_conversation_id ON retrieval_traces(conversation_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_retrieval_traces_timestamp ON retrieval_traces(timestamp)"
            )

            conn.commit()
            logger.info("Database initialized successfully")

    @staticmethod
    def _row_to_user(row: sqlite3.Row) -> User:
        return User(
            user_id=row["user_id"],
            email=row["email"],
            full_name=row["full_name"],
            created_at=datetime.fromisoformat(row["created_at"]),
            last_login=datetime.fromisoformat(row["last_login"]) if row["last_login"] else None,
            status=UserStatus(row["status"]),
            total_queries=row["total_queries"],
        )

    @staticmethod
    def _row_to_conversation(row: sqlite3.Row) -> Conversation:
        return Conversation(
            conversation_id=row["conversation_id"],
            user_id=row["user_id"],
            session_id=row["session_id"],
            message=row["message"],
            response=row["response"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            conversation_type=row["conversation_type"],
            response_time_ms=row["response_time_ms"],
            attachments=row["attachments"],
        )

    def create_user(self, user: User) -> Optional[int]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO users (email, full_name, created_at, status)
                    VALUES (?, ?, ?, ?)
                    """,
                    (user.email, user.full_name, user.created_at, user.status.value),
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.warning(f"User with email {user.email} already exists")
            return None
        except Exception as exc:
            logger.error(f"Error creating user: {exc}")
            return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
                row = cursor.fetchone()
            return self._row_to_user(row) if row else None
        except Exception as exc:
            logger.error(f"Error getting user by email: {exc}")
            return None

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
            return self._row_to_user(row) if row else None
        except Exception as exc:
            logger.error(f"Error getting user by id: {exc}")
            return None

    def update_user_login(self, user_id: int):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET last_login = ? WHERE user_id = ?",
                    (datetime.now(), user_id),
                )
                conn.commit()
        except Exception as exc:
            logger.error(f"Error updating user login: {exc}")

    def save_conversation(self, conversation: Conversation) -> Optional[int]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO conversations (
                        user_id, session_id, message, response, timestamp,
                        conversation_type, response_time_ms, attachments
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        conversation.user_id,
                        conversation.session_id,
                        conversation.message,
                        conversation.response,
                        conversation.timestamp,
                        conversation.conversation_type,
                        conversation.response_time_ms,
                        conversation.attachments,
                    ),
                )
                cursor.execute(
                    "UPDATE users SET total_queries = total_queries + 1 WHERE user_id = ?",
                    (conversation.user_id,),
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as exc:
            logger.error(f"Error saving conversation: {exc}")
            return None

    def get_session_summaries(self, user_id: int) -> List[dict]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT
                        session_id,
                        MAX(timestamp) AS last_updated,
                        (
                            SELECT c2.message
                            FROM conversations c2
                            WHERE c2.user_id = c.user_id
                              AND c2.session_id = c.session_id
                            ORDER BY c2.timestamp ASC
                            LIMIT 1
                        ) AS first_message
                    FROM conversations c
                    WHERE user_id = ?
                      AND session_id IS NOT NULL
                      AND session_id != ''
                    GROUP BY session_id
                    ORDER BY last_updated DESC
                    """,
                    (user_id,),
                )
                rows = cursor.fetchall()

            return [
                {
                    "session_id": row["session_id"],
                    "first_message": row["first_message"] or "(empty)",
                    "last_updated": row["last_updated"],
                }
                for row in rows
            ]
        except Exception as exc:
            logger.error(f"Error getting session summaries: {exc}")
            return []

    def get_conversations_by_session(self, user_id: int, session_id: str) -> List[Conversation]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT *
                    FROM conversations
                    WHERE user_id = ?
                      AND session_id = ?
                    ORDER BY timestamp ASC
                    """,
                    (user_id, session_id),
                )
                rows = cursor.fetchall()
            return [self._row_to_conversation(row) for row in rows]
        except Exception as exc:
            logger.error(f"Error getting conversations by session: {exc}")
            return []

    def save_retrieval_trace(self, trace: RetrievalTrace) -> Optional[int]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO retrieval_traces (
                        conversation_id, query_input, retrieved_chunks,
                        final_answer, num_chunks_retrieved, timestamp
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        trace.conversation_id,
                        trace.query_input,
                        trace.retrieved_chunks,
                        trace.final_answer,
                        trace.num_chunks_retrieved,
                        trace.timestamp,
                    ),
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as exc:
            logger.error(f"Error saving retrieval trace: {exc}")
            return None
