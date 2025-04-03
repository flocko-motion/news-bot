import hashlib
from datetime import date
from pathlib import Path
import json
from typing import Optional, Any

class Cache:
    def __init__(self):
        self.cache_dir = Path.home() / ".news-bot" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_cache_path(self, key: str) -> Path:
        """Get the cache file path for a key."""
        hashed_key = self.hash_string(key)
        return self.cache_dir / hashed_key
        
    def has(self, key: str) -> bool:
        """Check if a cache entry exists."""
        cache_path = self._get_cache_path(key)
        return cache_path.exists()

    def get(self, key: str) -> Optional[str]:
        """Get content from cache if it exists."""
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"Error reading cache for {key}: {e}")
        return None
        
    def put(self, key: str, content: str) -> None:
        """Store content in cache."""
        cache_path = self._get_cache_path(key)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"Error writing cache for {key}: {e}")

    def age(self, key: str) -> Optional[int]:
        """Get the age of a cached item in calendar days.

        Returns:
            Number of calendar days since the cache was created, or None if not found
        """
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            mtime = cache_path.stat().st_mtime
            file_date = date.fromtimestamp(mtime)
            today = date.today()
            days_diff = (today - file_date).days
            return days_diff
        return 0

    @staticmethod
    def hash_string(s: str) -> str:
        """Create a hash of a string."""
        return hashlib.sha256(s.encode('utf-8')).hexdigest() 