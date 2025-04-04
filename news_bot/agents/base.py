from pathlib import Path
from typing import Dict, Any, Optional
from openai import OpenAI
import time

class Assistant:
    _api_key = None

    def __init__(self, name: str, instructions: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=self.api_key())
        self.assistant = self._create_assistant(name, instructions, model)

    @classmethod
    def api_key(cls) -> str:
        if cls._api_key:
            return cls._api_key

        """Load OpenAI API key from ~/.news-bot/openai-api.key"""
        home = Path.home()
        key_path = home / '.news-bot' / 'openai-api.key'

        if not key_path.exists():
            print(f"API key not found at {key_path}")
            exit(1)

        with open(key_path) as f:
            api_key = f.read().strip()

        if not api_key:
            print(f"API key file is empty at {key_path}")
            exit(1)

        cls._api_key = api_key.strip()

        return cls._api_key

    def _create_assistant(self, name: str, instructions: str, model: str):
        """Create an OpenAI Assistant with specific tools and instructions."""
        return self.client.beta.assistants.create(
            name=name,
            instructions=instructions,
            model=model
        )
        
    def _wait_for_run(self, thread_id: str, run_id: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
        """Wait for a run to complete with timeout."""
        start_time = time.time()
        
        while True:
            if time.time() - start_time > timeout:
                return {
                    "error": "Timeout waiting for analysis",
                    "status": "timeout"
                }
                
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            
            if run.status == "completed":
                return {"status": "completed"}
                
            if run.status == "failed":
                return {
                    "error": f"Run failed: {run.last_error}",
                    "status": "failed"
                }
                
            if run.status == "expired":
                return {
                    "error": "Run expired",
                    "status": "expired"
                }
                
            time.sleep(1)
            
    def _get_assistant_response(self, thread_id: str) -> str:
        messages = self.client.beta.threads.messages.list(
            thread_id=thread_id
        )
        return messages.data[0].content[0].text.value 