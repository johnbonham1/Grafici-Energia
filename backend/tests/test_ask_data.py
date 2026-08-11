from datetime import date, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Dataset
from app.repository import get_or_create_dataset, upsert_observation
from app.schemas import AskDataRequest
from app.services.ask_data import answer_data_question, parse_rule_intent


def make_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)()


def seed_pun(db) -> Dataset:
    dataset = get_or_create_dataset(db, key="pun", name="PUN Italia", unit="EUR/MWh", source="test")
    start = date(2025, 8, 1)
    for offset in range(410):
        observed_on = start + timedelta(days=offset)
        value = 100 + offset / 10
        upsert_observation(db, dataset=dataset, observed_on=observed_on, value=value)
    db.commit()
    return dataset


def test_rule_parser_handles_basic_questions() -> None:
    assert parse_rule_intent("media PUN ultimi 30 giorni").metric == "average"
    assert parse_rule_intent("massimo PUN 2022").period == {"type": "year", "value": 2022}
    assert parse_rule_intent("confronta PUN ultimi 30 giorni con anno precedente").metric == "compare_average"


def test_answer_data_question_calculates_average() -> None:
    db = make_session()
    seed_pun(db)

    response = answer_data_question(db, AskDataRequest(question="media PUN ultimi 30 giorni"))

    assert response.error is None
    assert response.metric == "average"
    assert response.value is not None
    assert response.calculation["observations"] == 30
    assert "30 osservazioni" in response.answer


def test_answer_data_question_calculates_latest_and_maximum() -> None:
    db = make_session()
    seed_pun(db)

    latest = answer_data_question(db, AskDataRequest(question="ultimo valore PUN disponibile"))
    maximum = answer_data_question(db, AskDataRequest(question="massimo PUN 2026"))

    assert latest.metric == "latest"
    assert maximum.metric == "maximum"
    assert maximum.value >= latest.value


def test_answer_data_question_compares_same_period_previous_year() -> None:
    db = make_session()
    seed_pun(db)

    response = answer_data_question(
        db,
        AskDataRequest(question="confronta PUN ultimi 30 giorni con anno precedente"),
    )

    assert response.error is None
    assert response.metric == "compare_average"
    assert response.calculation["comparison_observations"] == 30
