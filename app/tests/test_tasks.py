"""Tests for Celery tasks."""

from app.tasks import (
    send_daily_notifications,
    send_email_notification,
    send_push_notification,
    send_sms_notification,
)


def test_send_email_notification():
    result = send_email_notification("user@e.com", "Test", "Hello")
    assert result["status"] == "sent"


def test_send_sms_notification():
    result = send_sms_notification("+1234567890", "Hello")
    assert result["status"] == "sent"


def test_send_push_notification():
    result = send_push_notification("user123", "Alert", "Message")
    assert result["status"] == "sent"


def test_send_daily_notifications():
    result = send_daily_notifications()
    assert result["status"] == "batch_sent"
