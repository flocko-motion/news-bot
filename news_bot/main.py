import argparse
from pathlib import Path
from datetime import datetime
from formatters.digest_formatter import generate_digest_index
from formatters.html import generate_html
from sources import NewsFetcherFactory
from agents.news_assistant import NewsAssistant
from agents.digest_assistant import DigestAssistant

home = Path.home()
digests_dir = home / '.news-bot' / 'digests'


def main():
    """Main entry point with linear flow."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate news digest from regional sources')
    parser.add_argument('--ignore-cached-news', action='store_true', 
                       help='Ignore previously cached articles when generating the digest')

    # Initialize
    factory = NewsFetcherFactory()
    sources = factory.get_available_sources()
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

    articles = [article for article in articles if article.is_from_today()]
    print(f"Identified {len(articles)} articles from today.")

    # Step 2: Fetch and clean content
    for i, article in enumerate(articles, 1):
        print(f"Processing {i} of {len(articles)}")
        article.fetch()
        news_assistant.analyze_article(article)

    # Step 3: Generate digest
    digest = digest_assistant.create_digest(articles)

    # Step 4: Format and save result
    write_html(f"digest-{datetime.now().strftime('%Y%m%d')}.html",generate_html(articles, digest))
    write_html("index.html", generate_digest_index(digests_dir))
    copy_file(Path(__file__).parent / 'formatters' / 'templates' / 'styles.css')

def write_html(filename: str, content: str) -> None:
    index_path = digests_dir / filename
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)

def copy_file(src: Path) -> None:
    dest = digests_dir / src.name
    with open(src, 'rb') as fsrc, open(dest, 'wb') as fdst:
        fdst.write(fsrc.read())
    print(f"Copied {src} to {dest}")

if __name__ == "__main__":
    main()

