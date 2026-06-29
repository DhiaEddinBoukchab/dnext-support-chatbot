"""Shared FastAPI dependencies and runtime singletons."""

from fastapi import Header, HTTPException, status

from api.schemas import UserResponse
from core.config import Config
from infrastructure.database import DatabaseRepository
from services.auth import AuthenticationService
from services.chat import ChatService


db = DatabaseRepository(Config.API_DB_PATH)
auth = AuthenticationService(db)
chat_service: ChatService | None = None


def get_chat_service() -> ChatService:
    """Initialize the heavy chat stack lazily on first use."""
    global chat_service
    if chat_service is None:
        chat_service = ChatService(db, auth)
    return chat_service


def get_current_user(
    x_user_email: str | None = Header(default=None, alias="X-User-Email"),
    x_user_name: str | None = Header(default=None, alias="X-User-Name"),
) -> UserResponse:
    """Resolve the current user from upstream-provided identity headers."""
    if not x_user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-User-Email header",
        )

    full_name = x_user_name or x_user_email.split("@", 1)[0].replace(".", " ").title()
    success, message, user = auth.register_user(x_user_email, full_name)
    if not success or not user or not user.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    if not auth.verify_user_access(user.user_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or blocked",
        )

    return UserResponse(
        user_id=user.user_id,
        email=user.email,
        full_name=user.full_name,
        status=getattr(user.status, "value", str(user.status)),
    )
