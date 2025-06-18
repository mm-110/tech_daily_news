from typing import List
from app.ports.dbhandler import DBHandlerPort
from app.ports.models import NewArticleLink, ArticleSummary
from datetime import datetime

def update_db_with_summaries(
    db: DBHandlerPort,
    new_articles: List[NewArticleLink],
    summaries: List[ArticleSummary],
) -> List[ArticleSummary]:
    """
    Aggiorna il db con il riassunto di ogni articolo. Se il riassunto è vuoto, rimuove l'articolo dal db.
    Ritorna la lista di articoli validi (con riassunto).
    """
    valid_articles = []
    for art, summary in zip(new_articles, summaries):
        if summary.summary:
            db.mark_article_as_visited(art.url, summary=summary.summary)
            valid_articles.append(summary)
        else:
            # Rimuovi l'articolo dal db se il riassunto fallisce
            # (implementa remove_article_link se non esiste)
            if hasattr(db, 'remove_article_link'):
                db.remove_article_link(art.url)
    return valid_articles


def generate_newsletter_markdown(
    article_summaries: List[ArticleSummary],
    filename: str = None
) -> str:
    """
    Genera e salva una newsletter in formato markdown a partire da una lista di ArticleSummary.
    Ritorna il nome del file creato.
    """
    from datetime import datetime
    newsletter_title = "# Tech Daily News\n"
    newsletter_date = f"{datetime.now().isoformat()}\n"
    newsletter_parts = [newsletter_title, newsletter_date, "\n---\n"]
    for idx, art in enumerate(article_summaries):
        newsletter_parts.append(f"{art.summary}")
        if idx < len(article_summaries) - 1:
            newsletter_parts.append("\n---\n")
    newsletter_md = "".join(newsletter_parts)
    if not filename:
        filename = f"newsletter_{datetime.now().strftime('%Y%m%dT%H%M%S')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(newsletter_md)
    return filename