"""API v1 module for versioned routes."""

from app.api.v1.projects import router as projects_router

__all__ = ["projects_router"]
