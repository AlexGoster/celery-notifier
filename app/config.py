"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "Celery Notifier"
    app_version: str = "1.0.0"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/notifierdb"

    redis_url: str = "redis://localhost:6379/0"

    secret_key: str = "dev-secret-key-change-me-in-production-32b"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = "notifications@example.com"
    smtp_password: str = "dev-password"
    notifications_email: str = "admin@example.com"

    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8080"]

    log_level: str = "INFO"


settings = Settings()
