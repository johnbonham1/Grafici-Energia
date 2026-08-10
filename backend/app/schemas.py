from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    status: str
    environment: str
    database: str


class DatasetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str
    name: str
    unit: str
    source: str | None = None


class DatasetPayloadResponse(BaseModel):
    key: str
    name: str
    source_file: str
    payload: dict | list


class ObservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    observed_on: date
    value: float
    metadata_json: dict | None = None


class SeriesResponse(BaseModel):
    dataset: DatasetResponse
    observations: list[ObservationResponse]


class ScrapeRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_name: str
    status: str
    message: str | None = None
    rows_processed: int
    started_at: datetime
    finished_at: datetime | None = None


class DatasetStatusResponse(BaseModel):
    dataset_key: str
    latest_observed_on: date | None = None
    latest_job: ScrapeRunResponse | None = None
