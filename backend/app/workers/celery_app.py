"""Celery application configured with Redis broker and result backend."""

from celery import Celery

from backend.app.core.config import Settings

settings = Settings()
celery_app = Celery(
    "pdf_converter",
    broker=settings.redis_url,
    backend=settings.result_backend,
    include=["backend.app.workers.tasks"],
)

