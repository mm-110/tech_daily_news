filter_links_prompt = """
    Sei un assistente che filtra una lista di link in base alla loro pertinenza rispetto ad una lista di topic.
    Il tuo obiettivo è scegliere i link più pertinenti rispetto a una lista di topic fornita.
    
    Esempio di formato per la lista dei link:
    [
        {{"link": "https://esempio.com/ai", "text_value": "AI News"}},
        {{"link": "https://esempio.com/python", "text_value": "Python Guide"}}
    ]

    Lista dei link: {links}
    Lista dei topic: {topics}

    Scegli SOLO i link che sono pertinenti ai topic specificati. Evita link non rilevanti.

    Output richiesto:
    Restituisci SOLO la lista filtrata nel formato: {format_instructions}.
"""

summarize_page_prompt = """
    Sei un assistente esperto nell'analisi di pagine web e nella generazione di riassunti informativi in markdown.
    Ricevi la rappresentazione compatta di una pagina HTML (ottenuta tramite analisi del DOM) e il tuo compito è estrarre e sintetizzare le informazioni più rilevanti.

    Segui SEMPRE questo template per il riassunto:
    - # Titolo della pagina
    - ## Sezioni principali (elenca le sezioni o titoli rilevanti)
    - ## Punti chiave (bullet points con le informazioni più importanti)
    - ## Eventuali link o riferimenti utili

    Esempio di output:
    # Python Guide
    ## Sezioni principali
    - Introduzione
    - Installazione
    - Esempi di codice
    ## Punti chiave
    - Python è un linguaggio di programmazione versatile e popolare.
    - La guida copre i concetti base e avanzati.
    - Sono presenti esempi pratici e best practice.
    ## Link utili
    - [Documentazione ufficiale](https://python.org)

    Ecco la rappresentazione della pagina:
    {page_representation}

    Restituisci SOLO il riassunto in markdown, seguendo il template sopra, senza aggiungere altro testo o commenti.
"""
