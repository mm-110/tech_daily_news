from typing import List, Optional
from datetime import datetime
from app.ports.dbhandler import DBHandlerPort
from app.ports.models import NewsListingUrl, ArticleLinkDb

class MockDBHandler(DBHandlerPort):
    """
    Implementazione mockata di DBHandlerPort per test e sviluppo senza database reale.
    """
    def __init__(self):
        self._news_listing_urls = []
        self._article_links = []
        self._news_listing_id = 1
        self._article_link_id = 1

    def add_news_listing_url(self, url: str) -> NewsListingUrl:
        obj = NewsListingUrl(id=self._news_listing_id, url=url, added_at=datetime.utcnow())
        self._news_listing_urls.append(obj)
        self._news_listing_id += 1
        return obj

    def get_all_news_listing_urls(self) -> List[NewsListingUrl]:
        return list(self._news_listing_urls)

    def add_article_link(self, url: str, added_at: Optional[datetime] = None) -> ArticleLinkDb:
        if self.get_article_link_by_url(url):
            raise ValueError("Article link already exists")
        obj = ArticleLinkDb(
            id=self._article_link_id,
            url=url,
            added_at=added_at or datetime.utcnow(),
            visited=False,
            summary=None,
            tags=None,
            visited_at=None
        )
        self._article_links.append(obj)
        self._article_link_id += 1
        return obj

    def get_article_link_by_url(self, url: str) -> Optional[ArticleLinkDb]:
        for link in self._article_links:
            if link.url == url:
                return link
        return None

    def get_all_article_links(self, visited: Optional[bool] = None) -> List[ArticleLinkDb]:
        if visited is None:
            return list(self._article_links)
        return [a for a in self._article_links if a.visited == visited]

    def mark_article_as_visited(self, url: str, summary: Optional[str] = None, tags: Optional[List[str]] = None) -> None:
        link = self.get_article_link_by_url(url)
        if not link:
            raise ValueError("Article link not found")
        link.visited = True
        link.visited_at = datetime.utcnow()
        if summary:
            link.summary = summary
        if tags:
            link.tags = tags
