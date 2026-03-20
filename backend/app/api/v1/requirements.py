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
