"""Authentication helpers for the FastAPI service."""

from datetime import datetime
import logging
import re
from typing import Optional, Tuple

from domain.models import User, UserStatus
from infrastructure.database import DatabaseRepository


logger = logging.getLogger(__name__)


class AuthenticationService:
    """Resolve and validate users from upstream-provided identity data."""

    def __init__(self, db_repository: DatabaseRepository):
        self.db = db_repository

    @staticmethod
    def validate_email(email: str) -> bool:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_name(name: str) -> bool:
        return 2 <= len(name.strip()) <= 100

    def register_user(self, email: str, full_name: str) -> Tuple[bool, str, Optional[User]]:
        """Create or refresh a user record."""
        if not self.validate_email(email):
            return False, "Invalid email format", None

        if not self.validate_name(full_name):
            return False, "Name must be between 2 and 100 characters", None

        normalized_email = email.lower().strip()
        normalized_name = full_name.strip()

        existing_user = self.db.get_user_by_email(normalized_email)
        if existing_user:
            self.db.update_user_login(existing_user.user_id)
            logger.info(f"Existing user logged in: {normalized_email}")
            return True, "Welcome back!", existing_user

        user = User(
            email=normalized_email,
            full_name=normalized_name,
            created_at=datetime.now(),
            status=UserStatus.ACTIVE,
        )

        user_id = self.db.create_user(user)
        if user_id:
            user.user_id = user_id
            self.db.update_user_login(user_id)
            logger.info(f"New user registered: {normalized_email}")
            return True, "Registration successful!", user

        return False, "Failed to create user", None

    def verify_user_access(self, user_id: int) -> bool:
        """Allow only active users."""
        user = self.db.get_user_by_id(user_id)
        return bool(user and user.status == UserStatus.ACTIVE)
