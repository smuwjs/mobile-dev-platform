"""Base Celery task utilities and state tracking."""

import asyncio
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from celery import Task
from celery.result import AsyncResult

from app.celery.config import celery_app


class TaskState(str, Enum):
    """Celery task states."""

    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    REVOKED = "REVOKED"
    RETRY = "RETRY"


# In-memory task state storage
_task_states: dict[str, dict] = {}


def create_task_record(
    task_id: str | None = None,
    task_name: str | None = None,
    task_type: str | None = None,
    project_id: str | None = None,
    requirement_id: str | None = None,
    parent_id: str | None = None,
    metadata: dict | None = None,
) -> dict:
    """Create a new task state record."""
    now = datetime.now(timezone.utc)
    record_id = task_id or str(uuid.uuid4())

    record = {
        "id": record_id,
        "celery_task_id": None,
        "task_name": task_name,
        "task_type": task_type,
        "project_id": project_id,
        "requirement_id": requirement_id,
        "parent_id": parent_id,
        "state": TaskState.PENDING.value,
        "progress": 0,
        "result": None,
        "error": None,
        "metadata": metadata or {},
        "created_at": now,
        "started_at": None,
        "completed_at": None,
    }

    _task_states[record_id] = record
    return record


def get_task_state(task_id: str) -> dict | None:
    """Get task state by ID."""
    return _task_states.get(task_id)


def update_task_state(
    task_id: str,
    state: str | None = None,
    progress: int | None = None,
    result: Any = None,
    error: str | None = None,
    celery_task_id: str | None = None,
) -> dict | None:
    """Update task state."""
    record = _task_states.get(task_id)
    if not record:
        return None

    now = datetime.now(timezone.utc)

    if state is not None:
        record["state"] = state
        if state == TaskState.STARTED.value and record["started_at"] is None:
            record["started_at"] = now
        elif state in (
            TaskState.SUCCESS.value,
            TaskState.FAILURE.value,
            TaskState.REVOKED.value,
        ):
            record["completed_at"] = now

    if progress is not None:
        record["progress"] = max(0, min(100, progress))

    if result is not None:
        record["result"] = result

    if error is not None:
        record["error"] = error

    if celery_task_id is not None:
        record["celery_task_id"] = celery_task_id

    # Broadcast update via WebSocket
    _broadcast_task_state_update(record)

    return record


def list_task_states(
    project_id: str | None = None,
    requirement_id: str | None = None,
    state: str | None = None,
) -> list[dict]:
    """List task states with optional filters."""
    results = list(_task_states.values())

    if project_id:
        results = [r for r in results if r.get("project_id") == project_id]
    if requirement_id:
        results = [r for r in results if r.get("requirement_id") == requirement_id]
    if state:
        results = [r for r in results if r.get("state") == state]

    return sorted(results, key=lambda r: r.get("created_at", ""), reverse=True)


def _broadcast_task_state_update(record: dict):
    """Broadcast task state update via WebSocket."""
    try:
        from app.api.websocket import manager

        asyncio.create_task(
            manager.broadcast({
                "type": "celery_task_update",
                "task_id": record["id"],
                "data": {
                    "id": record["id"],
                    "task_name": record["task_name"],
                    "task_type": record["task_type"],
                    "state": record["state"],
                    "progress": record["progress"],
                    "result": record["result"],
                    "error": record["error"],
                    "project_id": record["project_id"],
                    "requirement_id": record["requirement_id"],
                    "created_at": record["created_at"].isoformat() if record["created_at"] else None,
                    "started_at": record["started_at"].isoformat() if record["started_at"] else None,
                    "completed_at": record["completed_at"].isoformat() if record["completed_at"] else None,
                },
            })
        )
    except Exception:
        pass


class CallbackTask(Task):
    """Base task class with callback support for state tracking."""

    def on_success(self, retval, task_id, args, kwargs):
        """Called on task success."""
        update_task_state(task_id, state=TaskState.SUCCESS.value, result=retval)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called on task failure."""
        update_task_state(
            task_id,
            state=TaskState.FAILURE.value,
            error=str(exc),
        )

    def on_start(self):
        """Called when task starts."""
        update_task_state(self.request.id, state=TaskState.STARTED.value)

    def on_progress(self, progress: int):
        """Update task progress."""
        update_task_state(self.request.id, progress=progress)


def get_async_result(task_id: str) -> AsyncResult:
    """Get Celery AsyncResult for a task."""
    return AsyncResult(task_id, app=celery_app)
