"""Auth API endpoints for user registration, login, and profile."""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from app.config import settings
from app.dependencies import CurrentUser
from app.services.auth import (
    create_access_token,
    create_user,
    get_user_by_email,
    get_user_by_username,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


# Pydantic schemas
class UserRegister(BaseModel):
    """User registration request schema."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6, max_length=100)
    full_name: str | None = Field(None, max_length=255)


class UserLogin(BaseModel):
    """User login request schema."""

    username: str
    password: str


class TokenResponse(BaseModel):
    """JWT token response schema."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """User response schema."""

    id: str
    email: str
    username: str
    full_name: str | None
    avatar_url: str | None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister) -> UserResponse:
    """Register a new user."""
    # Check if email already exists
    if get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Check if username already exists
    if get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    # Create user
    user = create_user(
        email=user_data.email,
        username=user_data.username,
        password=user_data.password,
        full_name=user_data.full_name,
    )

    return UserResponse(
        id=str(user["id"]),
        email=user["email"],
        username=user["username"],
        full_name=user.get("full_name"),
        avatar_url=user.get("avatar_url"),
        is_active=user.get("is_active", True),
        created_at=user["created_at"],
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin) -> TokenResponse:
    """Login and get JWT access token."""
    user = get_user_by_username(credentials.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
        )

    # Generate JWT token
    expires_delta = timedelta(minutes=settings.jwt.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user["id"]), "username": user["username"]},
        expires_delta=expires_delta,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.jwt.access_token_expire_minutes * 60,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: CurrentUser) -> UserResponse:
    """Get current authenticated user information."""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        avatar_url=current_user.avatar_url,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
    )
