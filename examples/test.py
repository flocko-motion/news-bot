from pathlib import Path
from news_bot.agents.news_assistant import NewsAssistant
from news_bot.agents.digest_assistant import DigestAssistant

def main():
    # Load API key
    api_key_path = Path.home() / ".news-bot" / "openai-api.key"
    if not api_key_path.exists():
        print(f"Error: OpenAI API key not found at {api_key_path}")
        exit(1)
        
    with open(api_key_path) as f:
        api_key = f.read().strip()
    
    # Test URLs
    urls = [
        # E-Bus article
        "https://www.amper-kurier.de/de/region/groebenzell/die-neuen-e-busse-sind-da-erster-einsatz-auf-der-mvv-buslinie-830",
        "https://www.amper-kurier.de/de/region/fuerstenfeldbruck/immer-schoen-locker-bleiben",
    ]
    
    # Initialize assistants
    news_assistant = NewsAssistant(api_key)
    digest_assistant = DigestAssistant(api_key)
    
    # Process articles
    print("\nFetching and analyzing articles...")
    articles = news_assistant.process_articles(urls)
    
    # Print individual article results
    for article in articles:
        print("\nArticle Analysis:")
        print(f"Title: {article['titel']}")
        print(f"Content: {article['inhalt']}")
        print(f"Source: {article['quelle']}")
        if article.get('error'):
            print(f"Error: {article['error']}")
    
    # Create and print digest
    print("\nCreating news digest...")
    digest = digest_assistant.create_digest(articles)
    print("\nNews Digest:")
    print(digest)

if __name__ == "__main__":
    main() 