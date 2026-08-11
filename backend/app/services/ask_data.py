import json
import re
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.config import get_settings
from app.repository import latest_observation_date, list_observations
from app.schemas import AskDataRequest, AskDataResponse


DATASETS = {
    "pun": {"aliases": ("pun", "elettricita", "elettrico"), "label": "PUN Italia"},
    "gas": {"aliases": ("ttf", "gas"), "label": "Gas TTF"},
}
METRICS = {"average", "minimum", "maximum", "latest", "ytd_average", "compare_average"}


@dataclass
class Intent:
    dataset_key: str
    metric: str
    period: dict[str, Any]
    comparison_period: dict[str, Any] | None = None


def answer_data_question(db: Session, request: AskDataRequest) -> AskDataResponse:
    question = request.question.strip()
    if not question:
        return AskDataResponse(answer="Scrivi una domanda sui dati.", error="empty_question")

    intent = parse_rule_intent(question, request.dataset_key)
    used_ai = False
    if intent is None:
        intent = parse_ai_intent(question, request.dataset_key)
        used_ai = intent is not None

    if intent is None:
        return AskDataResponse(
            answer=(
                "Non ho capito il calcolo. Prova con: \"media PUN ultimi 30 giorni\", "
                "\"massimo PUN 2022\" oppure \"confronta PUN ultimi 30 giorni con anno precedente\"."
            ),
            error="unsupported_question",
        )
    if intent.dataset_key not in DATASETS or intent.metric not in METRICS:
        return AskDataResponse(answer="Dataset o metrica non supportati per ora.", error="unsupported_intent")

    try:
        result = calculate_intent(db, intent)
    except ValueError as exc:
        return AskDataResponse(
            answer=str(exc),
            dataset_key=intent.dataset_key,
            metric=intent.metric,
            period=intent.period,
            used_ai=used_ai,
            error="calculation_failed",
        )

    return AskDataResponse(
        answer=format_answer(result),
        dataset_key=intent.dataset_key,
        metric=intent.metric,
        period=intent.period,
        value=result.get("value"),
        unit=result.get("unit"),
        calculation=result,
        used_ai=used_ai,
    )


def parse_rule_intent(question: str, default_dataset: str | None = None) -> Intent | None:
    text = normalize(question)
    dataset_key = detect_dataset(text, default_dataset)
    if not dataset_key:
        return None

    period = detect_period(text)
    if "confront" in text or "scost" in text or "anno precedente" in text or "vs" in text:
        if period["type"] == "all":
            period = {"type": "last_days", "value": 30}
        return Intent(dataset_key, "compare_average", period, {"type": "same_period_previous_year"})

    metric = detect_metric(text)
    if not metric:
        return None
    if metric == "ytd_average":
        period = {"type": "ytd", "value": None}
    return Intent(dataset_key, metric, period)


def parse_ai_intent(question: str, default_dataset: str | None = None) -> Intent | None:
    settings = get_settings()
    if not settings.openai_api_key:
        return None

    schema = {
        "type": "object",
        "properties": {
            "dataset_key": {"type": "string", "enum": ["pun", "gas"]},
            "metric": {"type": "string", "enum": sorted(METRICS)},
            "period": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["all", "last_days", "last_months", "ytd", "year", "month"]},
                    "value": {"type": ["integer", "string", "null"]},
                },
                "required": ["type", "value"],
                "additionalProperties": False,
            },
            "comparison_period": {
                "type": ["object", "null"],
                "properties": {
                    "type": {"type": "string", "enum": ["same_period_previous_year"]},
                    "value": {"type": ["integer", "string", "null"]},
                },
                "required": ["type", "value"],
                "additionalProperties": False,
            },
        },
        "required": ["dataset_key", "metric", "period", "comparison_period"],
        "additionalProperties": False,
    }
    payload = {
        "model": settings.openai_model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Trasforma domande italiane su dati energetici in JSON. Non calcolare numeri. "
                    f"Dataset disponibili: pun, gas. Dataset default: {default_dataset or 'pun'}."
                ),
            },
            {"role": "user", "content": question},
        ],
        "temperature": 0,
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "data_intent", "strict": True, "schema": schema},
        },
    }

    try:
        with httpx.Client(timeout=12.0) as client:
            response = client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json=payload,
            )
            response.raise_for_status()
        data = json.loads(response.json()["choices"][0]["message"]["content"])
        return Intent(
            dataset_key=data["dataset_key"],
            metric=data["metric"],
            period=data["period"],
            comparison_period=data.get("comparison_period"),
        )
    except Exception:
        return None


def calculate_intent(db: Session, intent: Intent) -> dict[str, Any]:
    latest = latest_observation_date(db, dataset_key=intent.dataset_key)
    if not latest:
        raise ValueError("Non ci sono dati disponibili per questo dataset.")

    start, end = resolve_period(intent.period, latest)
    dataset, observations = list_observations(db, dataset_key=intent.dataset_key, start=start, end=end)
    if not dataset or not observations:
        raise ValueError("Non ci sono osservazioni disponibili nel periodo richiesto.")

    values = [(observation.observed_on, observation.value) for observation in observations]
    base = {
        "dataset_key": dataset.key,
        "dataset_name": DATASETS.get(dataset.key, {}).get("label", dataset.name),
        "unit": dataset.unit,
        "period_start": start.isoformat() if start else values[0][0].isoformat(),
        "period_end": end.isoformat() if end else values[-1][0].isoformat(),
        "observations": len(values),
    }

    if intent.metric == "latest":
        observed_on, value = values[-1]
        return {**base, "metric": "latest", "value": value, "observed_on": observed_on.isoformat()}
    if intent.metric in {"average", "ytd_average"}:
        return {**base, "metric": intent.metric, "value": average(value for _, value in values)}
    if intent.metric == "minimum":
        observed_on, value = min(values, key=lambda item: item[1])
        return {**base, "metric": "minimum", "value": value, "observed_on": observed_on.isoformat()}
    if intent.metric == "maximum":
        observed_on, value = max(values, key=lambda item: item[1])
        return {**base, "metric": "maximum", "value": value, "observed_on": observed_on.isoformat()}
    if intent.metric == "compare_average":
        compare_start, compare_end = resolve_comparison_period(intent.comparison_period, start, end)
        _, previous = list_observations(db, dataset_key=intent.dataset_key, start=compare_start, end=compare_end)
        if not previous:
            raise ValueError("Non ci sono dati per il periodo di confronto.")
        current_average = average(value for _, value in values)
        previous_average = average(observation.value for observation in previous)
        change = ((current_average / previous_average) - 1) * 100 if previous_average else None
        return {
            **base,
            "metric": "compare_average",
            "value": change,
            "current_average": current_average,
            "comparison_average": previous_average,
            "comparison_start": compare_start.isoformat(),
            "comparison_end": compare_end.isoformat(),
            "comparison_observations": len(previous),
        }
    raise ValueError("Metrica non supportata.")


def detect_dataset(text: str, default_dataset: str | None) -> str | None:
    if default_dataset in DATASETS:
        return default_dataset
    for dataset_key, config in DATASETS.items():
        if any(alias in text for alias in config["aliases"]):
            return dataset_key
    return "pun"


def detect_metric(text: str) -> str | None:
    if "ytd" in text or "year to date" in text or "anno corrente" in text:
        return "ytd_average"
    if "massim" in text or "picco" in text:
        return "maximum"
    if "minim" in text:
        return "minimum"
    if "ultimo" in text or "ultima" in text or "valore disponibile" in text:
        return "latest"
    if "media" in text or "medio" in text:
        return "average"
    return None


def detect_period(text: str) -> dict[str, Any]:
    if "ultimo mese" in text or "ultimi 30 giorni" in text or "ultimi trenta giorni" in text:
        return {"type": "last_days", "value": 30}
    if "ultimo anno" in text or "ultimi 12 mesi" in text or "ultimi dodici mesi" in text:
        return {"type": "last_months", "value": 12}
    if "ytd" in text or "anno corrente" in text:
        return {"type": "ytd", "value": None}
    month = detect_month(text)
    if month:
        return {"type": "month", "value": month}
    match = re.search(r"\b(20\d{2})\b", text)
    if match:
        return {"type": "year", "value": int(match.group(1))}
    return {"type": "all", "value": None}


def detect_month(text: str) -> str | None:
    months = {
        "gennaio": 1,
        "febbraio": 2,
        "marzo": 3,
        "aprile": 4,
        "maggio": 5,
        "giugno": 6,
        "luglio": 7,
        "agosto": 8,
        "settembre": 9,
        "ottobre": 10,
        "novembre": 11,
        "dicembre": 12,
    }
    year = re.search(r"\b(20\d{2})\b", text)
    if not year:
        return None
    for month_name, month in months.items():
        if month_name in text:
            return f"{int(year.group(1)):04d}-{month:02d}"
    iso_month = re.search(r"\b(20\d{2})-(0[1-9]|1[0-2])\b", text)
    return iso_month.group(0) if iso_month else None


def resolve_period(period: dict[str, Any], latest: date) -> tuple[date | None, date | None]:
    period_type = period.get("type", "all")
    value = period.get("value")
    if period_type == "last_days":
        days = int(value or 30)
        return latest - timedelta(days=days - 1), latest
    if period_type == "last_months":
        months = int(value or 12)
        return add_months(latest, -months), latest
    if period_type == "ytd":
        return date(latest.year, 1, 1), latest
    if period_type == "year":
        year = int(value)
        return date(year, 1, 1), date(year, 12, 31)
    if period_type == "month":
        year, month = str(value).split("-")
        start = date(int(year), int(month), 1)
        return start, add_months(start, 1) - timedelta(days=1)
    return None, None


def resolve_comparison_period(period: dict[str, Any] | None, start: date | None, end: date | None) -> tuple[date, date]:
    if not start or not end:
        raise ValueError("Per il confronto serve un periodo esplicito.")
    if not period or period.get("type") == "same_period_previous_year":
        return add_years(start, -1), add_years(end, -1)
    raise ValueError("Periodo di confronto non supportato.")


def add_months(value: date, months: int) -> date:
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, month_days(year, month))
    return date(year, month, day)


def add_years(value: date, years: int) -> date:
    try:
        return value.replace(year=value.year + years)
    except ValueError:
        return value.replace(year=value.year + years, day=28)


def month_days(year: int, month: int) -> int:
    next_month = date(year + int(month == 12), 1 if month == 12 else month + 1, 1)
    return (next_month - timedelta(days=1)).day


def average(values: Any) -> float:
    items = list(values)
    return sum(items) / len(items)


def format_answer(result: dict[str, Any]) -> str:
    dataset = result["dataset_name"]
    unit = display_unit(result["unit"])
    metric = result["metric"]
    if metric == "latest":
        return f"L'ultimo valore disponibile di {dataset} è {fmt(result['value'])} {unit}, rilevato il {fmt_date(result['observed_on'])}."
    if metric == "average":
        return (
            f"La media di {dataset} dal {fmt_date(result['period_start'])} al {fmt_date(result['period_end'])} "
            f"è {fmt(result['value'])} {unit}, calcolata su {result['observations']} osservazioni."
        )
    if metric == "ytd_average":
        return (
            f"La media YTD di {dataset} dal {fmt_date(result['period_start'])} al {fmt_date(result['period_end'])} "
            f"è {fmt(result['value'])} {unit}, su {result['observations']} osservazioni."
        )
    if metric == "minimum":
        return f"Il minimo di {dataset} nel periodo è {fmt(result['value'])} {unit}, rilevato il {fmt_date(result['observed_on'])}."
    if metric == "maximum":
        return f"Il massimo di {dataset} nel periodo è {fmt(result['value'])} {unit}, rilevato il {fmt_date(result['observed_on'])}."
    if metric == "compare_average":
        sign = "+" if result["value"] and result["value"] > 0 else ""
        return (
            f"La media di {dataset} nel periodo selezionato è {fmt(result['current_average'])} {unit}; "
            f"nello stesso periodo dell'anno precedente era {fmt(result['comparison_average'])} {unit}. "
            f"Scostamento: {sign}{fmt(result['value'])}%."
        )
    return "Calcolo eseguito."


def fmt(value: float | None) -> str:
    if value is None:
        return "n.d."
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_date(value: str) -> str:
    return date.fromisoformat(value).strftime("%d/%m/%Y")


def display_unit(value: str) -> str:
    return value.replace("EUR/MWh", "€/MWh")


def normalize(value: str) -> str:
    return (
        value.lower()
        .replace("à", "a")
        .replace("è", "e")
        .replace("é", "e")
        .replace("ì", "i")
        .replace("ò", "o")
        .replace("ù", "u")
    )
