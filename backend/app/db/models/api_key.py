"""API Key database model for managing Claude API access."""

import uuid
import secrets
from datetime import datetime

from sqlalchemy import DateTime, String, Boolean, Integer, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base, TimestampMixin, UUIDMixin


class APIKey(Base, UUIDMixin, TimestampMixin):
    """API Key model for managing Claude Code API access."""

    __tablename__ = "api_keys"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    key_hash: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    key_prefix: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_system: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    rate_limit: Mapped[int] = mapped_column(
        Integer,
        default=100,
        nullable=False,
    )
    rate_limit_window: Mapped[int] = mapped_column(
        Integer,
        default=60,
        nullable=False,
    )
    permissions: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # Relationships
    user: Mapped["User | None"] = relationship("User", foreign_keys=[user_id])
    project: Mapped["Project | None"] = relationship("Project", foreign_keys=[project_id])

    def __repr__(self) -> str:
        return f"<APIKey(id={self.id}, name={self.name}, prefix={self.key_prefix})>"

    @property
    def is_expired(self) -> bool:
        """Check if the API key has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    @property
    def is_valid(self) -> bool:
        """Check if the API key is valid (active and not expired)."""
        return self.is_active and not self.is_expired


def generate_api_key() -> tuple[str, str]:
    """Generate a new API key and its hash.

    Returns:
        Tuple of (plain_key, hashed_key)
        The plain_key should be shown to the user once and never stored.
    """
    plain_key = f"oc_{secrets.token_urlsafe(32)}"
    import hashlib
    key_hash = hashlib.sha256(plain_key.encode()).hexdigest()
    return plain_key, key_hash


def get_key_prefix(key: str) -> str:
    """Get the prefix of an API key for identification."""
    return key[:16]
