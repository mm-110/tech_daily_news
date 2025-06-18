import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CrawlResult, DefaultMarkdownGenerator, PruningContentFilter
from src.llm import LLM

browser_conf = BrowserConfig(
    headless=False,
    use_managed_browser=True,
    use_persistent_context=True,
    user_data_dir="~/.crawl4ai/profile",
)

async def main():


    llm = LLM()

    async with AsyncWebCrawler() as crawler:
        result: CrawlResult = await crawler.arun(
            url = "https://news.ycombinator.com",
            config=CrawlerRunConfig(
                markdown_generator=DefaultMarkdownGenerator(
                    content_filter=PruningContentFilter()
                )
            ),
        )

        # Print stats and save the fit markdown
        # print(f"Raw: {len(result.markdown.raw_markdown)} chars")
        # print(f"Fit: {len(result.markdown.fit_markdown)} chars")

        markdown = result.markdown.fit_markdown
        # with open("python_wiki.md", "w", encoding="utf-8") as f:
        #     f.write(markdown)
        print("Starting link extraction...")
        links = llm.extract_article_links(markdown).links
        for link in links:
            print(f"Link: {link.link}, Text: {link.text_value}")

        # print(f"Extracted Links:")

if __name__ == "__main__":
    asyncio.run(main())