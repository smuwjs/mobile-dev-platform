"""OpenSpec API endpoints for generating requirement documents."""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.services.openspec import openspec_service

router = APIRouter(prefix="/openspec", tags=["openspec"])


# Pydantic Schemas

class ProposalRequest(BaseModel):
    """Request schema for generating a proposal."""

    project_id: str = Field(..., description="Project identifier")
    title: str = Field(..., min_length=1, max_length=255, description="Project or feature title")
    description: str = Field(..., min_length=1, description="Detailed requirement description")
    platform: str = Field(default="android", description="Target platform (android/ios/harmony)")
    requirements: list[str] | None = Field(default=None, description="List of specific requirements")


class ProposalResponse(BaseModel):
    """Response schema for proposal generation."""

    id: str
    project_id: str
    title: str
    description: str
    platform: str
    requirements: list[str]
    complexity: str
    estimated_hours: float
    status: str
    created_at: datetime
    content: dict


class DesignRequest(BaseModel):
    """Request schema for generating a design."""

    project_id: str = Field(..., description="Project identifier")
    proposal: dict = Field(..., description="Proposal document from generate_proposal")
    tech_stack: list[str] | None = Field(default=None, description="Technology stack")


class DesignResponse(BaseModel):
    """Response schema for design generation."""

    id: str
    project_id: str
    proposal_id: str
    title: str
    platform: str
    tech_stack: list[str]
    architecture: dict
    components: list[dict]
    data_models: list[dict]
    created_at: datetime
    content: dict


class SpecsRequest(BaseModel):
    """Request schema for generating specs."""

    project_id: str = Field(..., description="Project identifier")
    design: dict = Field(..., description="Design document from generate_design")


class SpecsResponse(BaseModel):
    """Response schema for specs generation."""

    specs: list[dict]
    count: int


class TasksRequest(BaseModel):
    """Request schema for generating tasks."""

    project_id: str = Field(..., description="Project identifier")
    specs: list[dict] = Field(..., description="List of specs from generate_specs")


class TasksResponse(BaseModel):
    """Response schema for tasks generation."""

    tasks: list[dict]
    count: int


class FullGenerateRequest(BaseModel):
    """Request schema for full OpenSpec generation."""

    project_id: str = Field(..., description="Project identifier")
    title: str = Field(..., min_length=1, max_length=255, description="Project or feature title")
    description: str = Field(..., min_length=1, description="Detailed requirement description")
    platform: str = Field(default="android", description="Target platform (android/ios/harmony)")
    requirements: list[str] | None = Field(default=None, description="List of specific requirements")
    tech_stack: list[str] | None = Field(default=None, description="Technology stack")


class FullGenerateResponse(BaseModel):
    """Response schema for full OpenSpec generation."""

    project_id: str
    proposal: dict
    design: dict
    specs: list[dict]
    tasks: list[dict]
    generated_at: datetime


# API Endpoints

@router.post("/proposal", response_model=ProposalResponse, status_code=status.HTTP_201_CREATED)
async def generate_proposal(request: ProposalRequest):
    """Generate a requirement proposal document.

    Creates a new proposal document with:
    - Complexity analysis
    - Hour estimation
    - Structured content (goals, requirements, constraints)
    """
    result = await openspec_service.generate_proposal(
        project_id=request.project_id,
        title=request.title,
        description=request.description,
        platform=request.platform,
        requirements=request.requirements,
    )
    return ProposalResponse(**result)


@router.post("/design", response_model=DesignResponse, status_code=status.HTTP_201_CREATED)
async def generate_design(request: DesignRequest):
    """Generate technical architecture design document.

    Creates a design document based on the proposal with:
    - Architecture diagram structure
    - Component breakdown
    - Data models
    - Tech stack selection
    """
    result = await openspec_service.generate_design(
        project_id=request.project_id,
        proposal=request.proposal,
        tech_stack=request.tech_stack,
    )
    return DesignResponse(**result)


@router.post("/specs", response_model=SpecsResponse, status_code=status.HTTP_201_CREATED)
async def generate_specs(request: SpecsRequest):
    """Generate functional specification breakdown.

    Creates specification items for each component in the design with:
    - Functional requirements
    - Non-functional requirements
    - Acceptance criteria
    """
    specs = await openspec_service.generate_specs(
        project_id=request.project_id,
        design=request.design,
    )
    return SpecsResponse(specs=specs, count=len(specs))


@router.post("/tasks", response_model=TasksResponse, status_code=status.HTTP_201_CREATED)
async def generate_tasks(request: TasksRequest):
    """Generate implementation task list.

    Creates actionable tasks from specs with:
    - Estimated hours
    - Dependencies
    - Priority levels
    """
    tasks = await openspec_service.generate_tasks(
        project_id=request.project_id,
        specs=request.specs,
    )
    return TasksResponse(tasks=tasks, count=len(tasks))


@router.post("/full", response_model=FullGenerateResponse, status_code=status.HTTP_201_CREATED)
async def generate_full(request: FullGenerateRequest):
    """Generate complete OpenSpec documentation in one flow.

    This endpoint runs the full pipeline:
    1. Generate proposal
    2. Generate design
    3. Generate specs
    4. Generate tasks

    Returns all generated documents in a single response.
    """
    result = await openspec_service.generate_full(
        project_id=request.project_id,
        title=request.title,
        description=request.description,
        platform=request.platform,
        requirements=request.requirements,
        tech_stack=request.tech_stack,
    )
    return FullGenerateResponse(**result)


# Query endpoints

@router.get("/proposal/{project_id}", response_model=ProposalResponse | None)
async def get_proposal(project_id: str):
    """Get the latest proposal for a project."""
    proposal = openspec_service.get_proposal(project_id)
    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposal not found for project {project_id}",
        )
    return ProposalResponse(**proposal)


@router.get("/design/{project_id}", response_model=DesignResponse | None)
async def get_design(project_id: str):
    """Get the latest design for a project."""
    design = openspec_service.get_design(project_id)
    if not design:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Design not found for project {project_id}",
        )
    return DesignResponse(**design)


@router.get("/specs/{project_id}", response_model=SpecsResponse)
async def get_specs(project_id: str):
    """Get all specs for a project."""
    specs = openspec_service.get_specs(project_id)
    return SpecsResponse(specs=specs, count=len(specs))


@router.get("/tasks/{project_id}", response_model=TasksResponse)
async def get_tasks(project_id: str):
    """Get all tasks for a project."""
    tasks = openspec_service.get_tasks(project_id)
    return TasksResponse(tasks=tasks, count=len(tasks))
