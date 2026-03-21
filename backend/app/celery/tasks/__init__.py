"""Celery tasks package."""

from app.celery.tasks import execution, requirement

__all__ = ["execution", "requirement"]
