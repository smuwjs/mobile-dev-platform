"""Alert database model for tracking execution alerts and anomalies."""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base, TimestampMixin, UUIDMixin


class AlertType(str, Enum):
    """Types of alerts that can be generated."""

    TIMEOUT = "timeout"  # No output timeout (5 minutes)
    COMPILE_ERROR = "compile_error"  # Compilation failure detected
    API_RATE_LIMIT = "api_rate_limit"  # API rate limit exceeded
    EXECUTION_ERROR = "execution_error"  # General execution error
    SESSION_TERMINATED = "session_terminated"  # Session unexpectedly terminated
    RESOURCE_EXHAUSTED = "resource_exhausted"  # Out of memory or disk


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Alert status."""

    PENDING = "pending"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class Alert(Base, UUIDMixin, TimestampMixin):
    """Alert model for tracking execution anomalies and warnings."""

    __tablename__ = "alerts"

    alert_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default=AlertStatus.PENDING.value,
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    execution_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )
    task_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    acknowledged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata",
        JSON,
        nullable=True,
    )

    # Relationships
    task: Mapped["Task | None"] = relationship(
        "Task",
        back_populates="alerts",
    )
    project: Mapped["Project | None"] = relationship(
        "Project",
        back_populates="alerts",
    )

    def __repr__(self) -> str:
        return f"<Alert(id={self.id}, type={self.alert_type}, severity={self.severity})>"