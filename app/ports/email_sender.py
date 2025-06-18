from abc import ABC, abstractmethod

class EmailSenderPort(ABC):
    """
    Porta astratta per l'invio di email con allegati.
    """
    @abstractmethod
    def send_newsletter(self, to: str, subject: str, markdown_path: str) -> None:
        """
        Invia la newsletter come allegato markdown all'indirizzo specificato.
        """
        pass
