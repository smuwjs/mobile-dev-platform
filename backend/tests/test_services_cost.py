"""Tests for cost service."""
import pytest
from datetime import datetime

from app.services.cost import CostService, cost_service, CostType, Currency


class TestCostService:
    """Tests for CostService class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = CostService()

    def test_create_cost(self):
        """Test creating a cost record."""
        cost = self.service.create_cost(
            project_id="project-1",
            cost_type=CostType.TOKEN,
            amount=1000.0,
            task_id="task-1",
            currency=Currency.USD,
            description="API usage",
        )

        assert cost["project_id"] == "project-1"
        assert cost["cost_type"] == "token"
        assert cost["amount"] == 1000.0
        assert cost["task_id"] == "task-1"
        assert cost["currency"] == "USD"
        assert cost["description"] == "API usage"
        assert "id" in cost
        assert "recorded_at" in cost

    def test_create_cost_defaults(self):
        """Test creating a cost record with default values."""
        cost = self.service.create_cost(
            project_id="project-1",
            cost_type=CostType.TIME,
            amount=60.0,
        )

        assert cost["currency"] == "USD"
        assert cost["task_id"] is None
        assert cost["description"] is None

    def test_create_cost_with_string_cost_type(self):
        """Test creating a cost record with string cost type."""
        cost = self.service.create_cost(
            project_id="project-1",
            cost_type="token",
            amount=500.0,
        )

        assert cost["cost_type"] == "token"

    def test_get_cost(self):
        """Test getting a cost by ID."""
        created = self.service.create_cost(
            project_id="project-1",
            cost_type=CostType.TOKEN,
            amount=100.0,
        )
        retrieved = self.service.get_cost(created["id"])

        assert retrieved is not None
        assert retrieved["id"] == created["id"]
        assert retrieved["amount"] == 100.0

    def test_get_cost_not_found(self):
        """Test getting a nonexistent cost."""
        result = self.service.get_cost("nonexistent-id")
        assert result is None

    def test_get_costs_empty(self):
        """Test getting costs when none exist."""
        costs, total = self.service.get_costs()
        assert costs == []
        assert total == 0

    def test_get_costs_multiple(self):
        """Test getting multiple costs."""
        self.service.create_cost(project_id="project-1", cost_type=CostType.TOKEN, amount=100.0)
        self.service.create_cost(project_id="project-1", cost_type=CostType.TIME, amount=60.0)
        self.service.create_cost(project_id="project-2", cost_type=CostType.TOKEN, amount=200.0)

        costs, total = self.service.get_costs()
        assert total == 3

    def test_get_costs_filter_by_project(self):
        """Test filtering costs by project."""
        self.service.create_cost(project_id="project-1", cost_type=CostType.TOKEN, amount=100.0)
        self.service.create_cost(project_id="project-1", cost_type=CostType.TOKEN, amount=200.0)
        self.service.create_cost(project_id="project-2", cost_type=CostType.TOKEN, amount=300.0)

        costs, total = self.service.get_costs(project_id="project-1")
        assert total == 2
        for c in costs:
            assert c["project_id"] == "project-1"

    def test_get_costs_filter_by_task(self):
        """Test filtering costs by task."""
        self.service.create_cost(project_id="project-1", task_id="task-1", cost_type=CostType.TOKEN, amount=100.0)
        self.service.create_cost(project_id="project-1", task_id="task-2", cost_type=CostType.TOKEN, amount=200.0)
        self.service.create_cost(project_id="project-1", cost_type=CostType.TOKEN, amount=300.0)

        costs, total = self.service.get_costs(task_id="task-1")
        assert total == 1
        assert costs[0]["task_id"] == "task-1"

    def test_get_costs_filter_by_cost_type(self):
        """Test filtering costs by cost type."""
        self.service.create_cost(project_id="project-1", cost_type=CostType.TOKEN, amount=100.0)
        self.service.create_cost(project_id="project-1", cost_type=CostType.TIME, amount=60.0)
        self.service.create_cost(project_id="project-1", cost_type=CostType.TOKEN, amount=200.0)

        costs, total = self.service.get_costs(cost_type=CostType.TOKEN)
        assert total == 2
        for c in costs:
            assert c["cost_type"] == "token"

    def test_get_costs_pagination(self):
        """Test paginating costs."""
        for i in range(25):
            self.service.create_cost(project_id="project-1", cost_type=CostType.TOKEN, amount=float(i))

        # First page
        costs, total = self.service.get_costs(page=1, page_size=10)
        assert total == 25
        assert len(costs) == 10

        # Second page
        costs, total = self.service.get_costs(page=2, page_size=10)
        assert total == 25
        assert len(costs) == 10

        # Third page (partial)
        costs, total = self.service.get_costs(page=3, page_size=10)
        assert total == 25
        assert len(costs) == 5

    def test_get_summary_empty(self):
        """Test getting summary when no costs exist."""
        summary = self.service.get_summary()

        assert summary["total_cost"] == 0.0
        assert summary["total_tokens"] == 0.0
        assert summary["total_time_seconds"] == 0.0
        assert summary["currency"] == "USD"

    def test_get_summary_tokens(self):
        """Test getting summary with token costs."""
        self.service.create_cost(project_id="project-1", cost_type=CostType.TOKEN, amount=1000.0)
        self.service.create_cost(project_id="project-1", cost_type=CostType.TOKEN, amount=2000.0)

        summary = self.service.get_summary()

        assert summary["total_tokens"] == 3000.0
        assert summary["total_time_seconds"] == 0.0
        # 1000 * 0.01 + 2000 * 0.01 = 30.0
        assert summary["total_cost"] == 30.0

    def test_get_summary_time(self):
        """Test getting summary with time costs."""
        self.service.create_cost(project_id="project-1", cost_type=CostType.TIME, amount=60.0)
        self.service.create_cost(project_id="project-1", cost_type=CostType.TIME, amount=120.0)

        summary = self.service.get_summary()

        assert summary["total_tokens"] == 0.0
        assert summary["total_time_seconds"] == 180.0
        # 60 * 0.05 + 120 * 0.05 = 9.0
        assert summary["total_cost"] == 9.0

    def test_get_summary_mixed(self):
        """Test getting summary with mixed costs."""
        self.service.create_cost(project_id="project-1", cost_type=CostType.TOKEN, amount=1000.0)
        self.service.create_cost(project_id="project-1", cost_type=CostType.TIME, amount=100.0)
        self.service.create_cost(project_id="project-2", cost_type=CostType.TOKEN, amount=500.0)

        summary = self.service.get_summary()

        assert summary["total_tokens"] == 1500.0
        assert summary["total_time_seconds"] == 100.0
        # (1000 + 500) * 0.01 + 100 * 0.05 = 15.0 + 5.0 = 20.0
        assert summary["total_cost"] == 20.0
        assert "project-1" in summary["by_project"]
        assert "project-2" in summary["by_project"]

    def test_get_summary_by_project(self):
        """Test getting summary filtered by project."""
        self.service.create_cost(project_id="project-1", cost_type=CostType.TOKEN, amount=1000.0)
        self.service.create_cost(project_id="project-2", cost_type=CostType.TOKEN, amount=2000.0)

        summary = self.service.get_summary(project_id="project-1")

        assert summary["total_tokens"] == 1000.0
        assert summary["total_time_seconds"] == 0.0

    def test_clear_all(self):
        """Test clearing all costs."""
        self.service.create_cost(project_id="project-1", cost_type=CostType.TOKEN, amount=100.0)
        self.service.create_cost(project_id="project-1", cost_type=CostType.TIME, amount=60.0)

        self.service.clear_all()

        costs, total = self.service.get_costs()
        assert total == 0


class TestCostServiceSingleton:
    """Tests for the cost_service singleton."""

    def setup_method(self):
        """Clear the singleton before each test."""
        cost_service.clear_all()

    def test_singleton_persists_data(self):
        """Test that the singleton persists data between operations."""
        cost_service.create_cost(project_id="project-1", cost_type=CostType.TOKEN, amount=100.0)

        cost_id = list(cost_service._store.keys())[0]
        cost = cost_service.get_cost(cost_id)
        assert cost["amount"] == 100.0
