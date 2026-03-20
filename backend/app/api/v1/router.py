"""API v1 router - aggregates all sub-routes."""

from fastapi import APIRouter

from app.api.v1.projects import router as projects_router
from app.api.v1.requirements import router as requirements_router, _standalone_requirements_router
from app.api.v1.tasks import router as tasks_router, _project_tasks_router

router = APIRouter(prefix="/api/v1")

# Include sub-routers
router.include_router(projects_router)
router.include_router(_project_tasks_router)
router.include_router(requirements_router)
router.include_router(tasks_router)
router.include_router(_standalone_requirements_router)
