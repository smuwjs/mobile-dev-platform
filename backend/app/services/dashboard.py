"""Dashboard service for business logic."""

from datetime import datetime
from dataclasses import dataclass


@dataclass
class ProjectStats:
    total: int
    active: int
    completed: int


@dataclass
class TaskStats:
    total: int
    pending: int
    running: int
    completed: int


@dataclass
class RequirementStats:
    total: int
    implemented: int
    pending: int


@dataclass
class CostStats:
    total_cost_usd: float
    total_tokens: float
    total_time_seconds: float


@dataclass
class DashboardStats:
    projects: ProjectStats
    tasks: TaskStats
    requirements: RequirementStats
    costs: CostStats
    last_updated: datetime


@dataclass
class Activity:
    id: str
    type: str
    description: str
    project_id: str | None
    timestamp: datetime


class DashboardService:
    """Service class for dashboard operations."""

    def __init__(self, projects_store: dict, tasks_store: dict, requirements_store: dict, costs_store: dict):
        """Initialize with references to other stores."""
        self._projects_store = projects_store
        self._tasks_store = tasks_store
        self._requirements_store = requirements_store
        self._costs_store = costs_store

    def get_stats(self) -> DashboardStats:
        """Calculate dashboard statistics."""
        all_projects = list(self._projects_store.values())
        all_tasks = list(self._tasks_store.values())
        all_requirements = list(self._requirements_store.values())
        all_costs = list(self._costs_store.values())

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

    def get_activities(self, limit: int = 20) -> list[Activity]:
        """Get recent activities from all stores."""
        activities = []

        # Projects
        for p in self._projects_store.values():
            activities.append(Activity(
                id=f"project-{p.get('id')}",
                type="project",
                description=f"Project '{p.get('name', 'unnamed')}' created",
                project_id=p.get("id"),
                timestamp=p.get("created_at", datetime.now()),
            ))

        # Requirements
        for r in self._requirements_store.values():
            activities.append(Activity(
                id=f"requirement-{r.get('id')}",
                type="requirement",
                description=f"Requirement '{r.get('title', 'untitled')}' created",
                project_id=r.get("project_id"),
                timestamp=r.get("created_at", datetime.now()),
            ))

        # Tasks
        for t in self._tasks_store.values():
            activities.append(Activity(
                id=f"task-{t.get('id')}",
                type="task",
                description=f"Task '{t.get('title', 'untitled')}' created",
                project_id=t.get("project_id"),
                timestamp=t.get("created_at", datetime.now()),
            ))

        # Costs
        for c in self._costs_store.values():
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
