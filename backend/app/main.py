from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import incidents, monitors, stats

app = FastAPI(
    title="CloudPulse API",
    description="API for website and API monitoring.",
    version="0.1.0",
)

# CORS разрешает frontend-домену обращаться к API из браузера.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем группы endpoint-ов по предметным областям.
app.include_router(monitors.router)
app.include_router(incidents.router)
app.include_router(stats.router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    # Используется Railway/Kubernetes healthcheck-ами.
    return {"status": "ok"}
