from pathlib import Path
import os

def load_api_key() -> str:
    """Load OpenAI API key from ~/.news-bot/openai-api.key"""
    home = Path.home()
    key_path = home / '.news-bot' / 'openai-api.key'
    
    if not key_path.exists():
        print(f"API key not found at {key_path}")
        os.exit(1)
        
    with open(key_path) as f:
        api_key = f.read().strip()
        
    if not api_key:
        print(f"API key file is empty at {key_path}")
        os.exit(1)
        
    return api_key.strip()