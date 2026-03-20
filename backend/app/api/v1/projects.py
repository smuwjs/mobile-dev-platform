"""Projects API endpoints with full CRUD operations."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory

router = APIRouter(prefix="/projects", tags=["projects"])


# Pydantic schemas
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    platform: str = Field(..., min_length=1, max_length=50)
    status: str = Field(default="planning", max_length=50)
    repository_url: str | None = None
    environment_variables: dict | None = None
    settings: dict | None = None
    owner_id: str = "default-user"
    started_at: datetime | None = None
    completed_at: datetime | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    platform: str | None = Field(None, min_length=1, max_length=50)
    status: str | None = Field(None, max_length=50)
    repository_url: str | None = None
    environment_variables: dict | None = None
    settings: dict | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class ProjectResponse(ProjectBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    items: list[ProjectResponse]
    total: int
    page: int
    page_size: int


# In-memory storage for demo (if DB not available)
_projects_store: dict[str, dict] = {}


async def get_db_session() -> AsyncSession:
    """Get async database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def _project_to_response(project: dict) -> ProjectResponse:
    """Convert project dict to response model."""
    return ProjectResponse(
        id=str(project["id"]),
        name=project["name"],
        description=project.get("description"),
        platform=project["platform"],
        status=project.get("status", "planning"),
        repository_url=project.get("repository_url"),
        environment_variables=project.get("environment_variables"),
        settings=project.get("settings"),
        owner_id=str(project["owner_id"]),
        started_at=project.get("started_at"),
        completed_at=project.get("completed_at"),
        created_at=project.get("created_at", datetime.now()),
        updated_at=project.get("updated_at", datetime.now()),
    )


@router.get("/", response_model=PaginatedResponse)
async def list_projects(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status_filter: str | None = Query(None, description="Filter by status"),
):
    """List all projects with pagination."""
    all_projects = list(_projects_store.values())

    # Filter by status if provided
    if status_filter:
        all_projects = [p for p in all_projects if p.get("status") == status_filter]

    total = len(all_projects)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = all_projects[start:end]

    return PaginatedResponse(
        items=[_project_to_response(p) for p in paginated],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    """Get project by ID."""
    if project_id not in _projects_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    return _project_to_response(_projects_store[project_id])


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(project: ProjectCreate):
    """Create a new project."""
    now = datetime.now()
    project_id = str(uuid.uuid4())

    new_project = {
        "id": project_id,
        "name": project.name,
        "description": project.description,
        "platform": project.platform,
        "status": project.status,
        "repository_url": project.repository_url,
        "environment_variables": project.environment_variables,
        "settings": project.settings,
        "owner_id": project.owner_id,
        "started_at": project.started_at,
        "completed_at": project.completed_at,
        "created_at": now,
        "updated_at": now,
    }

    _projects_store[project_id] = new_project
    return _project_to_response(new_project)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, project: ProjectUpdate):
    """Update a project."""
    if project_id not in _projects_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )

    existing = _projects_store[project_id]
    update_data = project.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        existing[key] = value

    existing["updated_at"] = datetime.now()
    _projects_store[project_id] = existing

    return _project_to_response(existing)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str):
    """Delete a project."""
    if project_id not in _projects_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )

    del _projects_store[project_id]
    return None


@router.get("/{project_id}/members")
async def list_project_members(project_id: str):
    """List project members."""
    if project_id not in _projects_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    return {"items": [], "total": 0}
