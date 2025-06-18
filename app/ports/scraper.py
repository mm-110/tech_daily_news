from abc import ABC, abstractmethod
from typing import List
from .models import ScrapeResult

class ScraperPort(ABC):
    """
    Porta astratta per lo scraping di pagine web.
    """
    @abstractmethod
    async def fetch_pages_content(self, urls: List[str]) -> List[ScrapeResult]:
        """
        Esegue lo scraping di una lista di URL restituendo il contenuto di ciascuna pagina.
        """
        pass
