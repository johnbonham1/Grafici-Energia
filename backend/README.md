# Dashboard AEIF Backend

Backend FastAPI per alimentare la dashboard con dati strutturati.

## Obiettivi

- esporre API dati per il frontend
- salvare serie storiche in PostgreSQL
- preparare job automatici di aggiornamento dati
- partire dal PUN come primo flusso giornaliero

## Servizi previsti su Render

- `dashboard-aeif-api`: Web Service FastAPI produzione
- `dashboard-aeif-pun-scraper`: Cron Job giornaliero produzione
- `dashboard-aeif-api-preprod`: Web Service FastAPI preproduzione
- `dashboard-aeif-db-preprod`: database PostgreSQL free condiviso
- `dashboard-aeif-pun-scraper-preprod`: Cron Job giornaliero preproduzione

## Job PUN

Il job `python -m app.jobs.update_pun` aggiorna il dataset `pun` in modo incrementale:

- legge dal DB l'ultima data gia disponibile;
- interroga il PUN Index GME ufficiale solo per le date mancanti, fino al giorno successivo a oggi;
- inserisce o aggiorna le osservazioni senza duplicarle;
- registra ogni esecuzione in `scrape_runs`.

La variabile `PUN_SOURCE_URL` resta disponibile come fallback per importare un CSV manuale. Se e vuota, il job usa automaticamente l'endpoint GME della pagina `PUN Index GME`.

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
