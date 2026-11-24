# Celery Notifier

[Проверенный запуск и ограничения](VERIFICATION.md).

FastAPI + Celery: задачи сохраняются в БД, worker создаёт запись уведомления
и завершает задачу. Повторная доставка не создаёт второе уведомление.
Каналы email/SMS/push являются тестовыми имитациями: реальные сообщения не отправляются.
Аутентификация не реализована; API предназначен для локальной проверки.

```bash
python -m venv .venv
# Активируйте .venv согласно вашей ОС.
python -m pip install . -r requirements-dev.txt
# Скопируйте .env.example в .env; используйте отдельную локальную БД и Redis.
alembic upgrade head
uvicorn app.main:app --host 127.0.0.1 --port 8000
celery -A app.celery_app:celery_app worker --pool=solo --loglevel=info
```

Маршруты: GET/POST `/tasks/`, GET `/tasks/{id}`, GET `/notifications/`,
GET `/notifications/{id}`, GET `/health`. POST принимает title, description и
task_type (email/sms/push). При недоступности очереди возвращается 503 и task_id,
а сохранённая задача имеет status=failed. Состояния: pending/running/completed/failed.

```bash
python -m pytest
docker compose up --build
```

Тесты используют временную SQLite-БД и memory-broker. Есть проверка настоящего
Celery worker с memory-очередью; эта проверка не подтверждает работу внешнего Redis
или SMTP. На Windows для worker используйте pool=solo.
