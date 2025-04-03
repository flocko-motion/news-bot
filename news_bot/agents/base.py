from typing import Dict, Any, Optional
from openai import OpenAI
import json
import time
from .api_key import load_api_key

class Assistant:
    def __init__(self, name: str, instructions: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=load_api_key())
        self.assistant = self._create_assistant(name, instructions, model)
        
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
            
    def _get_assistant_response(self, thread_id: str) -> Dict[str, Any]:
        """Get the latest message from the assistant."""
        messages = self.client.beta.threads.messages.list(
            thread_id=thread_id
        )
        return messages.data[0].content[0].text.value 