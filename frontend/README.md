# CloudPulse Frontend

React + Vite frontend for the CloudPulse monitoring dashboard.

## Current Status

The frontend contains the working CloudPulse dashboard, monitor management
screens, incident views, Docker support and Kubernetes-compatible API proxying:

- `GET /stats` powers the summary cards;
- `GET /monitors` powers the monitor table;
- each monitor row shows status, last checked time and latest check latency;
- monitor rows support view, manual check, enable/disable and delete actions;
- the Add Monitor page validates required fields and posts to `POST /monitors`;
- successful monitor creation redirects back to the Dashboard;
- the Monitor Details page reads `GET /monitors/{id}`;
- recent checks are loaded from `GET /monitors/{id}/checks`;
- monitor incidents are loaded from `GET /monitors/{id}/incidents`;
- manual checks can be triggered from the details page;
- the Incidents page lists `GET /incidents`;
- incidents can be filtered by `ALL`, `OPEN` and `RESOLVED`;
- the production frontend image builds the Vite app and serves it through nginx;
- Docker Compose exposes the frontend at `http://localhost:3000`;
- nginx proxies `/api/*` to the backend `api` service;
- success and error messages are shown inline.

## Local Setup

From `frontend/`:

```powershell
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

## Backend API URL

The frontend reads the backend URL from:

```text
VITE_API_BASE_URL=http://localhost:8000
```

Create `frontend/.env` from `frontend/.env.example` to override it locally.

The backend allows the default Vite origins through CORS:

```text
http://localhost:5173
http://127.0.0.1:5173
```

## Docker

From the repository root:

```powershell
docker compose up --build
```

Open:

```text
http://localhost:3000
```

The Docker build uses:

```text
VITE_API_BASE_URL=/api
```

nginx proxies `/api/` to `http://api:8000/` inside the Compose network.
