# Dashboard AEIF Backend

Backend FastAPI per alimentare la dashboard con dati strutturati.

## Obiettivi

- esporre API dati per il frontend
- salvare serie storiche in PostgreSQL
- preparare job automatici di aggiornamento dati
- partire dal PUN come primo flusso giornaliero

## Servizi previsti su Render

- `dashboard-aeif-api-preprod`: Web Service FastAPI
- `dashboard-aeif-db-preprod`: database PostgreSQL
- `dashboard-aeif-pun-scraper-preprod`: Cron Job giornaliero

## Comandi locali

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Inizializza DB:

```bash
python -m app.db_init
```

Esegui job PUN:

```bash
python -m app.jobs.update_pun
```

Se `DATABASE_URL` non e impostato, il backend usa `sqlite:///./dashboard_aeif.db` per sviluppo locale.
