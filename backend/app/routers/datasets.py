from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Dataset
from app.repository import list_observations
from app.schemas import DatasetResponse, SeriesResponse


router = APIRouter(tags=["datasets"])


@router.get("/datasets", response_model=list[DatasetResponse])
def datasets(db: Session = Depends(get_db)) -> list[Dataset]:
    return list(db.scalars(select(Dataset).order_by(Dataset.name)))


@router.get("/series/{dataset_key}", response_model=SeriesResponse)
def series(
    dataset_key: str,
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    db: Session = Depends(get_db),
) -> SeriesResponse:
    dataset, observations = list_observations(db, dataset_key=dataset_key, start=start, end=end)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return SeriesResponse(dataset=dataset, observations=observations)


@router.get("/pun", response_model=SeriesResponse)
def pun(
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    db: Session = Depends(get_db),
) -> SeriesResponse:
    dataset, observations = list_observations(db, dataset_key="pun", start=start, end=end)
    if not dataset:
        raise HTTPException(status_code=404, detail="PUN dataset not available yet")
    return SeriesResponse(dataset=dataset, observations=observations)
