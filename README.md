# Tech Daily News

## Obiettivo

Sistema automatico per la generazione di una newsletter tech giornaliera. Il sistema raccoglie notizie da fonti configurabili, estrae i link agli articoli, ne effettua lo scraping, genera un riassunto per ciascun articolo tramite LLM e produce una newsletter in formato markdown, che viene inviata via email (mock).

## Flusso Funzionale

1. **Input URL di listing**: L’utente fornisce una lista di URL di pagine listing/news, salvati su database.
2. **Raccolta periodica**: Un job recupera gli URL di listing e per ciascuno effettua scraping, collezionando i link agli articoli.
3. **Gestione link articoli**: I link raccolti vengono confrontati con quelli già presenti; solo i nuovi vengono aggiunti.
4. **Estrazione e sintesi contenuti**: Per ogni nuovo link, il sistema visita la pagina, estrae il contenuto, lo riassume tramite LLM e salva il riassunto.
5. **Generazione newsletter**: Tutti i riassunti vengono impacchettati in un file markdown e inviati via email (mockata).

## Setup & Esecuzione

1. **Clona il repository**
2. **Crea un ambiente virtuale**
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. **Installa le dipendenze**
   ```sh
   pip install -r requirements.txt
   ```
4. **Esegui la pipeline**
   ```sh
   python main_app.py
   ```
   Al termine, troverai la newsletter generata in formato markdown e un link per visualizzarla in HTML nel terminale.

## Struttura Principale

- `app/ports/` — interfacce astratte (DB, LLM, Scraper, Email, ...)
- `app/adapters/` — adapter concreti (mock DB, crawl4ai, langchain, mock email, ...)
- `app/domain/` — logica di dominio e orchestrazione pipeline
- `main_app.py` — entrypoint orchestratore
- `app/domain/newsletter_utils.py` — generazione e salvataggio newsletter

## TODO
- Endpoint FastAPI per input URL e gestione pipeline
- Adapter reale per PostgreSQL e invio email SMTP
- Scheduler periodico (Celery/APScheduler)
- Test automatici su porte e adapter
- Migliorare la qualità dei riassunti generati
- Aggiunta di tag tematici per ogni articolo
- Strategie di pulizia e normalizzazione dell'HTML estratto
- Generazione di un template HTML per lo stile della newsletter
- Containerizzazione del progetto (Docker)

---
