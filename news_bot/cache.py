import hashlib
from datetime import date
from pathlib import Path
import json
from typing import Optional, Any

CACHE_DIR = Path.home() / ".news-bot" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def get_cache_path(key: str) -> Path:
    """Get the cache file path for a key."""
    hashed_key = hash_string(key)
    return CACHE_DIR / hashed_key

def has(key: str) -> bool:
    """Check if a cache entry exists."""
    cache_path = get_cache_path(key)
    return cache_path.exists()

def get(key: str) -> Optional[str]:
    """Get content from cache if it exists."""
    cache_path = get_cache_path(key)
    if cache_path.exists():
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading cache for {key}: {e}")
    return None

def put(key: str, content: str) -> None:
    """Store content in cache."""
    cache_path = get_cache_path(key)
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"Error writing cache for {key}: {e}")

def age(key: str) -> Optional[int]:
    """Get the age of a cached item in calendar days.

    Returns:
        Number of calendar days since the cache was created, or None if not found
    """
    cache_path = get_cache_path(key)
    if cache_path.exists():
        mtime = cache_path.stat().st_mtime
        file_date = date.fromtimestamp(mtime)
        today = date.today()
        days_diff = (today - file_date).days
        return days_diff
    return 0

def hash_string(s: str) -> str:
    """Create a hash of a string."""
    return hashlib.sha256(s.encode('utf-8')).hexdigest() 