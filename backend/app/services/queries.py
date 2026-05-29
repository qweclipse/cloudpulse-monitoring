from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session, selectinload

from app import models


def list_monitor_checks(
    db: Session,
    monitor_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[models.CheckResult]:
    statement = (
        select(models.CheckResult)
        .where(models.CheckResult.monitor_id == monitor_id)
        .order_by(desc(models.CheckResult.checked_at), desc(models.CheckResult.id))
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())


def list_monitor_incidents(
    db: Session,
    monitor_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[models.Incident]:
    statement = (
        select(models.Incident)
        .options(selectinload(models.Incident.monitor))
        .where(models.Incident.monitor_id == monitor_id)
        .order_by(desc(models.Incident.started_at), desc(models.Incident.id))
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())


def list_incidents(
    db: Session,
    status: models.IncidentStatus | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[models.Incident]:
    statement = select(models.Incident).options(selectinload(models.Incident.monitor))

    if status is not None:
        statement = statement.where(models.Incident.status == status)

    statement = (
        statement.order_by(desc(models.Incident.started_at), desc(models.Incident.id))
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())


def get_stats(db: Session) -> dict[str, int | float | None]:
    total_monitors = _count_monitors(db)
    up_monitors = _count_monitors(db, models.MonitorStatus.UP)
    down_monitors = _count_monitors(db, models.MonitorStatus.DOWN)
    unknown_monitors = _count_monitors(db, models.MonitorStatus.UNKNOWN)
    active_incidents = db.scalar(
        select(func.count())
        .select_from(models.Incident)
        .where(models.Incident.status == models.IncidentStatus.OPEN)
    )
    average_latency_ms = db.scalar(
        select(func.avg(models.CheckResult.latency_ms)).where(
            models.CheckResult.latency_ms.is_not(None)
        )
    )

    return {
        "total_monitors": int(total_monitors or 0),
        "up_monitors": int(up_monitors or 0),
        "down_monitors": int(down_monitors or 0),
        "unknown_monitors": int(unknown_monitors or 0),
        "active_incidents": int(active_incidents or 0),
        "average_latency_ms": (
            float(average_latency_ms) if average_latency_ms is not None else None
        ),
    }


def _count_monitors(
    db: Session, status: models.MonitorStatus | None = None
) -> int:
    statement = select(func.count()).select_from(models.Monitor)
    if status is not None:
        statement = statement.where(models.Monitor.current_status == status)
    return int(db.scalar(statement) or 0)
