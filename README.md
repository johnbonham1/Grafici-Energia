# Grafici-Energia

Dashboard AEIF con grafici interattivi su mercati elettrici, ETS, industria, Innovation Fund e confronti internazionali.

## Documentazione operativa

- [Operativita ambienti e servizi](OPERATIONS.md)
- [Checklist rilascio](RELEASE_CHECKLIST.md)

## Link

Produzione Render:

https://dashboard-aeif.onrender.com/

Pre-produzione Render:

https://dashboard-aeif-preproduzione.onrender.com/

## Ambienti

- `main`: produzione
- `preprod`: pre-produzione

Ogni ambiente ha uno static site Render separato gia esistente. Il Blueprint Render gestisce solo backend, database e cron.

## Render Produzione

- static site: `dashboard-aeif` gia esistente, fuori dal Blueprint
- API: `dashboard-aeif-api-f497`
- database: configurato manualmente con `DATABASE_URL`
- cron PUN: `dashboard-aeif-pun-scraper-f497`
- branch collegato: `main`

Il frontend produzione legge i dati dall'API produzione. Se l'API non risponde, le pagine mostrano un messaggio di dati temporaneamente non disponibili.

Sul piano free di Render e' disponibile un solo database Postgres attivo. Per questo il Blueprint produzione non crea un secondo database: usa `DATABASE_URL` come variabile manuale.

## Aggiornamento PUN

- sorgente PUN: PUN Index GME ufficiale; `PUN_SOURCE_URL` resta solo come fallback CSV manuale
- frequenza cron: ogni giorno alle 11:30 UTC
- logica aggiornamento: il job legge l'ultima data `pun` presente nel database e importa solo le date mancanti fino al giorno successivo a oggi, includendo il dato day-ahead pubblicato dal GME
- verifica dati: `/api/series/pun`, `/api/series/pun/monthly`, `/api/pun/status`
- pagina prezzi: il grafico PUN/TTF usa il payload storico per il TTF e sovrascrive/estende la serie PUN con i valori live letti dal database tramite API
- pagina mercato energetico: il PUN mensile viene letto da `/api/series/pun/monthly`, che calcola la media mensile direttamente dalle osservazioni giornaliere nel database; in questo modo il job aggiorna una sola serie giornaliera e le viste aggregate restano coerenti automaticamente

## Render Pre-Produzione

- static site: `dashboard-aeif-preproduzione` gia esistente, fuori dal Blueprint
- API: `dashboard-aeif-api-preprod`
- database: `dashboard-aeif-db-preprod`
- cron PUN: `dashboard-aeif-pun-scraper-preprod`
- branch collegato: `preprod`

## Regole operative

1. Le modifiche in lavorazione si preparano su `preprod`.
2. Render pre-produzione pubblica automaticamente `preprod`.
3. Quando pre-produzione e' approvata, si apre una PR da `preprod` verso `main`.
4. Render produzione pubblica automaticamente `main`.

## File Principali

- `index.html`: home
- `assets/`: asset pubblici e caricatore API
- `dossiers/`: PDF scaricabili
- `backend/`: API, database e job di aggiornamento dati
- `OPERATIONS.md`: regole operative, ambienti e servizi Render
- `RELEASE_CHECKLIST.md`: controlli da fare prima e dopo un rilascio
