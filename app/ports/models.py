from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

@dataclass
class NewsListingUrl:
    id: int
    url: str
    added_at: datetime

@dataclass
class ArticleLinkDb:
    id: int
    url: str
    added_at: datetime
    visited: bool
    summary: Optional[str] = None
    tags: Optional[List[str]] = None
    visited_at: Optional[datetime] = None

@dataclass
class ScrapeResult:
    url: str
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None

@dataclass
class ArticleLinkExtractionInput:
    markdown: str
    # Altri parametri opzionali se necessario

class ArticleLinkLLM(BaseModel):
    link: str
    text_value: Optional[str] = None

class ArticleLinkExtractionOutput(BaseModel):
    links: List[ArticleLinkLLM]

class SummarizePageInput(BaseModel):
    page_representation: str

class SummarizePageOutput(BaseModel):
    summary_markdown: str

@dataclass
class ListingToArticles:
    listing_url: str
    markdown: str
    article_links: List[str]

@dataclass
class NewArticleLink:
    listing_url: str
    url: str
    added_at: datetime

@dataclass
class ArticleSummary:
    url: str
    summary: str
