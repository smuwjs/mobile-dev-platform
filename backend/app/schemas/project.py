"""Project Pydantic schemas for request/response validation."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ProjectBase(BaseModel):
    """Base project schema with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: str | None = Field(None, description="Project description")
    platform: str = Field(..., min_length=1, max_length=50, description="Target platform (Android/iOS/HarmonyOS)")
    status: str = Field(default="planning", max_length=50, description="Project status")
    repository_url: str | None = Field(None, max_length=500, description="Repository URL")
    environment_variables: dict[str, Any] | None = Field(None, description="Environment variables")
    settings: dict[str, Any] | None = Field(None, description="Project settings")
    started_at: datetime | None = Field(None, description="Project start date")
    completed_at: datetime | None = Field(None, description="Project completion date")
    # 本地开发目录
    local_path: str | None = Field(None, max_length=500, description="Local development directory")
    # 规范驱动框架
    spec_framework: str = Field(default="openspec", max_length=50, description="Spec framework (openspec/speckit/superpowers)")
    # 规范配置
    spec_config: dict[str, Any] | None = Field(None, description="Spec framework configuration")


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""

    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project (all fields optional)."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    platform: str | None = Field(None, min_length=1, max_length=50)
    status: str | None = Field(None, max_length=50)
    repository_url: str | None = Field(None, max_length=500)
    environment_variables: dict[str, Any] | None = None
    settings: dict[str, Any] | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class ProjectResponse(ProjectBase):
    """Schema for project response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ProjectListResponse(BaseModel):
    """Schema for paginated project list response."""

    items: list[ProjectResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ProjectMemberBase(BaseModel):
    """Base project membership schema."""

    user_id: uuid.UUID
    role: str = Field(default="member", max_length=50)


class ProjectMemberCreate(ProjectMemberBase):
    """Schema for adding a project member."""

    pass


class ProjectMemberResponse(ProjectMemberBase):
    """Schema for project member response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ProjectMemberListResponse(BaseModel):
    """Schema for project member list response."""

    items: list[ProjectMemberResponse]
    total: int
