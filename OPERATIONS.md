# Operativita Dashboard AEIF

Questo documento tiene allineati ambienti, servizi e regole operative della dashboard.

## Link principali

| Ambiente | Link pubblico | Branch |
| --- | --- | --- |
| Produzione | https://dashboard-aeif.onrender.com/ | `main` |
| Pre-produzione | https://dashboard-aeif-preproduzione.onrender.com/ | `preprod` |
| GitHub Pages | https://johnbonham1.github.io/Grafici-Energia/ | `main` |

## Servizi Render attivi

### Produzione

| Componente | Servizio |
| --- | --- |
| Static site | `Dashboard AEIF` |
| API | `dashboard-aeif-api-f497` |
| Cron PUN | `dashboard-aeif-pun-scraper-f497` |
| Database | configurato manualmente tramite `DATABASE_URL` |

### Pre-produzione

| Componente | Servizio |
| --- | --- |
| Static site | `Dashboard AEIF preproduzione` |
| API | `dashboard-aeif-api-preprod` |
| Cron PUN | `dashboard-aeif-pun-scraper-preprod` |
| Database | `dashboard-aeif-db-preprod` |

## Regole operative

1. Le modifiche si preparano su `preprod`.
2. Si verifica tutto sul link di pre-produzione.
3. Quando la pre-produzione e' approvata, si porta la modifica su `main`.
4. La produzione Render e GitHub Pages pubblicano da `main`.
5. I servizi Render duplicati sospesi non vanno riattivati senza una verifica esplicita.

## Collegamento dati

Il frontend non contiene piu' i dati dei grafici. Ogni pagina carica il proprio payload tramite `assets/api-loader.js`.

Mapping attuale:

| Host frontend | API usata |
| --- | --- |
| `dashboard-aeif.onrender.com` | `https://dashboard-aeif-api-f497.onrender.com` |
| `johnbonham1.github.io` | `https://dashboard-aeif-api-f497.onrender.com` |
| `dashboard-aeif-preproduzione.onrender.com` | `https://dashboard-aeif-api-preprod.onrender.com` |

Se l'API non risponde, la pagina mostra il messaggio: `Dati temporaneamente non disponibili. Riprova tra poco.`

## Note Render

- Il Blueprint gestisce backend e cron.
- Gli static site Render sono gia' esistenti e restano fuori dal Blueprint.
- In produzione il database e' collegato con variabile manuale `DATABASE_URL`.
- Sul piano free Render puo' esserci un solo database Postgres attivo per account.

