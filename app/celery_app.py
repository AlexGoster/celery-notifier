"""Celery application instance."""

from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "notifier",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.notifications"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,
    task_default_retry_delay=60,
    task_max_retries=3,
    result_expires=3600,
    beat_schedule={
        "send-daily-notifications": {
            "task": "app.tasks.notifications.send_daily_notifications",
            "schedule": crontab(minute="*/30"),
        },
    },
    beat_scheduler_kwargs={"sync_every": 1},
)
