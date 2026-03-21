"""Requirement database model."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base, TimestampMixin, UUIDMixin


class Requirement(Base, UUIDMixin, TimestampMixin):
    """Requirement model for project requirements with tree structure."""

    __tablename__ = "requirements"

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    priority: Mapped[int] = mapped_column(
        default=3,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
    )
    complexity: Mapped[int] = mapped_column(
        default=1,
        nullable=False,
    )
    estimated_hours: Mapped[float | None] = mapped_column(
        nullable=True,
    )
    actual_hours: Mapped[float] = mapped_column(
        default=0.0,
        nullable=False,
    )
    sort_order: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("requirements.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="requirements",
    )
    parent: Mapped["Requirement | None"] = relationship(
        "Requirement",
        remote_side="Requirement.id",
        back_populates="children",
    )
    children: Mapped[list["Requirement"]] = relationship(
        "Requirement",
        back_populates="parent",
        cascade="all, delete-orphan",
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="requirement",
        cascade="all, delete-orphan",
    )
    celery_task_states: Mapped[list["CeleryTaskState"]] = relationship(
        "CeleryTaskState",
        back_populates="requirement",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Requirement(id={self.id}, title={self.title})>"
