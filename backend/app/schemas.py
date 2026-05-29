from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field

from app.models import CheckStatus, IncidentStatus, MonitorStatus


# Общие поля монитора с валидацией входных данных.
class MonitorBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    url: AnyHttpUrl
    interval_seconds: int = Field(default=60, gt=0)
    expected_status_code: int = Field(default=200, ge=100, le=599)
    timeout_seconds: int = Field(default=10, gt=0)
    is_active: bool = True


# Payload для создания нового монитора.
class MonitorCreate(MonitorBase):
    pass


# Payload для частичного обновления монитора.
class MonitorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    url: AnyHttpUrl | None = None
    interval_seconds: int | None = Field(default=None, gt=0)
    expected_status_code: int | None = Field(default=None, ge=100, le=599)
    timeout_seconds: int | None = Field(default=None, gt=0)
    is_active: bool | None = None


# Ответ API с полной информацией о мониторе.
class MonitorRead(BaseModel):
    id: int
    name: str
    url: str
    interval_seconds: int
    expected_status_code: int
    timeout_seconds: int
    is_active: bool
    current_status: MonitorStatus
    last_checked_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Ответ API с результатом одной проверки.
class CheckResultRead(BaseModel):
    id: int
    monitor_id: int
    status: CheckStatus
    status_code: int | None
    latency_ms: int | None
    error_message: str | None
    checked_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Короткая версия монитора для вложения в инциденты.
class MonitorSummary(BaseModel):
    id: int
    name: str
    url: str
    current_status: MonitorStatus

    model_config = ConfigDict(from_attributes=True)


# Ответ API с данными инцидента и связанным монитором.
class IncidentRead(BaseModel):
    id: int
    monitor_id: int
    status: IncidentStatus
    reason: str
    started_at: datetime
    resolved_at: datetime | None
    duration_seconds: int | None
    monitor: MonitorSummary | None = None

    model_config = ConfigDict(from_attributes=True)


# Данные для верхних карточек dashboard.
class StatsRead(BaseModel):
    total_monitors: int
    up_monitors: int
    down_monitors: int
    unknown_monitors: int
    active_incidents: int
    average_latency_ms: float | None
