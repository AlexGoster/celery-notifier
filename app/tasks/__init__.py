"""Task execution functions (Celery tasks)."""

import asyncio
import json
import logging
from typing import Any

from celery import Task as CeleryTask
from celery import shared_task
from sqlalchemy import update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.celery_app import celery_app
from app.config import settings
from app.models import Notification, Task
from app.notifications.channels import get_channel

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_notification(
    self: CeleryTask, recipient: str, subject: str, body: str
) -> dict[str, Any]:
    try:
        logger.info(f"Sending email to {recipient}: {subject}")
        if not _mock_send_sms_or_email(recipient, subject, body):
            raise OSError("Notification delivery failed")
        return {"status": "sent", "recipient": recipient, "subject": subject}
    except Exception as exc:
        logger.warning(f"Email send failed, retrying: {exc}")
        raise self.retry(exc=exc) from exc


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_sms_notification(self: CeleryTask, recipient: str, body: str) -> dict[str, Any]:
    try:
        logger.info(f"Sending SMS to {recipient}: {body}")
        return {"status": "sent", "recipient": recipient, "body": body[:20]}
    except Exception as exc:
        raise self.retry(exc=exc) from exc


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_push_notification(
    self: CeleryTask, recipient: str, title: str, body: str
) -> dict[str, Any]:
    try:
        logger.info(f"Sending push to {recipient}: {title}")
        return {"status": "sent", "recipient": recipient, "title": title}
    except Exception as exc:
        raise self.retry(exc=exc) from exc


@shared_task
def send_daily_notifications() -> dict[str, Any]:
    logger.info("Sending daily notifications batch")
    return {"status": "batch_sent", "count": 0}


def _mock_send_sms_or_email(recipient: str, subject: str, body: str) -> bool:
    logger.info(f"[MOCK] Email to {recipient}: {subject}")
    return True


async def _process_notification(task_id: int) -> dict[str, Any]:
    engine = create_async_engine(settings.database_url, poolclass=NullPool)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with factory() as session:
            async with session.begin():
                claimed = await session.scalar(
                    update(Task)
                    .where(Task.id == task_id, Task.status.in_(["pending", "failed"]))
                    .values(status="running")
                    .returning(Task.id)
                )
                task = await session.get(Task, task_id)
                if task is None:
                    return {"status": "missing"}
                if claimed is None:
                    return {"status": task.status}
                recipient = (
                    settings.notifications_email
                    if task.task_type == "email"
                    else str(task.owner_id)
                )
                sent = await get_channel(task.task_type).send(
                    recipient, task.title, task.description or ""
                )
                if not sent:
                    raise OSError("Notification channel failed")
                session.add(
                    Notification(
                        task_id=task.id,
                        channel=task.task_type,
                        recipient=recipient,
                        subject=task.title,
                        body=task.description or "",
                        status="sent",
                    )
                )
                task.status = "completed"
                task.result = json.dumps({"status": "sent", "channel": task.task_type})
                return {"status": "completed", "task_id": task.id}
    finally:
        await engine.dispose()


@celery_app.task(
    name="app.tasks.process_notification",
    autoretry_for=(OSError,),
    retry_backoff=True,
    max_retries=3,
)
def process_notification(task_id: int) -> dict[str, Any]:
    return asyncio.run(_process_notification(task_id))
