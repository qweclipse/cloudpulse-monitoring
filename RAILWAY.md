# Railway Deployment

CloudPulse is a monorepo. Deploy it on Railway as separate services from the
same GitHub repository.

Repository:

```text
https://github.com/qweclipse/cloudpulse-monitoring
```

## Services

Create these Railway services:

- `api`: GitHub repo service, root directory `/backend`
- `worker`: GitHub repo service, root directory `/backend`
- `scheduler`: GitHub repo service, root directory `/backend`
- `frontend`: GitHub repo service, root directory `/frontend`
- `Postgres`: Railway PostgreSQL database
- `Redis`: Railway Redis database

## API Service

Root directory:

```text
/backend
```

The backend Dockerfile runs Alembic migrations and starts Uvicorn on
Railway's `$PORT`.

Variables:

```text
DATABASE_URL=<reference Railway Postgres DATABASE_URL>
REDIS_URL=<reference Railway Redis REDIS_URL>
REDIS_QUEUE_NAME=monitor_checks
ENVIRONMENT=railway
CORS_ORIGINS=["https://YOUR_FRONTEND_DOMAIN"]
```

Healthcheck path:

```text
/health
```

## Worker Service

Root directory:

```text
/backend
```

Start command:

```text
python -m app.worker
```

Variables:

```text
DATABASE_URL=<reference Railway Postgres DATABASE_URL>
REDIS_URL=<reference Railway Redis REDIS_URL>
REDIS_QUEUE_NAME=monitor_checks
ENVIRONMENT=railway
```

Do not expose a public domain for the worker.

## Scheduler Service

Root directory:

```text
/backend
```

Start command:

```text
python -m app.scheduler
```

Variables:

```text
DATABASE_URL=<reference Railway Postgres DATABASE_URL>
REDIS_URL=<reference Railway Redis REDIS_URL>
REDIS_QUEUE_NAME=monitor_checks
SCHEDULER_POLL_INTERVAL_SECONDS=10
ENVIRONMENT=railway
```

Do not expose a public domain for the scheduler.

## Frontend Service

Root directory:

```text
/frontend
```

Variables:

```text
VITE_API_BASE_URL=https://YOUR_API_DOMAIN
```

Include the `https://` prefix in `VITE_API_BASE_URL`.

After the frontend gets a Railway domain, update API `CORS_ORIGINS` with the
frontend domain and redeploy the API service.

## Deployment Order

1. Create PostgreSQL and Redis services.
2. Create and deploy `api`.
3. Generate/open the public domain for `api`.
4. Create and deploy `frontend` with `VITE_API_BASE_URL` set to the API domain.
5. Generate/open the public domain for `frontend`.
6. Update `api` `CORS_ORIGINS` with the frontend domain.
7. Create and deploy `worker`.
8. Create and deploy `scheduler`.

If Railway tries to build the repository root with Railpack, set the service
root directory to `/backend` or `/frontend`.
