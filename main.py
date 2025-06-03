from src.dom_processor import fetch_html, get_links, extract_main_text
from src.llm import LLM
from src.models import PageRepresentation
from src.newsletter_utils import save_newsletter_markdown


def main():
    url = "https://news.ycombinator.com"
    html_content = fetch_html(url)
    llm = LLM()

    if not html_content:
        print("Failed to fetch HTML content.")
        return

    print("HTML content fetched successfully.")

    # Estrai tutti i link assoluti con testo non vuoto
    absolute_links = [
        link for link in get_links(html_content, "absolute") if link.text_value
    ]

    # Filtra i link pertinenti ai topic desiderati tramite LLM
    filtered_links = llm.filter_links_by_topics(
        absolute_links, ["AI", "Python", "Markdown"]
    )

    print("Filtered Links:")
    for link in filtered_links.links:
        print(f"Link: {link.link}, Text: {link.text_value}")

    # Per ogni link filtrato, recupera l'html, estrai il testo principale e genera il riassunto
    page_contents = []
    for link in filtered_links.links:
        page_html = fetch_html(link.link)
        if not page_html:
            continue
        page_repr = extract_main_text(page_html)
        page_rep_obj = PageRepresentation(
            link=link.link, title=link.text_value, page_representation=page_repr
        )
        page_content = llm.summarize_page(page_rep_obj)
        page_contents.append(page_content)

    # Salva la newsletter in markdown tramite funzione dedicata
    if page_contents:
        try:
            filename = save_newsletter_markdown(page_contents)
            print(f"Newsletter salvata in {filename}")
        except Exception as e:
            print(f"Errore durante il salvataggio della newsletter: {e}")
    else:
        print("Nessun contenuto da inserire nella newsletter.")


if __name__ == "__main__":
    main()
