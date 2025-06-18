from app.ports.dbhandler import DBHandlerPort
from app.adapters.mock_dbhandler import MockDBHandler
from app.ports.scraper import ScraperPort
from app.adapters.crawl4ai_scraper import Crawl4AIScraperAdapter
from app.ports.llm import LLMPort
from app.adapters.langchain_llm_adapter import LangChainLLMAdapter
from app.domain.domain_utils import (
    pipeline_listing_to_articles,
    filter_and_save_new_articles,
    scrape_articles_content,
    pipeline_scrape_and_summarize_articles,
)
from app.domain.newsletter_utils import (
    update_db_with_summaries,
    generate_newsletter_markdown,
)
from app.ports.email_sender import EmailSenderPort
from app.adapters.mock_email_sender import MockEmailSender
import asyncio

# Dependency inversion: usiamo solo la porta nel codice applicativo


def main():
    db: DBHandlerPort = MockDBHandler()
    scraper: ScraperPort = Crawl4AIScraperAdapter()
    llm: LLMPort = LangChainLLMAdapter()
    email_sender: EmailSenderPort = MockEmailSender()

    db.add_news_listing_url("https://github.com/trending/python?since=daily")
    db.add_news_listing_url("https://news.ycombinator.com")

    listing_urls = [item.url for item in db.get_all_news_listing_urls()]

    results = asyncio.run(pipeline_listing_to_articles(listing_urls, scraper, llm))
    new_articles = asyncio.run(filter_and_save_new_articles(db, results))
    for art in new_articles:
        print(
            f"Nuovo articolo salvato: {art.url} (listing: {art.listing_url}, aggiunto: {art.added_at})"
        )

    # Pipeline: scraping + sintesi articoli con semaforo (max 3 in parallelo)
    if new_articles:
        summaries = asyncio.run(
            pipeline_scrape_and_summarize_articles(
                new_articles[:3], scraper, llm, max_parallel=3
            )
        )
        valid_summaries = update_db_with_summaries(db, new_articles, summaries)
        newsletter_file = generate_newsletter_markdown(valid_summaries)
        print(f"Newsletter generata: {newsletter_file}")
        # Invio newsletter via email (mock)
        email_sender.send_newsletter(
            to="destinatario@example.com",
            subject="Tech Daily News - Newsletter",
            markdown_path=newsletter_file,
        )


if __name__ == "__main__":
    main()
