"""Celery configuration."""

from celery import Celery
from kombu import Exchange, Queue

from app.config import settings


def create_celery_app() -> Celery:
    """Create and configure Celery application."""
    celery_app = Celery(
        "mobile_dev_platform",
        broker=settings.redis.url,
        backend=settings.redis.url,
        include=[
            "app.celery.tasks.requirement",
            "app.celery.tasks.execution",
        ],
    )

    # Celery configuration
    celery_app.conf.update(
        # Task serialization
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        # Result configuration
        result_expires=3600,  # 1 hour
        task_track_started=True,
        task_acks_late=True,
        task_reject_on_worker_lost=True,
        # Worker configuration
        worker_prefetch_multiplier=1,
        worker_concurrency=4,
        # Task routing
        task_default_queue="default",
        task_default_exchange="default",
        task_default_routing_key="default",
        # Periodic tasks (for monitoring)
        beat_schedule={},
    )

    # Define queues
    celery_app.conf.task_queues = (
        Queue(
            "default",
            Exchange("default"),
            routing_key="default",
        ),
        Queue(
            "requirements",
            Exchange("requirements"),
            routing_key="requirements",
        ),
        Queue(
            "execution",
            Exchange("execution"),
            routing_key="execution",
        ),
        Queue(
            "code_generation",
            Exchange("code_generation"),
            routing_key="code_generation",
        ),
        Queue(
            "test_generation",
            Exchange("test_generation"),
            routing_key="test_generation",
        ),
    )

    # Task routing rules
    celery_app.conf.task_routes = {
        "app.celery.tasks.requirement.*": {
            "queue": "requirements",
            "routing_key": "requirements",
        },
        "app.celery.tasks.execution.execute_code_generation": {
            "queue": "code_generation",
            "routing_key": "code_generation",
        },
        "app.celery.tasks.execution.execute_test_generation": {
            "queue": "test_generation",
            "routing_key": "test_generation",
        },
    }

    return celery_app


# Create the Celery app instance
celery_app = create_celery_app()
