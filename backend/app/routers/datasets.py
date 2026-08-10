from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Dataset, DatasetPayload
from app.repository import latest_observation_date, latest_scrape_run, list_observations
from app.schemas import DatasetPayloadResponse, DatasetResponse, DatasetStatusResponse, SeriesResponse


router = APIRouter(tags=["datasets"])


@router.get("/datasets", response_model=list[DatasetResponse])
def datasets(db: Session = Depends(get_db)) -> list[Dataset]:
    return list(db.scalars(select(Dataset).order_by(Dataset.name)))


@router.get("/payloads", response_model=list[DatasetPayloadResponse])
def payloads(db: Session = Depends(get_db)) -> list[DatasetPayloadResponse]:
    rows = db.scalars(select(DatasetPayload).order_by(DatasetPayload.name))
    return [
        DatasetPayloadResponse(
            key=row.key,
            name=row.name,
            source_file=row.source_file,
            payload=row.payload_json,
        )
        for row in rows
    ]


@router.get("/payloads/{payload_key}", response_model=DatasetPayloadResponse)
def payload(payload_key: str, db: Session = Depends(get_db)) -> DatasetPayloadResponse:
    row = db.scalar(select(DatasetPayload).where(DatasetPayload.key == payload_key))
    if not row:
        raise HTTPException(status_code=404, detail="Payload not found")
    return DatasetPayloadResponse(
        key=row.key,
        name=row.name,
        source_file=row.source_file,
        payload=row.payload_json,
    )


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


@router.get("/pun/status", response_model=DatasetStatusResponse)
def pun_status(db: Session = Depends(get_db)) -> DatasetStatusResponse:
    return DatasetStatusResponse(
        dataset_key="pun",
        latest_observed_on=latest_observation_date(db, dataset_key="pun"),
        latest_job=latest_scrape_run(db, job_name="pun_daily_update"),
    )
