"""
User management: fetch user details and update user status.
"""

import logging
from models import UserStatus

logger = logging.getLogger(__name__)


class UserManager:
    """Handles user detail queries and status mutations."""

    def __init__(self, db):
        self.db = db

    def get_user_details_md(self, user_id: int) -> str:
        """Return Markdown-formatted user details."""
        if not user_id:
            return "Please enter a user ID."

        user = self.db.get_user_by_id(user_id)
        if not user:
            return f"❌ User with ID {user_id} not found."

        conversations = self.db.get_user_conversations(user_id, limit=10)
        return f"""
## 👤 User Details

**Basic Information**
- User ID: {user.user_id}
- Email: {user.email}
- Full Name: {user.full_name}
- Status: {user.status.value}

**Activity**
- Total Queries: {user.total_queries}
- Created: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}
- Last Login: {user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never'}

**Recent Conversations:** {len(conversations)}
"""

    def update_status(self, user_id: int, new_status: str) -> str:
        """Update a user's status. Returns a result message."""
        if not user_id:
            return "Please enter a user ID."

        user = self.db.get_user_by_id(user_id)
        if not user:
            return f"❌ User with ID {user_id} not found."

        try:
            status = UserStatus(new_status.lower())
            self.db.update_user_status(user_id, status)
            return f"✅ User {user_id} status updated to **{status.value}**."
        except ValueError:
            return f"❌ Invalid status: {new_status}. Valid values: active, inactive, blocked."