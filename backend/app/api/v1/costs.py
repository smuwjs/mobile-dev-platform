"""Costs API endpoints for tracking project costs (tokens/time)."""

import uuid
from datetime import datetime
from enum import Enum

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/costs", tags=["costs"])


class CostType(str, Enum):
    TOKEN = "token"
    TIME = "time"


class Currency(str, Enum):
    USD = "USD"
    CNY = "CNY"


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


# In-memory storage
_costs_store: dict[str, dict] = {}


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
    all_costs = list(_costs_store.values())

    # Apply filters
    if project_id:
        all_costs = [c for c in all_costs if c.get("project_id") == project_id]
    if task_id:
        all_costs = [c for c in all_costs if c.get("task_id") == task_id]
    if cost_type:
        all_costs = [c for c in all_costs if c.get("cost_type") == cost_type.value]

    # Sort by recorded_at descending
    all_costs.sort(key=lambda x: x.get("recorded_at", datetime.now()), reverse=True)

    total = len(all_costs)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = all_costs[start:end]

    return PaginatedResponse(
        items=[_cost_to_response(c) for c in paginated],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/", response_model=CostResponse, status_code=status.HTTP_201_CREATED)
async def create_cost(cost: CostCreate):
    """Create a new cost record."""
    now = datetime.now()
    cost_id = str(uuid.uuid4())

    new_cost = {
        "id": cost_id,
        "project_id": cost.project_id,
        "task_id": cost.task_id,
        "cost_type": cost.cost_type.value,
        "amount": cost.amount,
        "currency": cost.currency.value,
        "description": cost.description,
        "recorded_at": now,
    }

    _costs_store[cost_id] = new_cost
    return _cost_to_response(new_cost)


@router.get("/summary", response_model=CostSummary)
async def get_cost_summary(
    project_id: str | None = Query(None, description="Filter by project ID"),
):
    """Get cost summary statistics."""
    all_costs = list(_costs_store.values())

    if project_id:
        all_costs = [c for c in all_costs if c.get("project_id") == project_id]

    total_tokens = sum(c.get("amount", 0) for c in all_costs if c.get("cost_type") == "token")
    total_time = sum(c.get("amount", 0) for c in all_costs if c.get("cost_type") == "time")
    total_cost = total_tokens * 0.01 + total_time * 0.05  # Rough estimate

    by_type = {
        "token": total_tokens,
        "time": total_time,
    }

    by_project: dict[str, float] = {}
    for c in all_costs:
        pid = c.get("project_id", "unknown")
        amount = c.get("amount", 0)
        by_project[pid] = by_project.get(pid, 0) + amount

    return CostSummary(
        total_cost=round(total_cost, 2),
        total_tokens=round(total_tokens, 2),
        total_time_seconds=round(total_time, 2),
        currency="USD",
        by_type={k: round(v, 2) for k, v in by_type.items()},
        by_project={k: round(v, 2) for k, v in by_project.items()},
    )
