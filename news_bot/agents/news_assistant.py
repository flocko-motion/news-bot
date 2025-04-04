from typing import Dict, Any, List

from sources.article import Article
from .base import Assistant
import cache
import json

class NewsAssistant(Assistant):
    def __init__(self):
        super().__init__(
            name="News Analyst",
            instructions="""
            Du bekommst bereinigte HTML-Snippets deutscher Regionalzeitungen. 
            Extrahiere den Artikeltext und gib ausschließlich eine kurze, prägnante Zusammenfassung aus – ohne Einleitung, Überschrift oder Kommentar.
            """
        )

    def analyze_article(self, article: Article):
        cache_key = "analyzed:" + article.source_url

        if cache.has(cache_key):
            print(f"Summary cache: {article.source_url}")
            article.summary = cache.get(cache_key)
            return

        print(f"Summary generation: {article.source_url}")
        thread = self.client.beta.threads.create()

        max_len = 50000
        cleaned_text = article.cleaned()
        if len(cleaned_text) > max_len:
            print(f"WARNING: Very long article with {len(cleaned_text)} chars: {article.source_url}")

        self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=cleaned_text[:max_len],
        )

        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self.assistant.id,
        )

        try:
            run_result = self._wait_for_run(thread.id, run.id)
            if run_result["status"] != "completed":
                article.error = "assistant failed: " +  run_result.get("error", "Unknown error")
                return

            # Get and parse the response
            result = self._get_assistant_response(thread.id)
            cache.put(cache_key, result)

            article.summary = result
            return
        except Exception as e:
            print("\nGPT Response:")
            print("-------------")
            print(self._get_assistant_response(thread.id))
            print("-------------")
            article.error = f"Failed to parse response: {str(e)}"
