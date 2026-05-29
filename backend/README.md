# CloudPulse Backend

Python FastAPI backend for the CloudPulse monitoring platform.

## Current Status

The backend contains the core CloudPulse API, background processing entrypoints,
database migrations, Docker support and pytest coverage.

Implemented:

- `app/main.py` with FastAPI application setup;
- `GET /health` endpoint returning `{"status": "ok"}`;
- `DATABASE_URL` configuration through environment variables;
- SQLAlchemy engine and database session dependency;
- SQLAlchemy models for monitors, check results and incidents;
- Alembic configuration and initial migration;
- CRUD API for monitors;
- checker service for website/API availability checks;
- manual check API endpoint;
- incident management for failed and recovered checks;
- read APIs for check history, incidents and dashboard stats;
- Dockerfile and Docker Compose support for API + PostgreSQL;
- Redis queue helpers for monitor checks;
- worker process for asynchronous monitor checks;
- scheduler process for automatic check planning.
- pytest tests for health, monitor creation, validation, list retrieval and
  checker behavior.

## Local Setup

From the repository root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open:

```text
http://localhost:8000/health
```

Expected response:

```json
{"status":"ok"}
```

Swagger UI will be available at:

```text
http://localhost:8000/docs
```

## Docker Compose

From the repository root:

```powershell
docker compose up --build
```

Requires a running Docker daemon, for example Docker Desktop or Rancher Desktop.

Services:

- `api`: FastAPI backend on `http://localhost:8000`
- `worker`: background worker that processes Redis check tasks
- `scheduler`: background scheduler that enqueues due monitor checks
- `postgres`: PostgreSQL on `localhost:5432`
- `redis`: Redis on `localhost:6379`

The `api` service waits for PostgreSQL and Redis health, runs:

```powershell
alembic upgrade head
```

and then starts:

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The `worker` service waits for the healthy API, PostgreSQL and Redis, then starts:

```powershell
python -m app.worker
```

The `scheduler` service waits for the healthy API, PostgreSQL and Redis, then starts:

```powershell
python -m app.scheduler
```

Useful checks:

```text
http://localhost:8000/health
http://localhost:8000/docs
```

## Tests

Backend tests use `pytest`, FastAPI `TestClient`, an in-memory SQLite database
and mocked HTTP clients for checker behavior.

From `backend/`:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest
```

Current tests cover:

- `GET /health`;
- monitor creation;
- monitor URL validation;
- monitor list retrieval;
- checker success behavior with a mocked HTTP response;
- checker failed status behavior and incident creation.

Stop and remove containers:

```powershell
docker compose down
```

Remove the local PostgreSQL volume as well:

```powershell
docker compose down -v
```

## Redis Queue

Queue helpers live in `app/services/queue.py`.

The backend reads Redis settings from:

```text
REDIS_URL=redis://localhost:6379/0
REDIS_QUEUE_NAME=monitor_checks
```

Available helpers:

- `enqueue_monitor_check(monitor_id)`: pushes a monitor id to the Redis list queue.
- `dequeue_monitor_check()`: pops the next monitor id from the Redis list queue.
- `dequeue_monitor_check(block=True)`: waits for a monitor id, useful for workers.

Quick local check with Redis running:

```powershell
python -c "from app.services.queue import enqueue_monitor_check, dequeue_monitor_check; enqueue_monitor_check(1); print(dequeue_monitor_check())"
```

## Worker

The worker lives in `app/worker.py`.

It continuously:

- waits for monitor ids in Redis;
- opens a database session;
- calls `check_monitor(db, monitor_id)`;
- logs successful and failed task processing;
- keeps running after one task fails.

Watch worker logs:

```powershell
docker compose logs -f worker
```

Enqueue a check task while Compose is running:

```powershell
docker compose exec api python -c "from app.services.queue import enqueue_monitor_check; enqueue_monitor_check(1)"
```

## Scheduler

The scheduler lives in `app/scheduler.py`.

It continuously:

- loads active monitors from PostgreSQL;
- checks whether `last_checked_at` is empty or older than `interval_seconds`;
- enqueues due monitor ids into Redis;
- skips monitor ids that are already waiting in the Redis list queue;
- logs each scheduling cycle.

Default settings:

```text
SCHEDULER_POLL_INTERVAL_SECONDS=10
```

Watch scheduler logs:

```powershell
docker compose logs -f scheduler
```

## Database Configuration

The backend reads PostgreSQL connection settings from `DATABASE_URL`.

Example:

```powershell
$env:DATABASE_URL = "postgresql+psycopg://cloudpulse:cloudpulse@localhost:5432/cloudpulse"
```

Or create `backend/.env` based on `backend/.env.example`.

The default local value is:

```text
postgresql+psycopg://cloudpulse:cloudpulse@localhost:5432/cloudpulse
```

Database tables are managed through Alembic migrations.

## Migrations

From `backend/`:

```powershell
.\.venv\Scripts\Activate.ps1
alembic upgrade head
```

To inspect the SQL without connecting to PostgreSQL:

```powershell
alembic upgrade head --sql
```

To create a new migration after model changes:

```powershell
alembic revision --autogenerate -m "describe change"
```

Alembic reads the same `DATABASE_URL` setting as the application.

## Monitor API

Available endpoints:

- `GET /monitors`
- `POST /monitors`
- `GET /monitors/{monitor_id}`
- `PUT /monitors/{monitor_id}`
- `DELETE /monitors/{monitor_id}`
- `POST /monitors/{monitor_id}/check`
- `GET /monitors/{monitor_id}/checks`
- `GET /monitors/{monitor_id}/incidents`
- `GET /incidents`
- `GET /stats`

Example request:

```json
{
  "name": "Example site",
  "url": "https://example.com",
  "interval_seconds": 60,
  "expected_status_code": 200,
  "timeout_seconds": 10,
  "is_active": true
}
```

New monitors are created with `current_status = UNKNOWN`.

To test the API:

```powershell
alembic upgrade head
uvicorn app.main:app --reload
```

Then open:

```text
http://localhost:8000/docs
```

## Checking Logic

The checker service lives in `app/services/checker.py`.

It can:

- load a monitor from the database;
- run HTTP `GET` against `monitor.url`;
- measure latency in milliseconds;
- compare the response status code with `expected_status_code`;
- create a `CheckResult`;
- update `Monitor.current_status` and `Monitor.last_checked_at`;
- open and resolve incidents based on check results;
- handle timeouts, connection errors, invalid URLs and unexpected status codes.

Direct service usage:

```powershell
python -c "from app.database import SessionLocal; from app.services.checker import check_monitor; db = SessionLocal(); print(check_monitor(db, 1).status); db.close()"
```

Manual API usage:

```powershell
curl -X POST http://localhost:8000/monitors/1/check
```

The endpoint returns the created `CheckResult` and updates the monitor status.

## Incident Logic

Incident behavior is implemented in `app/services/incident_service.py`.

Rules:

- a failed check opens a new `OPEN` incident when the monitor has no active incident;
- repeated failed checks do not create duplicate open incidents;
- a successful check resolves an existing open incident;
- resolved incidents get `resolved_at` and `duration_seconds`;
- incident `reason` stores the failure cause from the check result.

## Checks, Incidents And Stats API

History endpoints:

- `GET /monitors/{monitor_id}/checks` returns recent check results for one monitor.
- `GET /monitors/{monitor_id}/incidents` returns incidents for one monitor.
- `GET /incidents` returns all incidents and supports optional `status=OPEN` or `status=RESOLVED`.

Dashboard endpoint:

```text
GET /stats
```

Response fields:

- `total_monitors`
- `up_monitors`
- `down_monitors`
- `unknown_monitors`
- `active_incidents`
- `average_latency_ms`

`average_latency_ms` is `null` until at least one check result has latency data.

## Model Overview

- `Monitor`: monitored website/API configuration and current status.
- `CheckResult`: individual check result with status code, latency and error message.
- `Incident`: downtime incident lifecycle with open/resolved state.

Enums:

- `MonitorStatus`: `UNKNOWN`, `UP`, `DOWN`
- `CheckStatus`: `SUCCESS`, `FAILED`
- `IncidentStatus`: `OPEN`, `RESOLVED`
