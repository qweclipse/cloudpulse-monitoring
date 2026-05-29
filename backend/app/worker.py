import logging
import time

from redis import RedisError

from app.config import settings
from app.database import SessionLocal
from app.services.checker import MonitorNotFoundError, check_monitor
from app.services.queue import dequeue_monitor_check, get_redis_client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("cloudpulse.worker")


def process_monitor_check(monitor_id: int) -> None:
    # Обрабатывает одну задачу из очереди и фиксирует результат в БД.
    with SessionLocal() as db:
        try:
            result = check_monitor(db, monitor_id)
            logger.info(
                "Processed monitor_id=%s check_result_id=%s status=%s latency_ms=%s",
                monitor_id,
                result.id,
                result.status.value,
                result.latency_ms,
            )
        except MonitorNotFoundError:
            logger.warning("Skipping missing monitor_id=%s", monitor_id)
        except Exception:
            db.rollback()
            logger.exception("Failed to process monitor_id=%s", monitor_id)


def run_worker() -> None:
    # Бесконечный цикл фонового worker-а: ждет id монитора из Redis.
    logger.info(
        "Starting worker with redis_url=%s queue=%s",
        settings.redis_url,
        settings.redis_queue_name,
    )
    redis_client = get_redis_client()

    while True:
        try:
            monitor_id = dequeue_monitor_check(
                client=redis_client,
                block=True,
                timeout_seconds=settings.worker_queue_timeout_seconds,
            )
            if monitor_id is None:
                continue

            logger.info("Dequeued monitor_id=%s", monitor_id)
            process_monitor_check(monitor_id)
        except RedisError:
            logger.exception("Redis error while waiting for monitor check tasks")
            time.sleep(2)
        except KeyboardInterrupt:
            logger.info("Worker shutdown requested")
            break
        except Exception:
            logger.exception("Unexpected worker loop error")
            time.sleep(2)


if __name__ == "__main__":
    run_worker()
