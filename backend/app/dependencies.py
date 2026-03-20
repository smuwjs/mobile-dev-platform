"""FastAPI dependencies for dependency injection."""

import uuid
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory
from app.db.models import User


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
    db: DbSession,
    # In a real implementation, this would verify JWT token
    # For now, we use a placeholder that would be replaced with actual auth
) -> User:
    """Get current authenticated user.

    This is a placeholder. In production, this would:
    1. Extract JWT token from Authorization header
    2. Verify the token signature and expiration
    3. Look up the user from the database
    4. Return the user object

    Raises HTTPException if not authenticated.
    """
    # TODO: Implement actual JWT verification
    # For now, raise unauthorized error
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user_optional(
    db: DbSession,
) -> User | None:
    """Get current user if authenticated, None otherwise."""
    try:
        return await get_current_user(db)
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
