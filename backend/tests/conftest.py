"""Test configuration and fixtures."""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    from app.main import app
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    """Register a user and return auth headers."""
    # Register a test user
    client.post(
        "/api/v1/auth/register",
        json={"username": "testuser", "password": "testpass"}
    )
    # Login to get token
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "testpass"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
