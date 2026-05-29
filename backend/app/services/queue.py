from redis import Redis

from app.config import settings


def get_redis_client() -> Redis:
    return Redis.from_url(settings.redis_url, decode_responses=True)


def enqueue_monitor_check(
    monitor_id: int,
    client: Redis | None = None,
    skip_if_queued: bool = False,
) -> int:
    redis_client = client or get_redis_client()

    if skip_if_queued and is_monitor_check_queued(monitor_id, client=redis_client):
        return int(redis_client.llen(settings.redis_queue_name))

    return int(redis_client.rpush(settings.redis_queue_name, str(monitor_id)))


def dequeue_monitor_check(
    client: Redis | None = None,
    block: bool = False,
    timeout_seconds: int = 5,
) -> int | None:
    redis_client = client or get_redis_client()
    raw_monitor_id = None

    if block:
        result = redis_client.blpop(
            [settings.redis_queue_name],
            timeout=timeout_seconds,
        )
        if result is not None:
            _, raw_monitor_id = result
    else:
        raw_monitor_id = redis_client.lpop(settings.redis_queue_name)

    if raw_monitor_id is None:
        return None

    return int(raw_monitor_id)


def is_monitor_check_queued(monitor_id: int, client: Redis | None = None) -> bool:
    redis_client = client or get_redis_client()
    expected_value = str(monitor_id)
    queued_values = redis_client.lrange(settings.redis_queue_name, 0, -1)
    return expected_value in [_normalize_queue_value(value) for value in queued_values]


def _normalize_queue_value(value: bytes | str | int) -> str:
    if isinstance(value, bytes):
        return value.decode()
    return str(value)
