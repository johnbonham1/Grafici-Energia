from dataclasses import dataclass
from datetime import date, datetime
from io import StringIO


@dataclass(frozen=True)
class PunRecord:
    observed_on: date
    value: float
    metadata_json: dict | None = None


def parse_date(value: str) -> date:
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {value}")


def parse_pun_csv(text: str) -> list[PunRecord]:
    rows: list[PunRecord] = []
    for line in StringIO(text):
        raw = line.strip()
        if not raw or raw.lower().startswith(("date", "data")):
            continue

        delimiter = ";" if ";" in raw else ","
        parts = [part.strip() for part in raw.split(delimiter)]
        if len(parts) < 2:
            continue

        observed_on = parse_date(parts[0])
        value_text = parts[1]
        if "," in value_text and "." in value_text:
            value_text = value_text.replace(".", "").replace(",", ".")
        elif "," in value_text:
            value_text = value_text.replace(",", ".")
        value = float(value_text)
        rows.append(PunRecord(observed_on=observed_on, value=value))

    return rows


def fetch_pun_csv(source_url: str) -> list[PunRecord]:
    import httpx

    response = httpx.get(source_url, timeout=30)
    response.raise_for_status()
    return parse_pun_csv(response.text)
