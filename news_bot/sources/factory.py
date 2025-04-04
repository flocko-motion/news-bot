import os
from typing import Dict, Type, List
from .base import BaseNewsFetcher

class NewsFetcherFactory:
    def __init__(self, config_dir: str = "news_bot/config/sources"):
        self.config_dir = os.path.abspath(config_dir)
        print(f"Looking for configs in: {self.config_dir}")
        self.fetcher_class = BaseNewsFetcher

    def get_available_sources(self) -> List[str]:
        if not os.path.exists(self.config_dir):
            print(f"Config directory does not exist: {self.config_dir}")
            return []
            
        sources = []
        for filename in os.listdir(self.config_dir):
            if filename.endswith('.yaml'):
                source = filename[:-5]  # Remove .yaml extension
                sources.append(source)
        return sorted(sources)

    def create_fetcher(self, source: str) -> BaseNewsFetcher:
        config_path = os.path.join(self.config_dir, f"{source}.yaml")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
            
        return self.fetcher_class(source, config_path)