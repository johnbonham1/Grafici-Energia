from app.services.pun import extract_request_verification_token, parse_gme_pun_response, parse_pun_csv


def test_parse_pun_csv_accepts_italian_date_and_decimal_comma() -> None:
    records = parse_pun_csv("Data;PUN\n01/08/2026;112,45\n")

    assert len(records) == 1
    assert records[0].observed_on.isoformat() == "2026-08-01"
    assert records[0].value == 112.45


def test_extract_request_verification_token() -> None:
    token = extract_request_verification_token(
        '<input name="__RequestVerificationToken" type="hidden" value="abc123" />'
    )

    assert token == "abc123"


def test_parse_gme_pun_response_daily_value() -> None:
    records = parse_gme_pun_response([{"df": 20260811, "h": 0, "p": 181.142166, "qh": 96}])

    assert len(records) == 1
    assert records[0].observed_on.isoformat() == "2026-08-11"
    assert records[0].value == 181.142166
    assert records[0].metadata_json["source"] == "GME PUN Index GME"
