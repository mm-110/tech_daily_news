from typing import List
from crawl4ai import (
    AsyncWebCrawler,
    CrawlerRunConfig,
    DefaultMarkdownGenerator,
    PruningContentFilter,
    CrawlResult,
)
from app.ports.scraper import ScraperPort
from app.ports.models import ScrapeResult


class Crawl4AIScraperAdapter(ScraperPort):
    """
    Adapter concreto che usa crawl4ai per eseguire scraping parallelo di più URL.
    """

    async def fetch_pages_content(self, urls: List[str]) -> List[ScrapeResult]:
        results: List[ScrapeResult] = []
        async with AsyncWebCrawler() as crawler:
            crawl_results: List[CrawlResult] = await crawler.arun_many(
                urls=urls,
                config=CrawlerRunConfig(
                    markdown_generator=DefaultMarkdownGenerator(
                        content_filter=PruningContentFilter()
                    )
                ),
            )
            for result in crawl_results:
                results.append(
                    ScrapeResult(
                        url=result.url,
                        success=result.success,
                        content=(
                            result.markdown.fit_markdown if result.success else None
                        ),
                        error=result.error if not result.success else None,
                    )
                )
        return results
