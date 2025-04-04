import argparse
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime
import traceback

from formatters.digest_formatter import generate_digest_index
from sources.article import Article
from sources import NewsFetcherFactory
from agents.news_assistant import NewsAssistant
from agents.digest_assistant import DigestAssistant




def main():
    """Main entry point with linear flow."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate news digest from regional sources')
    parser.add_argument('--ignore-cached-news', action='store_true', 
                       help='Ignore previously cached articles when generating the digest')
    args = parser.parse_args()
    
    # Initialize
    factory = NewsFetcherFactory()
    sources = factory.get_available_sources()
    home = Path.home()
    digests_dir = home / '.news-bot' / 'digests'
    digests_dir.mkdir(parents=True, exist_ok=True)
    news_assistant = NewsAssistant()
    digest_assistant = DigestAssistant()

    
    if not sources:
        print("No source configurations found!")
        return
        
    print(f"Found {len(sources)} sources: {', '.join(sources)}")
    
    # Step 1: Gather URLs
    articles = sorted(
        [article for source in sources for article in NewsFetcherFactory().create_fetcher(source).fetch_articles()],
        key=lambda a: a.source_url
    )
        
    # Step 2: Fetch and clean content
    for i, article in enumerate(articles, 1):
        print(f"Processing {i} of {len(articles)}")
        article.fetch()
        news_assistant.analyze_article(article)

    # Step 3: Write digest
    digest = digest_assistant.create_digest(articles)

    digest_path = digests_dir / f"digest-{datetime.now().strftime('%Y%m%d')}.html"
    with open(digest_path, 'w') as f:
        f.write(digest)
    print(f"\nDigest saved to {digest_path}")
    
    # Generate index file
    generate_digest_index(digests_dir)


if __name__ == "__main__":
    main() 