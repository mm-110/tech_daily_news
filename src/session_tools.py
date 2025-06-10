from src.playwright_scraper import PlaywrightBrowserSessionHandler
from src.dom_processor import get_links, get_body_representation
from src.models import (
    OpenBrowserSessionOutput,
    CloseBrowserSessionOutput,
    NavigateToUrlInput,
    NavigateToUrlOutput,
    GetPageHTML,
    GetStructuredPageContentOutput,
    GetLinksFromPageOutput,
    GetBoundingBoxesInput,
    GetBoundingBoxesOutput,
    BoundingBox,
    HighlightBoundingBoxInput,
    HighlightBoundingBoxOutput,
    ScrollDirection,
    ScrollPageInput,
    ScrollPageOutput,
    ScreenshotElementInput,
    ScreenshotElementOutput,
    PageInfoInput,
    PageInfoOutput,
)
from src.vlm import VLM, ModelType
from bs4 import BeautifulSoup
from typing import List
from pydantic import BaseModel

BROWSER_HANDLER = PlaywrightBrowserSessionHandler(headless=False)

# --- Tool Input/Output Schemas ---

# --- Tool Functions ---


def open_browser_session() -> OpenBrowserSessionOutput:
    """
    Apre una nuova sessione del browser Chrome tramite Selenium. Se una sessione è già attiva, restituisce un errore.
    Esempio output:
        OpenBrowserSessionOutput(message="Browser session opened successfully.")
    """
    try:
        BROWSER_HANDLER.open_session()
        return OpenBrowserSessionOutput(message="Browser session opened successfully.")
    except RuntimeError as e:
        return OpenBrowserSessionOutput(
            message=f"Error opening browser session: {str(e)}"
        )


def close_browser_session() -> CloseBrowserSessionOutput:
    """
    Chiude la sessione del browser attualmente aperta. Se non esiste una sessione attiva, restituisce un errore.
    Esempio output:
        CloseBrowserSessionOutput(message="Browser session closed successfully.")
    """
    try:
        BROWSER_HANDLER.close_session()
        return CloseBrowserSessionOutput(message="Browser session closed successfully.")
    except RuntimeError as e:
        return CloseBrowserSessionOutput(
            message=f"Error closing browser session: {str(e)}"
        )


def navigate_to_url(input_data: NavigateToUrlInput) -> NavigateToUrlOutput:
    """
    Naviga il browser verso l'URL specificato. È necessario che la sessione sia già aperta.
    Args (input_data):
        url (str): L'URL verso cui navigare, ad esempio "https://www.example.com"
    Esempio input:
        NavigateToUrlInput(url="https://www.example.com")
    Esempio output:
        NavigateToUrlOutput(message="Navigated to https://www.example.com successfully.")
    """
    try:
        BROWSER_HANDLER.navigate(input_data.url)
        return NavigateToUrlOutput(
            message=f"Navigated to {input_data.url} successfully."
        )
    except RuntimeError as e:
        return NavigateToUrlOutput(
            message=f"Error navigating to {input_data.url}: {str(e)}"
        )


def get_html() -> GetPageHTML:
    """
    Restituisce una rappresentazione strutturata e compatta del contenuto HTML della pagina corrente, utile per l'analisi o l'estrazione di informazioni.
    Esempio output:
        GetStructuredPageContentOutput(structured_content="body:\n-div: ...\n-a: https://...")
    """
    try:
        content = BROWSER_HANDLER.get_page_content()
        return GetPageHTML(content=content)
    except RuntimeError as e:
        return GetPageHTML(content="")


def get_structured_page_content() -> GetStructuredPageContentOutput:
    """
    Restituisce una rappresentazione strutturata e compatta del contenuto HTML della pagina corrente, utile per l'analisi o l'estrazione di informazioni.
    Esempio output:
        GetStructuredPageContentOutput(structured_content="body:\n-div: ...\n-a: https://...")
    """
    try:
        content = BROWSER_HANDLER.get_page_content()
        page = BeautifulSoup(content, "html.parser")
        # Rimuovi tutti i tag <style> e <script>
        for tag in page(["style", "script"]):
            tag.decompose()
        structured_content = get_body_representation(page.body)
        return GetStructuredPageContentOutput(structured_content=structured_content)
    except RuntimeError as e:
        return GetStructuredPageContentOutput(
            structured_content=f"Error getting page content: {str(e)}"
        )


def get_links_from_page() -> GetLinksFromPageOutput:
    """
    Estrae tutti i link assoluti (href che iniziano con http/https) dalla pagina attualmente caricata nel browser.
    Esempio output:
        GetLinksFromPageOutput(links=["https://www.example.com", "https://www.google.com"])
    """
    try:
        content = BROWSER_HANDLER.get_page_content()
        links = get_links(content, "absolute")
        return GetLinksFromPageOutput(links=links)
    except RuntimeError as e:
        return GetLinksFromPageOutput(links=[f"Error getting links: {str(e)}"])


def safe_class(val):
    if isinstance(val, str):
        return val
    if isinstance(val, dict):
        return val.get("baseVal", "")
    return ""


def get_bounding_boxes(input_data: GetBoundingBoxesInput) -> GetBoundingBoxesOutput:
    """
    Recupera tutti i bounding box visibili a partire da un selettore (default: body).
    Ritorna una lista di BoundingBox con solo il tag di apertura (es: <div class="...">) e il numero di figli.
    """
    try:
        results = BROWSER_HANDLER.get_bounding_boxes(input_data.selector)
        bounding_boxes = []
        for box in results:
            bounding_boxes.append(
                BoundingBox(
                    tag=box.get("tag", ""),
                    css_selector=box["css_selector"],
                    xpath=box["xpath"],
                    x=box["x"],
                    y=box["y"],
                    width=box["width"],
                    height=box["height"],
                    num_children=box.get("num_children", 0),
                )
            )
        return GetBoundingBoxesOutput(bounding_boxes=bounding_boxes)
    except RuntimeError:
        return GetBoundingBoxesOutput(bounding_boxes=[])


def highlight_bounding_box(
    input_data: HighlightBoundingBoxInput,
) -> HighlightBoundingBoxOutput:
    """
    Colora con overlay il bounding box del selettore dato. Colore opzionale (default: random).
    """
    try:
        BROWSER_HANDLER.highlight_bounding_box(input_data.selector, input_data.color)
        return HighlightBoundingBoxOutput(
            message=f"Bounding box evidenziato per {input_data.selector}."
        )
    except RuntimeError as e:
        return HighlightBoundingBoxOutput(message=f"Errore: {str(e)}")


def scroll_page_down() -> ScrollPageOutput:
    """
    Esegue lo scroll verticale massimo verso il basso.
    """
    try:
        BROWSER_HANDLER.scroll_page(ScrollDirection.DOWN)
        return ScrollPageOutput(message="Scroll down eseguito.")
    except Exception as e:
        return ScrollPageOutput(message=f"Errore scroll down: {str(e)}")


def scroll_page_up() -> ScrollPageOutput:
    """
    Esegue lo scroll verticale massimo verso l'alto.
    """
    try:
        BROWSER_HANDLER.scroll_page(ScrollDirection.UP)
        return ScrollPageOutput(message="Scroll up eseguito.")
    except Exception as e:
        return ScrollPageOutput(message=f"Errore scroll up: {str(e)}")


def screenshot_element(input_data: ScreenshotElementInput) -> ScreenshotElementOutput:
    """
    Salva uno screenshot dell'elemento identificato dal selettore CSS nel percorso specificato.
    Restituisce anche il path dell'immagine salvata.
    """
    try:
        BROWSER_HANDLER.screenshot_element(
            selector=input_data.selector,
            path=input_data.path,
            output_format=input_data.output_format,
        )
        return ScreenshotElementOutput(
            message=f"Screenshot salvato in {input_data.path}",
            image_path=f"{input_data.path}.{input_data.output_format}",
        )
    except Exception as e:
        return ScreenshotElementOutput(
            message=f"Errore screenshot: {str(e)}", image_path=None
        )


def get_page_info(input: PageInfoInput) -> PageInfoOutput:
    """
    Restituisce informazioni sulla pagina corrente: tipo, url, width, height, area.
    """
    width, height = BROWSER_HANDLER.get_page_dimensions()
    return PageInfoOutput(
        page_type=input.page_type, url=input.url, width=width, height=height
    )


def describe_screenshot_element(
    screenshot_output: ScreenshotElementOutput,
    page_info: PageInfoOutput,
    bounding_box: BoundingBox,
    model=ModelType.LLAMA,
) -> str | None:
    """
    Descrive uno screenshot di un elemento usando VLM, dato ScreenshotElementOutput, PageInfoOutput e BoundingBox.
    """
    if not screenshot_output or not screenshot_output.image_path:
        return None
    vlm = VLM(model=model)
    return vlm.describe_image(
        file_path=screenshot_output.image_path,
        page_info=page_info,
        bounding_box=bounding_box,
    )
