"""Dashboard API endpoints for stats and activities."""

from datetime import datetime

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.api.v1.tasks import _tasks_store as tasks_store
from app.api.v1.requirements import _requirements_store as requirements_store
from app.api.v1.projects import _projects_store as projects_store
from app.api.v1.costs import _costs_store as costs_store
from app.services.dashboard import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class ProjectStats(BaseModel):
    total: int
    active: int
    completed: int


class TaskStats(BaseModel):
    total: int
    pending: int
    running: int
    completed: int


class RequirementStats(BaseModel):
    total: int
    implemented: int
    pending: int


class CostStats(BaseModel):
    total_cost_usd: float
    total_tokens: float
    total_time_seconds: float


class DashboardStats(BaseModel):
    projects: ProjectStats
    tasks: TaskStats
    requirements: RequirementStats
    costs: CostStats
    last_updated: datetime


class Activity(BaseModel):
    id: str
    type: str
    description: str
    project_id: str | None
    timestamp: datetime


class ActivityList(BaseModel):
    activities: list[Activity]
    total: int


# Create dashboard service with store references
dashboard_service = DashboardService(
    projects_store=projects_store,
    tasks_store=tasks_store,
    requirements_store=requirements_store,
    costs_store=costs_store,
)


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get dashboard statistics."""
    stats = dashboard_service.get_stats()
    return DashboardStats(
        projects=ProjectStats(**stats.projects.__dict__),
        tasks=TaskStats(**stats.tasks.__dict__),
        requirements=RequirementStats(**stats.requirements.__dict__),
        costs=CostStats(**stats.costs.__dict__),
        last_updated=stats.last_updated,
    )


@router.get("/activities", response_model=ActivityList)
async def get_recent_activities(
    limit: int = Query(20, ge=1, le=100, description="Number of activities to return"),
):
    """Get recent activities."""
    activities = dashboard_service.get_activities(limit)
    return ActivityList(
        activities=[Activity(**a.__dict__) for a in activities],
        total=len(activities)
    )
