from datetime import datetime
from typing import List, Dict, Any
from urllib.parse import urlparse
import yaml

from sources.article import Article
from sources.fetcher import extract_urls


class BaseNewsFetcher():
    def __init__(self, source: str, config_path: str):
        self.source = source

        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
            
        self.source_url = self.config['source_url']
        self.skip_patterns = self.config['skip_patterns']
        self.article_sections = self.config['article_sections']

    def _is_article_url(self, url: str) -> bool:
        """Check if a URL looks like an article URL."""
        path = urlparse(url).path
        
        # Skip utility and navigation pages
        for pattern in self.skip_patterns:
            if pattern in path:
                print(f"Ignored URL (skip pattern): {url}")
                return False
            
        # Articles are under specific sections
        if not any(section in path for section in self.article_sections):
            print(f"Ignored URL (not in article sections): {url}")
            return False
            
        if not self._validate_article_path(path):
            print(f"Ignored URL (invalid path structure): {url}")
            return False
            
        return True

    def _validate_article_path(self, path: str) -> bool:
        """Validate the article path structure based on config."""
        parts = path.strip("/").split("/")
        validation = self.config['path_validation']
        
        # Check minimum parts
        if len(parts) < validation['min_parts']:
            return False
            
        # Check required parts
        if 'required_parts' in validation:
            for i, part in enumerate(validation['required_parts']):
                if i >= len(parts) or parts[i] != part:
                    return False
                    
        # Check excluded parts
        if 'exclude_parts' in validation:
            if any(part in validation['exclude_parts'] for part in parts):
                return False
                
        # Check must end with
        if 'must_end_with' in validation:
            if not parts[-1].endswith(validation['must_end_with']):
                return False
                
        return True

    def fetch_articles(self) -> List[Article]:
        print(f"\nFetching URLs from {self.source}...")
        urls =  extract_urls(self.source_url, self._is_article_url)
        articles = [
            Article(
                date=datetime.now(),  # Will be parsed from article later
                source_name=self.source,
                source_url=url
            )
            for url in urls
        ]
        print(f"✓ Found {len(articles)} articles")
        return articles
