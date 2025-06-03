# Tech Daily News

Tech Daily News è uno script Python che recupera, filtra e riassume automaticamente le principali notizie tech dal web, generando una newsletter in formato markdown.

## Requisiti
- Python >= 3.11
- [uv](https://github.com/astral-sh/uv) (per la gestione rapida degli ambienti e delle dipendenze)

## Installazione

1. **Clona il repository**

```sh
git clone <URL_DEL_REPO>
cd tech-daily-news
```

2. **Installa le dipendenze**

```sh
uv pip install -r pyproject.toml
```

## Configurazione

- Assicurati di avere accesso a internet per il recupero delle pagine e l'utilizzo degli LLM.
- Per utilizzare modelli OpenAI o Ollama, configura le relative API key/endpoint se necessario (vedi documentazione LangChain/OpenAI/Ollama).

## Utilizzo

Per avviare la generazione della newsletter:

```sh
python main.py
```

Al termine, troverai un file markdown (`newsletter_YYYYMMDDTHHMMSS.md`) con la newsletter generata nella cartella principale del progetto.

## Struttura del progetto

- `main.py` — Script principale: esegue il flusso di scraping, filtraggio, riassunto e generazione newsletter.
- `src/dom_processor.py` — Funzioni per il parsing HTML e l'estrazione dei contenuti.
- `src/llm.py` — Integrazione con LLM (OpenAI/Ollama) per filtraggio e riassunti.
- `src/models.py` — Modelli dati (Link, PageRepresentation, PageContent, ecc.).
- `src/newsletter_utils.py` — Funzione per la generazione e il salvataggio della newsletter in markdown.
- `src/prompts.py` — Prompt utilizzati per l'interazione con gli LLM.

## TODO

- Integrazione di Selenium o altri browser automator per evitare blocchi da parte di alcuni siti.
- Generalizzare il recupero delle informazioni da altri siti, non solo news.ycombinator.com.
- Parametrizzare gli URL da cui si vuole ricevere la newsletter (tramite file di configurazione o argomenti da linea di comando).
- Parametrizzare i topic di interesse per la selezione dei contenuti (tramite file di configurazione o argomenti da linea di comando).

## Note
- Il progetto utilizza un fake user agent per evitare blocchi durante lo scraping.
- Puoi personalizzare i topic di interesse modificando la lista in `main.py`.
- Per performance migliori, puoi filtrare i link anche per dominio o pattern specifici.

## Licenza
MIT
