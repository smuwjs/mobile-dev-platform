"""API Key management endpoints."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory
from app.db.models import User
from app.services.api_key import APIKeyService
from app.dependencies import get_current_user

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


async def get_db():
    """Dependency for database session."""
    async with async_session_factory() as session:
        yield session


class APIKeyCreateRequest(BaseModel):
    """Request model for creating an API key."""

    name: str
    user_id: UUID | None = None
    project_id: UUID | None = None
    expires_in_days: int | None = None
    rate_limit: int = 100
    rate_limit_window: int = 60
    permissions: dict | None = None


class APIKeyCreateResponse(BaseModel):
    """Response model for API key creation."""

    id: UUID
    name: str
    key: str  # Only shown once at creation!
    key_prefix: str
    user_id: UUID | None
    project_id: UUID | None
    is_active: bool
    is_system: bool
    expires_at: datetime | None
    rate_limit: int
    rate_limit_window: int
    permissions: dict | None
    created_at: datetime


class APIKeyResponse(BaseModel):
    """Response model for API key (without the actual key)."""

    id: UUID
    name: str
    key_prefix: str
    user_id: UUID | None
    project_id: UUID | None
    is_active: bool
    is_system: bool
    is_expired: bool
    is_valid: bool
    last_used_at: datetime | None
    expires_at: datetime | None
    rate_limit: int
    rate_limit_window: int
    permissions: dict | None
    created_at: datetime


class APIKeyUpdateRequest(BaseModel):
    """Request model for updating an API key."""

    name: str | None = None
    rate_limit: int | None = None
    rate_limit_window: int | None = None
    is_active: bool | None = None


@router.post("/", response_model=APIKeyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    request: APIKeyCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Create a new API key.

    The actual API key is only returned once at creation time.
    Store it securely - it cannot be retrieved again!
    """
    service = APIKeyService(db)

    api_key, plain_key = await service.create_api_key(
        name=request.name,
        user_id=request.user_id,
        project_id=request.project_id,
        expires_in_days=request.expires_in_days,
        rate_limit=request.rate_limit,
        rate_limit_window=request.rate_limit_window,
        permissions=request.permissions,
    )

    return APIKeyCreateResponse(
        id=api_key.id,
        name=api_key.name,
        key=plain_key,  # Only available at creation!
        key_prefix=api_key.key_prefix,
        user_id=api_key.user_id,
        project_id=api_key.project_id,
        is_active=api_key.is_active,
        is_system=api_key.is_system,
        expires_at=api_key.expires_at,
        rate_limit=api_key.rate_limit,
        rate_limit_window=api_key.rate_limit_window,
        permissions=api_key.permissions,
        created_at=api_key.created_at,
    )


@router.get("/", response_model=list[APIKeyResponse])
async def list_api_keys(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    include_system: bool = False,
):
    """List all API keys (optionally filtered)."""
    service = APIKeyService(db)
    keys = await service.list_active_keys(include_system=include_system)
    return [
        APIKeyResponse(
            id=k.id,
            name=k.name,
            key_prefix=k.key_prefix,
            user_id=k.user_id,
            project_id=k.project_id,
            is_active=k.is_active,
            is_system=k.is_system,
            is_expired=k.is_expired,
            is_valid=k.is_valid,
            last_used_at=k.last_used_at,
            expires_at=k.expires_at,
            rate_limit=k.rate_limit,
            rate_limit_window=k.rate_limit_window,
            permissions=k.permissions,
            created_at=k.created_at,
        )
        for k in keys
    ]


@router.get("/{key_id}", response_model=APIKeyResponse)
async def get_api_key(
    key_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get an API key by ID."""
    service = APIKeyService(db)
    api_key = await service.get_api_key_by_id(key_id)

    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    return APIKeyResponse(
        id=api_key.id,
        name=api_key.name,
        key_prefix=api_key.key_prefix,
        user_id=api_key.user_id,
        project_id=api_key.project_id,
        is_active=api_key.is_active,
        is_system=api_key.is_system,
        is_expired=api_key.is_expired,
        is_valid=api_key.is_valid,
        last_used_at=api_key.last_used_at,
        expires_at=api_key.expires_at,
        rate_limit=api_key.rate_limit,
        rate_limit_window=api_key.rate_limit_window,
        permissions=api_key.permissions,
        created_at=api_key.created_at,
    )


@router.patch("/{key_id}", response_model=APIKeyResponse)
async def update_api_key(
    key_id: UUID,
    request: APIKeyUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Update an API key."""
    service = APIKeyService(db)
    api_key = await service.get_api_key_by_id(key_id)

    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    if request.rate_limit is not None and request.rate_limit_window is not None:
        await service.update_rate_limit(key_id, request.rate_limit, request.rate_limit_window)

    if request.is_active is not None:
        api_key.is_active = request.is_active
        await db.commit()
        await db.refresh(api_key)

    return APIKeyResponse(
        id=api_key.id,
        name=api_key.name,
        key_prefix=api_key.key_prefix,
        user_id=api_key.user_id,
        project_id=api_key.project_id,
        is_active=api_key.is_active,
        is_system=api_key.is_system,
        is_expired=api_key.is_expired,
        is_valid=api_key.is_valid,
        last_used_at=api_key.last_used_at,
        expires_at=api_key.expires_at,
        rate_limit=api_key.rate_limit,
        rate_limit_window=api_key.rate_limit_window,
        permissions=api_key.permissions,
        created_at=api_key.created_at,
    )


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Delete an API key permanently."""
    service = APIKeyService(db)
    deleted = await service.delete_api_key(key_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )


@router.post("/{key_id}/deactivate", response_model=APIKeyResponse)
async def deactivate_api_key(
    key_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Deactivate an API key (can be reactivated later)."""
    service = APIKeyService(db)
    api_key = await service.get_api_key_by_id(key_id)

    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    await service.deactivate_api_key(key_id)
    await db.refresh(api_key)

    return APIKeyResponse(
        id=api_key.id,
        name=api_key.name,
        key_prefix=api_key.key_prefix,
        user_id=api_key.user_id,
        project_id=api_key.project_id,
        is_active=api_key.is_active,
        is_system=api_key.is_system,
        is_expired=api_key.is_expired,
        is_valid=api_key.is_valid,
        last_used_at=api_key.last_used_at,
        expires_at=api_key.expires_at,
        rate_limit=api_key.rate_limit,
        rate_limit_window=api_key.rate_limit_window,
        permissions=api_key.permissions,
        created_at=api_key.created_at,
    )
