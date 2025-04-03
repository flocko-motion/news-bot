from abc import ABC, abstractmethod
from typing import List
from ..models import Article

class NewsFetcher(ABC):
    def __init__(self, source_url: str):
        self.source_url = source_url
        
    @abstractmethod
    def fetch_articles(self) -> List[Article]:
        """Fetch articles from the source."""
        pass 