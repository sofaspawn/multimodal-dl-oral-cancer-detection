from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies.auth import get_current_user
from app.models import User
from app.schemas.prediction import AuthResponse, LoginRequest, RegisterRequest, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        return service.register(
            email=payload.email,
            full_name=payload.full_name,
            password=payload.password,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        return service.login(email=payload.email, password=payload.password)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    return UserResponse.model_validate(user)
