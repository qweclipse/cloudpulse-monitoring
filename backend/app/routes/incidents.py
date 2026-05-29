from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.services import queries

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.get("", response_model=list[schemas.IncidentRead])
def list_incidents(
    status: models.IncidentStatus | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[schemas.IncidentRead]:
    return queries.list_incidents(db, status=status, skip=skip, limit=limit)
