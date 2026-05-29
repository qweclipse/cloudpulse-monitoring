import json

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# Преобразует CORS_ORIGINS из Railway/.env в список доменов для FastAPI.
def parse_cors_origins(value: str) -> list[str]:
    raw_value = value.strip()
    if not raw_value:
        return []

    if raw_value.startswith("[") and raw_value.endswith("]"):
        try:
            parsed_value = json.loads(raw_value)
        except json.JSONDecodeError:
            raw_value = raw_value[1:-1]
        else:
            if isinstance(parsed_value, list):
                return [
                    origin.strip()
                    for origin in parsed_value
                    if isinstance(origin, str) and origin.strip()
                ]
            return []

    return [
        origin.strip().strip('"').strip("'")
        for origin in raw_value.split(",")
        if origin.strip()
    ]


class Settings(BaseSettings):
    # Все runtime-настройки приложения читаются из env или .env.
    app_name: str = "CloudPulse API"
    environment: str = "local"
    database_url: str = (
        "postgresql+psycopg://cloudpulse:cloudpulse@localhost:5432/cloudpulse"
    )
    redis_url: str = "redis://localhost:6379/0"
    redis_queue_name: str = "monitor_checks"
    worker_queue_timeout_seconds: int = 5
    scheduler_poll_interval_seconds: int = 10
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return parse_cors_origins(self.cors_origins)

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        # Railway выдает postgresql://, а SQLAlchemy здесь использует драйвер psycopg.
        if isinstance(value, str) and value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value


# Единый объект настроек импортируется всеми слоями приложения.
settings = Settings()
