"""Notification channels abstraction."""

from abc import ABC, abstractmethod
from collections.abc import Callable


class NotificationChannel(ABC):
    @abstractmethod
    async def send(self, recipient: str, subject: str, body: str) -> bool: ...


class EmailChannel(NotificationChannel):
    async def send(self, recipient: str, subject: str, body: str) -> bool:
        logger = __import__("logging").getLogger(__name__)
        logger.info(f"[EMAIL] To {recipient}: {subject}")
        return True


class SMSChannel(NotificationChannel):
    async def send(self, recipient: str, subject: str, body: str) -> bool:
        logger = __import__("logging").getLogger(__name__)
        logger.info(f"[SMS] To {recipient}: {body}")
        return True


class PushChannel(NotificationChannel):
    async def send(self, recipient: str, subject: str, body: str) -> bool:
        logger = __import__("logging").getLogger(__name__)
        logger.info(f"[PUSH] To {recipient}: {subject}")
        return True


def get_channel(channel_name: str) -> NotificationChannel:
    mapping: dict[str, Callable[[], NotificationChannel]] = {
        "email": EmailChannel,
        "sms": SMSChannel,
        "push": PushChannel,
    }
    cls = mapping.get(channel_name)
    if not cls:
        raise ValueError(f"Unknown channel: {channel_name}")
    return cls()
