import os
from datetime import timezone

from app.database import SessionLocal, init_db
from app.models import ScrapeRun, utcnow
from app.repository import get_or_create_dataset, upsert_observation
from app.services.pun import fetch_pun_csv


def main() -> None:
    init_db()
    source_url = os.getenv("PUN_SOURCE_URL")

    with SessionLocal() as db:
        run = ScrapeRun(job_name="pun_daily_update", status="running")
        db.add(run)
        db.commit()
        db.refresh(run)

        try:
            if not source_url:
                run.status = "skipped"
                run.message = "PUN_SOURCE_URL not configured"
                run.finished_at = utcnow().astimezone(timezone.utc)
                db.commit()
                print(run.message)
                return

            records = fetch_pun_csv(source_url)
            dataset = get_or_create_dataset(
                db,
                key="pun",
                name="Prezzo Unico Nazionale",
                unit="EUR/MWh",
                source=source_url,
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
