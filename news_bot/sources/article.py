from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List, Callable, Optional
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup, NavigableString
import cache
from sources.fetcher import fetch_page


@dataclass
class Article:
	source_name: str
	source_url: Optional[str] = None
	date: datetime = datetime.now()
	title: Optional[str] = None
	text: Optional[str] = None
	summary: Optional[str] = None
	digest: Optional[str] = None
	raw: Optional[str] = None
	error: Optional[str] = None


	def cache_key_raw(self):
		return "raw:" + self.source_url

	def cache_key_cleaned(self):
		return "cleaned:" + self.source_url

	def cache_key_title(self):
		return "title:" + self.source_url


	def is_cached(self) -> bool:
		"""Check if the article is cached."""
		return cache.has(self.cache_key_raw())

	def fetch(self) -> bool:
		if not self.source_url:
			self.error = "No source URL provided"
			return False

		if self.is_cached():
			print(f"Content cache: {self.source_url}")
			self.raw = cache.get(self.cache_key_raw())
		else:
			print(f"Content fetch: {self.source_url}")
			self.raw = fetch_page(self.source_url)
			if not self.raw:
				self.error = "Failed to fetch page"
				return False
			cache.put(self.cache_key_raw(), self.raw)

		return True

	def cleaned(self) -> str:
		if cache.has(self.cache_key_cleaned()):
			return cache.get(self.cache_key_cleaned())

		soup = BeautifulSoup(self.raw, 'html.parser')

		title_tag = soup.find('title')
		if title_tag:
			self.title = title_tag.get_text().strip()
			cache.put(self.cache_key_title(), self.title)

		for element in soup(['header','script', 'style', 'img','picture', 'source', 'head', 'polygon', 'button', 'iframe', 'svg']):
			element.decompose()

		for li in soup.find_all('li'):
			for content in li.contents:
				if isinstance(content, NavigableString) and content.strip() == '':
					content.extract()
			if len(li.contents) == 0 or (len(li.contents) == 1 and li.find('a')):
				li.decompose()
		for node in soup.find_all('ul'):
			if len(node.contents) == 0:
				node.decompose()
		for node in soup.find_all('a'):
			if len(node.contents) == 0:
				node.decompose()

		for node in soup.find_all(['span', 'em', 'i', 'b', 'li', 'ul', 'table', 'nav']):
			node.unwrap()

		for div in soup.find_all('div'):
			if not div.find(['article', 'h1', 'h2', 'h3', 'p', 'strong']):
				div.unwrap()

		for tag in soup.find_all():
			for attribute in list(tag.attrs):
				del tag[attribute]
		text = str(soup)
		text = ' '.join(text.split())
		soup = BeautifulSoup(text, 'html.parser')

		# self.text = soup.get_text(separator="\n", strip=True)
		cleaned = str(soup)
		cache.put(self.cache_key_cleaned(), cleaned)
		return cleaned


	def load_cache(self):
		data = cache.get(self.cache_key_raw())
		if data:
			self.raw = data
			self.cached = True
		else:
			self.cached = False

	def save_cache(self):
		if self.raw:
			cache.put(self.cache_key_raw(), self.raw)
			self.cached = True

	def __str__(self) -> str:
		return f"Article({self.source_name}, {self.source_url}, {self.date}, {self.title})"

	def is_from_today(self):
		age = cache.age(self.cache_key_raw())
		if age > 0:
			return False
		return True



