from dataclasses import dataclass
from datetime import date, datetime
from io import StringIO
import re


@dataclass(frozen=True)
class PunRecord:
    observed_on: date
    value: float
    metadata_json: dict | None = None


GME_PUN_PAGE_URL = "https://gme.mercatoelettrico.org/it-it/Home/Esiti/Elettricita/MGP/Esiti/PUN"
GME_PUN_API_URL = "https://gme.mercatoelettrico.org/DesktopModules/GmeEsitiPrezziME/API/item/GetMEPrezzi"
GME_PUN_MODULE_ID = "530"
GME_PUN_TAB_ID = "48"


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


def format_gme_date(value: date) -> str:
    return value.strftime("%Y%m%d")


def extract_request_verification_token(html: str) -> str:
    match = re.search(r'name="__RequestVerificationToken"\s+type="hidden"\s+value="([^"]+)"', html)
    if not match:
        match = re.search(r'value="([^"]+)"\s+name="__RequestVerificationToken"', html)
    if not match:
        raise ValueError("GME request verification token not found")
    return match.group(1)


def parse_gme_pun_response(payload: list[dict]) -> list[PunRecord]:
    records: list[PunRecord] = []
    for item in payload:
        flow_date = str(item.get("df", ""))
        value = item.get("p")
        if len(flow_date) != 8 or value is None:
            continue
        records.append(
            PunRecord(
                observed_on=datetime.strptime(flow_date, "%Y%m%d").date(),
                value=float(value),
                metadata_json={
                    "source": "GME PUN Index GME",
                    "granularity": "daily",
                    "raw": item,
                },
            )
        )
    return records


def fetch_gme_pun_range(start: date, end: date) -> list[PunRecord]:
    import httpx

    with httpx.Client(timeout=30, follow_redirects=True) as client:
        page_response = client.get(GME_PUN_PAGE_URL)
        page_response.raise_for_status()
        token = extract_request_verification_token(page_response.text)

        response = client.get(
            GME_PUN_API_URL,
            params={
                "DataInizio": format_gme_date(start),
                "DataFine": format_gme_date(end),
                "Granularita": "d",
                "Mercato": "MGP",
                "Zona": "PUN",
                "Tipologia": "PUN",
            },
            headers={
                "ModuleId": GME_PUN_MODULE_ID,
                "TabId": GME_PUN_TAB_ID,
                "RequestVerificationToken": token,
                "X-Requested-With": "XMLHttpRequest",
                "Referer": GME_PUN_PAGE_URL,
            },
        )
        response.raise_for_status()
        return parse_gme_pun_response(response.json())
