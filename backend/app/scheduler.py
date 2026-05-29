import logging
import time
from datetime import datetime, timezone

from redis import RedisError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.config import settings
from app.database import SessionLocal
from app.services.queue import (
    enqueue_monitor_check,
    get_redis_client,
    is_monitor_check_queued,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("cloudpulse.scheduler")


def is_monitor_due(monitor: models.Monitor, now: datetime | None = None) -> bool:
    # Новый монитор проверяется сразу, остальные - по interval_seconds.
    current_time = now or datetime.now(timezone.utc)

    if monitor.last_checked_at is None:
        return True

    last_checked_at = _as_aware_datetime(monitor.last_checked_at)
    elapsed_seconds = (current_time - last_checked_at).total_seconds()
    return elapsed_seconds >= monitor.interval_seconds


def get_due_monitors(
    db: Session,
    now: datetime | None = None,
) -> list[models.Monitor]:
    # Сначала берем активные мониторы, потом фильтруем их по расписанию.
    statement = (
        select(models.Monitor)
        .where(models.Monitor.is_active.is_(True))
        .order_by(models.Monitor.id)
    )
    monitors = db.scalars(statement).all()
    return [monitor for monitor in monitors if is_monitor_due(monitor, now=now)]


def schedule_due_checks(
    db: Session,
    redis_client=None,
    now: datetime | None = None,
) -> int:
    # Кладет due-мониторы в Redis, избегая повторов в очереди.
    due_monitors = get_due_monitors(db, now=now)
    enqueued_count = 0

    for monitor in due_monitors:
        if is_monitor_check_queued(monitor.id, client=redis_client):
            logger.info("Monitor_id=%s is already queued", monitor.id)
            continue

        enqueue_monitor_check(monitor.id, client=redis_client)
        enqueued_count += 1
        logger.info("Enqueued monitor_id=%s", monitor.id)

    return enqueued_count


def run_scheduler() -> None:
    # Бесконечный цикл для отдельного Railway/Docker/K8s процесса scheduler.
    logger.info(
        "Starting scheduler with poll_interval=%ss queue=%s",
        settings.scheduler_poll_interval_seconds,
        settings.redis_queue_name,
    )
    redis_client = get_redis_client()

    while True:
        try:
            with SessionLocal() as db:
                enqueued_count = schedule_due_checks(db, redis_client=redis_client)
                logger.info("Scheduler cycle complete enqueued=%s", enqueued_count)
        except RedisError:
            logger.exception("Redis error while scheduling monitor checks")
        except KeyboardInterrupt:
            logger.info("Scheduler shutdown requested")
            break
        except Exception:
            logger.exception("Unexpected scheduler loop error")

        time.sleep(settings.scheduler_poll_interval_seconds)


def _as_aware_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


if __name__ == "__main__":
    run_scheduler()
