# Grafici-Energia

Dashboard statica con grafici interattivi su mercati elettrici, ETS, industria, Innovation Fund e confronti internazionali.

## Link

Produzione:

https://johnbonham1.github.io/Grafici-Energia/

Pre-produzione:

https://johnbonham1.github.io/Grafici-Energia/staging/

## Struttura

La root del repository contiene la versione pubblica di produzione.

La cartella `staging/` contiene una copia navigabile del sito usata per verificare le modifiche prima della pubblicazione.

## Regole operative

1. Le modifiche in lavorazione si preparano dentro `staging/`.
2. Il link pubblico in root non si modifica finche la versione staging non e approvata.
3. Quando staging e approvato, i file da `staging/` vengono copiati nella root e pubblicati in produzione.
4. I branch temporanei `agent/...` servono solo per singole PR e possono essere eliminati dopo il merge.

## File principali

- `index.html`: home di produzione
- `staging/index.html`: home di pre-produzione
- `dossiers/`: PDF scaricabili in produzione
- `staging/dossiers/`: PDF scaricabili in pre-produzione
- `assets/`: asset pubblici di produzione
- `staging/assets/`: asset pubblici di pre-produzione
