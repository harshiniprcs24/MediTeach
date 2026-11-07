from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.schemas.user import UserRegister, UserLogin, TokenResponse, ForgotPasswordRequest, RefreshTokenRequest
from app.services.auth_service import AuthService
from app.core.security import get_current_user_id

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""
    service = AuthService(db)
    return await service.register(payload)


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate and receive access + refresh tokens."""
    service = AuthService(db)
    return await service.login(payload)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(user_id: str = Depends(get_current_user_id)):
    """Logout current user (client should discard tokens)."""
    return None


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(payload: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Send a password reset email."""
    service = AuthService(db)
    await service.forgot_password(payload.email)
    return {"message": "If that email exists, a reset link has been sent."}


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Exchange a refresh token for a new access token."""
    service = AuthService(db)
    return await service.refresh_tokens(payload.refresh_token)
