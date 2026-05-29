from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_monitor(client: TestClient) -> None:
    response = client.post(
        "/monitors",
        json={
            "name": "Example API",
            "url": "https://example.com/health",
            "interval_seconds": 30,
            "expected_status_code": 200,
            "timeout_seconds": 5,
            "is_active": True,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Example API"
    assert data["url"] == "https://example.com/health"
    assert data["interval_seconds"] == 30
    assert data["expected_status_code"] == 200
    assert data["timeout_seconds"] == 5
    assert data["is_active"] is True
    assert data["current_status"] == "UNKNOWN"
    assert data["last_checked_at"] is None


def test_create_monitor_rejects_invalid_url(client: TestClient) -> None:
    response = client.post(
        "/monitors",
        json={
            "name": "Broken URL",
            "url": "not-a-url",
            "interval_seconds": 60,
            "expected_status_code": 200,
            "timeout_seconds": 10,
            "is_active": True,
        },
    )

    assert response.status_code == 422


def test_list_monitors(client: TestClient) -> None:
    first = client.post(
        "/monitors",
        json={
            "name": "First",
            "url": "https://first.example.com",
            "interval_seconds": 60,
            "expected_status_code": 200,
            "timeout_seconds": 10,
            "is_active": True,
        },
    )
    second = client.post(
        "/monitors",
        json={
            "name": "Second",
            "url": "https://second.example.com",
            "interval_seconds": 120,
            "expected_status_code": 204,
            "timeout_seconds": 3,
            "is_active": False,
        },
    )

    assert first.status_code == 201
    assert second.status_code == 201

    response = client.get("/monitors")

    assert response.status_code == 200
    data = response.json()
    assert [monitor["name"] for monitor in data] == ["First", "Second"]
    assert [monitor["current_status"] for monitor in data] == ["UNKNOWN", "UNKNOWN"]
    assert data[0]["is_active"] is True
    assert data[1]["is_active"] is False
