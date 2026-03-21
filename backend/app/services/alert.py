"""Alert service for detecting and managing execution anomalies.

This service provides:
- No-output timeout detection (5 minutes)
- Compilation failure detection
- API rate limit detection and automatic handling
- Alert generation, acknowledgment, and resolution
"""

import asyncio
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class AlertType(str, Enum):
    """Types of alerts."""

    TIMEOUT = "timeout"
    COMPILE_ERROR = "compile_error"
    API_RATE_LIMIT = "api_rate_limit"
    EXECUTION_ERROR = "execution_error"
    SESSION_TERMINATED = "session_terminated"
    RESOURCE_EXHAUSTED = "resource_exhausted"


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


@dataclass
class Alert:
    """Alert data structure."""

    id: str
    alert_type: AlertType
    severity: AlertSeverity
    status: AlertStatus
    title: str
    message: str
    execution_id: str | None = None
    task_id: str | None = None
    project_id: str | None = None
    triggered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    acknowledged_at: datetime | None = None
    resolved_at: datetime | None = None
    metadata: dict = field(default_factory=dict)


class AlertService:
    """Service for alert detection and management.

    Provides:
    - Timeout detection (no output for 5 minutes)
    - Compilation error detection
    - API rate limit detection and handling
    - Alert lifecycle management
    """

    # Timeout threshold in seconds (5 minutes)
    NO_OUTPUT_TIMEOUT_SECONDS = 300

    # Common compilation error patterns
    COMPILE_ERROR_PATTERNS = [
        re.compile(r"error[:\s]+(.+)", re.IGNORECASE),
        re.compile(r"failed to compile", re.IGNORECASE),
        re.compile(r"compilation failed", re.IGNORECASE),
        re.compile(r"SyntaxError:"),
        re.compile(r"ImportError:"),
        re.compile(r"ModuleNotFoundError:"),
        re.compile(r"TypeError:.*cannot be compiled", re.IGNORECASE),
        re.compile(r"\[(\d+)\]\s*error", re.IGNORECASE),
        re.compile(r"Build failed", re.IGNORECASE),
        re.compile(r"make.*failed", re.IGNORECASE),
        re.compile(r"npm ERR!", re.IGNORECASE),
        re.compile(r"cargo.*error", re.IGNORECASE),
        re.compile(r"gradle.*failed", re.IGNORECASE),
        re.compile(r"compilation error", re.IGNORECASE),
        re.compile(r"Command failed with exit code", re.IGNORECASE),
    ]

    # API rate limit patterns
    RATE_LIMIT_PATTERNS = [
        re.compile(r"rate.?limit", re.IGNORECASE),
        re.compile(r"too many requests", re.IGNORECASE),
        re.compile(r"429\s", re.IGNORECASE),
        re.compile(r"retry.?after", re.IGNORECASE),
        re.compile(r"quota exceeded", re.IGNORECASE),
        re.compile(r"max.?retries", re.IGNORECASE),
        re.compile(r"throttl", re.IGNORECASE),
    ]

    def __init__(self):
        """Initialize the alert service."""
        self._alerts: dict[str, Alert] = {}
        self._execution_last_output: dict[str, datetime] = {}
        self._rate_limit_backoff: dict[str, int] = {}  # execution_id -> backoff seconds
        self._monitoring_tasks: dict[str, asyncio.Task] = {}

    def _create_alert(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        title: str,
        message: str,
        execution_id: str | None = None,
        task_id: str | None = None,
        project_id: str | None = None,
        metadata: dict | None = None,
    ) -> Alert:
        """Create and store a new alert."""
        alert_id = str(uuid.uuid4())
        alert = Alert(
            id=alert_id,
            alert_type=alert_type,
            severity=severity,
            status=AlertStatus.PENDING,
            title=title,
            message=message,
            execution_id=execution_id,
            task_id=task_id,
            project_id=project_id,
            triggered_at=datetime.now(timezone.utc),
            metadata=metadata or {},
        )
        self._alerts[alert_id] = alert
        return alert

    def record_output(self, execution_id: str) -> None:
        """Record that output was received for an execution.

        Used for timeout detection.
        """
        self._execution_last_output[execution_id] = datetime.now(timezone.utc)

    def check_timeout(self, execution_id: str) -> Alert | None:
        """Check if an execution has timed out (no output for 5 minutes).

        Args:
            execution_id: The execution identifier

        Returns:
            Alert if timeout detected, None otherwise
        """
        if execution_id not in self._execution_last_output:
            return None

        last_output = self._execution_last_output[execution_id]
        now = datetime.now(timezone.utc)
        elapsed = (now - last_output).total_seconds()

        if elapsed >= self.NO_OUTPUT_TIMEOUT_SECONDS:
            return self._create_alert(
                alert_type=AlertType.TIMEOUT,
                severity=AlertSeverity.WARNING,
                title=f"Execution timeout: no output for {int(elapsed)} seconds",
                message=f"Execution {execution_id} has not produced output for {int(elapsed)} seconds (threshold: {self.NO_OUTPUT_TIMEOUT_SECONDS}s). "
                        "This may indicate the process is stuck or waiting for input.",
                execution_id=execution_id,
                metadata={
                    "elapsed_seconds": elapsed,
                    "threshold_seconds": self.NO_OUTPUT_TIMEOUT_SECONDS,
                    "last_output_at": last_output.isoformat(),
                },
            )
        return None

    def check_compile_errors(self, output: str, execution_id: str | None = None) -> list[Alert]:
        """Check output for compilation errors.

        Args:
            output: The output to check
            execution_id: Optional execution identifier

        Returns:
            List of alerts for detected compilation errors
        """
        alerts = []
        lines = output.split("\n")

        for i, line in enumerate(lines):
            for pattern in self.COMPILE_ERROR_PATTERNS:
                match = pattern.search(line)
                if match:
                    error_msg = match.group(1) if match.groups() else line.strip()
                    alerts.append(self._create_alert(
                        alert_type=AlertType.COMPILE_ERROR,
                        severity=AlertSeverity.ERROR,
                        title=f"Compilation error detected: {error_msg[:50]}",
                        message=f"Compilation error found at line {i+1}: {line.strip()}",
                        execution_id=execution_id,
                        metadata={
                            "line_number": i + 1,
                            "error_line": line.strip(),
                            "error_type": "compile_error",
                            "matched_pattern": pattern.pattern,
                        },
                    ))
                    break  # Only alert once per line
        return alerts

    def check_rate_limit(self, output: str, execution_id: str | None = None) -> Alert | None:
        """Check output for API rate limit indicators.

        Args:
            output: The output to check
            execution_id: Optional execution identifier

        Returns:
            Alert if rate limit detected, None otherwise
        """
        for pattern in self.RATE_LIMIT_PATTERNS:
            if pattern.search(output):
                current_backoff = self._rate_limit_backoff.get(execution_id or "", 60)
                return self._create_alert(
                    alert_type=AlertType.API_RATE_LIMIT,
                    severity=AlertSeverity.WARNING,
                    title="API rate limit detected",
                    message=f"API rate limit detected. Automatic backoff of {current_backoff}s recommended before retry.",
                    execution_id=execution_id,
                    metadata={
                        "recommended_backoff_seconds": current_backoff,
                        "matched_pattern": pattern.pattern,
                    },
                )
        return None

    def get_rate_limit_backoff(self, execution_id: str) -> int:
        """Get the current backoff time for an execution after rate limit.

        Args:
            execution_id: The execution identifier

        Returns:
            Backoff time in seconds (60, 120, 240, 480...)
        """
        return self._rate_limit_backoff.get(execution_id, 60)

    def increase_rate_limit_backoff(self, execution_id: str) -> int:
        """Increase the backoff time for an execution after rate limit.

        Args:
            execution_id: The execution identifier

        Returns:
            New backoff time in seconds
        """
        current = self._rate_limit_backoff.get(execution_id, 60)
        new_backoff = min(current * 2, 3600)  # Max 1 hour
        self._rate_limit_backoff[execution_id] = new_backoff
        return new_backoff

    def reset_rate_limit_backoff(self, execution_id: str) -> None:
        """Reset the backoff time for an execution.

        Args:
            execution_id: The execution identifier
        """
        if execution_id in self._rate_limit_backoff:
            del self._rate_limit_backoff[execution_id]

    def detect_all_issues(self, output: str, execution_id: str | None = None) -> list[Alert]:
        """Run all detection checks on output.

        Args:
            output: The output to check
            execution_id: Optional execution identifier

        Returns:
            List of all detected alerts
        """
        alerts = []

        # Check for rate limit first (most important for API calls)
        rate_limit_alert = self.check_rate_limit(output, execution_id)
        if rate_limit_alert:
            alerts.append(rate_limit_alert)

        # Check for compilation errors
        compile_alerts = self.check_compile_errors(output, execution_id)
        alerts.extend(compile_alerts)

        return alerts

    def get_alert(self, alert_id: str) -> Alert | None:
        """Get an alert by ID."""
        return self._alerts.get(alert_id)

    def get_alerts(
        self,
        execution_id: str | None = None,
        task_id: str | None = None,
        project_id: str | None = None,
        alert_type: AlertType | None = None,
        severity: AlertSeverity | None = None,
        status: AlertStatus | None = None,
        limit: int = 100,
    ) -> list[Alert]:
        """Get filtered list of alerts."""
        alerts = list(self._alerts.values())

        if execution_id:
            alerts = [a for a in alerts if a.execution_id == execution_id]
        if task_id:
            alerts = [a for a in alerts if a.task_id == task_id]
        if project_id:
            alerts = [a for a in alerts if a.project_id == project_id]
        if alert_type:
            alerts = [a for a in alerts if a.alert_type == alert_type]
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        if status:
            alerts = [a for a in alerts if a.status == status]

        # Sort by triggered_at descending
        alerts.sort(key=lambda x: x.triggered_at, reverse=True)

        return alerts[:limit]

    def acknowledge_alert(self, alert_id: str) -> Alert | None:
        """Acknowledge an alert."""
        alert = self._alerts.get(alert_id)
        if alert and alert.status == AlertStatus.PENDING:
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.now(timezone.utc)
        return alert

    def resolve_alert(self, alert_id: str) -> Alert | None:
        """Resolve an alert."""
        alert = self._alerts.get(alert_id)
        if alert and alert.status != AlertStatus.RESOLVED:
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now(timezone.utc)
        return alert

    def dismiss_alert(self, alert_id: str) -> Alert | None:
        """Dismiss an alert."""
        alert = self._alerts.get(alert_id)
        if alert and alert.status == AlertStatus.PENDING:
            alert.status = AlertStatus.DISMISSED
        return alert

    def get_pending_count(
        self,
        execution_id: str | None = None,
        severity: AlertSeverity | None = None,
    ) -> int:
        """Get count of pending alerts."""
        alerts = self.get_alerts(
            execution_id=execution_id,
            severity=severity,
            status=AlertStatus.PENDING,
        )
        return len(alerts)

    def clear_execution_data(self, execution_id: str) -> None:
        """Clear all data related to an execution (for cleanup)."""
        if execution_id in self._execution_last_output:
            del self._execution_last_output[execution_id]
        if execution_id in self._rate_limit_backoff:
            del self._rate_limit_backoff[execution_id]

    def clear_all(self) -> None:
        """Clear all alerts (for testing)."""
        self._alerts.clear()
        self._execution_last_output.clear()
        self._rate_limit_backoff.clear()


# Global singleton instance
alert_service = AlertService()