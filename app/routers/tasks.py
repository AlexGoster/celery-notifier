"""Task routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models import Task
from app.schemas import TaskCreate, TaskResponse, TaskListResponse
from app.celery_app import celery_app

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    db_task = Task(
        title=task.title, description=task.description, task_type=task.task_type, owner_id=1
    )
    db.add(db_task)
    await db.flush()
    await db.refresh(db_task)
    celery_app.send_task(
        f"app.tasks.notifications.send_{task.task_type}_notification",
        args=[db_task.id],
    )
    return db_task


@router.get("/", response_model=TaskListResponse)
async def list_tasks(
    status_filter: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Task)
    if status_filter:
        stmt = stmt.where(Task.status == status_filter)
    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one()
    stmt = stmt.order_by(Task.created_at.desc()).offset((page-1)*page_size).limit(page_size)
    result = await db.execute(stmt)
    tasks = result.scalars().all()
    return TaskListResponse(items=tasks, total=total, page=page, page_size=page_size)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task