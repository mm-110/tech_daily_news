from datetime import datetime
from typing import List
from src.models import PageContent

def save_newsletter_markdown(page_contents: List[PageContent], filename: str = None) -> str:
    """
    Genera e salva una newsletter in formato markdown a partire da una lista di PageContent.
    Ritorna il nome del file creato.
    """
    newsletter_title = "# Tech Daily News\n"
    newsletter_date = f"{datetime.now().isoformat()}\n"
    newsletter_parts = [newsletter_title, newsletter_date]
    newsletter_parts.append("\n---\n")
    for idx, content in enumerate(page_contents):
        newsletter_parts.append(f"[Link originale]({content.link})\n\n{content.content}")
        if idx < len(page_contents) - 1:
            newsletter_parts.append("\n---\n")
    newsletter_md = "".join(newsletter_parts)
    if not filename:
        filename = f"newsletter_{datetime.now().strftime('%Y%m%dT%H%M%S')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(newsletter_md)
    return filename
