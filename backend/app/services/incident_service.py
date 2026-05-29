from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models


# Ищет последний открытый инцидент, чтобы не создавать дубликаты.
def get_open_incident(db: Session, monitor_id: int) -> models.Incident | None:
    statement = (
        select(models.Incident)
        .where(
            models.Incident.monitor_id == monitor_id,
            models.Incident.status == models.IncidentStatus.OPEN,
        )
        .order_by(models.Incident.started_at.desc(), models.Incident.id.desc())
        .limit(1)
    )
    return db.scalars(statement).first()


def handle_check_result(
    db: Session,
    monitor: models.Monitor,
    check_result: models.CheckResult,
) -> models.Incident | None:
    # FAILED открывает инцидент, SUCCESS закрывает активный инцидент.
    if check_result.status == models.CheckStatus.FAILED:
        return _open_incident_if_needed(db, monitor, check_result)

    if check_result.status == models.CheckStatus.SUCCESS:
        return _resolve_incident_if_needed(db, monitor, check_result)

    return None


def _open_incident_if_needed(
    db: Session,
    monitor: models.Monitor,
    check_result: models.CheckResult,
) -> models.Incident:
    # Если инцидент уже открыт, оставляем его активным.
    open_incident = get_open_incident(db, monitor.id)
    if open_incident is not None:
        return open_incident

    incident = models.Incident(
        monitor_id=monitor.id,
        status=models.IncidentStatus.OPEN,
        reason=_build_failure_reason(check_result),
        started_at=_event_time(check_result),
    )
    db.add(incident)
    return incident


def _resolve_incident_if_needed(
    db: Session,
    monitor: models.Monitor,
    check_result: models.CheckResult,
) -> models.Incident | None:
    # Время простоя считаем от начала инцидента до успешной проверки.
    open_incident = get_open_incident(db, monitor.id)
    if open_incident is None:
        return None

    resolved_at = _event_time(check_result)
    started_at = _as_aware_datetime(open_incident.started_at)
    duration_seconds = max(round((resolved_at - started_at).total_seconds()), 0)

    open_incident.status = models.IncidentStatus.RESOLVED
    open_incident.resolved_at = resolved_at
    open_incident.duration_seconds = duration_seconds
    db.add(open_incident)
    return open_incident


def _build_failure_reason(check_result: models.CheckResult) -> str:
    if check_result.error_message:
        return check_result.error_message

    if check_result.status_code is not None:
        return f"Check failed with status code {check_result.status_code}"

    return "Monitor check failed"


def _event_time(check_result: models.CheckResult) -> datetime:
    return _as_aware_datetime(check_result.checked_at)


def _as_aware_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
