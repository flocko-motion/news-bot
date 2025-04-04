from typing import Dict, Any, List, Callable, Optional
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup, NavigableString
import cache


def create_error_response(url: str, error: str) -> Dict[str, Any]:
    """Create a standardized error response."""
    return {
        "error": error,
        "content": None,
        "url": url,
        "cached": False,
    }


def create_success_response(url: str, content: str, cached: bool = False) -> Dict[str, Any]:
    """Create a standardized success response."""
    return {
        "error": None,
        "content": content,
        "url": url,
        "cached": cached,
    }


def _create_session() -> requests.Session:
    """Create a configured requests session."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    })
    return session


def fetch_page(url: str) -> Optional[str]:
    """Fetch and parse a page, returning the BeautifulSoup object or None on error."""
    try:
        session = _create_session()
        response = session.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching page {url}: {str(e)}")
        return None


def fetch_article(url: str) -> Dict[str, Any]:
    """Fetch and clean content from a URL, removing only scripts and styles."""

    # Check cache first
    cached_content = cache.get(url)
    if cached_content:
        print(f"Using cached content for {url}")
        return create_success_response(url, cached_content, cached=True)

    try:
        print(f"Fetching article from {url}")
        session = _create_session()
        response = session.get(url, timeout=10)

        if response.status_code == 410:
            return create_error_response(url, "Article has been permanently removed")
        elif response.status_code == 404:
            return create_error_response(url, "Article not found")
        elif response.status_code == 403:
            return create_error_response(url, "Access forbidden - might require subscription")

        response.raise_for_status()

        # Parse HTML just to remove scripts and styles
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove scripts and styles - they just add noise
        for element in soup(['script', 'style']):
            element.decompose()

        # Get the raw text
        text = soup.get_text(separator="\n", strip=True)

        if not text.strip():
            return create_error_response(url, "Article content is empty")

        # Cache the cleaned content
        cache.put(url, text)

        return create_success_response(url, text)

    except requests.Timeout:
        return create_error_response(url, "Request timed out")
    except requests.ConnectionError:
        return create_error_response(url, "Could not connect to server")
    except Exception as e:
        print(f"Error fetching {url}: {str(e)}")
        return create_error_response(url, str(e))

def extract_urls(url: str, is_valid_url: Callable[[str], bool]) -> List[str]:
    """Extract URLs from a page that match the given validation function."""
    raw = fetch_page(url)
    soup = BeautifulSoup(raw, 'html.parser') if raw else None
    if not soup:
        return []

    # Get all links
    all_links = soup.find_all('a', href=True)
    print(f"Found {len(all_links)} total links")

    # Filter for valid URLs
    valid_urls = set()
    for link in all_links:
        href = link['href']
        if href.startswith('/'):
            # Use the base domain from the input URL
            href = urljoin(url, href)
        elif not href.startswith(('http://', 'https://')):
            continue

        if is_valid_url(href):
            valid_urls.add(href)

    # Print unique URLs
    print("\nFound valid URLs:")
    for url in sorted(valid_urls):
        print(url)

    print(f"\nTotal unique valid URLs found: {len(valid_urls)}")
    return list(valid_urls)

