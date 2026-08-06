# Grafici-Energia

Dashboard statica con grafici interattivi su mercati elettrici, ETS, industria, Innovation Fund e confronti internazionali.

## Link

Produzione Render:

https://dashboard-aeif.onrender.com/

Pre-produzione Render:

https://dashboard-aeif-preprod.onrender.com/

Backup GitHub Pages:

https://johnbonham1.github.io/Grafici-Energia/

## Ambienti

- `main`: produzione
- `preprod`: pre-produzione

Ogni ambiente viene pubblicato da un servizio Render Static Site separato.

## Render

Configurazione produzione:

- servizio: `dashboard-aeif`
- branch collegato: `main`
- build command: `echo "Static site ready"`
- publish directory: `.`

Configurazione pre-produzione:

- servizio: `dashboard-aeif-preprod`
- branch collegato: `preprod`
- build command: `echo "Static site ready"`
- publish directory: `.`

## Regole operative

1. Le modifiche in lavorazione si preparano sul branch `preprod`.
2. Render pre-produzione pubblica automaticamente il branch `preprod`.
3. Quando pre-produzione e approvata, si apre una PR da `preprod` verso `main`.
4. Render produzione pubblica automaticamente il branch `main`.

## File principali

- `index.html`: home
- `dossiers/`: PDF scaricabili
- `assets/`: asset pubblici
