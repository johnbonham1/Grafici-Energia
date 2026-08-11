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
- sorgente PUN: PUN Index GME ufficiale; `PUN_SOURCE_URL` resta solo come fallback CSV manuale
- frequenza cron: ogni giorno alle 11:30 UTC
- logica aggiornamento PUN: il job legge l'ultima data `pun` presente nel database e importa solo le date mancanti fino al giorno successivo a oggi, includendo il dato day-ahead pubblicato dal GME
- il Blueprint Render gestisce solo backend, database e cron; gli static site restano servizi separati gia esistenti
- seed iniziale: il backend importa nel DB i dati gia presenti nel frontend
- verifica dati: `/api/payloads`, `/api/payloads/daily_prices`, `/api/series/pun`, `/api/pun/status`
- pagina prezzi: il grafico PUN/TTF usa il payload storico per il TTF e sovrascrive/estende la serie PUN con i valori live letti dal database tramite API
- pagina mercato energetico: il PUN mensile viene letto da `/api/series/pun/monthly`, che calcola la media mensile direttamente dalle osservazioni giornaliere nel database; in questo modo il job aggiorna una sola serie giornaliera e le viste aggregate restano coerenti automaticamente
- assistente dati: la pagina PUN/TTF include un box `Chiedi ai dati PUN` che interroga `/api/ask-data`; i calcoli sono sempre eseguiti dal backend sul database, mentre OpenAI serve solo, se configurato, per interpretare domande meno standard

Per attivarlo su Render:

1. Apri Render.
2. Scegli New > Blueprint.
3. Collega il repository `johnbonham1/Grafici-Energia`.
4. Usa `render.yaml` come configurazione.
5. Avvia il deploy.

Variabili opzionali per l'assistente dati:

- `OPENAI_API_KEY`: chiave API OpenAI da inserire solo nel servizio API pre-produzione `dashboard-aeif-api-preprod`
- `OPENAI_MODEL`: default `gpt-4.1-nano`

Senza `OPENAI_API_KEY`, l'assistente resta comunque attivo per domande standard come media, minimo, massimo, ultimo valore e confronto con anno precedente. Nessun modello AI calcola direttamente i valori numerici.

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
