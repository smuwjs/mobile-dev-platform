"""Metric database model for tracking quantitative data."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base, TimestampMixin, UUIDMixin


class Metric(Base, UUIDMixin, TimestampMixin):
    """Metric model for tracking quantitative data."""

    __tablename__ = "metrics"

    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    task_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    metric_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    metric_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    value: Mapped[float] = mapped_column(
        Numeric(12, 4),
        nullable=False,
    )
    unit: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata",
        JSON,
        nullable=True,
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # Relationships
    project: Mapped["Project | None"] = relationship(
        "Project",
        back_populates="metrics",
    )
    task: Mapped["Task | None"] = relationship(
        "Task",
        back_populates="metrics",
    )

    def __repr__(self) -> str:
        return f"<Metric(id={self.id}, name={self.metric_name}, value={self.value})>"


# Metric types for common tracking
class MetricNames:
    """Standard metric names."""

    TOKEN_USAGE_INPUT = "token_usage_input"
    TOKEN_USAGE_OUTPUT = "token_usage_output"
    DURATION_SECONDS = "duration_seconds"
    COST_TOTAL = "cost_total"
    COST_TOKEN = "cost_token"
    COST_LABOR = "cost_labor"
    API_CALLS = "api_calls"
    ERROR_COUNT = "error_count"
    LINES_OF_CODE = "lines_of_code"
    TEST_COVERAGE = "test_coverage"


class MetricTypes:
    """Standard metric types."""

    COUNTER = "counter"
    GAUGE = "gauge"
    TIMER = "timer"
    COST = "cost"
