import sqlite3

from celery.contrib.testing.worker import start_worker

from app.celery_app import celery_app
from app.config import settings
from app.tasks import process_notification


async def test_api_notification_is_persisted_and_repeat_is_safe(client):
    response = await client.post(
        "/tasks/", json={"title": "Saved notification", "task_type": "email"}
    )
    assert response.status_code == 201
    task_id = response.json()["id"]
    assert (await client.get(f"/tasks/{task_id}")).json()["status"] == "completed"
    notifications = (await client.get("/notifications/")).json()
    assert len(notifications) == 1 and notifications[0]["task_id"] == task_id
    from fastapi.concurrency import run_in_threadpool

    await run_in_threadpool(process_notification.apply, args=[task_id])
    assert len((await client.get("/notifications/")).json()) == 1


async def test_broker_failure_is_503_and_observable(client, monkeypatch):
    def fail(*args, **kwargs):
        raise OSError("Test queue failure")

    monkeypatch.setattr(process_notification, "delay", fail)
    response = await client.post("/tasks/", json={"title": "Queue failure"})
    assert response.status_code == 503
    task_id = response.json()["detail"]["task_id"]
    assert (await client.get(f"/tasks/{task_id}")).json()["status"] == "failed"
    assert (await client.get("/notifications/")).json() == []


def test_real_worker_executes_memory_queue():
    path = settings.database_url.removeprefix("sqlite+aiosqlite:///")
    with sqlite3.connect(path) as db:
        task_id = db.execute(
            "INSERT INTO background_tasks (title, task_type, status, retry_count, owner_id) "
            "VALUES ('Worker test', 'push', 'pending', 0, 1)"
        ).lastrowid
    celery_app.conf.task_always_eager = False
    try:
        with start_worker(celery_app, pool="solo", perform_ping_check=False, shutdown_timeout=10):
            result = process_notification.delay(task_id).get(timeout=10)
            assert result["status"] == "completed"
        with sqlite3.connect(path) as db:
            assert db.execute(
                "SELECT status FROM background_tasks WHERE id=?", (task_id,)
            ).fetchone() == ("completed",)
            assert db.execute(
                "SELECT count(*) FROM notifications WHERE task_id=?", (task_id,)
            ).fetchone() == (1,)
    finally:
        celery_app.conf.task_always_eager = True
