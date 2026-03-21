"""Task service for business logic."""

import uuid
from datetime import datetime
from typing import Any


class TaskService:
    """Service class for task operations with in-memory storage."""

    def __init__(self):
        """Initialize with in-memory storage."""
        self._store: dict[str, dict] = {}

    def create_task(
        self,
        title: str,
        project_id: str,
        description: str | None = None,
        requirement_id: str | None = None,
        status: str = "pending",
        progress: int = 0,
        created_by: str = "default-user",
    ) -> dict:
        """Create a new task."""
        now = datetime.now()
        task_id = str(uuid.uuid4())

        new_task = {
            "id": task_id,
            "project_id": project_id,
            "requirement_id": requirement_id,
            "title": title,
            "description": description,
            "status": status,
            "progress": progress,
            "created_by": created_by,
            "created_at": now,
            "started_at": None,
            "completed_at": None,
        }

        self._store[task_id] = new_task
        return new_task

    def get_task(self, task_id: str) -> dict | None:
        """Get a task by ID."""
        return self._store.get(task_id)

    def get_tasks(
        self,
        project_id: str | None = None,
        status_filter: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict], int]:
        """Get paginated list of tasks."""
        all_tasks = list(self._store.values())

        # Filter by project_id if provided
        if project_id:
            all_tasks = [t for t in all_tasks if t.get("project_id") == project_id]

        # Filter by status if provided
        if status_filter:
            all_tasks = [t for t in all_tasks if t.get("status") == status_filter]

        total = len(all_tasks)
        start = (page - 1) * page_size
        end = start + page_size
        paginated = all_tasks[start:end]

        return paginated, total

    def update_task(
        self,
        task_id: str,
        title: str | None = None,
        description: str | None = None,
        status: str | None = None,
        progress: int | None = None,
    ) -> dict | None:
        """Update a task."""
        if task_id not in self._store:
            return None

        existing = self._store[task_id]

        # Handle status transitions
        if status and status != existing.get("status"):
            if status == "running" and existing.get("status") != "running":
                existing["started_at"] = datetime.now()
            elif status in ("completed", "failed") and existing.get("status") != status:
                existing["completed_at"] = datetime.now()
                existing["progress"] = 100 if status == "completed" else existing.get("progress", 0)

        if title is not None:
            existing["title"] = title
        if description is not None:
            existing["description"] = description
        if status is not None:
            existing["status"] = status
        if progress is not None:
            existing["progress"] = progress

        self._store[task_id] = existing
        return existing

    def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        if task_id not in self._store:
            return False

        del self._store[task_id]
        return True

    def set_execution(
        self,
        task_id: str,
        execution_task_id: str,
        command: str = "claude-code-clawdbot-skill",
    ) -> dict | None:
        """Set task execution info."""
        if task_id not in self._store:
            return None

        task = self._store[task_id]
        task["status"] = "running"
        task["started_at"] = datetime.now()
        task["progress"] = 0
        task["execution_task_id"] = execution_task_id
        self._store[task_id] = task
        return task

    def get_execution(self, task_id: str) -> dict | None:
        """Get task execution info."""
        if task_id not in self._store:
            return None

        task = self._store[task_id]
        execution_task_id = task.get("execution_task_id")

        if not execution_task_id:
            return {"status": "not_started", "result": None}

        from app.services.executor import get_task as get_execution_task

        execution = get_execution_task(execution_task_id)
        if not execution:
            return {"status": "not_found", "result": None}

        return {
            "status": execution["status"],
            "result": execution["result"],
            "error": execution.get("error"),
            "started_at": execution.get("started_at"),
            "completed_at": execution.get("completed_at"),
        }

    def clear_all(self) -> None:
        """Clear all tasks (for testing)."""
        self._store.clear()


# Global instance
task_service = TaskService()
