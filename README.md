# Grafici-Energia

Dashboard statica con grafici interattivi su mercati elettrici, ETS, industria, Innovation Fund e confronti internazionali.

## Link

Produzione Render:

https://dashboard-aeif.onrender.com/

Pre-produzione Render:

https://dashboard-aeif-preprod.onrender.com/

## Render

Questo branch contiene `render.yaml` per creare il servizio Render Static Site di pre-produzione.

Configurazione prevista:

- servizio: `dashboard-aeif-preprod`
- build command: `echo "Static site ready"`
- publish directory: `.`
- deploy automatico a ogni modifica del branch collegato
- branch collegato: `preprod`

Backend pre-produzione:

- API: `dashboard-aeif-api-preprod`
- database: `dashboard-aeif-db-preprod`
- cron PUN: `dashboard-aeif-pun-scraper-preprod`
- sorgente PUN: variabile ambiente `PUN_SOURCE_URL`

Per attivarlo su Render:

1. Apri Render.
2. Scegli New > Blueprint.
3. Collega il repository `johnbonham1/Grafici-Energia`.
4. Usa `render.yaml` come configurazione.
5. Avvia il deploy.

Il servizio di produzione resta collegato al branch `main`.

## Struttura

La root del branch `preprod` contiene la versione di pre-produzione.

## Regole operative

1. Le modifiche in lavorazione si preparano sul branch `preprod`.
2. Render pre-produzione pubblica automaticamente il branch `preprod`.
3. Quando pre-produzione e approvata, si apre una PR da `preprod` verso `main`.
4. Render produzione pubblica automaticamente il branch `main`.

## File principali

- `index.html`: home
- `dossiers/`: PDF scaricabili
- `assets/`: asset pubblici
- `backend/`: API, database e job di aggiornamento dati
