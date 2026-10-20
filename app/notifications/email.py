"""Email notification sender."""

from app.notifications.channels import EmailChannel


async def send_email(recipient: str, subject: str, body: str) -> bool:
    channel = EmailChannel()
    return await channel.send(recipient, subject, body)
