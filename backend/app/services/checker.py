from datetime import datetime, timezone
from time import perf_counter

import httpx
from sqlalchemy.orm import Session

from app import models
from app.services import incident_service


class MonitorNotFoundError(Exception):
    # Доменная ошибка, которую API превращает в HTTP 404.
    def __init__(self, monitor_id: int) -> None:
        super().__init__(f"Monitor {monitor_id} not found")
        self.monitor_id = monitor_id


def check_monitor(
    db: Session,
    monitor_id: int,
    client: httpx.Client | None = None,
) -> models.CheckResult:
    # Выполняет HTTP-запрос, сохраняет результат и обновляет статус монитора.
    monitor = db.get(models.Monitor, monitor_id)
    if monitor is None:
        raise MonitorNotFoundError(monitor_id)

    checked_at = datetime.now(timezone.utc)
    request_started_at = perf_counter()
    status_code: int | None = None
    error_message: str | None = None

    owns_client = client is None
    http_client = client or httpx.Client(follow_redirects=True)

    try:
        # Ожидаемый код ответа считается успешной проверкой.
        response = http_client.get(
            monitor.url,
            timeout=monitor.timeout_seconds,
            follow_redirects=True,
        )
        status_code = response.status_code

        if response.status_code == monitor.expected_status_code:
            check_status = models.CheckStatus.SUCCESS
            monitor_status = models.MonitorStatus.UP
        else:
            check_status = models.CheckStatus.FAILED
            monitor_status = models.MonitorStatus.DOWN
            error_message = (
                f"Unexpected status code: got {response.status_code}, "
                f"expected {monitor.expected_status_code}"
            )
    except httpx.TimeoutException as exc:
        check_status = models.CheckStatus.FAILED
        monitor_status = models.MonitorStatus.DOWN
        error_message = f"Request timed out after {monitor.timeout_seconds}s: {exc}"
    except (httpx.InvalidURL, httpx.UnsupportedProtocol) as exc:
        check_status = models.CheckStatus.FAILED
        monitor_status = models.MonitorStatus.DOWN
        error_message = f"Invalid URL: {exc}"
    except httpx.RequestError as exc:
        check_status = models.CheckStatus.FAILED
        monitor_status = models.MonitorStatus.DOWN
        error_message = f"Request error: {exc}"
    finally:
        if owns_client:
            http_client.close()

    # Задержка считается даже для ошибок, чтобы видеть время до сбоя.
    latency_ms = max(round((perf_counter() - request_started_at) * 1000), 0)

    check_result = models.CheckResult(
        monitor_id=monitor.id,
        status=check_status,
        status_code=status_code,
        latency_ms=latency_ms,
        error_message=error_message,
        checked_at=checked_at,
    )
    monitor.current_status = monitor_status
    monitor.last_checked_at = checked_at

    db.add(monitor)
    db.add(check_result)
    # На основе результата открываем или закрываем инцидент.
    incident_service.handle_check_result(db, monitor, check_result)
    db.commit()
    db.refresh(monitor)
    db.refresh(check_result)
    return check_result
