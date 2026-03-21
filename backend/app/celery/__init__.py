"""Celery package for async task processing."""

from app.celery.config import celery_app

__all__ = ["celery_app"]
