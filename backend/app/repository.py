from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Dataset, DatasetPayload, Observation


def get_or_create_dataset(db: Session, *, key: str, name: str, unit: str, source: str | None = None) -> Dataset:
    dataset = db.scalar(select(Dataset).where(Dataset.key == key))
    if dataset:
        dataset.name = name
        dataset.unit = unit
        dataset.source = source
        return dataset

    dataset = Dataset(key=key, name=name, unit=unit, source=source)
    db.add(dataset)
    db.flush()
    return dataset


def upsert_observation(
    db: Session,
    *,
    dataset: Dataset,
    observed_on: date,
    value: float,
    metadata_json: dict | None = None,
) -> Observation:
    observation = db.scalar(
        select(Observation).where(
            Observation.dataset_id == dataset.id,
            Observation.observed_on == observed_on,
        )
    )
    if observation:
        observation.value = value
        observation.metadata_json = metadata_json
        return observation

    observation = Observation(
        dataset_id=dataset.id,
        observed_on=observed_on,
        value=value,
        metadata_json=metadata_json,
    )
    db.add(observation)
    return observation


def upsert_payload(
    db: Session,
    *,
    key: str,
    name: str,
    source_file: str,
    payload: dict | list,
) -> DatasetPayload:
    dataset_payload = db.scalar(select(DatasetPayload).where(DatasetPayload.key == key))
    if dataset_payload:
        dataset_payload.name = name
        dataset_payload.source_file = source_file
        dataset_payload.payload_json = payload
        return dataset_payload

    dataset_payload = DatasetPayload(
        key=key,
        name=name,
        source_file=source_file,
        payload_json=payload,
    )
    db.add(dataset_payload)
    return dataset_payload


def list_observations(
    db: Session,
    *,
    dataset_key: str,
    start: date | None = None,
    end: date | None = None,
) -> tuple[Dataset | None, list[Observation]]:
    dataset = db.scalar(select(Dataset).where(Dataset.key == dataset_key))
    if not dataset:
        return None, []

    query = select(Observation).where(Observation.dataset_id == dataset.id)
    if start:
        query = query.where(Observation.observed_on >= start)
    if end:
        query = query.where(Observation.observed_on <= end)

    observations = list(db.scalars(query.order_by(Observation.observed_on)))
    return dataset, observations
