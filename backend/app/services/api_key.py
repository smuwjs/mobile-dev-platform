"""API Key management service for Claude Code API access."""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.api_key import APIKey, generate_api_key, get_key_prefix


class APIKeyService:
    """Service for managing API keys."""

    def __init__(self, db: AsyncSession):
        """Initialize the API key service."""
        self.db = db

    async def create_api_key(
        self,
        name: str,
        user_id: UUID | None = None,
        project_id: UUID | None = None,
        expires_in_days: int | None = None,
        rate_limit: int = 100,
        rate_limit_window: int = 60,
        permissions: dict | None = None,
        is_system: bool = False,
    ) -> tuple[APIKey, str]:
        """Create a new API key.

        Args:
            name: Human-readable name for the key
            user_id: Optional user ID to associate with the key
            project_id: Optional project ID to associate with the key
            expires_in_days: Number of days until expiration (None = never)
            rate_limit: Maximum requests per window
            rate_limit_window: Window size in seconds
            permissions: Optional permission restrictions
            is_system: Whether this is a system-level key

        Returns:
            Tuple of (APIKey model, plain_key)
            The plain_key is only available at creation time - store it securely!
        """
        plain_key, key_hash = generate_api_key()
        key_prefix = get_key_prefix(plain_key)

        expires_at = None
        if expires_in_days is not None:
            expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

        api_key = APIKey(
            name=name,
            key_hash=key_hash,
            key_prefix=key_prefix,
            user_id=user_id,
            project_id=project_id,
            is_system=is_system,
            expires_at=expires_at,
            rate_limit=rate_limit,
            rate_limit_window=rate_limit_window,
            permissions=permissions,
        )

        self.db.add(api_key)
        await self.db.commit()
        await self.db.refresh(api_key)

        return api_key, plain_key

    async def verify_api_key(self, plain_key: str) -> APIKey | None:
        """Verify an API key and return the associated model.

        Args:
            plain_key: The plain text API key

        Returns:
            APIKey model if valid, None if invalid
        """
        key_hash = hashlib.sha256(plain_key.encode()).hexdigest()

        result = await self.db.execute(
            select(APIKey).where(
                APIKey.key_hash == key_hash,
                APIKey.is_active == True,
            )
        )
        api_key = result.scalar_one_or_none()

        if api_key is None:
            return None

        if not api_key.is_valid:
            return None

        # Update last used timestamp
        await self.db.execute(
            update(APIKey)
            .where(APIKey.id == api_key.id)
            .values(last_used_at=datetime.now(timezone.utc))
        )
        await self.db.commit()

        return api_key

    async def get_api_key_by_id(self, key_id: UUID) -> APIKey | None:
        """Get an API key by its ID."""
        result = await self.db.execute(
            select(APIKey).where(APIKey.id == key_id)
        )
        return result.scalar_one_or_none()

    async def get_api_keys_for_user(self, user_id: UUID) -> list[APIKey]:
        """Get all API keys for a user."""
        result = await self.db.execute(
            select(APIKey)
            .where(APIKey.user_id == user_id)
            .order_by(APIKey.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_api_keys_for_project(self, project_id: UUID) -> list[APIKey]:
        """Get all API keys for a project."""
        result = await self.db.execute(
            select(APIKey)
            .where(APIKey.project_id == project_id)
            .order_by(APIKey.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_active_keys(
        self,
        include_system: bool = True,
        limit: int = 100,
    ) -> list[APIKey]:
        """List all active API keys."""
        query = select(APIKey).where(APIKey.is_active == True)

        if not include_system:
            query = query.where(APIKey.is_system == False)

        query = query.order_by(APIKey.created_at.desc()).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def deactivate_api_key(self, key_id: UUID) -> bool:
        """Deactivate an API key.

        Args:
            key_id: The ID of the key to deactivate

        Returns:
            True if deactivated, False if not found
        """
        result = await self.db.execute(
            update(APIKey)
            .where(APIKey.id == key_id)
            .values(is_active=False)
        )
        await self.db.commit()
        return result.rowcount > 0

    async def delete_api_key(self, key_id: UUID) -> bool:
        """Delete an API key permanently.

        Args:
            key_id: The ID of the key to delete

        Returns:
            True if deleted, False if not found
        """
        api_key = await self.get_api_key_by_id(key_id)
        if api_key is None:
            return False

        await self.db.delete(api_key)
        await self.db.commit()
        return True

    async def update_rate_limit(
        self,
        key_id: UUID,
        rate_limit: int,
        rate_limit_window: int,
    ) -> bool:
        """Update rate limit settings for an API key."""
        result = await self.db.execute(
            update(APIKey)
            .where(APIKey.id == key_id)
            .values(rate_limit=rate_limit, rate_limit_window=rate_limit_window)
        )
        await self.db.commit()
        return result.rowcount > 0

    def check_rate_limit(self, api_key: APIKey, request_count: int) -> bool:
        """Check if a request is within rate limits.

        Args:
            api_key: The API key to check
            request_count: Number of requests made in the current window

        Returns:
            True if within limits, False if exceeded
        """
        return request_count < api_key.rate_limit
