from pydantic import BaseModel
from typing import List


class Link(BaseModel):
    link: str
    text_value: str


class LinkList(BaseModel):
    links: List[Link]


class PageContent(BaseModel):
    """Model representing the content of a page."""
    link: str
    title: str
    content: str


class PageRepresentation(BaseModel):
    """Model representing the representation of a page, including its title and link."""
    link: str
    title: str
    page_representation: str
