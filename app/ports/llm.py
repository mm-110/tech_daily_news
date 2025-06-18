from abc import ABC, abstractmethod
from typing import List
from app.ports.models import ArticleLinkExtractionInput, ArticleLinkExtractionOutput, SummarizePageInput, SummarizePageOutput

class LLMPort(ABC):
    """
    Porta astratta per interazione con LLM: estrazione link articoli e sintesi pagina.
    """
    @abstractmethod
    def extract_article_links(self, data: ArticleLinkExtractionInput) -> ArticleLinkExtractionOutput:
        """
        Estrae i link agli articoli da una rappresentazione markdown/listing.
        """
        pass

    @abstractmethod
    def summarize_page(self, data: SummarizePageInput) -> SummarizePageOutput:
        """
        Riassume una pagina in markdown e genera tag tematici.
        """
        pass
