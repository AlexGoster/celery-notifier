"""Task execution functions (Celery tasks)."""

import asyncio
import logging
from typing import Any

from celery import shared_task

from app.config import settings
from app.models import Task, Notification, Base
from app.database import async_session

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_notification(self, recipient: str, subject: str, body: str) -> dict[str, Any]:
    try:
        logger.info(f"Sending email to {recipient}: {subject}")
        result = _mock_send_sms_or_email(recipient, subject, body)
        return {"status": "sent", "recipient": recipient, "subject": subject}
    except Exception as exc:
        logger.warning(f"Email send failed, retrying: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_sms_notification(self, recipient: str, body: str) -> dict[str, Any]:
    try:
        logger.info(f"Sending SMS to {recipient}: {body}")
        return {"status": "sent", "recipient": recipient, "body": body[:20]}
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_push_notification(self, recipient: str, title: str, body: str) -> dict[str, Any]:
    try:
        logger.info(f"Sending push to {recipient}: {title}")
        return {"status": "sent", "recipient": recipient, "title": title}
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task
def send_daily_notifications() -> dict[str, Any]:
    logger.info("Sending daily notifications batch")
    return {"status": "batch_sent", "count": 0}


def _mock_send_sms_or_email(recipient: str, subject: str, body: str) -> bool:
    logger.info(f"[MOCK] Email to {recipient}: {subject}")
    return True
