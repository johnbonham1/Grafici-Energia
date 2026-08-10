import os
from datetime import date, timedelta, timezone

from app.database import SessionLocal, init_db
from app.models import ScrapeRun, utcnow
from app.repository import get_or_create_dataset, latest_observation_date, upsert_observation
from app.services.pun import GME_PUN_PAGE_URL, fetch_gme_pun_range, fetch_pun_csv


def main() -> None:
    init_db()
    source_url = os.getenv("PUN_SOURCE_URL")
    today = date.today()

    with SessionLocal() as db:
        run = ScrapeRun(job_name="pun_daily_update", status="running")
        db.add(run)
        db.commit()
        db.refresh(run)

        try:
            if source_url:
                records = fetch_pun_csv(source_url)
                source = source_url
            else:
                last_date = latest_observation_date(db, dataset_key="pun")
                start = (last_date + timedelta(days=1)) if last_date else today
                end = today + timedelta(days=1)
                if start > end:
                    records = []
                else:
                    records = fetch_gme_pun_range(start, end)
                source = GME_PUN_PAGE_URL

            dataset = get_or_create_dataset(
                db,
                key="pun",
                name="PUN Index GME",
                unit="EUR/MWh",
                source=source,
            )
            for record in records:
                upsert_observation(
                    db,
                    dataset=dataset,
                    observed_on=record.observed_on,
                    value=record.value,
                    metadata_json=record.metadata_json,
                )

            run.status = "success"
            run.rows_processed = len(records)
            run.message = f"Imported {len(records)} PUN observations"
            run.finished_at = utcnow().astimezone(timezone.utc)
            db.commit()
            print(run.message)
        except Exception as exc:
            run.status = "failed"
            run.message = str(exc)
            run.finished_at = utcnow().astimezone(timezone.utc)
            db.commit()
            raise


if __name__ == "__main__":
    main()
