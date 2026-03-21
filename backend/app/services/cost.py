"""Cost service for business logic."""

import uuid
from datetime import datetime
from enum import Enum


class CostType(str, Enum):
    TOKEN = "token"
    TIME = "time"


class Currency(str, Enum):
    USD = "USD"
    CNY = "CNY"


class CostService:
    """Service class for cost operations with in-memory storage."""

    def __init__(self):
        """Initialize with in-memory storage."""
        self._store: dict[str, dict] = {}

    def create_cost(
        self,
        project_id: str,
        cost_type: CostType,
        amount: float,
        task_id: str | None = None,
        currency: Currency = Currency.USD,
        description: str | None = None,
    ) -> dict:
        """Create a new cost record."""
        now = datetime.now()
        cost_id = str(uuid.uuid4())

        new_cost = {
            "id": cost_id,
            "project_id": project_id,
            "task_id": task_id,
            "cost_type": cost_type.value if isinstance(cost_type, CostType) else cost_type,
            "amount": amount,
            "currency": currency.value if isinstance(currency, Currency) else currency,
            "description": description,
            "recorded_at": now,
        }

        self._store[cost_id] = new_cost
        return new_cost

    def get_cost(self, cost_id: str) -> dict | None:
        """Get a cost record by ID."""
        return self._store.get(cost_id)

    def get_costs(
        self,
        project_id: str | None = None,
        task_id: str | None = None,
        cost_type: CostType | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict], int]:
        """Get paginated list of costs."""
        all_costs = list(self._store.values())

        # Apply filters
        if project_id:
            all_costs = [c for c in all_costs if c.get("project_id") == project_id]
        if task_id:
            all_costs = [c for c in all_costs if c.get("task_id") == task_id]
        if cost_type:
            cost_type_val = cost_type.value if isinstance(cost_type, CostType) else cost_type
            all_costs = [c for c in all_costs if c.get("cost_type") == cost_type_val]

        # Sort by recorded_at descending
        all_costs.sort(key=lambda x: x.get("recorded_at", datetime.now()), reverse=True)

        total = len(all_costs)
        start = (page - 1) * page_size
        end = start + page_size
        paginated = all_costs[start:end]

        return paginated, total

    def get_summary(
        self,
        project_id: str | None = None,
    ) -> dict:
        """Get cost summary statistics."""
        all_costs = list(self._store.values())

        if project_id:
            all_costs = [c for c in all_costs if c.get("project_id") == project_id]

        total_tokens = sum(c.get("amount", 0) for c in all_costs if c.get("cost_type") == "token")
        total_time = sum(c.get("amount", 0) for c in all_costs if c.get("cost_type") == "time")
        total_cost = total_tokens * 0.01 + total_time * 0.05

        by_type = {
            "token": total_tokens,
            "time": total_time,
        }

        by_project: dict[str, float] = {}
        for c in all_costs:
            pid = c.get("project_id", "unknown")
            amount = c.get("amount", 0)
            by_project[pid] = by_project.get(pid, 0) + amount

        return {
            "total_cost": round(total_cost, 2),
            "total_tokens": round(total_tokens, 2),
            "total_time_seconds": round(total_time, 2),
            "currency": "USD",
            "by_type": {k: round(v, 2) for k, v in by_type.items()},
            "by_project": {k: round(v, 2) for k, v in by_project.items()},
        }

    def clear_all(self) -> None:
        """Clear all costs (for testing)."""
        self._store.clear()


# Global instance
cost_service = CostService()
