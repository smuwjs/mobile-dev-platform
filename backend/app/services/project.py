"""Project service for business logic."""

import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Project, ProjectMembership, User
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
)


class ProjectService:
    """Service class for project operations."""

    def __init__(self, db: AsyncSession):
        """Initialize with database session."""
        self.db = db

    async def create_project(
        self,
        project_data: ProjectCreate,
        owner_id: uuid.UUID,
    ) -> Project:
        """Create a new project."""
        project = Project(
            name=project_data.name,
            description=project_data.description,
            platform=project_data.platform,
            status=project_data.status,
            repository_url=project_data.repository_url,
            environment_variables=project_data.environment_variables,
            settings=project_data.settings,
            owner_id=owner_id,
            started_at=project_data.started_at,
            completed_at=project_data.completed_at,
        )
        self.db.add(project)
        await self.db.flush()

        # Add owner as a member with 'owner' role
        membership = ProjectMembership(
            project_id=project.id,
            user_id=owner_id,
            role="owner",
        )
        self.db.add(membership)
        await self.db.flush()

        await self.db.refresh(project)
        return project

    async def get_project_by_id(
        self,
        project_id: uuid.UUID,
    ) -> Project | None:
        """Get a project by ID."""
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def get_projects(
        self,
        page: int = 1,
        page_size: int = 20,
        owner_id: uuid.UUID | None = None,
    ) -> tuple[list[Project], int]:
        """Get paginated list of projects."""
        query = select(Project)

        if owner_id:
            query = query.where(Project.owner_id == owner_id)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(Project.created_at.desc())

        result = await self.db.execute(query)
        projects = list(result.scalars().all())

        return projects, total

    async def update_project(
        self,
        project_id: uuid.UUID,
        project_data: ProjectUpdate,
    ) -> Project | None:
        """Update a project."""
        project = await self.get_project_by_id(project_id)
        if not project:
            return None

        update_data = project_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)

        await self.db.flush()
        await self.db.refresh(project)
        return project

    async def delete_project(
        self,
        project_id: uuid.UUID,
    ) -> bool:
        """Delete a project."""
        project = await self.get_project_by_id(project_id)
        if not project:
            return False

        await self.db.delete(project)
        await self.db.flush()
        return True

    async def get_project_members(
        self,
        project_id: uuid.UUID,
    ) -> list[ProjectMembership]:
        """Get all members of a project."""
        result = await self.db.execute(
            select(ProjectMembership)
            .where(ProjectMembership.project_id == project_id)
            .options(selectinload(ProjectMembership.user))
        )
        return list(result.scalars().all())

    async def add_project_member(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        role: str = "member",
    ) -> ProjectMembership:
        """Add a member to a project."""
        membership = ProjectMembership(
            project_id=project_id,
            user_id=user_id,
            role=role,
        )
        self.db.add(membership)
        await self.db.flush()
        await self.db.refresh(membership)
        return membership

    async def remove_project_member(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        """Remove a member from a project."""
        result = await self.db.execute(
            select(ProjectMembership).where(
                ProjectMembership.project_id == project_id,
                ProjectMembership.user_id == user_id,
            )
        )
        membership = result.scalar_one_or_none()
        if not membership:
            return False

        await self.db.delete(membership)
        await self.db.flush()
        return True
