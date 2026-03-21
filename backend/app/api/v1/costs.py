"""Costs API endpoints for tracking project costs (tokens/time)."""

from datetime import datetime
from enum import Enum

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.services.cost import cost_service, CostType, Currency

router = APIRouter(prefix="/costs", tags=["costs"])


# Pydantic schemas
class CostBase(BaseModel):
    project_id: str = Field(..., min_length=1)
    task_id: str | None = None
    cost_type: CostType
    amount: float = Field(..., gt=0)
    currency: Currency = Currency.USD
    description: str | None = None


class CostCreate(CostBase):
    pass


class CostResponse(CostBase):
    id: str
    recorded_at: datetime

    class Config:
        from_attributes = True


class CostSummary(BaseModel):
    total_cost: float
    total_tokens: float
    total_time_seconds: float
    currency: str
    by_type: dict[str, float]
    by_project: dict[str, float]


class PaginatedResponse(BaseModel):
    items: list[CostResponse]
    total: int
    page: int
    page_size: int


def _cost_to_response(cost: dict) -> CostResponse:
    """Convert cost dict to response model."""
    return CostResponse(
        id=str(cost["id"]),
        project_id=str(cost["project_id"]),
        task_id=cost.get("task_id"),
        cost_type=cost["cost_type"],
        amount=cost["amount"],
        currency=cost["currency"],
        description=cost.get("description"),
        recorded_at=cost.get("recorded_at", datetime.now()),
    )


@router.get("/", response_model=PaginatedResponse)
async def list_costs(
    project_id: str | None = Query(None, description="Filter by project ID"),
    task_id: str | None = Query(None, description="Filter by task ID"),
    cost_type: CostType | None = Query(None, description="Filter by cost type"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """Get cost records list."""
    costs, total = cost_service.get_costs(
        project_id=project_id,
        task_id=task_id,
        cost_type=cost_type,
        page=page,
        page_size=page_size,
    )

    return PaginatedResponse(
        items=[_cost_to_response(c) for c in costs],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/", response_model=CostResponse, status_code=status.HTTP_201_CREATED)
async def create_cost(cost: CostCreate):
    """Create a new cost record."""
    new_cost = cost_service.create_cost(
        project_id=cost.project_id,
        cost_type=cost.cost_type,
        amount=cost.amount,
        task_id=cost.task_id,
        currency=cost.currency,
        description=cost.description,
    )
    return _cost_to_response(new_cost)


@router.get("/summary", response_model=CostSummary)
async def get_cost_summary(
    project_id: str | None = Query(None, description="Filter by project ID"),
):
    """Get cost summary statistics."""
    summary = cost_service.get_summary(project_id=project_id)
    return CostSummary(**summary)


# Export for dashboard service access
_costs_store = cost_service._store
