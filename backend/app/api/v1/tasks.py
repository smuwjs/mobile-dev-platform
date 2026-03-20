"""Tasks API endpoints with full CRUD operations."""

import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/tasks", tags=["tasks"])


# Pydantic schemas
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    status: str = Field(default="pending", max_length=50)
    progress: int = Field(default=0, ge=0, le=100)
    created_by: str = "default-user"


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    project_id: str = Field(..., min_length=1)
    requirement_id: str | None = None
    status: str = Field(default="pending", max_length=50)
    progress: int = Field(default=0, ge=0, le=100)
    created_by: str = "default-user"


class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    status: str | None = Field(None, max_length=50)
    progress: int | None = Field(None, ge=0, le=100)


class TaskResponse(TaskBase):
    id: str
    project_id: str
    requirement_id: str | None = None
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    items: list[TaskResponse]
    total: int
    page: int
    page_size: int


# In-memory storage
_tasks_store: dict[str, dict] = {}


def _task_to_response(task: dict) -> TaskResponse:
    """Convert task dict to response model."""
    return TaskResponse(
        id=str(task["id"]),
        project_id=str(task["project_id"]),
        requirement_id=task.get("requirement_id"),
        title=task["title"],
        description=task.get("description"),
        status=task.get("status", "pending"),
        progress=task.get("progress", 0),
        created_by=str(task.get("created_by", "default-user")),
        created_at=task.get("created_at", datetime.now()),
        started_at=task.get("started_at"),
        completed_at=task.get("completed_at"),
    )


# Project-scoped tasks router
_project_tasks_router = APIRouter(prefix="/projects/{project_id}/tasks", tags=["tasks"])


@_project_tasks_router.get("/", response_model=PaginatedResponse)
async def list_project_tasks(
    project_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status_filter: str | None = Query(None, description="Filter by status"),
):
    """List all tasks for a project."""
    all_tasks = [
        t for t in _tasks_store.values() if t.get("project_id") == project_id
    ]

    if status_filter:
        all_tasks = [t for t in all_tasks if t.get("status") == status_filter]

    total = len(all_tasks)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = all_tasks[start:end]

    return PaginatedResponse(
        items=[_task_to_response(t) for t in paginated],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate):
    """Create a new task."""
    now = datetime.now()
    task_id = str(uuid.uuid4())

    new_task = {
        "id": task_id,
        "project_id": task.project_id,
        "requirement_id": task.requirement_id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "progress": task.progress,
        "created_by": task.created_by,
        "created_at": now,
        "started_at": None,
        "completed_at": None,
    }

    _tasks_store[task_id] = new_task
    return _task_to_response(new_task)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """Get task by ID."""
    if task_id not in _tasks_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
    return _task_to_response(_tasks_store[task_id])


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task: TaskUpdate):
    """Update a task."""
    if task_id not in _tasks_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    existing = _tasks_store[task_id]
    update_data = task.model_dump(exclude_unset=True)

    # Handle status transitions
    if "status" in update_data:
        new_status = update_data["status"]
        if new_status == "running" and existing.get("status") != "running":
            existing["started_at"] = datetime.now()
        elif new_status in ("completed", "failed") and existing.get("status") != new_status:
            existing["completed_at"] = datetime.now()
            existing["progress"] = 100 if new_status == "completed" else existing.get("progress", 0)

    for key, value in update_data.items():
        existing[key] = value

    _tasks_store[task_id] = existing

    return _task_to_response(existing)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str):
    """Delete a task."""
    if task_id not in _tasks_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    del _tasks_store[task_id]
    return None


@router.post("/{task_id}/execute", response_model=TaskResponse)
async def execute_task(task_id: str):
    """Execute a task (calls Claude Code)."""
    if task_id not in _tasks_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    task = _tasks_store[task_id]

    if task["status"] == "running":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task is already running",
        )

    # Update task status to running
    task["status"] = "running"
    task["started_at"] = datetime.now()
    task["progress"] = 0
    _tasks_store[task_id] = task

    # In production, this would trigger Claude Code execution
    # For now, we simulate execution by updating progress
    # The actual Claude Code integration would happen asynchronously

    return _task_to_response(task)
