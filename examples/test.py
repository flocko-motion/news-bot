from pathlib import Path

from sources.article import Article
from news_bot.agents.news_assistant import NewsAssistant
from news_bot.agents.digest_assistant import DigestAssistant


def fetch_single_article():
    """Fetch and analyze a single article."""
    url = "https://www.sueddeutsche.de/muenchen/fuerstenfeldbruck/puchheim-amphibien-massaker-rodung-baumschul-gelaende-li.3229693'"
    article = Article("test", url)
    res = article.fetch()
    print(res)

if __name__ == "__main__":
    # main()
    fetch_single_article()