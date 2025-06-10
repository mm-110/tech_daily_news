from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from dataclasses import dataclass


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


class SelectorType(Enum):
    CSS = "css"
    XPATH = "xpath"


class ContainerFinderResult(Enum):
    SUCCESS = "success"
    LEAF_NODE_FOUND = "leaf_node_found"
    SELECTOR_NOT_FOUND = "selector_not_found"
    INVALID_SELECTOR = "invalid_selector"
    DEPTH_LIMIT_REACHED = "depth_limit_reached"


class BoundingBox(BaseModel):
    tag: str  # L'intero tag HTML del bounding box (incluso markup)
    css_selector: str  # selettore CSS full path
    xpath: str  # selettore XPath
    x: int  # coordinata X assoluta
    y: int  # coordinata Y assoluta
    width: int
    height: int
    num_children: int  # numero di figli diretti

    def area(self) -> int:
        """Calcola l'area del bounding box."""
        return self.width * self.height


@dataclass
class ContainerSearchResult:
    result_type: ContainerFinderResult
    container: Optional[BoundingBox]
    search_path: List[BoundingBox]
    message: str
    depth: int


# --- Tool Input/Output Schemas ---


class NavigateToUrlInput(BaseModel):
    url: str


class NavigateToUrlOutput(BaseModel):
    message: str


class OpenBrowserSessionOutput(BaseModel):
    message: str


class CloseBrowserSessionOutput(BaseModel):
    message: str


class GetPageHTML(BaseModel):
    content: str


class GetStructuredPageContentOutput(BaseModel):
    structured_content: str


class GetLinksFromPageOutput(BaseModel):
    links: List[str]


class GetBoundingBoxesInput(BaseModel):
    selector: str = "body"  # selettore di partenza (default: body)


class GetBoundingBoxesOutput(BaseModel):
    bounding_boxes: List[BoundingBox]


class HighlightBoundingBoxInput(BaseModel):
    selector: str
    color: str = None  # colore opzionale (default: random)


class HighlightBoundingBoxOutput(BaseModel):
    message: str


class ScrollDirection(str, Enum):
    UP = "UP"
    DOWN = "DOWN"


class ScrollPageInput(BaseModel):
    direction: ScrollDirection


class ScrollPageOutput(BaseModel):
    message: str


class ScreenshotElementInput(BaseModel):
    selector: str  # selettore CSS dell'elemento
    path: str  # percorso file dove salvare lo screenshot
    output_format: str


class ScreenshotElementOutput(BaseModel):
    message: str
    image_path: str = None


class PageInfoInput(BaseModel):
    page_type: str  # es: HOMEPAGE, LISTING PAGE, PRODUCT PAGE, CONTENT PAGE
    url: str


class PageInfoOutput(BaseModel):
    page_type: str
    url: str
    width: int
    height: int

    def area(self) -> int:
        return self.width * self.height
