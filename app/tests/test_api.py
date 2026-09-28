"""Tests for task API."""

from httpx import AsyncClient


async def test_create_task(client: AsyncClient, init_db):
    resp = await client.post("/tasks/", json={"title": "Test task", "task_type": "email"})
    assert resp.status_code == 201
    assert resp.json()["title"] == "Test task"


async def test_list_tasks(client: AsyncClient, init_db):
    await client.post("/tasks/", json={"title": "Task A", "task_type": "sms"})
    resp = await client.get("/tasks/")
    assert resp.status_code == 200
    assert len(resp.json()["items"]) >= 1


async def test_get_task(client: AsyncClient, init_db):
    create = await client.post("/tasks/", json={"title": "Get me", "task_type": "push"})
    task_id = create.json()["id"]
    resp = await client.get(f"/tasks/{task_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Get me"


async def test_list_pagination(client: AsyncClient, init_db):
    for i in range(25):
        await client.post("/tasks/", json={"title": f"Task {i}", "task_type": "email"})
    resp = await client.get("/tasks/?page=1&page_size=10")
    assert resp.status_code == 200
    assert len(resp.json()["items"]) == 10


async def test_create_task_missing_title(client: AsyncClient, init_db):
    resp = await client.post("/tasks/", json={"task_type": "email"})
    assert resp.status_code == 422


async def test_health(client: AsyncClient, init_db):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"