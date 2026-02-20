"""
Admin authentication: verifies admin credentials against the database.
"""

import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class AdminAuth:
    """Thin wrapper around DB admin verification with login-state tracking."""

    def __init__(self, db, auth_service):
        self.db = db
        self.auth = auth_service
        self.is_authenticated = False

    def login(self, username: str, password: str) -> Tuple[bool, str]:
        if self.auth.verify_admin(username, password):
            self.is_authenticated = True
            logger.info(f"Admin logged in: {username}")
            return True, "✅ Authentication successful!"
        logger.warning(f"Failed admin login attempt: {username}")
        return False, "❌ Invalid credentials"