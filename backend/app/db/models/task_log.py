"""TaskLog database model for task execution logs."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base, TimestampMixin, UUIDMixin


class TaskLog(Base, UUIDMixin, TimestampMixin):
    """TaskLog model for tracking task execution logs."""

    __tablename__ = "task_logs"

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )
    log_level: Mapped[str] = mapped_column(
        String(20),
        default="info",
        nullable=False,
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata",
        JSON,
        nullable=True,
    )
    step_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    task: Mapped["Task"] = relationship(
        "Task",
        back_populates="task_logs",
    )

    def __repr__(self) -> str:
        return f"<TaskLog(id={self.id}, task_id={self.task_id}, log_level={self.log_level})>"
