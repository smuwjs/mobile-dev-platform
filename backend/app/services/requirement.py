"""Requirement service for business logic."""

import uuid
from datetime import datetime


class RequirementService:
    """Service class for requirement operations with in-memory storage."""

    def __init__(self):
        """Initialize with in-memory storage."""
        self._store: dict[str, dict] = {}

    def create_requirement(
        self,
        title: str,
        project_id: str,
        description: str | None = None,
        priority: str = "medium",
        status: str = "pending",
        created_by: str = "default-user",
    ) -> dict:
        """Create a new requirement."""
        now = datetime.now()
        requirement_id = str(uuid.uuid4())

        new_requirement = {
            "id": requirement_id,
            "project_id": project_id,
            "title": title,
            "description": description,
            "priority": priority,
            "status": status,
            "created_by": created_by,
            "created_at": now,
            "updated_at": now,
        }

        self._store[requirement_id] = new_requirement
        return new_requirement

    def get_requirement(self, requirement_id: str) -> dict | None:
        """Get a requirement by ID."""
        return self._store.get(requirement_id)

    def get_requirements(
        self,
        project_id: str | None = None,
        status_filter: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict], int]:
        """Get paginated list of requirements."""
        all_requirements = list(self._store.values())

        # Filter by project_id if provided
        if project_id:
            all_requirements = [r for r in all_requirements if r.get("project_id") == project_id]

        # Filter by status if provided
        if status_filter:
            all_requirements = [r for r in all_requirements if r.get("status") == status_filter]

        total = len(all_requirements)
        start = (page - 1) * page_size
        end = start + page_size
        paginated = all_requirements[start:end]

        return paginated, total

    def update_requirement(
        self,
        requirement_id: str,
        title: str | None = None,
        description: str | None = None,
        priority: str | None = None,
        status: str | None = None,
    ) -> dict | None:
        """Update a requirement."""
        if requirement_id not in self._store:
            return None

        existing = self._store[requirement_id]

        if title is not None:
            existing["title"] = title
        if description is not None:
            existing["description"] = description
        if priority is not None:
            existing["priority"] = priority
        if status is not None:
            existing["status"] = status

        existing["updated_at"] = datetime.now()
        self._store[requirement_id] = existing
        return existing

    def delete_requirement(self, requirement_id: str) -> bool:
        """Delete a requirement."""
        if requirement_id not in self._store:
            return False

        del self._store[requirement_id]
        return True

    def clear_all(self) -> None:
        """Clear all requirements (for testing)."""
        self._store.clear()


# Global instance
requirement_service = RequirementService()
