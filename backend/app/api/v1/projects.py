"""Projects API endpoints."""

import math
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Project
from app.dependencies import DbSession, get_current_user
from app.schemas.project import (
    ProjectCreate,
    ProjectListResponse,
    ProjectMemberCreate,
    ProjectMemberListResponse,
    ProjectMemberResponse,
    ProjectResponse,
    ProjectUpdate,
)
from app.services.project import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


def get_project_service(db: DbSession) -> ProjectService:
    """Get project service instance."""
    return ProjectService(db)


ProjectServiceDep = Annotated[ProjectService, Depends(get_project_service)]


@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    db: DbSession,
    service: ProjectServiceDep,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> ProjectListResponse:
    """Get paginated list of projects."""
    projects, total = await service.get_projects(page=page, page_size=page_size)

    return ProjectListResponse(
        items=[ProjectResponse.model_validate(p) for p in projects],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 0,
    )


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    db: DbSession,
    service: ProjectServiceDep,
    project_data: ProjectCreate,
    # In real implementation, this would come from JWT token
    # current_user: CurrentUser,
    owner_id: uuid.UUID = Query(..., description="Owner user ID"),
) -> ProjectResponse:
    """Create a new project."""
    project = await service.create_project(project_data, owner_id)
    return ProjectResponse.model_validate(project)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    db: DbSession,
    service: ProjectServiceDep,
) -> ProjectResponse:
    """Get a project by ID."""
    project = await service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return ProjectResponse.model_validate(project)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    db: DbSession,
    service: ProjectServiceDep,
    project_data: ProjectUpdate,
) -> ProjectResponse:
    """Update a project."""
    project = await service.update_project(project_id, project_data)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return ProjectResponse.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: uuid.UUID,
    db: DbSession,
    service: ProjectServiceDep,
) -> None:
    """Delete a project."""
    deleted = await service.delete_project(project_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )


@router.get("/{project_id}/members", response_model=ProjectMemberListResponse)
async def get_project_members(
    project_id: uuid.UUID,
    db: DbSession,
    service: ProjectServiceDep,
) -> ProjectMemberListResponse:
    """Get all members of a project."""
    # Check project exists
    project = await service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    members = await service.get_project_members(project_id)
    return ProjectMemberListResponse(
        items=[ProjectMemberResponse.model_validate(m) for m in members],
        total=len(members),
    )


@router.post("/{project_id}/members", response_model=ProjectMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_project_member(
    project_id: uuid.UUID,
    db: DbSession,
    service: ProjectServiceDep,
    member_data: ProjectMemberCreate,
) -> ProjectMemberResponse:
    """Add a member to a project."""
    # Check project exists
    project = await service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    member = await service.add_project_member(
        project_id,
        member_data.user_id,
        member_data.role,
    )
    return ProjectMemberResponse.model_validate(member)


@router.delete("/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_project_member(
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    db: DbSession,
    service: ProjectServiceDep,
) -> None:
    """Remove a member from a project."""
    # Check project exists
    project = await service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    removed = await service.remove_project_member(project_id, user_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project member not found",
        )
