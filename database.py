"""
Database repository - Following Repository Pattern and Interface Segregation Principle
Separates data access logic from business logic
"""

import sqlite3
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from pathlib import Path
from models import User, Conversation, AdminUser, UserStatus
import hashlib


logger = logging.getLogger(__name__)


class DatabaseRepository:
    """
    Database repository - DIP: Depends on abstractions (models) not concrete implementations
    OCP: Open for extension (new methods) but closed for modification
    """
    
    def __init__(self, db_path: str = "data/chatbot.db"):
        """Initialize database connection"""
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _initialize_database(self):
        """Create database tables if they don't exist"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    last_login TIMESTAMP,
                    status TEXT NOT NULL DEFAULT 'active',
                    total_queries INTEGER DEFAULT 0
                )
            ''')
            
            # Conversations table (session_id included from the start for new DBs)
            cursor.execute('''
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
            ''')
            
            # Admin users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin_users (
                    admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL
                )
            ''')
            
            # Indexes for better query performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_conversations_user_id 
                ON conversations(user_id)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_conversations_timestamp 
                ON conversations(timestamp)
            ''')

            # ── Lightweight migrations for older databases ──────────────────
            # Must run BEFORE any index that references the new columns
            cursor.execute("PRAGMA table_info(conversations)")
            existing_cols = {row["name"] for row in cursor.fetchall()}

            if "attachments" not in existing_cols:
                cursor.execute("ALTER TABLE conversations ADD COLUMN attachments TEXT")
                logger.info("Migration: added 'attachments' column")

            if "session_id" not in existing_cols:
                cursor.execute("ALTER TABLE conversations ADD COLUMN session_id TEXT")
                logger.info("Migration: added 'session_id' column")

            # Index on session_id created AFTER migration so the column is guaranteed to exist
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_conversations_session_id
                ON conversations(session_id)
            ''')

            conn.commit()
            logger.info("✅ Database initialized successfully")
    
    # ==================== USER OPERATIONS ====================
    
    def create_user(self, user: User) -> Optional[int]:
        """Create new user - returns user_id"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (email, full_name, created_at, status)
                    VALUES (?, ?, ?, ?)
                ''', (user.email, user.full_name, user.created_at, user.status.value))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.warning(f"User with email {user.email} already exists")
            return None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
                row = cursor.fetchone()
                
                if row:
                    return User(
                        user_id=row['user_id'],
                        email=row['email'],
                        full_name=row['full_name'],
                        created_at=datetime.fromisoformat(row['created_at']),
                        last_login=datetime.fromisoformat(row['last_login']) if row['last_login'] else None,
                        status=UserStatus(row['status']),
                        total_queries=row['total_queries']
                    )
                return None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
                row = cursor.fetchone()
                
                if row:
                    return User(
                        user_id=row['user_id'],
                        email=row['email'],
                        full_name=row['full_name'],
                        created_at=datetime.fromisoformat(row['created_at']),
                        last_login=datetime.fromisoformat(row['last_login']) if row['last_login'] else None,
                        status=UserStatus(row['status']),
                        total_queries=row['total_queries']
                    )
                return None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def update_user_login(self, user_id: int):
        """Update user's last login time"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users 
                    SET last_login = ? 
                    WHERE user_id = ?
                ''', (datetime.now(), user_id))
                conn.commit()
        except Exception as e:
            logger.error(f"Error updating user login: {e}")
    
    def update_user_status(self, user_id: int, status: UserStatus):
        """Update user status"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users 
                    SET status = ? 
                    WHERE user_id = ?
                ''', (status.value, user_id))
                conn.commit()
        except Exception as e:
            logger.error(f"Error updating user status: {e}")
    
    def increment_user_queries(self, user_id: int):
        """Increment user's total query count"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users 
                    SET total_queries = total_queries + 1 
                    WHERE user_id = ?
                ''', (user_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"Error incrementing user queries: {e}")
    
    def get_all_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        """Get all users with pagination"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM users 
                    ORDER BY created_at DESC 
                    LIMIT ? OFFSET ?
                ''', (limit, offset))
                rows = cursor.fetchall()
                
                return [
                    User(
                        user_id=row['user_id'],
                        email=row['email'],
                        full_name=row['full_name'],
                        created_at=datetime.fromisoformat(row['created_at']),
                        last_login=datetime.fromisoformat(row['last_login']) if row['last_login'] else None,
                        status=UserStatus(row['status']),
                        total_queries=row['total_queries']
                    )
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    # ==================== CONVERSATION OPERATIONS ====================
    
    def save_conversation(self, conversation: Conversation) -> Optional[int]:
        """Save a conversation to the database - returns conversation_id"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO conversations 
                    (user_id, session_id, message, response, timestamp,
                     conversation_type, response_time_ms, attachments)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    conversation.user_id,
                    getattr(conversation, 'session_id', None),
                    conversation.message,
                    conversation.response,
                    conversation.timestamp,
                    conversation.conversation_type,
                    conversation.response_time_ms,
                    conversation.attachments,
                ))
                conn.commit()
                
                # Increment user's query count
                self.increment_user_queries(conversation.user_id)
                
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            return None

    # ── NEW: return one summary row per session for the sidebar ────────────
    def get_session_summaries(self, user_id: int) -> List[dict]:
        """
        Return one entry per distinct session_id for a user.
        Each entry contains the first user message (sidebar title) and
        the timestamp of the most recent message in that session.

        Returns: [{"session_id": str, "first_message": str, "last_updated": str}, ...]
        Ordered by last_updated DESC.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    '''
                    SELECT
                        session_id,
                        MAX(timestamp) AS last_updated,
                        (
                            SELECT c2.message
                            FROM   conversations c2
                            WHERE  c2.user_id    = c.user_id
                              AND  c2.session_id = c.session_id
                            ORDER  BY c2.timestamp ASC
                            LIMIT  1
                        ) AS first_message
                    FROM conversations c
                    WHERE user_id   = ?
                      AND session_id IS NOT NULL
                      AND session_id != ''
                    GROUP BY session_id
                    ORDER BY last_updated DESC
                    ''',
                    (user_id,)
                )
                rows = cursor.fetchall()

            result = []
            for row in rows:
                result.append({
                    "session_id":    row["session_id"],
                    "first_message": row["first_message"] or "(empty)",
                    "last_updated":  row["last_updated"],
                })
            return result
        except Exception as e:
            logger.error(f"Error getting session summaries: {e}")
            return []

    # ── NEW: load all exchanges for a session (for memory restoration) ─────
    def get_conversations_by_session(self, user_id: int, session_id: str) -> List[Conversation]:
        """
        Return ALL Conversation rows for a given (user_id, session_id),
        ordered by timestamp ASC so they can be replayed in chronological order.
        Used by restore_session_from_db() to rebuild in-memory chat history.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    '''
                    SELECT *
                    FROM   conversations
                    WHERE  user_id    = ?
                      AND  session_id = ?
                    ORDER  BY timestamp ASC
                    ''',
                    (user_id, session_id)
                )
                rows = cursor.fetchall()

            return [
                Conversation(
                    conversation_id=row['conversation_id'],
                    user_id=row['user_id'],
                    session_id=row['session_id'],
                    message=row['message'],
                    response=row['response'],
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    conversation_type=row['conversation_type'],
                    response_time_ms=row['response_time_ms'],
                    attachments=row['attachments'],
                )
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Error getting conversations by session: {e}")
            return []

    def get_user_conversations(self, user_id: int, limit: int = 50) -> List[Conversation]:
        """Get all conversations for a specific user (used by admin/analytics)"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM conversations 
                    WHERE user_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (user_id, limit))
                rows = cursor.fetchall()
                
                return [
                    Conversation(
                        conversation_id=row['conversation_id'],
                        user_id=row['user_id'],
                        session_id=row['session_id'],
                        message=row['message'],
                        response=row['response'],
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        conversation_type=row['conversation_type'],
                        response_time_ms=row['response_time_ms'],
                        attachments=row['attachments'],
                    )
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"Error getting user conversations: {e}")
            return []
    
    def get_conversation_by_id(self, conversation_id: int) -> Optional[Conversation]:
        """Get a specific conversation by ID"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM conversations WHERE conversation_id = ?', (conversation_id,))
                row = cursor.fetchone()
                
                if row:
                    return Conversation(
                        conversation_id=row['conversation_id'],
                        user_id=row['user_id'],
                        session_id=row['session_id'],
                        message=row['message'],
                        response=row['response'],
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        conversation_type=row['conversation_type'],
                        response_time_ms=row['response_time_ms'],
                        attachments=row['attachments'],
                    )
                return None
        except Exception as e:
            logger.error(f"Error getting conversation by ID: {e}")
            return None
    
    def get_recent_conversations(self, limit: int = 50) -> List[Tuple[Conversation, User]]:
        """Get recent conversations (admin dashboard)"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT c.*, u.email, u.full_name 
                    FROM conversations c
                    JOIN users u ON c.user_id = u.user_id
                    ORDER BY c.timestamp DESC 
                    LIMIT ?
                ''', (limit,))
                rows = cursor.fetchall()
                
                results = []
                for row in rows:
                    conversation = Conversation(
                        conversation_id=row['conversation_id'],
                        user_id=row['user_id'],
                        session_id=row['session_id'],
                        message=row['message'],
                        response=row['response'],
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        conversation_type=row['conversation_type'],
                        response_time_ms=row['response_time_ms'],
                        attachments=row['attachments'],
                    )
                    user = User(
                        user_id=row['user_id'],
                        email=row['email'],
                        full_name=row['full_name'],
                        created_at=datetime.now(),
                        status=UserStatus.ACTIVE
                    )
                    results.append((conversation, user))
                
                return results
        except Exception as e:
            logger.error(f"Error getting recent conversations: {e}")
            return []
    
    # ==================== ADMIN OPERATIONS ====================
    
    def create_admin(self, username: str, password: str) -> Optional[int]:
        """Create admin user with hashed password"""
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            admin = AdminUser(username=username, password_hash=password_hash)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO admin_users (username, password_hash, created_at)
                    VALUES (?, ?, ?)
                ''', (admin.username, admin.password_hash, admin.created_at))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.warning(f"Admin user {username} already exists")
            return None
        except Exception as e:
            logger.error(f"Error creating admin: {e}")
            return None
    
    def verify_admin(self, username: str, password: str) -> bool:
        """Verify admin credentials"""
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM admin_users 
                    WHERE username = ? AND password_hash = ?
                ''', (username, password_hash))
                
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error verifying admin: {e}")
            return False
    
    # ==================== ANALYTICS ====================
    
    def delete_user_conversations(self, user_id: int) -> int:
        """Delete all conversations for a user. Returns number of deleted records."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM conversations WHERE user_id = ?', (user_id,))
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Error deleting conversations for user {user_id}: {e}")
            return 0

    def delete_user(self, user_id: int) -> bool:
        """Delete a user and all their conversations"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM conversations WHERE user_id = ?', (user_id,))
                cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            return False

    def get_statistics(self) -> dict:
        """Get overall statistics aggregated over the whole dataset."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) as count FROM users')
                total_users = cursor.fetchone()['count']
                
                week_ago = datetime.now() - timedelta(days=7)
                cursor.execute('''
                    SELECT COUNT(*) as count FROM users 
                    WHERE last_login >= ?
                ''', (week_ago,))
                active_users = cursor.fetchone()['count']
                
                cursor.execute('SELECT COUNT(*) as count FROM conversations')
                total_conversations = cursor.fetchone()['count']
                
                today = datetime.now().date()
                cursor.execute('''
                    SELECT COUNT(*) as count FROM conversations 
                    WHERE DATE(timestamp) = ?
                ''', (today,))
                conversations_today = cursor.fetchone()['count']
                
                cursor.execute('''
                    SELECT AVG(response_time_ms) as avg_time 
                    FROM conversations 
                    WHERE response_time_ms IS NOT NULL
                ''')
                avg_response_time = cursor.fetchone()['avg_time'] or 0
                
                return {
                    'total_users': total_users,
                    'active_users_7d': active_users,
                    'total_conversations': total_conversations,
                    'conversations_today': conversations_today,
                    'avg_response_time_ms': round(avg_response_time, 2)
                }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}

    def get_conversations_filtered(
        self,
        user_email: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        conversation_type: Optional[str] = None,
        limit: int = 200,
    ) -> List[Tuple[Conversation, User]]:
        """Get conversations with optional filters."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                query = '''
                    SELECT c.*, u.email, u.full_name 
                    FROM conversations c
                    JOIN users u ON c.user_id = u.user_id
                    WHERE 1 = 1
                '''
                params: list = []
                
                if user_email:
                    query += ' AND u.email LIKE ?'
                    params.append(f"%{user_email}%")
                
                if date_from:
                    query += ' AND c.timestamp >= ?'
                    params.append(date_from)
                
                if date_to:
                    query += ' AND c.timestamp <= ?'
                    params.append(date_to)
                
                if conversation_type:
                    query += ' AND c.conversation_type = ?'
                    params.append(conversation_type)
                
                query += ' ORDER BY c.timestamp DESC LIMIT ?'
                params.append(limit)
                
                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()
                
                results: List[Tuple[Conversation, User]] = []
                for row in rows:
                    conversation = Conversation(
                        conversation_id=row['conversation_id'],
                        user_id=row['user_id'],
                        session_id=row['session_id'],
                        message=row['message'],
                        response=row['response'],
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        conversation_type=row['conversation_type'],
                        response_time_ms=row['response_time_ms'],
                        attachments=row['attachments'],
                    )
                    user = User(
                        user_id=row['user_id'],
                        email=row['email'],
                        full_name=row['full_name'],
                        created_at=datetime.now(),
                        status=UserStatus.ACTIVE,
                    )
                    results.append((conversation, user))
                
                return results
        except Exception as e:
            logger.error(f"Error getting filtered conversations: {e}")
            return []

    def get_conversations_timeseries(self, days: int = 14) -> List[Tuple[str, int]]:
        """Get conversation counts per day for the last `days` days."""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days - 1)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    '''
                    SELECT DATE(timestamp) as day, COUNT(*) as count 
                    FROM conversations 
                    WHERE DATE(timestamp) BETWEEN ? AND ?
                    GROUP BY DATE(timestamp)
                    ORDER BY DATE(timestamp) ASC
                    ''',
                    (start_date, end_date),
                )
                rows = cursor.fetchall()
                
                return [(row['day'], row['count']) for row in rows]
        except Exception as e:
            logger.error(f"Error getting conversations timeseries: {e}")
            return []