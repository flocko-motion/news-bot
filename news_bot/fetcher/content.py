from typing import Dict, Any, List, Callable
import requests
from bs4 import BeautifulSoup
from ..cache import Cache
from urllib.parse import urljoin
import re

class ContentFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
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
        self.cache = Cache()
        
    def fetch_page(self, url: str) -> BeautifulSoup:
        """Fetch and parse a page, returning the BeautifulSoup object."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"Error fetching page {url}: {str(e)}")
            raise
            
    def extract_urls(self, url: str, is_valid_url: Callable[[str], bool]) -> List[str]:
        """Extract URLs from a page that match the given validation function."""
        soup = self.fetch_page(url)
        
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
            
    def fetch_article(self, url: str) -> Dict[str, Any]:
        """Fetch and clean content from a URL, removing only scripts and styles."""
        # Check cache first
        cached_content = self.cache.get(url)
        if cached_content:
            print(f"Using cached content for {url}")
            return {
                "error": None,
                "content": cached_content,
                "url": url,
                "cached": True,
            }
            
        try:
            print(f"Fetching article from {url}")
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 410:
                return {
                    "error": "Article has been permanently removed",
                    "content": None,
                    "url": url,
                    "cached": False,
                }
            elif response.status_code == 404:
                return {
                    "error": "Article not found",
                    "content": None,
                    "url": url,
                    "cached": False,
                }
            elif response.status_code == 403:
                return {
                    "error": "Access forbidden - might require subscription",
                    "content": None,
                    "url": url,
                    "cached": False,
                }
                
            response.raise_for_status()
            
            # Parse HTML just to remove scripts and styles
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove scripts and styles - they just add noise
            for element in soup(['script', 'style']):
                element.decompose()
                
            # Get the raw text
            text = soup.get_text(separator='\n', strip=True)
            
            if not text.strip():
                return {
                    "error": "Article content is empty",
                    "content": None,
                    "url": url,
                    "cached": False,
                }
            
            # Cache the cleaned content
            self.cache.put(url, text)
            
            return {
                "error": None,
                "content": text,
                "url": url,
                "cached": False,
            }
            
        except requests.Timeout:
            return {
                "error": "Request timed out",
                "content": None,
                "url": url,
                "cached": False,
            }
        except requests.ConnectionError:
            return {
                "error": "Could not connect to server",
                "content": None,
                "url": url,
                "cached": False,
            }
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return {
                "error": str(e),
                "content": None,
                "url": url,
                "cached": False,
            } 