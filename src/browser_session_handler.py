from abc import ABC, abstractmethod

class BrowserSessionHandler(ABC):
    @abstractmethod
    def open_session(self):
        pass

    @abstractmethod
    def close_session(self):
        pass

    @abstractmethod
    def navigate(self, url: str):
        pass

    @abstractmethod
    def get_page_content(self):
        pass

    @abstractmethod
    def is_open(self):
        pass

    @abstractmethod
    def get_bounding_boxes(self, selector: str = "body"):
        pass

    @abstractmethod
    def highlight_bounding_box(self, selector: str, color: str = None):
        pass

    @abstractmethod
    def screenshot_element(self, selector: str, path: str, output_format: str = 'png'):
        pass

    @abstractmethod
    def scroll_page(self, direction: str):
        pass

    @abstractmethod
    def get_page_dimensions(self):
        """Restituisce (width, height) della pagina (viewport o intera pagina)."""
        pass
