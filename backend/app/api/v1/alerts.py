"""Alert API endpoints for managing execution alerts and anomalies.

Provides endpoints for:
- Listing and filtering alerts
- Getting alert details
- Acknowledging/resolving/dismissing alerts
- Getting alert statistics
"""

from datetime import datetime
from enum import Enum

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.services.alert import (
    AlertSeverity,
    AlertStatus,
    AlertType,
    alert_service,
)

router = APIRouter(prefix="/alerts", tags=["alerts"])


# Enums for API
class AlertTypeEnum(str, Enum):
    TIMEOUT = "timeout"
    COMPILE_ERROR = "compile_error"
    API_RATE_LIMIT = "api_rate_limit"
    EXECUTION_ERROR = "execution_error"
    SESSION_TERMINATED = "session_terminated"
    RESOURCE_EXHAUSTED = "resource_exhausted"


class AlertSeverityEnum(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatusEnum(str, Enum):
    PENDING = "pending"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


# Pydantic Schemas

class AlertResponse(BaseModel):
    """Response schema for an alert."""

    id: str
    alert_type: str
    severity: str
    status: str
    title: str
    message: str
    execution_id: str | None = None
    task_id: str | None = None
    project_id: str | None = None
    triggered_at: datetime
    acknowledged_at: datetime | None = None
    resolved_at: datetime | None = None
    metadata: dict = Field(default_factory=dict)

    class Config:
        from_attributes = True


class AlertListResponse(BaseModel):
    """Response schema for a list of alerts."""

    items: list[AlertResponse]
    total: int
    pending_count: int


class AlertStatsResponse(BaseModel):
    """Response schema for alert statistics."""

    total: int
    pending: int
    acknowledged: int
    resolved: int
    dismissed: int
    by_type: dict[str, int]
    by_severity: dict[str, int]


class AcknowledgeRequest(BaseModel):
    """Request schema for acknowledging an alert."""

    alert_id: str = Field(..., description="Alert ID to acknowledge")


class ResolveRequest(BaseModel):
    """Request schema for resolving an alert."""

    alert_id: str = Field(..., description="Alert ID to resolve")


class DismissRequest(BaseModel):
    """Request schema for dismissing an alert."""

    alert_id: str = Field(..., description="Alert ID to dismiss")


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str
    success: bool = True


class RateLimitResponse(BaseModel):
    """Response schema for rate limit backoff info."""

    execution_id: str
    recommended_backoff_seconds: int


# Helper function to convert Alert to response
def _alert_to_response(alert) -> AlertResponse:
    """Convert Alert dataclass to response model."""
    return AlertResponse(
        id=alert.id,
        alert_type=alert.alert_type.value if isinstance(alert.alert_type, AlertType) else alert.alert_type,
        severity=alert.severity.value if isinstance(alert.severity, AlertSeverity) else alert.severity,
        status=alert.status.value if isinstance(alert.status, AlertStatus) else alert.status,
        title=alert.title,
        message=alert.message,
        execution_id=alert.execution_id,
        task_id=alert.task_id,
        project_id=alert.project_id,
        triggered_at=alert.triggered_at,
        acknowledged_at=alert.acknowledged_at,
        resolved_at=alert.resolved_at,
        metadata=alert.metadata,
    )


# API Endpoints

@router.get("/", response_model=AlertListResponse)
async def list_alerts(
    execution_id: str | None = Query(None, description="Filter by execution ID"),
    task_id: str | None = Query(None, description="Filter by task ID"),
    project_id: str | None = Query(None, description="Filter by project ID"),
    alert_type: AlertTypeEnum | None = Query(None, description="Filter by alert type"),
    severity: AlertSeverityEnum | None = Query(None, description="Filter by severity"),
    status_filter: AlertStatusEnum | None = Query(None, alias="status", description="Filter by status"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of alerts to return"),
):
    """Get list of alerts with optional filters."""
    # Convert enum values
    alert_type_val = AlertType(alert_type.value) if alert_type else None
    severity_val = AlertSeverity(severity.value) if severity else None
    status_val = AlertStatus(status_filter.value) if status_filter else None

    alerts = alert_service.get_alerts(
        execution_id=execution_id,
        task_id=task_id,
        project_id=project_id,
        alert_type=alert_type_val,
        severity=severity_val,
        status=status_val,
        limit=limit,
    )

    pending_count = alert_service.get_pending_count(
        execution_id=execution_id,
        severity=severity_val,
    )

    return AlertListResponse(
        items=[_alert_to_response(a) for a in alerts],
        total=len(alerts),
        pending_count=pending_count,
    )


@router.get("/stats", response_model=AlertStatsResponse)
async def get_alert_stats(
    project_id: str | None = Query(None, description="Filter by project ID"),
):
    """Get alert statistics."""
    all_alerts = alert_service.get_alerts(project_id=project_id, limit=1000)

    stats = {
        "total": len(all_alerts),
        "pending": 0,
        "acknowledged": 0,
        "resolved": 0,
        "dismissed": 0,
        "by_type": {},
        "by_severity": {},
    }

    for alert in all_alerts:
        status_str = alert.status.value if isinstance(alert.status, AlertStatus) else alert.status
        type_str = alert.alert_type.value if isinstance(alert.alert_type, AlertType) else alert.alert_type
        severity_str = alert.severity.value if isinstance(alert.severity, AlertSeverity) else alert.severity

        if status_str == "pending":
            stats["pending"] += 1
        elif status_str == "acknowledged":
            stats["acknowledged"] += 1
        elif status_str == "resolved":
            stats["resolved"] += 1
        elif status_str == "dismissed":
            stats["dismissed"] += 1

        stats["by_type"][type_str] = stats["by_type"].get(type_str, 0) + 1
        stats["by_severity"][severity_str] = stats["by_severity"].get(severity_str, 0) + 1

    return AlertStatsResponse(**stats)


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: str):
    """Get a specific alert by ID."""
    alert = alert_service.get_alert(alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found",
        )
    return _alert_to_response(alert)


@router.post("/acknowledge", response_model=MessageResponse)
async def acknowledge_alert(request: AcknowledgeRequest):
    """Acknowledge an alert."""
    alert = alert_service.acknowledge_alert(request.alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {request.alert_id} not found",
        )
    return MessageResponse(message=f"Alert {request.alert_id} acknowledged")


@router.post("/resolve", response_model=MessageResponse)
async def resolve_alert(request: ResolveRequest):
    """Resolve an alert."""
    alert = alert_service.resolve_alert(request.alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {request.alert_id} not found",
        )
    return MessageResponse(message=f"Alert {request.alert_id} resolved")


@router.post("/dismiss", response_model=MessageResponse)
async def dismiss_alert(request: DismissRequest):
    """Dismiss an alert."""
    alert = alert_service.dismiss_alert(request.alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {request.alert_id} not found",
        )
    return MessageResponse(message=f"Alert {request.alert_id} dismissed")


@router.get("/rate-limit/backoff/{execution_id}", response_model=RateLimitResponse)
async def get_rate_limit_backoff(execution_id: str):
    """Get the current rate limit backoff for an execution."""
    backoff = alert_service.get_rate_limit_backoff(execution_id)
    return RateLimitResponse(
        execution_id=execution_id,
        recommended_backoff_seconds=backoff,
    )


@router.post("/rate-limit/reset/{execution_id}", response_model=MessageResponse)
async def reset_rate_limit_backoff(execution_id: str):
    """Reset the rate limit backoff for an execution."""
    alert_service.reset_rate_limit_backoff(execution_id)
    return MessageResponse(message=f"Rate limit backoff reset for execution {execution_id}")