"""Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    task_type: str = Field(default="email", pattern="^(email|sms|push)$")


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    task_type: str
    status: str
    result: str | None
    retry_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    total: int
    page: int
    page_size: int


class NotificationResponse(BaseModel):
    id: int
    task_id: int
    channel: str
    recipient: str
    subject: str | None
    status: str
    sent_at: datetime

    model_config = {"from_attributes": True}
