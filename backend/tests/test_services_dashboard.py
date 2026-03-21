"""Tests for dashboard service."""
import pytest
from datetime import datetime, timedelta

from app.services.dashboard import (
    DashboardService,
    ProjectStats,
    TaskStats,
    RequirementStats,
    CostStats,
    DashboardStats,
    Activity,
)


class TestDashboardService:
    """Tests for DashboardService class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.projects_store = {}
        self.tasks_store = {}
        self.requirements_store = {}
        self.costs_store = {}
        self.service = DashboardService(
            projects_store=self.projects_store,
            tasks_store=self.tasks_store,
            requirements_store=self.requirements_store,
            costs_store=self.costs_store,
        )

    def _add_project(self, name: str, status: str = "planning"):
        """Helper to add a project."""
        now = datetime.now()
        project_id = f"project-{len(self.projects_store)}"
        self.projects_store[project_id] = {
            "id": project_id,
            "name": name,
            "status": status,
            "created_at": now,
        }
        return project_id

    def _add_task(self, title: str, project_id: str, status: str = "pending"):
        """Helper to add a task."""
        now = datetime.now()
        task_id = f"task-{len(self.tasks_store)}"
        self.tasks_store[task_id] = {
            "id": task_id,
            "title": title,
            "project_id": project_id,
            "status": status,
            "created_at": now,
        }
        return task_id

    def _add_requirement(self, title: str, project_id: str, status: str = "pending"):
        """Helper to add a requirement."""
        now = datetime.now()
        req_id = f"req-{len(self.requirements_store)}"
        self.requirements_store[req_id] = {
            "id": req_id,
            "title": title,
            "project_id": project_id,
            "status": status,
            "created_at": now,
        }
        return req_id

    def _add_cost(self, project_id: str, cost_type: str, amount: float):
        """Helper to add a cost."""
        now = datetime.now()
        cost_id = f"cost-{len(self.costs_store)}"
        self.costs_store[cost_id] = {
            "id": cost_id,
            "project_id": project_id,
            "cost_type": cost_type,
            "amount": amount,
            "recorded_at": now,
        }
        return cost_id

    def test_get_stats_empty(self):
        """Test getting stats when all stores are empty."""
        stats = self.service.get_stats()

        assert stats.projects.total == 0
        assert stats.tasks.total == 0
        assert stats.requirements.total == 0
        assert stats.costs.total_cost_usd == 0.0

    def test_get_stats_projects(self):
        """Test project statistics."""
        self._add_project("Project 1", "active")
        self._add_project("Project 2", "active")
        self._add_project("Project 3", "completed")

        stats = self.service.get_stats()

        assert stats.projects.total == 3
        assert stats.projects.active == 2
        assert stats.projects.completed == 1

    def test_get_stats_tasks(self):
        """Test task statistics."""
        project_id = self._add_project("Project 1")
        self._add_task("Task 1", project_id, "pending")
        self._add_task("Task 2", project_id, "pending")
        self._add_task("Task 3", project_id, "running")
        self._add_task("Task 4", project_id, "completed")

        stats = self.service.get_stats()

        assert stats.tasks.total == 4
        assert stats.tasks.pending == 2
        assert stats.tasks.running == 1
        assert stats.tasks.completed == 1

    def test_get_stats_requirements(self):
        """Test requirement statistics."""
        project_id = self._add_project("Project 1")
        self._add_requirement("Req 1", project_id, "pending")
        self._add_requirement("Req 2", project_id, "implemented")
        self._add_requirement("Req 3", project_id, "pending")

        stats = self.service.get_stats()

        assert stats.requirements.total == 3
        assert stats.requirements.pending == 2
        assert stats.requirements.implemented == 1

    def test_get_stats_costs(self):
        """Test cost statistics."""
        self._add_project("Project 1")
        self._add_cost("project-0", "token", 1000.0)
        self._add_cost("project-0", "token", 2000.0)
        self._add_cost("project-0", "time", 60.0)

        stats = self.service.get_stats()

        # Tokens: 3000 * 0.01 = 30
        # Time: 60 * 0.05 = 3
        # Total: 33
        assert stats.costs.total_cost_usd == 33.0
        assert stats.costs.total_tokens == 3000.0
        assert stats.costs.total_time_seconds == 60.0

    def test_get_activities_empty(self):
        """Test getting activities when all stores are empty."""
        activities = self.service.get_activities()
        assert activities == []

    def test_get_activities_from_projects(self):
        """Test getting activities from projects."""
        self._add_project("Project Alpha")
        self._add_project("Project Beta")

        activities = self.service.get_activities()

        assert len(activities) == 2
        for a in activities:
            assert a.type == "project"
            assert "Project" in a.description

    def test_get_activities_from_tasks(self):
        """Test getting activities from tasks."""
        project_id = self._add_project("Project 1")
        self._add_task("Build UI", project_id)
        self._add_task("Write Tests", project_id)

        activities = self.service.get_activities()

        assert len(activities) == 2
        for a in activities:
            assert a.type == "task"
            assert "UI" in a.description or "Tests" in a.description

    def test_get_activities_from_requirements(self):
        """Test getting activities from requirements."""
        project_id = self._add_project("Project 1")
        self._add_requirement("Auth Feature", project_id)

        activities = self.service.get_activities()

        assert len(activities) == 1
        assert activities[0].type == "requirement"
        assert "Auth Feature" in activities[0].description

    def test_get_activities_from_costs(self):
        """Test getting activities from costs."""
        self._add_project("Project 1")
        self._add_cost("project-0", "token", 100.0)

        activities = self.service.get_activities()

        assert len(activities) == 1
        assert activities[0].type == "cost"
        assert "100.0 token" in activities[0].description

    def test_get_activities_sorted_by_timestamp(self):
        """Test that activities are sorted by timestamp descending."""
        project_id = self._add_project("Project 1")

        # Add with slight delays to ensure different timestamps
        old_time = datetime.now() - timedelta(hours=1)
        self.tasks_store["task-0"]["created_at"] = old_time

        self._add_task("Recent Task", project_id)

        activities = self.service.get_activities()

        assert len(activities) == 2
        assert activities[0].type == "task"  # Most recent first
        assert activities[1].type == "task"  # Oldest second

    def test_get_activities_limit(self):
        """Test limiting activities."""
        for i in range(25):
            self._add_project(f"Project {i}")

        activities = self.service.get_activities(limit=10)

        assert len(activities) == 10

    def test_get_activities_all_types(self):
        """Test activities from all store types."""
        project_id = self._add_project("Project 1")
        self._add_task("Task", project_id)
        self._add_requirement("Req", project_id)
        self._add_cost(project_id, "token", 100.0)

        activities = self.service.get_activities()

        assert len(activities) == 4
        types = {a.type for a in activities}
        assert types == {"project", "task", "requirement", "cost"}
