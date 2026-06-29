from datetime import datetime
import logging

from fastapi import Depends, FastAPI, HTTPException, status

from auth_service import AuthenticationService
from config import Config
from database import DatabaseRepository
from models import UserStatus
from api.auth import create_access_token, get_token_payload
from api.schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    LoginRequest,
    LoginResponse,
    ReindexResponse,
    SessionHistoryResponse,
    SessionSummary,
    UserResponse,
)
from api.service import ChatService


logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S',
)
logger = logging.getLogger(__name__)


db = DatabaseRepository(Config.API_DB_PATH)
auth = AuthenticationService(db)
chat_service: ChatService | None = None

app = FastAPI(
    title="Dnext Support Chatbot API",
    version="0.1.0",
    description="Local REST API for testing the current chatbot logic before AWS migration.",
)


def get_chat_service() -> ChatService:
    """Initialize the heavy chat stack lazily on first use."""
    global chat_service
    if chat_service is None:
        chat_service = ChatService(db, auth)
    return chat_service


def get_current_user(payload: dict = Depends(get_token_payload)) -> UserResponse:
    """Resolve the current user from the JWT payload."""
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user = db.get_user_by_id(int(user_id))
    if not user or not auth.verify_user_access(user.user_id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or blocked")

    return UserResponse(
        user_id=user.user_id,
        email=user.email,
        full_name=user.full_name,
        status=user.status.value if isinstance(user.status, UserStatus) else str(user.status),
    )


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health endpoint for local testing and containers."""
    return HealthResponse(
        status="ok",
        providers=Config.provider_summary(),
        docs_folder=Config.DOCS_FOLDER,
        timestamp=datetime.utcnow(),
    )


@app.post("/api/v1/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    """Create or reuse a local user and return a JWT for localhost testing."""
    success, message, user = auth.register_user(payload.email, payload.full_name)
    if not success or not user or not user.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    token = create_access_token(user)
    return LoginResponse(
        access_token=token,
        expires_in_minutes=Config.JWT_EXPIRE_MINUTES,
        user=UserResponse(
            user_id=user.user_id,
            email=user.email,
            full_name=user.full_name,
            status=user.status.value,
        ),
    )


@app.post("/api/v1/chat/query", response_model=ChatResponse)
def chat_query(payload: ChatRequest, current_user: UserResponse = Depends(get_current_user)):
    """Process a text query through the current RAG pipeline."""
    try:
        result = get_chat_service().process_query(
            user_id=current_user.user_id,
            query=payload.query,
            session_id=payload.session_id,
        )
        return ChatResponse(**result)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Chat query failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@app.get("/api/v1/chat/sessions", response_model=list[SessionSummary])
def list_sessions(current_user: UserResponse = Depends(get_current_user)):
    """List the current user's sessions."""
    return get_chat_service().list_sessions(current_user.user_id)


@app.get("/api/v1/chat/sessions/{session_id}", response_model=SessionHistoryResponse)
def get_session(session_id: str, current_user: UserResponse = Depends(get_current_user)):
    """Load one session history."""
    return get_chat_service().get_session_history(current_user.user_id, session_id)


@app.post("/api/v1/knowledge/reindex", response_model=ReindexResponse)
def reindex_knowledge(current_user: UserResponse = Depends(get_current_user)):
    """Rebuild the local docs index after changing files under docs_md/."""
    return get_chat_service().reindex_documents()
