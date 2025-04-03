from typing import Dict, Any, List
from .base import Assistant

class DigestAssistant(Assistant):
    def __init__(self, api_key: str):
        super().__init__(
            api_key=api_key,
            name="News Digest",
            instructions="""Du erstellst einen sehr kurzen Überblick über die wichtigsten Nachrichten. Der User gibt dir eine Liste von Artikeln mit ihren Zusammenfassungen.
            
            Deine Aufgabe ist es:
            1. Nur die wichtigsten Ereignisse in 1-2 Sätzen pro Geschichte zu nennen
            2. Artikel mit Fehlern zu ignorieren
            3. Ähnliche Artikel zu einer Geschichte zusammenzufassen
            4. Einen extrem knappen Überblick zu erstellen
            
            Formatiere deine Antwort wie folgt:
            
            # Nachrichtenüberblick
            
            ## [Titel der ersten Geschichte]
            [1-2 Sätze Zusammenfassung]
            Quellen: [URLs]
            
            ## [Titel der zweiten Geschichte]
            [1-2 Sätze Zusammenfassung]
            Quellen: [URLs]"""
        )
        
    def create_digest(self, articles: List[Dict[str, Any]]) -> str:
        """Create a digest from multiple articles."""
        # Filter out articles with errors
        valid_articles = [article for article in articles if not article.get('error')]
        
        if not valid_articles:
            return "Keine gültigen Artikel gefunden."
            
        # Create a new thread for this conversation
        thread = self.client.beta.threads.create()
        
        # Format articles for the assistant
        articles_text = "\n\n".join([
            f"Titel: {article['titel']}\nInhalt: {article['inhalt']}\nQuelle: {article['quelle']}"
            for article in valid_articles
        ])
        
        # Add the user's request to analyze the articles
        self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"Erstelle einen sehr kurzen Überblick über diese Artikel:\n\n{articles_text}"
        )
        
        # Create a run
        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self.assistant.id
        )
        
        # Wait for the run to complete
        run_result = self._wait_for_run(thread.id, run.id)
        if run_result["status"] != "completed":
            return f"Fehler beim Erstellen des Überblicks: {run_result.get('error', 'Unbekannter Fehler')}"
        
        # Get the response
        return self._get_assistant_response(thread.id) 