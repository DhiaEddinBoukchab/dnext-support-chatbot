"""
Authentication service - SRP: Handles all authentication logic
"""

from typing import Optional, Tuple
from datetime import datetime
import re
import logging
from models import User, UserStatus
from database import DatabaseRepository


logger = logging.getLogger(__name__)


class AuthenticationService:
    """
    Authentication service - SRP: Single responsibility of managing authentication
    DIP: Depends on DatabaseRepository abstraction
    """
    
    def __init__(self, db_repository: DatabaseRepository):
        """Initialize with database repository"""
        self.db = db_repository
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_name(self, name: str) -> bool:
        """Validate name (not empty, reasonable length)"""
        return len(name.strip()) >= 2 and len(name.strip()) <= 100
    
    def register_user(self, email: str, full_name: str) -> Tuple[bool, str, Optional[User]]:
        """
        Register a new user
        Returns: (success, message, user)
        """
        # Validate email
        if not self.validate_email(email):
            return False, "Invalid email format", None
        
        # Validate name
        if not self.validate_name(full_name):
            return False, "Name must be between 2 and 100 characters", None
        
        # Check if user exists
        existing_user = self.db.get_user_by_email(email)
        if existing_user:
            # User exists - just update login time and return
            self.db.update_user_login(existing_user.user_id)
            logger.info(f"Existing user logged in: {email}")
            return True, "Welcome back!", existing_user
        
        # Create new user
        user = User(
            email=email.lower().strip(),
            full_name=full_name.strip(),
            created_at=datetime.now(),
            status=UserStatus.ACTIVE
        )
        
        user_id = self.db.create_user(user)
        if user_id:
            user.user_id = user_id
            self.db.update_user_login(user_id)
            logger.info(f"New user registered: {email}")
            return True, "Registration successful!", user
        
        return False, "Failed to create user", None
    
    def verify_user_access(self, user_id: int) -> bool:
        """Check if user has access (not blocked)"""
        user = self.db.get_user_by_id(user_id)
        if not user:
            return False
        
        return user.status == UserStatus.ACTIVE
    
    def verify_admin(self, username: str, password: str) -> bool:
        """Verify admin credentials"""
        return self.db.verify_admin(username, password)