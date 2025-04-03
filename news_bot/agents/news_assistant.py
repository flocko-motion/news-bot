from typing import Dict, Any, List
from .base import Assistant
from ..fetcher.content import ContentFetcher
from ..cache import Cache
import json

class NewsAssistant(Assistant):
    def __init__(self):
        super().__init__(
            name="News Analyst",
            instructions="""Du erstellst Zusammenfassungen von Nachrichtenartikeln aus Deutschen Regionalzeitungen. Der User gibt dir den Text eines Artikels, den du analysieren sollst.
            Du erstellst daraus eine Zusammenfassung im JSON-Format. Die Zusammenfassung sollte kurz und prägnant sein.
            
            ACHTUNG: der input text ist ein Textauszug aus einem HTML Dokument - er enthält viele HTML Tags und ist nicht formatiert. Du solltest den Text bereinigen und nur den eigentlichen Inhalt verwenden.
            
            Deine Antwort sollte folgendes Format haben:
            {
                "titel": "string - der Titel des Artikels",
                "inhalt": "string - kurze Zusammenfassung des Artikels"
            }"""
        )
        self.fetcher = ContentFetcher()
        self.cache = Cache()
        
    def analyze_article(self, article: Dict[str, str]) -> Dict[str, Any]:
        """Analyze a single article using the assistant."""
        # Check cache first
        cache_key = "analyzed:" + article["url"]
        cached_result = self.cache.get(cache_key)
        if cached_result:
            print(f"Using cached analysis for {article['url']}")
            try:
                result = json.loads(cached_result)
                return result
            except json.JSONDecodeError:
                print("Error reading cached analysis, will reanalyze")

        # Create a new thread for this conversation
        thread = self.client.beta.threads.create()
        
        # Add the user's request to analyze the article
        self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"Analysiere:\n\nQuelle: {article['url']}\n\n{article['content']}"
        )
        
        # Create a run with structured output
        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self.assistant.id,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "article_analysis",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "titel": {"type": "string"},
                            "inhalt": {"type": "string"}
                        },
                        "required": ["titel", "inhalt"]
                    }
                }
            }
        )
        
        # Wait for the run to complete
        run_result = self._wait_for_run(thread.id, run.id)
        if run_result["status"] != "completed":
            return {
                "error": run_result.get("error", "Unknown error"),
                "titel": "",
                "inhalt": "",
                "quelle": article["url"]
            }
        
        # Get and parse the response
        try:
            result = json.loads(self._get_assistant_response(thread.id))
            result["quelle"] = article["url"]
            
            # Cache the result
            self.cache.put(cache_key, json.dumps(result))
            
            return result
        except Exception as e:
            print("\nGPT Response:")
            print("-------------")
            print(self._get_assistant_response(thread.id))
            print("-------------")
            return {
                "error": f"Failed to parse response: {str(e)}",
                "titel": "",
                "inhalt": "",
                "quelle": article["url"]
            }
        
    def process_articles(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Process multiple articles and return their summaries."""
        return [self.analyze_article(url) for url in urls] 