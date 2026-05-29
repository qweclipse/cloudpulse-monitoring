from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CloudPulse API"
    environment: str = "local"
    database_url: str = (
        "postgresql+psycopg://cloudpulse:cloudpulse@localhost:5432/cloudpulse"
    )
    redis_url: str = "redis://localhost:6379/0"
    redis_queue_name: str = "monitor_checks"
    worker_queue_timeout_seconds: int = 5
    scheduler_poll_interval_seconds: int = 10
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
