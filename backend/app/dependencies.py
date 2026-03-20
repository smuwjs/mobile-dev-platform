"""FastAPI dependencies for dependency injection."""

import uuid
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory
from app.db.models import User
from app.services.auth import decode_access_token, get_user_by_id

# HTTP Bearer security scheme
security = HTTPBearer()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Database session dependency."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Type alias for database dependency
DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> User:
    """Get current authenticated user from JWT token.

    Extracts JWT token from Authorization header, verifies it,
    and returns the corresponding user.

    Raises HTTPException if not authenticated.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise credentials_exception

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # Try to get user from in-memory store first
    from app.services.auth import get_user_by_id as get_auth_user

    user_data = get_auth_user(user_id)
    if user_data is None:
        raise credentials_exception

    # Get user from database
    async with async_session_factory() as session:
        from sqlalchemy import select

        result = await session.execute(select(User).where(User.id == uuid.UUID(user_id)))
        user = result.scalar_one_or_none()

        if user is None:
            raise credentials_exception

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
            )

        return user


async def get_current_user_optional(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)] = None,
) -> User | None:
    """Get current user if authenticated, None otherwise."""
    if credentials is None:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


# Type aliases for dependencies
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentUserOptional = Annotated[User | None, Depends(get_current_user_optional)]


async def require_project_member(
    project_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    """Check if current user is a member of the project.

    Raises HTTPException if not a member.
    """
    # TODO: Implement project membership check
    pass


async def require_project_owner(
    project_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    """Check if current user is the owner of the project.

    Raises HTTPException if not the owner.
    """
    # TODO: Implement project ownership check
    pass
