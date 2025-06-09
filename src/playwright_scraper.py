import os
from playwright.sync_api import sync_playwright
from src.browser_session_handler import BrowserSessionHandler
from PIL import Image  # aggiunto per upscaling


class PlaywrightBrowserSessionHandler(BrowserSessionHandler):
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None

    def open_session(self):
        if self.browser is not None:
            raise RuntimeError("Session already open.")
        
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.page = self.browser.new_page()

    def close_session(self):
        if self.browser:
            self.browser.close()
            self.browser = None
            self.page = None
        if self.playwright:
            self.playwright.stop()
            self.playwright = None

    def navigate(self, url: str):
        if not self.browser or not self.page:
            raise RuntimeError("Session not open. Call open_session() first.")
        self.page.goto(url, wait_until='networkidle')

    def get_page_content(self):
        if not self.browser or not self.page:
            raise RuntimeError("Session not open. Call open_session() first.")
        return self.page.content()

    def is_open(self):
        return self.browser is not None and self.page is not None

    def get_bounding_boxes(self, selector: str = "body"):
        """
        Recupera tutti i bounding box visibili a partire da un selettore (default: body).
        Ritorna una lista di dict con html, selettore css (full path), xpath (full path), coordinate, dimensioni, attributi del tag e numero figli.
        Il campo 'tag' contiene sempre il tag di apertura (es: <div class="...">).
        """
        if not self.browser or not self.page:
            raise RuntimeError("Session not open. Call open_session() first.")
        js = """
        (selector) => {
            // Sanifica il selettore: rimuovi spazi e virgole finali
            if (!selector || typeof selector !== 'string') return [];
            selector = selector.trim();
            while (selector.endsWith(',')) selector = selector.slice(0, -1).trim();
            if (!selector) return [];
            function getXPathForElement(el) {
                if (!el || !(el instanceof Element)) return '';
                if (el === document.documentElement) return '/html';
                var parentNode = el.parentNode;
                if (!parentNode || parentNode.nodeType !== Node.ELEMENT_NODE) {
                    if (el === document.body) return '/html/body';
                    return el.tagName ? '/' + el.tagName.toLowerCase() : '';
                }
                var siblings = parentNode.children;
                for (var i = 0; i < siblings.length; i++) {
                    var sibling = siblings[i];
                    if (sibling === el) {
                        let parentPath = getXPathForElement(parentNode);
                        let tagName = el.tagName.toLowerCase();
                        return parentPath + '/' + tagName + '[' + (i + 1) + ']';
                    }
                }
                return '';
            }
            function getCssSelector(el) {
                if (!(el instanceof Element)) return '';
                var path = [];
                while (el && el.nodeType === Node.ELEMENT_NODE) {
                    var selector = el.nodeName.toLowerCase();
                    var sib = el, nth = 1;
                    while (sib = sib.previousElementSibling) {
                        if (sib.nodeName.toLowerCase() == selector) nth++;
                    }
                    if (nth != 1) selector += ':nth-of-type(' + nth + ')';
                    path.unshift(selector);
                    el = el.parentNode;
                }
                return path.join(' > ');
            }
            function getAttributesFull(el) {
                var attrs = {};
                if (el && el.attributes) {
                    for (var i = 0; i < el.attributes.length; i++) {
                        var attr = el.attributes[i];
                        attrs[attr.name] = attr.value;
                    }
                }
                attrs['id'] = el.id || '';
                attrs['class'] = el.className || '';
                return attrs;
            }
            function getNumChildren(el) {
                if (!el || !el.children) return 0;
                return el.children.length;
            }
            function getTagOpening(el) {
                if (!el || !el.outerHTML) return '';
                const html = el.outerHTML;
                const end = html.indexOf('>');
                if (end !== -1) return html.slice(0, end+1);
                return '';
            }
            function getBoundingBoxes(selector) {
                var elements = [];
                try {
                    elements = Array.from(document.querySelectorAll(selector));
                } catch (e) {
                    return [];
                }
                var results = [];
                elements.forEach(function(root) {
                    var walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT, null, false);
                    var currentNode = root;
                    do {
                        var el = currentNode;
                        if (!document.body.contains(el)) { 
                            currentNode = walker.nextNode(); 
                            continue; 
                        }
                        var rect = el.getBoundingClientRect();
                        var style = window.getComputedStyle(el);
                        let isVisible = rect.width > 0 && rect.height > 0 && 
                                       style.display !== 'none' && 
                                       style.visibility !== 'hidden' && 
                                       parseFloat(style.opacity) > 0 && 
                                       el.offsetParent !== null;
                        if (isVisible) {
                            results.push({
                                tag: getTagOpening(el),
                                css_selector: getCssSelector(el),
                                xpath: getXPathForElement(el),
                                attributes: getAttributesFull(el),
                                id: el.id || '',
                                class: el.className || '',
                                x: Math.round(rect.left + window.scrollX),
                                y: Math.round(rect.top + window.scrollY),
                                width: Math.round(rect.width),
                                height: Math.round(rect.height),
                                num_children: getNumChildren(el)
                            });
                        }
                        currentNode = walker.nextNode();
                    } while(currentNode);
                });
                return results;
            }
            return getBoundingBoxes(selector);
        }
        """
        return self.page.evaluate(js, selector)

    def highlight_bounding_box(self, selector: str, color: str = None):
        """
        Colora con overlay il bounding box del selettore dato. Colore opzionale (default: random).
        """
        if not self.browser or not self.page:
            raise RuntimeError("Session not open. Call open_session() first.")
        js = """
        (selector, color) => {
            function randomColor() {
                var palette = ["#FF5733","#33FF57","#3357FF","#F39C12","#8E44AD","#16A085","#E74C3C","#2C3E50"];
                return palette[Math.floor(Math.random()*palette.length)];
            }
            color = color || randomColor();
            var elements = document.querySelectorAll(selector);
            elements.forEach(function(el) {
                var rect = el.getBoundingClientRect();
                var overlay = document.createElement('div');
                overlay.style.position = 'absolute';
                overlay.style.left = (rect.left + window.scrollX) + 'px';
                overlay.style.top = (rect.top + window.scrollY) + 'px';
                overlay.style.width = rect.width + 'px';
                overlay.style.height = rect.height + 'px';
                overlay.style.backgroundColor = color;
                overlay.style.opacity = '0.3';
                overlay.style.pointerEvents = 'none';
                overlay.style.zIndex = 9999;
                overlay.className = 'ai-bbox-overlay';
                document.body.appendChild(overlay);
            });
        }
        """
        # Playwright accetta solo UN argomento extra oltre al JS: un tuple/lista di argomenti
        self.page.evaluate(js, [selector, color])

    def screenshot_element(self, selector: str, path: str, output_format: str = 'png'):
        """
        Fa lo screenshot dell'elemento identificato dal selettore CSS, se visibile.
        Salva direttamente nel formato richiesto ('png' o 'jpeg').
        Il parametro 'path' deve essere passato SENZA estensione: l'estensione viene aggiunta qui in base all'output_format.
        """
        if not self.browser or not self.page:
            raise RuntimeError("Session not open. Call open_session() first.")

        # 1. Rimuove overlay fissi che possono bloccare la vista
        self.page.evaluate("""
            const elements = Array.from(document.querySelectorAll('*'));
            for (const el of elements) {
                const style = window.getComputedStyle(el);
                if (style.position == 'fixed' && parseFloat(style.opacity) > 0.1 && 
                    style.display !== 'none' && style.visibility !== 'hidden') {
                    el.remove();
                }
            }
        """)

        # 2. Trova l'elemento
        try:
            element = self.page.query_selector(selector)
            if not element:
                print(f"[WARN] Nessun elemento trovato con selettore '{selector}'")
                return
        except Exception as e:
            print(f"[WARN] Errore nel trovare elemento '{selector}': {e}")
            return

        # 3. Verifica visibilità reale
        is_visible = self.page.evaluate("""
            (el) => {
                if (!el) return false;
                const rect = el.getBoundingClientRect();
                const style = window.getComputedStyle(el);
                return rect.width > 0 && rect.height > 0 && 
                       style.display !== 'none' && 
                       style.visibility !== 'hidden' && 
                       parseFloat(style.opacity) > 0;
            }
        """, element)

        if not is_visible:
            print(f"[WARN] Elemento '{selector}' non visibile, skippo lo screenshot.")
            return

        # 4. Scrolla l'elemento in vista
        element.scroll_into_view_if_needed()

        # 5. Screenshot dell'elemento nel formato richiesto
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            ext = '.jpg' if output_format.lower() in ['jpeg', 'jpg'] else '.png'
            full_path = path + ext
            if output_format.lower() in ['jpeg', 'jpg']:
                element.screenshot(path=full_path, type='jpeg', quality=70)
            else:
                element.screenshot(path=full_path, type='png', quality=70)
            print(f"[INFO] Screenshot salvato in: {full_path} ({output_format})")
            return full_path
        except Exception as e:
            print(f"[ERROR] Impossibile salvare screenshot: {e}")
            return None

    def scroll_page(self, direction: str):
        """
        Effettua lo scroll verticale massimo in una direzione (UP o DOWN).
        """
        if not self.browser or not self.page:
            raise RuntimeError("Session not open. Call open_session() first.")
        
        if direction == "DOWN":
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        elif direction == "UP":
            self.page.evaluate("window.scrollTo(0, 0)")
        else:
            raise ValueError("Direction must be 'UP' or 'DOWN'")

    def get_page_dimensions(self):
        """Restituisce (width, height) della pagina (intera, non solo viewport)."""
        if not self.browser or not self.page:
            raise RuntimeError("Session not open. Call open_session() first.")
        js = """
        () => {
            return {
                width: Math.max(document.body.scrollWidth, document.documentElement.scrollWidth),
                height: Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)
            };
        }
        """
        dims = self.page.evaluate(js)
        return dims['width'], dims['height']


# Esempio di utilizzo
if __name__ == "__main__":
    import time
    
    handler = PlaywrightBrowserSessionHandler(headless=False)
    try:
        handler.open_session()
        handler.navigate("https://www.example.com")
        content = handler.get_page_content()
        print(content[:500])  # Print first 500 characters of the page content
        time.sleep(2)  # Wait for a while to see the browser in action
    finally:
        handler.close_session()