from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.services import queries

router = APIRouter(tags=["stats"])


# Агрегированные значения для карточек на dashboard.
@router.get("/stats", response_model=schemas.StatsRead)
def get_stats(db: Session = Depends(get_db)) -> schemas.StatsRead:
    return queries.get_stats(db)
