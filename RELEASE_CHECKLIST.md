# Checklist rilascio

Usare questa lista prima di portare una modifica da pre-produzione a produzione.

## 1. Verifica pre-produzione

- [ ] Home pre-produzione aperta correttamente: https://dashboard-aeif-preproduzione.onrender.com/
- [ ] Scheda mercati elettrici mensili caricata.
- [ ] Scheda prezzi giornalieri PUN/TTF caricata.
- [ ] Scheda EU ETS emissioni/CAGR caricata.
- [ ] Scheda EU ETS industria/PIL caricata.
- [ ] Scheda Innovation Fund caricata.
- [ ] Scheda confronto internazionale caricata.
- [ ] Nessuna pagina mostra `Dati temporaneamente non disponibili`.

## 2. Verifica API

- [ ] API pre-produzione `/health` risponde `status: ok`.
- [ ] API produzione `/health` risponde `status: ok`.
- [ ] Payload principali disponibili:
  - [ ] `daily_prices`
  - [ ] `energy_monthly`
  - [ ] `ets`
  - [ ] `innovation_fund`
  - [ ] `international_comparison`

## 3. Promozione

- [ ] Modifica approvata su pre-produzione.
- [ ] PR da `preprod` verso `main` creata.
- [ ] PR mergiata su `main`.
- [ ] Render produzione completato.
- [ ] GitHub Pages completato.

## 4. Verifica produzione

- [ ] Home produzione aperta correttamente: https://dashboard-aeif.onrender.com/
- [ ] GitHub Pages aperta correttamente: https://johnbonham1.github.io/Grafici-Energia/
- [ ] Le pagine produzione puntano a `dashboard-aeif-api-f497`.
- [ ] Nessuna pagina mostra `Dati temporaneamente non disponibili`.

