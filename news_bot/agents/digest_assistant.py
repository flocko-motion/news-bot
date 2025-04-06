from typing import Dict, Any, List

import cache
from sources.article import Article
from .base import Assistant

class DigestAssistant(Assistant):
    def __init__(self):
        super().__init__(
            name="News Digest",
            instructions="""Du erstellst einen sehr kurzen Überblick über die wichtigsten Nachrichten. Der User gibt dir eine Liste von Artikeln mit ihren Zusammenfassungen.

            Deine Aufgabe ist es:
            1. Irrelevante News zu ignorieren (z.b. Werbung, Wetter, Sport, Verkehrsinfos)
            2. Die wichtigsten Stories in den vielen Artikeln zu identifizieren, lasse keine relevanten Stories aus
            3. Die Userin will ein Abstract der Gesamtlage, am besten gruppiert nach Themen
            4. Die Userin ist Lokalpolitikerin und interessiert sich für alle relevanten Themen. Einer der Schwerpunkte ist Umweltschutz. 
            5. Jeder Absatz sollte mit HTML-Links auf die Quellen enden, also die verwendeten Artikel. Beispiel: ..text...text...text (<a href="http:/...">Merkur</a>)
            6. Strukturiere den Text mit HTML-Tags für Absätze, hebe wichtige stellen mit <b> hervor.


            Deine Ausgabe sollte einfachs HTML sein (nur content, der später in ein Template eingefügt wird, kein CSS oder JavaScript). Sie sollte nur den Text und Links enthalten.

            HTML Formatvorlage (wiederholt genutzt pro Thema):

            <div class="story">
                <h3 class="story-title">{{Themenbereich}}</h3>
                <div class="story-summary">{{Lagebericht zum Thema}}</div>
                <div class="story-sources">
                  <a class="story-source" href="{{source_url}}">{{source_name}}</a>
                  ...
                </div>
            </div>
            <div class="story">
              ...
            </div>
            ...
            """
        )
        
    def create_digest(self, articles: List[Article]) -> str:
        print (f"Creating digest for {len(articles)} articles (This might take a little while)")

        cache_key = "digest:" + cache.hash_string(str([str(article) for article in articles]))
        if cache.has(cache_key):
            print(f"Digest cache: {cache_key}")
            return cache.get(cache_key)

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
        
        digest = self._get_assistant_response(thread.id)
        cache.put(cache_key, digest)
        return digest