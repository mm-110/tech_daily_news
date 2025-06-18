from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from app.ports.models import NewsListingUrl, ArticleLinkDb

class DBHandlerPort(ABC):
    """
    Porta astratta per la gestione del database.
    Espone operazioni CRUD per le tabelle news_listing_urls e article_links.
    """

    # --- News Listing URLs ---

    @abstractmethod
    def add_news_listing_url(self, url: str) -> NewsListingUrl:
        """Aggiunge un nuovo URL di listing."""
        pass

    @abstractmethod
    def get_all_news_listing_urls(self) -> List[NewsListingUrl]:
        """Recupera tutti gli URL di listing."""
        pass

    # --- Article Links ---

    @abstractmethod
    def add_article_link(self, url: str, added_at: Optional[datetime] = None) -> ArticleLinkDb:
        """Aggiunge un nuovo link articolo."""
        pass

    @abstractmethod
    def get_article_link_by_url(self, url: str) -> Optional[ArticleLinkDb]:
        """Recupera un articolo tramite URL."""
        pass

    @abstractmethod
    def get_all_article_links(self, visited: Optional[bool] = None) -> List[ArticleLinkDb]:
        """Recupera tutti i link articoli, opzionalmente filtrando per visitato."""
        pass

    @abstractmethod
    def mark_article_as_visited(self, url: str, summary: Optional[str] = None, tags: Optional[List[str]] = None) -> None:
        """Segna un articolo come visitato, opzionalmente aggiornando riassunto e tag."""
        pass
