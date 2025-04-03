from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Article:
    title: str
    text: str
    date: datetime
    source_url: str
    article_url: Optional[str] = None 