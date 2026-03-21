"""Project database model."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base, TimestampMixin, UUIDMixin


class Project(Base, UUIDMixin, TimestampMixin):
    """Project model for mobile app development projects."""

    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    platform: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="planning",
        nullable=False,
    )
    repository_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    tech_stack: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )
    architecture: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    environment_variables: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )
    settings: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    requirements: Mapped[list["Requirement"]] = relationship(
        "Requirement",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    memberships: Mapped[list["ProjectMembership"]] = relationship(
        "ProjectMembership",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    cost_records: Mapped[list["CostRecord"]] = relationship(
        "CostRecord",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    celery_task_states: Mapped[list["CeleryTaskState"]] = relationship(
        "CeleryTaskState",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    metrics: Mapped[list["Metric"]] = relationship(
        "Metric",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name}, platform={self.platform})>"
