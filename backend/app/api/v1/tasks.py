"""Tasks API endpoints with full CRUD operations."""

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, status, BackgroundTasks
from pydantic import BaseModel, Field

from app.services.task import task_service
from app.services.executor import (
    create_task as create_execution_task,
    execute_task,
    get_task as get_execution_task,
    TaskStatus,
)


def broadcast_task_update(task_id: str, task_data: dict):
    """Broadcast task update via WebSocket."""
    try:
        from app.api.websocket import broadcast_task_update as ws_broadcast
        ws_broadcast(task_id, task_data)
    except Exception:
        pass


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
    # Claude Code 相关字段
    claude_session_id: str | None = None
    token_usage: dict | None = None
    artifacts: dict | None = None
    execution_log: dict | None = None

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    items: list[TaskResponse]
    total: int
    page: int
    page_size: int


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
        claude_session_id=task.get("claude_session_id"),
        token_usage=task.get("token_usage"),
        artifacts=task.get("artifacts"),
        execution_log=task.get("execution_log"),
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
    tasks, total = task_service.get_tasks(
        project_id=project_id,
        status_filter=status_filter,
        page=page,
        page_size=page_size,
    )

    return PaginatedResponse(
        items=[_task_to_response(t) for t in tasks],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate):
    """Create a new task."""
    new_task = task_service.create_task(
        title=task.title,
        project_id=task.project_id,
        description=task.description,
        requirement_id=task.requirement_id,
        status=task.status,
        progress=task.progress,
        created_by=task.created_by,
    )

    # Broadcast task creation
    broadcast_task_update(new_task["id"], _task_to_response(new_task).model_dump())

    return _task_to_response(new_task)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """Get task by ID."""
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
    return _task_to_response(task)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task: TaskUpdate):
    """Update a task."""
    update_data = task.model_dump(exclude_unset=True)
    updated = task_service.update_task(task_id, **update_data)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    # Broadcast task update
    broadcast_task_update(task_id, _task_to_response(updated).model_dump())

    return _task_to_response(updated)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str):
    """Delete a task."""
    deleted = task_service.delete_task(task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
    return None


@router.post("/{task_id}/execute", response_model=TaskResponse)
async def execute_task_endpoint(
    task_id: str,
    background_tasks: BackgroundTasks,
):
    """Execute a task (calls Claude Code).

    This endpoint creates an execution task and runs it in the background.
    """
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    if task["status"] == "running":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task is already running",
        )

    # Create execution task
    execution_task_id = str(task_id)  # Use task_id as execution_task_id for simplicity
    create_execution_task(
        task_id=execution_task_id,
        command="claude-code-clawdbot-skill",
        project_id=task["project_id"],
        requirement_id=task.get("requirement_id"),
    )

    # Update task status to running via service
    task_service.set_execution(task_id, execution_task_id)
    updated_task = task_service.get_task(task_id)

    # Execute in background
    background_tasks.add_task(
        execute_task,
        execution_task_id,
        "claude-code-clawdbot-skill",
    )

    return _task_to_response(updated_task)


@router.get("/{task_id}/execution", response_model=dict)
async def get_task_execution(task_id: str):
    """Get task execution status and result."""
    execution = task_service.get_execution(task_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
    return execution


# Export for dashboard service access
_tasks_store = task_service._store
