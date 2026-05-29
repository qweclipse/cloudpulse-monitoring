from types import SimpleNamespace

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.services.checker import check_monitor


class FakeHttpClient:
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code
        self.requests: list[dict[str, object]] = []

    def get(self, url: str, timeout: int, follow_redirects: bool) -> SimpleNamespace:
        self.requests.append(
            {
                "url": url,
                "timeout": timeout,
                "follow_redirects": follow_redirects,
            }
        )
        return SimpleNamespace(status_code=self.status_code)


def test_check_monitor_success_updates_monitor_and_creates_result(
    db_session: Session,
) -> None:
    monitor = create_monitor(db_session)
    fake_client = FakeHttpClient(status_code=200)

    result = check_monitor(db_session, monitor.id, client=fake_client)

    db_session.refresh(monitor)
    assert result.status == models.CheckStatus.SUCCESS
    assert result.status_code == 200
    assert result.error_message is None
    assert result.latency_ms is not None
    assert monitor.current_status == models.MonitorStatus.UP
    assert monitor.last_checked_at is not None
    assert fake_client.requests == [
        {
            "url": "https://example.com/health",
            "timeout": 5,
            "follow_redirects": True,
        }
    ]


def test_check_monitor_unexpected_status_opens_incident(
    db_session: Session,
) -> None:
    monitor = create_monitor(db_session)
    fake_client = FakeHttpClient(status_code=500)

    result = check_monitor(db_session, monitor.id, client=fake_client)

    db_session.refresh(monitor)
    incidents = list(db_session.scalars(select(models.Incident)).all())
    assert result.status == models.CheckStatus.FAILED
    assert result.status_code == 500
    assert result.error_message == "Unexpected status code: got 500, expected 200"
    assert monitor.current_status == models.MonitorStatus.DOWN
    assert len(incidents) == 1
    assert incidents[0].status == models.IncidentStatus.OPEN
    assert incidents[0].reason == result.error_message


def create_monitor(db_session: Session) -> models.Monitor:
    monitor = models.Monitor(
        name="Example",
        url="https://example.com/health",
        interval_seconds=60,
        expected_status_code=200,
        timeout_seconds=5,
        is_active=True,
        current_status=models.MonitorStatus.UNKNOWN,
    )
    db_session.add(monitor)
    db_session.commit()
    db_session.refresh(monitor)
    return monitor
