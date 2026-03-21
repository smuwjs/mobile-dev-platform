"""Tests for projects endpoints."""
import pytest


class TestProjectsList:
    """Tests for listing projects."""

    def test_list_projects_empty(self, client, auth_headers):
        """Test listing projects when none exist."""
        response = client.get("/api/v1/projects/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 0

    def test_list_projects_pagination(self, client, auth_headers):
        """Test projects pagination."""
        response = client.get(
            "/api/v1/projects/",
            params={"page": 1, "page_size": 10},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 10


class TestProjectsCreate:
    """Tests for creating projects."""

    def test_create_project(self, client, auth_headers):
        """Test creating a new project."""
        response = client.post(
            "/api/v1/projects/",
            json={
                "name": "Test Project",
                "platform": "android",
                "description": "A test project"
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Project"
        assert data["platform"] == "android"
        assert "id" in data

    def test_create_project_missing_name(self, client, auth_headers):
        """Test creating project without name fails."""
        response = client.post(
            "/api/v1/projects/",
            json={"platform": "android"},
            headers=auth_headers
        )
        assert response.status_code == 422  # Validation error


class TestProjectsGet:
    """Tests for getting a single project."""

    def test_get_project(self, client, auth_headers):
        """Test getting a project by ID."""
        # Create a project first
        create_response = client.post(
            "/api/v1/projects/",
            json={"name": "Get Test", "platform": "ios"},
            headers=auth_headers
        )
        project_id = create_response.json()["id"]

        # Get the project
        response = client.get(f"/api/v1/projects/{project_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Get Test"

    def test_get_project_not_found(self, client, auth_headers):
        """Test getting nonexistent project fails."""
        response = client.get(
            "/api/v1/projects/nonexistent-id",
            headers=auth_headers
        )
        assert response.status_code == 404


class TestProjectsUpdate:
    """Tests for updating projects."""

    def test_update_project(self, client, auth_headers):
        """Test updating a project."""
        # Create a project first
        create_response = client.post(
            "/api/v1/projects/",
            json={"name": "Original Name", "platform": "android"},
            headers=auth_headers
        )
        project_id = create_response.json()["id"]

        # Update the project
        response = client.put(
            f"/api/v1/projects/{project_id}",
            json={"name": "Updated Name"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"

    def test_update_project_not_found(self, client, auth_headers):
        """Test updating nonexistent project fails."""
        response = client.put(
            "/api/v1/projects/nonexistent-id",
            json={"name": "New Name"},
            headers=auth_headers
        )
        assert response.status_code == 404


class TestProjectsDelete:
    """Tests for deleting projects."""

    def test_delete_project(self, client, auth_headers):
        """Test deleting a project."""
        # Create a project first
        create_response = client.post(
            "/api/v1/projects/",
            json={"name": "To Delete", "platform": "harmony"},
            headers=auth_headers
        )
        project_id = create_response.json()["id"]

        # Delete the project
        response = client.delete(
            f"/api/v1/projects/{project_id}",
            headers=auth_headers
        )
        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get(
            f"/api/v1/projects/{project_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    def test_delete_project_not_found(self, client, auth_headers):
        """Test deleting nonexistent project fails."""
        response = client.delete(
            "/api/v1/projects/nonexistent-id",
            headers=auth_headers
        )
        assert response.status_code == 404
