"""Tests for requirement service."""
import pytest
from datetime import datetime

from app.services.requirement import RequirementService, requirement_service


class TestRequirementService:
    """Tests for RequirementService class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = RequirementService()

    def test_create_requirement(self):
        """Test creating a requirement."""
        req = self.service.create_requirement(
            title="Test Requirement",
            project_id="project-1",
            description="A test requirement",
            priority="high",
            status="pending",
            created_by="test-user",
        )

        assert req["title"] == "Test Requirement"
        assert req["project_id"] == "project-1"
        assert req["description"] == "A test requirement"
        assert req["priority"] == "high"
        assert req["status"] == "pending"
        assert req["created_by"] == "test-user"
        assert "id" in req
        assert "created_at" in req
        assert "updated_at" in req

    def test_create_requirement_defaults(self):
        """Test creating a requirement with default values."""
        req = self.service.create_requirement(
            title="Minimal Requirement",
            project_id="project-1",
        )

        assert req["title"] == "Minimal Requirement"
        assert req["priority"] == "medium"
        assert req["status"] == "pending"
        assert req["created_by"] == "default-user"

    def test_get_requirement(self):
        """Test getting a requirement by ID."""
        created = self.service.create_requirement(title="Get Test", project_id="project-1")
        retrieved = self.service.get_requirement(created["id"])

        assert retrieved is not None
        assert retrieved["id"] == created["id"]
        assert retrieved["title"] == "Get Test"

    def test_get_requirement_not_found(self):
        """Test getting a nonexistent requirement."""
        result = self.service.get_requirement("nonexistent-id")
        assert result is None

    def test_get_requirements_empty(self):
        """Test getting requirements when none exist."""
        reqs, total = self.service.get_requirements()
        assert reqs == []
        assert total == 0

    def test_get_requirements_multiple(self):
        """Test getting multiple requirements."""
        self.service.create_requirement(title="Req 1", project_id="project-1")
        self.service.create_requirement(title="Req 2", project_id="project-1")
        self.service.create_requirement(title="Req 3", project_id="project-2")

        reqs, total = self.service.get_requirements()
        assert total == 3

    def test_get_requirements_filter_by_project(self):
        """Test filtering requirements by project."""
        self.service.create_requirement(title="Req 1", project_id="project-1")
        self.service.create_requirement(title="Req 2", project_id="project-1")
        self.service.create_requirement(title="Req 3", project_id="project-2")

        reqs, total = self.service.get_requirements(project_id="project-1")
        assert total == 2
        for r in reqs:
            assert r["project_id"] == "project-1"

    def test_get_requirements_filter_by_status(self):
        """Test filtering requirements by status."""
        self.service.create_requirement(title="Req 1", project_id="project-1", status="pending")
        self.service.create_requirement(title="Req 2", project_id="project-1", status="implemented")
        self.service.create_requirement(title="Req 3", project_id="project-1", status="pending")

        reqs, total = self.service.get_requirements(status_filter="pending")
        assert total == 2
        for r in reqs:
            assert r["status"] == "pending"

    def test_get_requirements_pagination(self):
        """Test paginating requirements."""
        for i in range(25):
            self.service.create_requirement(title=f"Req {i}", project_id="project-1")

        # First page
        reqs, total = self.service.get_requirements(page=1, page_size=10)
        assert total == 25
        assert len(reqs) == 10

        # Second page
        reqs, total = self.service.get_requirements(page=2, page_size=10)
        assert total == 25
        assert len(reqs) == 10

        # Third page (partial)
        reqs, total = self.service.get_requirements(page=3, page_size=10)
        assert total == 25
        assert len(reqs) == 5

    def test_update_requirement(self):
        """Test updating a requirement."""
        created = self.service.create_requirement(title="Original", project_id="project-1")
        original_updated_at = created["updated_at"]

        updated = self.service.update_requirement(
            created["id"],
            title="Updated",
            priority="low",
            status="implemented",
        )

        assert updated is not None
        assert updated["title"] == "Updated"
        assert updated["priority"] == "low"
        assert updated["status"] == "implemented"
        assert updated["updated_at"] > original_updated_at

    def test_update_requirement_not_found(self):
        """Test updating a nonexistent requirement."""
        result = self.service.update_requirement("nonexistent-id", title="New Title")
        assert result is None

    def test_delete_requirement(self):
        """Test deleting a requirement."""
        created = self.service.create_requirement(title="To Delete", project_id="project-1")
        deleted = self.service.delete_requirement(created["id"])

        assert deleted is True
        assert self.service.get_requirement(created["id"]) is None

    def test_delete_requirement_not_found(self):
        """Test deleting a nonexistent requirement."""
        result = self.service.delete_requirement("nonexistent-id")
        assert result is False

    def test_clear_all(self):
        """Test clearing all requirements."""
        self.service.create_requirement(title="Req 1", project_id="project-1")
        self.service.create_requirement(title="Req 2", project_id="project-1")

        self.service.clear_all()

        reqs, total = self.service.get_requirements()
        assert total == 0


class TestRequirementServiceSingleton:
    """Tests for the requirement_service singleton."""

    def setup_method(self):
        """Clear the singleton before each test."""
        requirement_service.clear_all()

    def test_singleton_persists_data(self):
        """Test that the singleton persists data between operations."""
        requirement_service.create_requirement(title="Singleton Req", project_id="project-1")

        req_id = list(requirement_service._store.keys())[0]
        req = requirement_service.get_requirement(req_id)
        assert req["title"] == "Singleton Req"
