"""Celery task state tracking model."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base, TimestampMixin, UUIDMixin


class CeleryTaskState(Base, UUIDMixin, TimestampMixin):
    """Model for tracking Celery task states and progress.

    This provides persistent storage for Celery task information,
    complementing the in-memory storage in app.celery.tasks.base.
    """

    __tablename__ = "celery_task_states"

    task_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    task_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )
    celery_task_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
        index=True,
    )
    state: Mapped[str] = mapped_column(
        String(50),
        default="PENDING",
        nullable=False,
        index=True,
    )
    progress: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    result: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )
    error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Foreign keys
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    requirement_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("requirements.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    task_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
    )

    # Metadata stored as JSON
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata",
        JSON,
        nullable=True,
    )

    # Timestamps
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    project: Mapped["Project | None"] = relationship(
        "Project",
        back_populates="celery_task_states",
    )
    requirement: Mapped["Requirement | None"] = relationship(
        "Requirement",
        back_populates="celery_task_states",
    )
    task: Mapped["Task | None"] = relationship(
        "Task",
        back_populates="celery_task_states",
    )

    def __repr__(self) -> str:
        return f"<CeleryTaskState(id={self.id}, task_name={self.task_name}, state={self.state})>"
