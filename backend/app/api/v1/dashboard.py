"""Dashboard API endpoints for stats and activities."""

from datetime import datetime, timedelta

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.api.v1.tasks import _tasks_store as tasks_store
from app.api.v1.requirements import _requirements_store as requirements_store
from app.api.v1.projects import _projects_store as projects_store
from app.api.v1.costs import _costs_store as costs_store

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


def _get_dashboard_stats() -> DashboardStats:
    """Calculate dashboard statistics."""
    all_projects = list(projects_store.values())
    all_tasks = list(tasks_store.values())
    all_requirements = list(requirements_store.values())
    all_costs = list(costs_store.values())

    # Project stats
    project_stats = ProjectStats(
        total=len(all_projects),
        active=sum(1 for p in all_projects if p.get("status") == "active"),
        completed=sum(1 for p in all_projects if p.get("status") == "completed"),
    )

    # Task stats
    task_stats = TaskStats(
        total=len(all_tasks),
        pending=sum(1 for t in all_tasks if t.get("status") == "pending"),
        running=sum(1 for t in all_tasks if t.get("status") == "running"),
        completed=sum(1 for t in all_tasks if t.get("status") == "completed"),
    )

    # Requirement stats
    req_stats = RequirementStats(
        total=len(all_requirements),
        implemented=sum(1 for r in all_requirements if r.get("status") == "implemented"),
        pending=sum(1 for r in all_requirements if r.get("status") == "pending"),
    )

    # Cost stats
    total_tokens = sum(c.get("amount", 0) for c in all_costs if c.get("cost_type") == "token")
    total_time = sum(c.get("amount", 0) for c in all_costs if c.get("cost_type") == "time")
    total_cost = total_tokens * 0.01 + total_time * 0.05

    cost_stats = CostStats(
        total_cost_usd=round(total_cost, 2),
        total_tokens=round(total_tokens, 2),
        total_time_seconds=round(total_time, 2),
    )

    return DashboardStats(
        projects=project_stats,
        tasks=task_stats,
        requirements=req_stats,
        costs=cost_stats,
        last_updated=datetime.now(),
    )


def _get_recent_activities(limit: int = 20) -> list[Activity]:
    """Get recent activities from all stores."""
    activities = []

    # Projects
    for p in projects_store.values():
        activities.append(Activity(
            id=f"project-{p.get('id')}",
            type="project",
            description=f"Project '{p.get('name', 'unnamed')}' created",
            project_id=p.get("id"),
            timestamp=p.get("created_at", datetime.now()),
        ))

    # Requirements
    for r in requirements_store.values():
        activities.append(Activity(
            id=f"requirement-{r.get('id')}",
            type="requirement",
            description=f"Requirement '{r.get('title', 'untitled')}' created",
            project_id=r.get("project_id"),
            timestamp=r.get("created_at", datetime.now()),
        ))

    # Tasks
    for t in tasks_store.values():
        activities.append(Activity(
            id=f"task-{t.get('id')}",
            type="task",
            description=f"Task '{t.get('title', 'untitled')}' created",
            project_id=t.get("project_id"),
            timestamp=t.get("created_at", datetime.now()),
        ))

    # Costs
    for c in costs_store.values():
        activities.append(Activity(
            id=f"cost-{c.get('id')}",
            type="cost",
            description=f"Cost recorded: {c.get('amount')} {c.get('cost_type')}",
            project_id=c.get("project_id"),
            timestamp=c.get("recorded_at", datetime.now()),
        ))

    # Sort by timestamp descending
    activities.sort(key=lambda x: x.timestamp, reverse=True)

    return activities[:limit]


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get dashboard statistics."""
    return _get_dashboard_stats()


@router.get("/activities", response_model=ActivityList)
async def get_recent_activities(
    limit: int = Query(20, ge=1, le=100, description="Number of activities to return"),
):
    """Get recent activities."""
    activities = _get_recent_activities(limit)
    return ActivityList(activities=activities, total=len(activities))
