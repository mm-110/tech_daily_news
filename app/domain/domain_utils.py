import asyncio
import datetime
from app.ports.scraper import ScraperPort
from app.ports.llm import LLMPort
from typing import List, Dict
from app.ports.models import (
    ScrapeResult,
    ArticleLinkExtractionInput,
    ListingToArticles,
    NewArticleLink,
    SummarizePageInput,
    SummarizePageOutput,
)


async def scrape_and_save_markdown(
    urls: List[str], scraper: ScraperPort, output_path: str
):
    """
    Esegue scraping asincrono di una lista di URL e salva i risultati in un file markdown.
    """
    tasks = [asyncio.create_task(scraper.fetch_pages_content([url])) for url in urls]
    all_results = await asyncio.gather(*tasks)
    # all_results è una lista di liste (ogni task restituisce una lista di ScrapeResult)
    with open(output_path, "w", encoding="utf-8") as f:
        for results in all_results:
            for res in results:
                f.write(f"# {res.url}\n\n")
                if res.success and res.content:
                    f.write(res.content + "\n\n")
                else:
                    f.write(f"**Errore:** {res.error}\n\n")


async def scrape_and_return_markdown(
    urls: List[str], scraper: ScraperPort
) -> List[ScrapeResult]:
    """
    Esegue scraping asincrono di una lista di URL e restituisce i risultati come lista di ScrapeResult.
    """
    tasks = [asyncio.create_task(scraper.fetch_pages_content([url])) for url in urls]
    all_results = await asyncio.gather(*tasks)
    # Appiattisce la lista di liste
    return [res for results in all_results for res in results]


async def extract_significant_links_from_markdown(
    markdown_list: List[str], llm: LLMPort
) -> List[str]:
    """
    Usa l'LLM per estrarre i link significativi da una lista di markdown.
    """
    links = []
    for markdown in markdown_list:
        result = llm.extract_article_links(
            ArticleLinkExtractionInput(markdown=markdown)
        )
        links.extend([l.link for l in result.links])
    return links


async def pipeline_listing_to_articles(
    listing_urls: List[str], scraper: ScraperPort, llm: LLMPort
) -> List[ListingToArticles]:
    """
    Esegue scraping dei listing, estrae i markdown e i link articoli per ciascun listing.
    Ritorna una lista di oggetti che associano ogni listing ai suoi articoli estratti.
    """
    # Scraping asincrono dei listing
    tasks = [
        asyncio.create_task(scraper.fetch_pages_content([url])) for url in listing_urls
    ]
    all_results = await asyncio.gather(*tasks)
    # all_results: List[List[ScrapeResult]]
    results_flat = [res for results in all_results for res in results]
    output: List[ListingToArticles] = []
    for res in results_flat:
        if res.success and res.content:
            article_links = [
                l.link
                for l in llm.extract_article_links(
                    ArticleLinkExtractionInput(markdown=res.content)
                ).links
            ]
            output.append(
                ListingToArticles(
                    listing_url=res.url,
                    markdown=res.content,
                    article_links=article_links,
                )
            )
        else:
            output.append(
                ListingToArticles(
                    listing_url=res.url, markdown=res.content or "", article_links=[]
                )
            )
    return output


async def filter_and_save_new_articles(
    db, listing_to_articles: List[ListingToArticles]
) -> List[NewArticleLink]:
    """
    Filtra i link articoli già presenti nel DB e salva solo i nuovi, associandoli al listing di provenienza.
    Ritorna la lista dei nuovi articoli inseriti.
    """
    new_articles: List[NewArticleLink] = []
    for item in listing_to_articles:
        for article_url in item.article_links:
            # Verifica se già presente
            if not db.get_article_link_by_url(article_url):
                new_article = NewArticleLink(
                    listing_url=item.listing_url,
                    url=article_url,
                    added_at=datetime.datetime.utcnow(),
                )
                db.add_article_link(article_url, added_at=new_article.added_at)
                new_articles.append(new_article)
    return new_articles


async def scrape_articles_content(
    article_links: List[NewArticleLink], scraper: ScraperPort
) -> List[ScrapeResult]:
    """
    Esegue scraping asincrono dei link articoli filtrati e ritorna i risultati.
    """
    urls = [a.url for a in article_links]
    tasks = [asyncio.create_task(scraper.fetch_pages_content([url])) for url in urls]
    all_results = await asyncio.gather(*tasks)
    return [res for results in all_results for res in results]


class ArticleSummary:
    def __init__(self, url: str, summary: str):
        self.url = url
        self.summary = summary


async def pipeline_scrape_and_summarize_articles(
    article_links: List[NewArticleLink],
    scraper: ScraperPort,
    llm: LLMPort,
    max_parallel: int = 3
) -> List[ArticleSummary]:
    """
    Scrapa il contenuto di ogni articolo e genera riassunto tramite LLM, con semaforo per il parallelismo.
    """
    urls = [a.url for a in article_links]
    # Scraping asincrono dei contenuti
    tasks = [asyncio.create_task(scraper.fetch_pages_content([url])) for url in urls]
    all_results = await asyncio.gather(*tasks)
    scrape_results: List[ScrapeResult] = [res for results in all_results for res in results]
    output: List[ArticleSummary] = []
    semaphore = asyncio.Semaphore(max_parallel)

    async def summarize_with_semaphore(res: ScrapeResult) -> ArticleSummary:
        async with semaphore:
            if res.success and res.content:
                summary_obj: SummarizePageOutput = llm.summarize_page(SummarizePageInput(page_representation=res.content))
                return ArticleSummary(url=res.url, summary=summary_obj.summary_markdown)
            else:
                return ArticleSummary(url=res.url, summary="")

    summary_tasks = [asyncio.create_task(summarize_with_semaphore(res)) for res in scrape_results]
    output = await asyncio.gather(*summary_tasks)
    return output
