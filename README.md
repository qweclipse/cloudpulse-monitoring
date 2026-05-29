# CloudPulse

CloudPulse is a cloud-native website and API monitoring platform. Users add URLs,
the system checks them on a schedule, stores latency and status history, opens
incidents during outages, resolves incidents after recovery, and shows the
current state in a React dashboard.

## Project Status

Stages 0-26 from `cloudpulse_project_plan.txt` are implemented. Detailed notes
for every stage are tracked in `PROGRESS.md`.

The project currently includes:

- FastAPI backend with monitor CRUD, check history, incidents and stats APIs.
- PostgreSQL persistence through SQLAlchemy and Alembic migrations.
- Redis queue for asynchronous checks.
- Worker and scheduler processes.
- React + Vite dashboard.
- Docker Compose stack for local development.
- Kubernetes manifests for Rancher Desktop.
- GitHub Actions CI workflow.
- Optional Google Cloud Run deployment workflow.
- Basic backend tests with pytest.

## Architecture

CloudPulse is split into small services. The API owns the business logic and
database access. The scheduler finds due monitors and adds check jobs to Redis.
The worker consumes jobs, runs HTTP checks, writes check results, and opens or
resolves incidents. The frontend calls the API and presents the monitoring
dashboard.

```text
Browser
  |
  v
Frontend (React + Vite, nginx)
  |
  v
Backend API (FastAPI)
  |
  +--> PostgreSQL
  |
  +--> Redis queue <-- Scheduler
          |
          v
        Worker --> monitored websites/APIs
```

## Services

- `frontend`: React dashboard served by nginx.
- `api`: FastAPI HTTP API on port `8000`.
- `postgres`: PostgreSQL database for monitors, check results and incidents.
- `redis`: Redis list queue for scheduled monitor checks.
- `worker`: background process that executes queued checks.
- `scheduler`: background process that enqueues due monitor checks.

## Main Features

- Create, list, update and delete monitors.
- Validate monitor URLs and configuration.
- Run manual monitor checks.
- Run automatic scheduled checks.
- Measure latency and HTTP status code.
- Store check history.
- Track monitor state: `UNKNOWN`, `UP`, `DOWN`.
- Open incidents on failed checks.
- Avoid duplicate open incidents.
- Resolve incidents after successful recovery checks.
- Dashboard summary stats.
- Monitor details page with checks and incidents.
- Incidents page with `ALL`, `OPEN`, `RESOLVED` filters.

## Repository Layout

```text
.
|-- backend/
|   |-- app/
|   |-- alembic/
|   |-- tests/
|   |-- Dockerfile
|   `-- requirements.txt
|-- frontend/
|   |-- src/
|   |-- Dockerfile
|   `-- package.json
|-- k8s/
|-- .github/workflows/
|-- docs/screenshots/
|-- docker-compose.yml
|-- .env.example
|-- PROGRESS.md
`-- cloudpulse_project_plan.txt
```

## Local Run With Docker Compose

Requirements:

- Docker Desktop or Rancher Desktop with Docker-compatible CLI.
- Free local ports `3000`, `8000`, `5432`, `6379`, or adjusted values in `.env`.

Start the full stack:

```powershell
copy .env.example .env
docker compose up --build
```

Open:

```text
http://localhost:3000
http://localhost:3000/api/health
http://localhost:8000/health
http://localhost:8000/docs
```

Useful commands:

```powershell
docker compose ps
docker compose logs -f api
docker compose logs -f worker
docker compose logs -f scheduler
docker compose down
```

The API container runs `alembic upgrade head` before starting Uvicorn. The
frontend image builds the Vite app and serves it through nginx. In Compose,
frontend requests use `/api` and nginx proxies them to the internal `api`
service.

## Local Backend

Run the backend without containers:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

```text
http://localhost:8000/health
http://localhost:8000/docs
```

## Local Frontend

Run the frontend without containers:

```powershell
cd frontend
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

The local frontend reads `VITE_API_BASE_URL` from `frontend/.env`. See
`frontend/.env.example`.

## Backend Tests

Tests use `pytest`, FastAPI `TestClient`, in-memory SQLite, and mocked HTTP
clients for checker behavior.

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest
```

Current coverage includes:

- `GET /health`.
- Monitor creation.
- Monitor URL validation.
- Monitor list retrieval.
- Checker success behavior with a mocked HTTP response.
- Checker failed status behavior and incident creation.

## Kubernetes With Rancher Desktop

Requirements:

- Rancher Desktop with Kubernetes enabled.
- Active context `rancher-desktop`.
- Local images loaded into Rancher Desktop containerd namespace `k8s.io`.

Build and load local images when needed:

```powershell
docker build -t cloudpulse-backend:local .\backend
docker build --build-arg VITE_API_BASE_URL=/api -t cloudpulse-frontend:local .\frontend

docker save cloudpulse-backend:local -o cloudpulse-backend-local.tar
wsl -d rancher-desktop -- nerdctl -n k8s.io load -i /mnt/f/ac/VWM/cloudpulse-backend-local.tar
Remove-Item .\cloudpulse-backend-local.tar

docker save cloudpulse-frontend:local -o cloudpulse-frontend-local.tar
wsl -d rancher-desktop -- nerdctl -n k8s.io load -i /mnt/f/ac/VWM/cloudpulse-frontend-local.tar
Remove-Item .\cloudpulse-frontend-local.tar
```

Apply manifests:

```powershell
kubectl config use-context rancher-desktop
kubectl apply -f k8s/
kubectl get pods
kubectl get services
```

Open the API:

```powershell
kubectl port-forward service/api-service 8000:8000
```

```text
http://localhost:8000/health
```

Open the frontend:

```powershell
kubectl port-forward service/frontend-service 3000:80
```

```text
http://localhost:3000
http://localhost:3000/api/health
```

If Docker Compose already uses local port `3000`, use another local port:

```powershell
kubectl port-forward service/frontend-service 13000:80
```

## Kubernetes Objects

- `cloudpulse-config`: non-secret runtime settings.
- `cloudpulse-secret`: local development PostgreSQL password.
- `postgres`: Deployment, PVC and ClusterIP Service.
- `redis`: Deployment and ClusterIP Service.
- `api`: Deployment and `api-service`.
- `worker`: Deployment.
- `scheduler`: Deployment.
- `frontend`: Deployment and `frontend-service`.

## API Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | API health check |
| `GET` | `/stats` | Dashboard counters and average latency |
| `GET` | `/monitors` | List monitors |
| `POST` | `/monitors` | Create monitor |
| `GET` | `/monitors/{monitor_id}` | Read monitor details |
| `PUT` | `/monitors/{monitor_id}` | Update monitor |
| `DELETE` | `/monitors/{monitor_id}` | Delete monitor |
| `POST` | `/monitors/{monitor_id}/check` | Run manual check |
| `GET` | `/monitors/{monitor_id}/checks` | List monitor check results |
| `GET` | `/monitors/{monitor_id}/incidents` | List monitor incidents |
| `GET` | `/incidents` | List all incidents |

Example monitor payload:

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

## CI/CD

CI workflow: `.github/workflows/ci.yml`.

It runs on push and pull request:

- Installs backend dependencies.
- Imports the FastAPI app.
- Runs backend tests when test files are present.
- Installs frontend dependencies with `npm ci`.
- Builds the frontend.
- Builds backend and frontend Docker images.

Deployment workflow: `.github/workflows/deploy.yml`.

It is a manual workflow prepared for Google Cloud Run:

- Authenticates through Workload Identity Federation.
- Builds backend and frontend images.
- Pushes images to Google Artifact Registry.
- Deploys backend and frontend services to Cloud Run.

Required GitHub Secrets:

- `GCP_WORKLOAD_IDENTITY_PROVIDER`
- `GCP_SERVICE_ACCOUNT`
- `CLOUD_RUN_DATABASE_URL`
- `CLOUD_RUN_REDIS_URL`

Required GitHub Variables:

- `GCP_PROJECT_ID`
- `GAR_LOCATION`
- `GAR_REPOSITORY`
- `CLOUD_RUN_REGION`
- `CLOUD_RUN_BACKEND_SERVICE`
- `CLOUD_RUN_FRONTEND_SERVICE`
- `FRONTEND_API_BASE_URL`
- `CLOUD_RUN_CORS_ORIGINS`
- `REDIS_QUEUE_NAME`, optional

## Screenshots

Screenshot placeholders live in `docs/screenshots/`.

Suggested screenshots for project defense:

- Dashboard with summary cards and monitors table.
- Add Monitor form.
- Monitor Details with recent checks and incidents.
- Incidents page with filters.
- Swagger UI at `/docs`.
- Kubernetes pods/services in Rancher Desktop.
- GitHub Actions CI run.

## Security And Secrets

- `.env.example`, `backend/.env.example`, and `frontend/.env.example` contain
  local development defaults only.
- `k8s/secret.yaml` contains a local development password and must be replaced
  before any non-local deployment.
- Google Cloud credentials are not stored in the repository. Deployment uses
  GitHub Secrets and Workload Identity Federation.
- Before publishing or deploying, configure production database and Redis
  credentials through environment variables or GitHub Secrets.

## Known Limitations

- No user accounts or authentication yet.
- No alert delivery channels yet, such as email, Slack or webhooks.
- No charts yet; latency and uptime are shown as tables and summary values.
- Cloud Run workflow deploys frontend and API only. Production worker,
  scheduler, PostgreSQL and Redis-compatible services still need final cloud
  architecture decisions.
- Cloud Run workflow does not run Alembic migrations as a separate deployment
  step yet.
- Kubernetes manifests are optimized for local Rancher Desktop development, not
  hardened production clusters.
- `k8s/secret.yaml` is a local placeholder and not a production secret.
- Backend tests use SQLite for speed; PostgreSQL-specific behavior is still
  verified through Compose/Kubernetes flows.

## Troubleshooting

If `kubectl apply` fails with `failed to download openapi`, wait until Rancher
Desktop Kubernetes is fully ready:

```powershell
kubectl config use-context rancher-desktop
kubectl get nodes
```

If local Docker builds hang or `docker buildx ls` reports `DeadlineExceeded`,
restart Docker Desktop or Rancher Desktop and retry the build.

If ports are already busy, change them in `.env` for Docker Compose or use a
different local port for `kubectl port-forward`.

## Future Improvements

- Add authentication and per-user monitor ownership.
- Add alert channels and notification rules.
- Add uptime and latency charts.
- Add frontend tests.
- Add Redis queue tests and worker/scheduler integration tests.
- Add production migration workflow.
- Add Helm chart or Kustomize overlays.
- Add Cloud Run worker/scheduler strategy or move production orchestration to
  GKE.
- Add observability: structured logs, metrics and tracing.
