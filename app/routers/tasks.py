"""Task routes."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Task
from app.schemas import TaskCreate, TaskListResponse, TaskResponse

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)) -> Task:
    db_task = Task(
        title=task.title, description=task.description, task_type=task.task_type, owner_id=1
    )
    db.add(db_task)
    await db.flush()
    await db.refresh(db_task)
    await db.commit()
    from app.tasks import process_notification

    try:
        await run_in_threadpool(process_notification.delay, db_task.id)
    except Exception:
        db_task.status = "failed"
        db_task.result = "Queue unavailable"
        await db.commit()
        raise HTTPException(
            status_code=503, detail={"message": "Queue unavailable", "task_id": db_task.id}
        ) from None
    await db.refresh(db_task)
    return db_task


@router.get("/", response_model=TaskListResponse)
async def list_tasks(
    status_filter: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> TaskListResponse:
    stmt = select(Task)
    if status_filter:
        stmt = stmt.where(Task.status == status_filter)
    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one()
    stmt = stmt.order_by(Task.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    tasks = result.scalars().all()
    return TaskListResponse(
        items=[TaskResponse.model_validate(task) for task in tasks],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)) -> Task:
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
