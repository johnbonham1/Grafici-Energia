import json
from datetime import date
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.repository import get_or_create_dataset, upsert_observation, upsert_payload


SEED_FILE = Path(__file__).resolve().parents[1] / "seed_data" / "frontend_payloads.json"


DATASET_META = {
    "pun": ("PUN Italia", "EUR/MWh", "grafico_prezzi_giornalieri.html"),
    "gas": ("Gas TTF", "EUR/MWh", "grafico_prezzi_giornalieri.html"),
    "energy_monthly_eua": ("Quote ETS EUA mensili", "EUR/t", "grafico_energia (2).html"),
    "energy_monthly_pun": ("PUN Italia mensile", "EUR/MWh", "grafico_energia (2).html"),
    "energy_monthly_gas": ("Gas TTF mensile", "EUR/MWh", "grafico_energia (2).html"),
    "energy_monthly_term": ("Quota termoelettrico", "%", "grafico_energia (2).html"),
    "ets_price": ("Prezzo medio EUA", "EUR/t", "EU_ETS_grafici_principali.html"),
    "ets_emissions": ("Emissioni verificate ETS", "MtCO2eq", "EU_ETS_grafici_principali.html"),
    "ets_gdp": ("PIL EU-27", "trl EUR", "EU_ETS_industria.html"),
    "ets_industry_va": ("Valore aggiunto industria EU-27", "trl EUR", "EU_ETS_industria.html"),
    "ets_industry_weight": ("Peso industria sul PIL EU-27", "%", "EU_ETS_industria.html"),
    "ets_emissions_cagr": ("CAGR emissioni ETS", "%", "EU_ETS_grafici_principali.html"),
}


def parse_period(value: str | int) -> date:
    text = str(value)
    if len(text) == 4:
        return date(int(text), 1, 1)
    if len(text) == 7:
        year, month = text.split("-")
        return date(int(year), int(month), 1)
    return date.fromisoformat(text)


def seed_frontend_data(db: Session) -> int:
    if not SEED_FILE.exists():
        return 0

    seed = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    payloads = seed["payloads"]
    for item in payloads:
        upsert_payload(
            db,
            key=item["key"],
            name=item["name"],
            source_file=item["source_file"],
            payload=item["payload"],
        )

    rows = 0
    rows += seed_daily_prices(db, payload_by_key(payloads, "daily_prices"))
    rows += seed_energy_monthly(db, payload_by_key(payloads, "energy_monthly"))
    rows += seed_ets(db, payload_by_key(payloads, "ets")["data"])
    db.commit()
    return rows


def payload_by_key(payloads: list[dict[str, Any]], key: str) -> Any:
    for item in payloads:
        if item["key"] == key:
            return item["payload"]
    raise KeyError(key)


def seed_daily_prices(db: Session, rows: list[dict[str, Any]]) -> int:
    return seed_row_series(
        db,
        rows=rows,
        date_key="date",
        value_keys={"pun": "pun", "gas": "gas"},
    )


def seed_energy_monthly(db: Session, rows: list[dict[str, Any]]) -> int:
    return seed_row_series(
        db,
        rows=rows,
        date_key="date",
        value_keys={
            "eua": "energy_monthly_eua",
            "pun": "energy_monthly_pun",
            "gas": "energy_monthly_gas",
            "term": "energy_monthly_term",
        },
    )


def seed_row_series(
    db: Session,
    *,
    rows: list[dict[str, Any]],
    date_key: str,
    value_keys: dict[str, str],
) -> int:
    count = 0
    datasets = {
        row_key: get_or_create_dataset(
            db,
            key=dataset_key,
            name=DATASET_META[dataset_key][0],
            unit=DATASET_META[dataset_key][1],
            source=DATASET_META[dataset_key][2],
        )
        for row_key, dataset_key in value_keys.items()
    }
    for row in rows:
        observed_on = parse_period(row[date_key])
        for row_key, dataset in datasets.items():
            value = row.get(row_key)
            if value is None:
                continue
            upsert_observation(db, dataset=dataset, observed_on=observed_on, value=float(value))
            count += 1
    return count


def seed_ets(db: Session, data: dict[str, list[Any]]) -> int:
    count = 0
    annual_series = {
        "prezzo26": ("ets_price", "years26"),
        "emiss": ("ets_emissions", "years21"),
        "gdp": ("ets_gdp", "years21"),
        "va": ("ets_industry_va", "years21"),
        "peso": ("ets_industry_weight", "years21"),
        "cagr": ("ets_emissions_cagr", "years21"),
    }
    for values_key, (dataset_key, years_key) in annual_series.items():
        dataset = get_or_create_dataset(
            db,
            key=dataset_key,
            name=DATASET_META[dataset_key][0],
            unit=DATASET_META[dataset_key][1],
            source=DATASET_META[dataset_key][2],
        )
        for year, value in zip(data[years_key], data[values_key], strict=False):
            if value is None:
                continue
            upsert_observation(db, dataset=dataset, observed_on=parse_period(year), value=float(value))
            count += 1
    return count
