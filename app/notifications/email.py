"""Email notification sender."""

from app.config import settings
from app.notifications.channels import EmailChannel


def send_email(recipient: str, subject: str, body: str) -> bool:
    channel = EmailChannel()
    return channel.send(recipient, subject, body)
