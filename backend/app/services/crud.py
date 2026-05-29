from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas


def list_monitors(db: Session, skip: int = 0, limit: int = 100) -> list[models.Monitor]:
    statement = (
        select(models.Monitor)
        .order_by(models.Monitor.id)
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())


def get_monitor(db: Session, monitor_id: int) -> models.Monitor | None:
    return db.get(models.Monitor, monitor_id)


def create_monitor(
    db: Session, monitor_in: schemas.MonitorCreate
) -> models.Monitor:
    monitor_data = monitor_in.model_dump()
    monitor_data["url"] = str(monitor_in.url)

    monitor = models.Monitor(
        **monitor_data,
        current_status=models.MonitorStatus.UNKNOWN,
    )
    db.add(monitor)
    db.commit()
    db.refresh(monitor)
    return monitor


def update_monitor(
    db: Session,
    monitor: models.Monitor,
    monitor_in: schemas.MonitorUpdate,
) -> models.Monitor:
    update_data = monitor_in.model_dump(exclude_unset=True)
    if "url" in update_data and monitor_in.url is not None:
        update_data["url"] = str(monitor_in.url)

    for field_name, value in update_data.items():
        setattr(monitor, field_name, value)

    db.add(monitor)
    db.commit()
    db.refresh(monitor)
    return monitor


def delete_monitor(db: Session, monitor: models.Monitor) -> None:
    db.delete(monitor)
    db.commit()
