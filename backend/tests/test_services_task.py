"""Tests for task service."""
import pytest
from datetime import datetime

from app.services.task import TaskService, task_service


class TestTaskService:
    """Tests for TaskService class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = TaskService()

    def test_create_task(self):
        """Test creating a task."""
        task = self.service.create_task(
            title="Test Task",
            project_id="project-1",
            description="A test task",
            priority="high",
            status="pending",
            progress=0,
            created_by="test-user",
        )

        assert task["title"] == "Test Task"
        assert task["project_id"] == "project-1"
        assert task["description"] == "A test task"
        assert task["status"] == "pending"
        assert task["progress"] == 0
        assert task["created_by"] == "test-user"
        assert "id" in task
        assert "created_at" in task

    def test_create_task_defaults(self):
        """Test creating a task with default values."""
        task = self.service.create_task(
            title="Minimal Task",
            project_id="project-1",
        )

        assert task["title"] == "Minimal Task"
        assert task["status"] == "pending"
        assert task["progress"] == 0
        assert task["created_by"] == "default-user"

    def test_get_task(self):
        """Test getting a task by ID."""
        created = self.service.create_task(title="Get Test", project_id="project-1")
        retrieved = self.service.get_task(created["id"])

        assert retrieved is not None
        assert retrieved["id"] == created["id"]
        assert retrieved["title"] == "Get Test"

    def test_get_task_not_found(self):
        """Test getting a nonexistent task."""
        result = self.service.get_task("nonexistent-id")
        assert result is None

    def test_get_tasks_empty(self):
        """Test getting tasks when none exist."""
        tasks, total = self.service.get_tasks()
        assert tasks == []
        assert total == 0

    def test_get_tasks_multiple(self):
        """Test getting multiple tasks."""
        self.service.create_task(title="Task 1", project_id="project-1")
        self.service.create_task(title="Task 2", project_id="project-1")
        self.service.create_task(title="Task 3", project_id="project-2")

        tasks, total = self.service.get_tasks()
        assert total == 3

    def test_get_tasks_filter_by_project(self):
        """Test filtering tasks by project."""
        self.service.create_task(title="Task 1", project_id="project-1")
        self.service.create_task(title="Task 2", project_id="project-1")
        self.service.create_task(title="Task 3", project_id="project-2")

        tasks, total = self.service.get_tasks(project_id="project-1")
        assert total == 2
        for t in tasks:
            assert t["project_id"] == "project-1"

    def test_get_tasks_filter_by_status(self):
        """Test filtering tasks by status."""
        self.service.create_task(title="Task 1", project_id="project-1", status="pending")
        self.service.create_task(title="Task 2", project_id="project-1", status="running")
        self.service.create_task(title="Task 3", project_id="project-1", status="pending")

        tasks, total = self.service.get_tasks(status_filter="pending")
        assert total == 2
        for t in tasks:
            assert t["status"] == "pending"

    def test_get_tasks_pagination(self):
        """Test paginating tasks."""
        for i in range(25):
            self.service.create_task(title=f"Task {i}", project_id="project-1")

        # First page
        tasks, total = self.service.get_tasks(page=1, page_size=10)
        assert total == 25
        assert len(tasks) == 10

        # Second page
        tasks, total = self.service.get_tasks(page=2, page_size=10)
        assert total == 25
        assert len(tasks) == 10

        # Third page (partial)
        tasks, total = self.service.get_tasks(page=3, page_size=10)
        assert total == 25
        assert len(tasks) == 5

    def test_update_task(self):
        """Test updating a task."""
        created = self.service.create_task(title="Original", project_id="project-1")
        updated = self.service.update_task(
            created["id"],
            title="Updated",
            status="running",
            progress=50,
        )

        assert updated is not None
        assert updated["title"] == "Updated"
        assert updated["status"] == "running"
        assert updated["progress"] == 50
        assert updated["started_at"] is not None

    def test_update_task_not_found(self):
        """Test updating a nonexistent task."""
        result = self.service.update_task("nonexistent-id", title="New Title")
        assert result is None

    def test_update_task_status_transition_to_completed(self):
        """Test status transition to completed sets completed_at."""
        created = self.service.create_task(title="Task", project_id="project-1", status="running")
        updated = self.service.update_task(created["id"], status="completed")

        assert updated["status"] == "completed"
        assert updated["completed_at"] is not None
        assert updated["progress"] == 100

    def test_update_task_status_transition_to_failed(self):
        """Test status transition to failed keeps progress."""
        created = self.service.create_task(title="Task", project_id="project-1", status="running", progress=30)
        updated = self.service.update_task(created["id"], status="failed")

        assert updated["status"] == "failed"
        assert updated["completed_at"] is not None
        assert updated["progress"] == 30  # Progress unchanged on failure

    def test_delete_task(self):
        """Test deleting a task."""
        created = self.service.create_task(title="To Delete", project_id="project-1")
        deleted = self.service.delete_task(created["id"])

        assert deleted is True
        assert self.service.get_task(created["id"]) is None

    def test_delete_task_not_found(self):
        """Test deleting a nonexistent task."""
        result = self.service.delete_task("nonexistent-id")
        assert result is False

    def test_clear_all(self):
        """Test clearing all tasks."""
        self.service.create_task(title="Task 1", project_id="project-1")
        self.service.create_task(title="Task 2", project_id="project-1")

        self.service.clear_all()

        tasks, total = self.service.get_tasks()
        assert total == 0


class TestTaskServiceSingleton:
    """Tests for the task_service singleton."""

    def setup_method(self):
        """Clear the singleton before each test."""
        task_service.clear_all()

    def test_singleton_persists_data(self):
        """Test that the singleton persists data between operations."""
        task_service.create_task(title="Singleton Task", project_id="project-1")

        task = task_service.get_task(task_service._store.keys().__iter__().__next__())
        assert task["title"] == "Singleton Task"
