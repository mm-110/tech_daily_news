import os
from app.ports.email_sender import EmailSenderPort

class MockEmailSender(EmailSenderPort):
    """
    Adapter mock per l'invio email: stampa info e fornisce link per visualizzare la newsletter in browser.
    """
    def send_newsletter(self, to: str, subject: str, markdown_path: str) -> None:
        print(f"[MOCK EMAIL] Newsletter inviata a: {to}\nOggetto: {subject}\nAllegato: {markdown_path}")
        # Prova a convertire il markdown in HTML e aprire nel browser
        try:
            import markdown
            import webbrowser
            with open(markdown_path, "r", encoding="utf-8") as f:
                md_content = f.read()
            html = markdown.markdown(md_content)
            html_path = markdown_path.replace(".md", ".html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"[MOCK EMAIL] Visualizza la newsletter: file://{os.path.abspath(html_path)}")
        except Exception as e:
            print(f"[MOCK EMAIL] Impossibile generare anteprima HTML: {e}")
