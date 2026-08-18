from datetime import datetime
from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.core.security import create_access_token, decode_token
from app.models.store import User, UserStore
from app.schemas.prediction import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    UserResponse,
)

router = APIRouter(tags=["auth"])

# Simple in-memory token store for demo
# In production, use Redis or database
TOKEN_STORE: dict[str, int] = {}  # token -> user_id


async def get_current_user_id(authorization: str = Header(None)) -> int:
    """Extract user_id from Bearer token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    token = authorization[7:]
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    user = UserStore.get_by_id(payload.sub)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user.id


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest):
    if UserStore.exists(payload.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    user = User.create(email=payload.email, full_name=payload.full_name, password=payload.password)
    UserStore.add(user)
    token = create_access_token(user.id)
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(id=user.id, email=user.email, full_name=user.full_name, created_at=user.created_at),
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest):
    user = UserStore.get_by_email(payload.email)
    if user is None or not user.check_password(payload.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    token = create_access_token(user.id)
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(id=user.id, email=user.email, full_name=user.full_name, created_at=user.created_at),
    )


@router.get("/me", response_model=UserResponse)
def me(user_id: int = Depends(get_current_user_id)):
    user = UserStore.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(id=user.id, email=user.email, full_name=user.full_name, created_at=user.created_at)