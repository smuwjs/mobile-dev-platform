"""Requirements API endpoints with full CRUD operations."""

import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/projects/{project_id}/requirements", tags=["requirements"])


# Pydantic schemas
class RequirementBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    priority: str = Field(default="medium", max_length=50)
    status: str = Field(default="pending", max_length=50)
    created_by: str = "default-user"


class RequirementCreate(RequirementBase):
    pass


class RequirementUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    priority: str | None = Field(None, max_length=50)
    status: str | None = Field(None, max_length=50)


class RequirementResponse(RequirementBase):
    id: str
    project_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    items: list[RequirementResponse]
    total: int
    page: int
    page_size: int


# In-memory storage
_requirements_store: dict[str, dict] = {}


def _requirement_to_response(requirement: dict) -> RequirementResponse:
    """Convert requirement dict to response model."""
    return RequirementResponse(
        id=str(requirement["id"]),
        project_id=str(requirement["project_id"]),
        title=requirement["title"],
        description=requirement.get("description"),
        priority=requirement.get("priority", "medium"),
        status=requirement.get("status", "pending"),
        created_by=str(requirement.get("created_by", "default-user")),
        created_at=requirement.get("created_at", datetime.now()),
        updated_at=requirement.get("updated_at", datetime.now()),
    )


@router.get("/", response_model=PaginatedResponse)
async def list_requirements(
    project_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status_filter: str | None = Query(None, description="Filter by status"),
):
    """List all requirements for a project."""
    all_requirements = [
        r for r in _requirements_store.values() if r.get("project_id") == project_id
    ]

    if status_filter:
        all_requirements = [r for r in all_requirements if r.get("status") == status_filter]

    total = len(all_requirements)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = all_requirements[start:end]

    return PaginatedResponse(
        items=[_requirement_to_response(r) for r in paginated],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/", response_model=RequirementResponse, status_code=status.HTTP_201_CREATED)
async def create_requirement(project_id: str, requirement: RequirementCreate):
    """Create a new requirement for a project."""
    now = datetime.now()
    requirement_id = str(uuid.uuid4())

    new_requirement = {
        "id": requirement_id,
        "project_id": project_id,
        "title": requirement.title,
        "description": requirement.description,
        "priority": requirement.priority,
        "status": requirement.status,
        "created_by": requirement.created_by,
        "created_at": now,
        "updated_at": now,
    }

    _requirements_store[requirement_id] = new_requirement
    return _requirement_to_response(new_requirement)


# Standalone routes for requirement detail (outside project context)
_standalone_requirements_router = APIRouter(prefix="/requirements", tags=["requirements"])


@_standalone_requirements_router.get("/{requirement_id}", response_model=RequirementResponse)
async def get_requirement(requirement_id: str):
    """Get requirement by ID."""
    if requirement_id not in _requirements_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requirement {requirement_id} not found",
        )
    return _requirement_to_response(_requirements_store[requirement_id])


@_standalone_requirements_router.put("/{requirement_id}", response_model=RequirementResponse)
async def update_requirement(requirement_id: str, requirement: RequirementUpdate):
    """Update a requirement."""
    if requirement_id not in _requirements_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requirement {requirement_id} not found",
        )

    existing = _requirements_store[requirement_id]
    update_data = requirement.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        existing[key] = value

    existing["updated_at"] = datetime.now()
    _requirements_store[requirement_id] = existing

    return _requirement_to_response(existing)


@_standalone_requirements_router.delete("/{requirement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_requirement(requirement_id: str):
    """Delete a requirement."""
    if requirement_id not in _requirements_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requirement {requirement_id} not found",
        )

    del _requirements_store[requirement_id]
    return None


# Decomposition API endpoints
class DecomposeRequest(BaseModel):
    """Request to decompose a requirement."""
    requirement_text: str = Field(..., min_length=1, description="Requirement description to decompose")
    project_id: str = Field(..., description="Project ID")
    requirement_id: str | None = Field(None, description="Existing requirement ID if updating")


class DecomposeResponse(BaseModel):
    """Response from requirement decomposition."""
    requirement_id: str
    complexity: int
    estimated_total_hours: float
    sub_requirements: list[dict]
    tasks: list[dict]
    validation: dict


@_standalone_requirements_router.post("/decompose", response_model=DecomposeResponse)
async def decompose_requirement(decompose_req: DecomposeRequest):
    """Decompose a requirement into sub-requirements and tasks.

    This endpoint analyzes the requirement text and generates:
    - Sub-requirements with priorities and estimates
    - Actionable tasks with dependencies
    - Validation results with any conflicts
    """
    from app.services.requirement_analysis import requirement_analysis_service

    result = await requirement_analysis_service.analyze_requirement(
        requirement_text=decompose_req.requirement_text,
        project_id=decompose_req.project_id,
        parent_id=decompose_req.requirement_id,
    )

    return DecomposeResponse(
        requirement_id=result.requirement_id,
        complexity=int(result.complexity),
        estimated_total_hours=result.estimated_total_hours,
        sub_requirements=[
            {
                "id": sr.id,
                "title": sr.title,
                "description": sr.description,
                "priority": sr.priority,
                "complexity": int(sr.complexity),
                "estimated_hours": sr.estimated_hours,
                "dependencies": sr.dependencies,
            }
            for sr in result.sub_requirements
        ],
        tasks=result.tasks,
        validation={
            "status": result.validation_result.status.value,
            "conflicts": result.validation_result.conflicts,
            "warnings": result.validation_result.warnings,
            "suggestions": result.validation_result.suggestions,
        },
    )


@_standalone_requirements_router.post("/{requirement_id}/decompose", response_model=DecomposeResponse)
async def decompose_existing_requirement(requirement_id: str):
    """Decompose an existing requirement.

    Uses the existing requirement's text to generate sub-requirements and tasks.
    """
    if requirement_id not in _requirements_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requirement {requirement_id} not found",
        )

    requirement = _requirements_store[requirement_id]

    from app.services.requirement_analysis import requirement_analysis_service

    result = await requirement_analysis_service.analyze_requirement(
        requirement_text=requirement["description"] or requirement["title"],
        project_id=requirement["project_id"],
        parent_id=requirement_id,
    )

    return DecomposeResponse(
        requirement_id=result.requirement_id,
        complexity=int(result.complexity),
        estimated_total_hours=result.estimated_total_hours,
        sub_requirements=[
            {
                "id": sr.id,
                "title": sr.title,
                "description": sr.description,
                "priority": sr.priority,
                "complexity": int(sr.complexity),
                "estimated_hours": sr.estimated_hours,
                "dependencies": sr.dependencies,
            }
            for sr in result.sub_requirements
        ],
        tasks=result.tasks,
        validation={
            "status": result.validation_result.status.value,
            "conflicts": result.validation_result.conflicts,
            "warnings": result.validation_result.warnings,
            "suggestions": result.validation_result.suggestions,
        },
    )


@_standalone_requirements_router.post("/{requirement_id}/validate")
async def validate_requirement(requirement_id: str):
    """Validate a requirement for conflicts and consistency.

    Returns validation results including any detected conflicts,
    warnings, and suggestions for improvement.
    """
    if requirement_id not in _requirements_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requirement {requirement_id} not found",
        )

    requirement = _requirements_store[requirement_id]

    from app.services.requirement_analysis import requirement_analysis_service

    result = await requirement_analysis_service.analyze_requirement(
        requirement_text=requirement["description"] or requirement["title"],
        project_id=requirement["project_id"],
        parent_id=requirement_id,
    )

    return {
        "requirement_id": requirement_id,
        "status": result.validation_result.status.value,
        "complexity": int(result.complexity),
        "estimated_hours": result.estimated_total_hours,
        "conflicts": result.validation_result.conflicts,
        "warnings": result.validation_result.warnings,
        "suggestions": result.validation_result.suggestions,
    }


# Celery task state API endpoints
class CeleryTaskStateResponse(BaseModel):
    """Response model for Celery task state."""
    id: str
    task_name: str | None
    task_type: str | None
    state: str
    progress: int
    result: dict | None
    error: str | None
    project_id: str | None
    requirement_id: str | None
    celery_task_id: str | None
    created_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None


@_standalone_requirements_router.get("/celery-tasks/{task_id}", response_model=CeleryTaskStateResponse)
async def get_celery_task_state(task_id: str):
    """Get the state of a Celery task.

    Returns the current state, progress, and result of a Celery task.
    """
    from app.celery.tasks.base import get_task_state, get_async_result

    # Try in-memory store first
    state = get_task_state(task_id)

    if state:
        return CeleryTaskStateResponse(
            id=state["id"],
            task_name=state.get("task_name"),
            task_type=state.get("task_type"),
            state=state.get("state", "PENDING"),
            progress=state.get("progress", 0),
            result=state.get("result"),
            error=state.get("error"),
            project_id=state.get("project_id"),
            requirement_id=state.get("requirement_id"),
            celery_task_id=state.get("celery_task_id"),
            created_at=state.get("created_at"),
            started_at=state.get("started_at"),
            completed_at=state.get("completed_at"),
        )

    # Try Celery result
    async_result = get_async_result(task_id)
    return CeleryTaskStateResponse(
        id=task_id,
        task_name=None,
        task_type=None,
        state=async_result.state,
        progress=async_result.info.get("progress", 0) if async_result.info else 0,
        result=async_result.result if async_result.ready() else None,
        error=str(async_result.info) if async_result.failed() else None,
        project_id=None,
        requirement_id=None,
        celery_task_id=task_id,
        created_at=None,
        started_at=None,
        completed_at=None,
    )


@_standalone_requirements_router.get("/celery-tasks", response_model=list[CeleryTaskStateResponse])
async def list_celery_tasks(
    project_id: str | None = Query(None, description="Filter by project ID"),
    requirement_id: str | None = Query(None, description="Filter by requirement ID"),
    state: str | None = Query(None, description="Filter by state"),
):
    """List Celery task states.

    Returns all task states with optional filtering by project, requirement, or state.
    """
    from app.celery.tasks.base import list_task_states

    states = list_task_states(
        project_id=project_id,
        requirement_id=requirement_id,
        state=state,
    )

    return [
        CeleryTaskStateResponse(
            id=s["id"],
            task_name=s.get("task_name"),
            task_type=s.get("task_type"),
            state=s.get("state", "PENDING"),
            progress=s.get("progress", 0),
            result=s.get("result"),
            error=s.get("error"),
            project_id=s.get("project_id"),
            requirement_id=s.get("requirement_id"),
            celery_task_id=s.get("celery_task_id"),
            created_at=s.get("created_at"),
            started_at=s.get("started_at"),
            completed_at=s.get("completed_at"),
        )
        for s in states
    ]
