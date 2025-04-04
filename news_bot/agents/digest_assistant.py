from typing import Dict, Any, List

from sources.article import Article
from .base import Assistant

class DigestAssistant(Assistant):
    def __init__(self):
        super().__init__(
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
        
    def create_digest(self, articles: List[Article]) -> str:
        print (f"Creating digest for {len(articles)} articles")
        articles_text = "\n\n".join([
            f"Quelle: {article.source_name}\nURL: {article.source_url}\nTitel: {article.title}\nInhalt: {article.summary}"
            for article in articles
        ])
        
        thread = self.client.beta.threads.create()
        self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=articles_text
        )
        
        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self.assistant.id
        )
        
        run_result = self._wait_for_run(thread.id, run.id)
        if run_result["status"] != "completed":
            raise Exception(f"Fehler beim Erstellen des Überblicks: {run_result.get('error', 'Unbekannter Fehler')}")
        
        return self._get_assistant_response(thread.id)