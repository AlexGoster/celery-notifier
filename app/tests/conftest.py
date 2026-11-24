"""Isolated API and Celery tests sharing a disposable SQLite database."""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.celery_app import celery_app
from app.config import settings
from app.database import Base, get_db
from app.main import app


@pytest.fixture(autouse=True)
async def init_db(tmp_path, monkeypatch):
    url = f"sqlite+aiosqlite:///{(tmp_path / 'notifier-test.db').as_posix()}"
    monkeypatch.setattr(settings, "database_url", url)
    engine = create_async_engine(url)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db():
        async with factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    celery_app.conf.update(
        broker_url="memory://",
        result_backend="cache+memory://",
        task_always_eager=True,
        task_eager_propagates=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield factory
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
