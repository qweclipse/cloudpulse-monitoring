from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.services import checker, crud, queries

router = APIRouter(prefix="/monitors", tags=["monitors"])


@router.get("", response_model=list[schemas.MonitorRead])
def list_monitors(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[schemas.MonitorRead]:
    return crud.list_monitors(db, skip=skip, limit=limit)


@router.post(
    "",
    response_model=schemas.MonitorRead,
    status_code=status.HTTP_201_CREATED,
)
def create_monitor(
    monitor_in: schemas.MonitorCreate,
    db: Session = Depends(get_db),
) -> schemas.MonitorRead:
    return crud.create_monitor(db, monitor_in)


@router.get("/{monitor_id}", response_model=schemas.MonitorRead)
def get_monitor(
    monitor_id: int,
    db: Session = Depends(get_db),
) -> schemas.MonitorRead:
    monitor = crud.get_monitor(db, monitor_id)
    if monitor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitor not found",
        )
    return monitor


@router.post("/{monitor_id}/check", response_model=schemas.CheckResultRead)
def run_monitor_check(
    monitor_id: int,
    db: Session = Depends(get_db),
) -> schemas.CheckResultRead:
    try:
        return checker.check_monitor(db, monitor_id)
    except checker.MonitorNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitor not found",
        ) from exc


@router.get("/{monitor_id}/checks", response_model=list[schemas.CheckResultRead])
def list_monitor_checks(
    monitor_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[schemas.CheckResultRead]:
    monitor = crud.get_monitor(db, monitor_id)
    if monitor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitor not found",
        )
    return queries.list_monitor_checks(db, monitor_id, skip=skip, limit=limit)


@router.get("/{monitor_id}/incidents", response_model=list[schemas.IncidentRead])
def list_monitor_incidents(
    monitor_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[schemas.IncidentRead]:
    monitor = crud.get_monitor(db, monitor_id)
    if monitor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitor not found",
        )
    return queries.list_monitor_incidents(db, monitor_id, skip=skip, limit=limit)


@router.put("/{monitor_id}", response_model=schemas.MonitorRead)
def update_monitor(
    monitor_id: int,
    monitor_in: schemas.MonitorUpdate,
    db: Session = Depends(get_db),
) -> schemas.MonitorRead:
    monitor = crud.get_monitor(db, monitor_id)
    if monitor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitor not found",
        )
    return crud.update_monitor(db, monitor, monitor_in)


@router.delete("/{monitor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_monitor(
    monitor_id: int,
    db: Session = Depends(get_db),
) -> None:
    monitor = crud.get_monitor(db, monitor_id)
    if monitor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitor not found",
        )
    crud.delete_monitor(db, monitor)
