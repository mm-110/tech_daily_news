from src.models import Link
from bs4 import BeautifulSoup, Tag, NavigableString
from typing import Optional, Callable, Dict, List, Union
import requests


def fetch_html(url: str, timeout: int = 10) -> Optional[str]:
    """
    Recupera l'HTML di un sito tramite una richiesta HTTP GET.
    Restituisce il contenuto HTML come stringa, oppure None in caso di errore.
    Utilizza un fake user agent per evitare blocchi da parte dei siti.
    """
    try:
        try:
            from fake_useragent import UserAgent

            user_agent = UserAgent().random
        except ImportError:
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        headers = {"User-Agent": user_agent}
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Errore durante il recupero di {url}: {e}")
        return None


def get_links(html: str, link_type: str) -> List[Link]:
    """
    Estrae i link dal codice HTML in base al tipo specificato (absolute, relative, ecc.).
    Restituisce una lista di oggetti Link.
    """
    soup = BeautifulSoup(html, "html.parser")

    def is_valid_absolute_link(href: Optional[str]) -> bool:
        return bool(href) and href.startswith(("http://", "https://"))

    def is_valid_relative_link(href: Optional[str]) -> bool:
        return bool(href) and href.startswith("/")

    def is_valid_relative_non_rooted_link(href: Optional[str]) -> bool:
        return bool(href) and not href.startswith(
            ("/", "http://", "https://", "#", "javascript:", "tel:", "mailto:")
        )

    def is_anchor_link(href: Optional[str]) -> bool:
        return bool(href) and href.startswith("#")

    def is_javascript_link(href: Optional[str]) -> bool:
        return bool(href) and href.startswith("javascript:")

    def is_tel_link(href: Optional[str]) -> bool:
        return bool(href) and href.startswith("tel:")

    def is_mailto_link(href: Optional[str]) -> bool:
        return bool(href) and href.startswith("mailto:")

    link_checkers: Dict[str, Callable[[Optional[str]], bool]] = {
        "absolute": is_valid_absolute_link,
        "relative": is_valid_relative_link,
        "relative_non_rooted": is_valid_relative_non_rooted_link,
        "anchor": is_anchor_link,
        "javascript": is_javascript_link,
        "tel": is_tel_link,
        "mailto": is_mailto_link,
    }

    if link_type not in link_checkers:
        raise ValueError(f"Invalid link type: {link_type}")

    checker_function = link_checkers[link_type]
    links: List[Link] = []
    for a in soup.find_all("a"):
        href = a.get("href")
        if checker_function(href):
            valore = a.get_text(strip=True) if a.get_text() else ""
            links.append(Link(link=href, text_value=valore))
    return links


def get_body_representation(
    element: Union[Tag, NavigableString], depth: int = 0, result: str = ""
) -> str:
    """
    Funzione ricorsiva per analizzare l'HTML e generare la rappresentazione con tipo di tag e indentazione.
    """
    if isinstance(element, Tag):
        if element.name == "a":
            href = element.get("href", "")
            result += "-" * depth + f"{element.name}: {href}\n"
        elif element.name == "img":
            src = element.get("src", "")
            result += "-" * depth + f"{element.name}: {src}\n"
        for child in element.children:
            result = get_body_representation(child, depth + 1, result)
    elif isinstance(element, NavigableString):
        stripped_text = element.strip()
        if (
            stripped_text
            and hasattr(element, "parent")
            and hasattr(element.parent, "name")
        ):
            result += "-" * depth + f"{element.parent.name}: {stripped_text}\n"
    return result


def extract_main_text(html: str) -> str:
    """
    Estrae il testo principale da una pagina HTML, rimuovendo elementi poco rilevanti come style, script, header, footer, nav, ecc.
    """
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(
        ["style", "script", "header", "footer", "nav", "aside", "form", "noscript"]
    ):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    lines = [line for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


if __name__ == "__main__":
    # Example usage
    html_content = """
    <html>
        <body>
            <h1>Title</h1>
            <p>This is a paragraph.</p>
            <a href="https://example.com">Example Link</a>
            <img src="image.jpg" alt="Image">
        </body>
    </html>
    """

    print(get_body_representation(BeautifulSoup(html_content, "html.parser").body))
    print(get_links(html_content, "absolute"))
    print(get_links(html_content, "relative"))
