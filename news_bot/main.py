import argparse
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime
import traceback
from .fetcher import NewsFetcher
from .models import Article
from .sources import NewsFetcherFactory
from .agents.api_key import load_api_key
from .agents.news_assistant import NewsAssistant
from .agents.digest_assistant import DigestAssistant
from .fetcher.content import ContentFetcher
from .cache import Cache

def gather_article_urls(sources: List[str]) -> List[Article]:
    """Gather article URLs from all configured sources."""
    factory = NewsFetcherFactory()
    all_articles = []
    
    for source in sources:
        try:
            print(f"\nFetching URLs from {source}...")
            fetcher = factory.create_fetcher(source)
            urls = fetcher.fetch_articles()
            
            articles = [
                Article(
                    title="",  # Will be filled by the analyzer
                    text="",   # Will be filled by the analyzer
                    date=datetime.now(),  # Will be parsed from article later
                    source_url=source,
                    article_url=url
                )
                for url in urls
            ]
            
            all_articles.extend(articles)
            print(f"✓ Found {len(articles)} articles")
        except Exception as e:
            print(f"⚠️ Error fetching from {source}:")
            traceback.print_exc()
            continue
            
    return all_articles

def download_article_content(articles: List[Article], ignore_cached: bool = False) -> List[Dict[str, Any]]:
    """Download and process content for all articles."""
    content_fetcher = ContentFetcher()
    cache = Cache()
    processed_articles = []
    
    for i, article in enumerate(articles, 1):
        if not article.article_url:
            print(f"Skipping article {i}/{len(articles)}: No URL available")
            continue

        if ignore_cached and cache.has(article.article_url):
            print(f"Cache entry for {article.article_url} is cached, ignoring old news")
            continue

        age = cache.age(article.article_url)
        if age > 1:
            print(f"Cache entry for {article.article_url} is {age} days old, ignoring")
            continue

        print(f"\nFetching article {i}/{len(articles)}: {article.article_url}")

        result = content_fetcher.fetch_article(article.article_url)
        if result.get('error') or not result.get('content'):
            print(f"Error fetching article: {result.get('error', 'No content found')}")
            continue

        processed_article = {
            "url": article.article_url,
            "content": result['content'],
            "source": article.source_url,
            "title": "",  # Will be filled by the analyzer
            "date": article.date
        }
        processed_articles.append(processed_article)

    return processed_articles

def analyze_articles(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Analyze articles using the news assistant."""
    news_assistant = NewsAssistant()
    analyzed_articles = []
    
    for i, article in enumerate(articles, 1):
        try:
            print(f"\nSummarizing {i}/{len(articles)}: {article['url']}")
            result = news_assistant.analyze_article(article)
            
            if result.get('error'):
                print(f"Error analyzing article: {result['error']}")
                continue
                
            article.update({
                "title": result['titel'],
                "summary": result['inhalt']
            })
            analyzed_articles.append(article)
            
        except Exception as e:
            print(f"Error analyzing article:")
            traceback.print_exc()
            continue
            
    return analyzed_articles

def create_digest(articles: List[Dict[str, Any]]) -> str:
    """Create a digest of all analyzed articles."""
    digest_assistant = DigestAssistant()
    
    try:
        print("\nCreating digest...")
        digest = digest_assistant.create_digest(articles)
        return digest
    except Exception as e:
        print("Error creating digest:")
        traceback.print_exc()
        return "Error creating digest"

def format_digest(digest: str) -> str:
    """Format the digest by adding HTML page structure and the current date."""
    current_date = datetime.now().strftime("%d.%m.%Y")

    return f"""
        <!DOCTYPE html>
        <html lang="de">
        <head>
            <meta charset="UTF-8">
            <title>Neues aus der Region - {current_date}</title>
        </head>
        <body>
            <h1>Neues aus der Region - {current_date}</h1>
            {digest}
        </body>
        </html>
    """

def generate_digest_index(digests_dir: Path) -> None:
    """Generate an index.html file listing all digests in descending date order."""
    # Get all HTML files in the digests directory
    digest_files = sorted(
        [f for f in digests_dir.glob("digest-*.html") if f.is_file()],
        key=lambda x: x.stem[7:17],  # Sort by date part of filename
        reverse=True
    )
    
    # Generate HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <title>News Digests</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
            h1 {{ color: #333; }}
            .digest-list {{ list-style: none; padding: 0; }}
            .digest-item {{ margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 4px; }}
            .digest-date {{ color: #666; font-size: 0.9em; }}
            a {{ color: #0066cc; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <h1>News Digests</h1>
        <ul class="digest-list">
    """
    
    for digest_file in digest_files:
        date = digest_file.stem[7:17]
            
        html_content += f"""
            <li class="digest-item">
                <a href="{digest_file.name}">Digest vom {date}</a>
            </li>
        """
    
    html_content += """
        </ul>
    </body>
    </html>
    """
    
    # Write index file
    index_path = digests_dir / "index.html"
    with open(index_path, 'w') as f:
        f.write(html_content)
    print(f"Index file updated at {index_path}")

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
    load_api_key()

    
    if not sources:
        print("No source configurations found!")
        return
        
    print(f"Found {len(sources)} sources: {', '.join(sources)}")
    
    # Step 1: Gather URLs
    articles = gather_article_urls(sources)
        
    # Step 2: Download content
    fetched_articles = []
    if articles:
        fetched_articles = download_article_content(articles, ignore_cached=args.ignore_cached_news)
    
    # Step 3: Analyze articles
    analyzed_articles = []
    if fetched_articles:
        fetched_articles = sorted(fetched_articles, key=lambda x: x['url'])
        analyzed_articles = analyze_articles(fetched_articles)
            
    # Step 4: Create digest
    if analyzed_articles:
        digest = create_digest(analyzed_articles)
        print("\nDigest:")
        print("-------")
        print(digest)

        # Step 5: Format digest
        digest = format_digest(digest)

        digest_path = digests_dir / f"digest-{datetime.now().strftime('%Y%m%d')}.html"
        with open(digest_path, 'w') as f:
            f.write(digest)
        print(f"\nDigest saved to {digest_path}")
    
    # Generate index file
    generate_digest_index(digests_dir)


if __name__ == "__main__":
    main() 