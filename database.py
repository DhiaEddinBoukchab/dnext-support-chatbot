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
            
            # Users table
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
            
            # Conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    response TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    conversation_type TEXT DEFAULT 'TECHNICAL',
                    response_time_ms INTEGER,
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
            
            # Create indexes for better query performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_conversations_user_id 
                ON conversations(user_id)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_conversations_timestamp 
                ON conversations(timestamp)
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
        """Save a conversation - returns conversation_id"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO conversations 
                    (user_id, message, response, timestamp, conversation_type, response_time_ms)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    conversation.user_id,
                    conversation.message,
                    conversation.response,
                    conversation.timestamp,
                    conversation.conversation_type,
                    conversation.response_time_ms
                ))
                conn.commit()
                
                # Increment user's query count
                self.increment_user_queries(conversation.user_id)
                
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            return None
    
    def get_user_conversations(self, user_id: int, limit: int = 50) -> List[Conversation]:
        """Get all conversations for a specific user"""
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
                        message=row['message'],
                        response=row['response'],
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        conversation_type=row['conversation_type'],
                        response_time_ms=row['response_time_ms']
                    )
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"Error getting user conversations: {e}")
            return []
    
    def get_recent_conversations(self, limit: int = 100) -> List[Tuple[Conversation, User]]:
        """Get recent conversations across all users"""
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
                        message=row['message'],
                        response=row['response'],
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        conversation_type=row['conversation_type'],
                        response_time_ms=row['response_time_ms']
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
                # Delete conversations first (foreign key constraint)
                cursor.execute('DELETE FROM conversations WHERE user_id = ?', (user_id,))
                # Then delete the user
                cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            return False

    def get_statistics(self) -> dict:
        """Get overall statistics"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Total users
                cursor.execute('SELECT COUNT(*) as count FROM users')
                total_users = cursor.fetchone()['count']
                
                # Active users (logged in last 7 days)
                week_ago = datetime.now() - timedelta(days=7)
                cursor.execute('''
                    SELECT COUNT(*) as count FROM users 
                    WHERE last_login >= ?
                ''', (week_ago,))
                active_users = cursor.fetchone()['count']
                
                # Total conversations
                cursor.execute('SELECT COUNT(*) as count FROM conversations')
                total_conversations = cursor.fetchone()['count']
                
                # Conversations today
                today = datetime.now().date()
                cursor.execute('''
                    SELECT COUNT(*) as count FROM conversations 
                    WHERE DATE(timestamp) = ?
                ''', (today,))
                conversations_today = cursor.fetchone()['count']
                
                # Average response time
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