from app.services.pun import parse_pun_csv


def test_parse_pun_csv_accepts_italian_date_and_decimal_comma() -> None:
    records = parse_pun_csv("Data;PUN\n01/08/2026;112,45\n")

    assert len(records) == 1
    assert records[0].observed_on.isoformat() == "2026-08-01"
    assert records[0].value == 112.45
