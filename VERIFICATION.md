# Проверка проекта

Проверки выполнялись 10–20 октября 2026. Исходная рабочая копия была чистой.

13 тестов прошли. API задач, commit до публикации, failure 503, повторы без дубликатов; настоящий Celery worker (memory и Redis), PostgreSQL, сохранение уведомления. Миграции up/down/up и Alembic check; Ruff/strict mypy.

Email/SMS/push — имитации, внешние сообщения не отправлялись. API без аутентификации.

## Повторный запуск

Команды из папки проекта после создания и активации Python venv. Для API задайте DATABASE_URL отдельной локальной БД и тестовый SECRET_KEY по примеру конфигурации; не используйте рабочие подключения.

```bash
python -m venv .venv
# Активируйте .venv согласно ОС.
python -m pip install . -r requirements-dev.txt
python -m alembic upgrade head
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
# В другом терминале с тем же окружением:
python -m celery -A app.celery_app:celery_app worker --pool=solo --loglevel=info
```

Тесты в отдельном тестовом окружении:

```bash
python -m pytest -o addopts= -q
```

Docker-проверки использовали отдельную сеть, PostgreSQL *_test и Redis; реальные данные, платежи и внешние сообщения не затрагивались. Результат локального запуска не означает production-ready.
