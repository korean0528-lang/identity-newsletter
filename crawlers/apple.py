import re
import time
import requests
from bs4 import BeautifulSoup
from .base import Article, BaseCrawler, HEADERS

BASE_URL = "https://developer.apple.com"
NEWS_URL = f"{BASE_URL}/news/"

# Only fetch body for the most recent N articles to avoid too many requests
MAX_BODY_FETCH = 30


class AppleCrawler(BaseCrawler):
    source_name = "Apple"
    language = "en"

    def fetch(self) -> list[Article]:
        articles = []
        try:
            resp = requests.get(NEWS_URL, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # Collect article links from the listing page
            candidates = []
            for item in soup.select("a.news-index-item, li.news-item, article"):
                title_tag = item.find(["h2", "h3", "h4"])
                title = title_tag.get_text(strip=True) if title_tag else ""
                if not title:
                    title = item.get_text(strip=True)[:100]

                href = item.get("href", "")
                if not href:
                    a = item.find("a")
                    href = a.get("href", "") if a else ""

                if not href or not title:
                    continue

                url = href if href.startswith("http") else BASE_URL + href
                date_tag = item.find(["time", "span"], class_=re.compile(r"date|time", re.I))
                published = date_tag.get_text(strip=True) if date_tag else ""
                candidates.append((title, url, published))

            # Fetch individual article body for recent items
            for i, (title, url, published) in enumerate(candidates[:MAX_BODY_FETCH]):
                summary = _fetch_article_body(url)
                articles.append(Article(
                    id=url,
                    source=self.source_name,
                    title=title,
                    url=url,
                    summary=summary,
                    language=self.language,
                    published=published,
                ))
                if i < len(candidates) - 1:
                    time.sleep(0.3)  # polite crawling

        except Exception as e:
            print(f"  [Apple] Scraping error: {e}")

        return articles


def _fetch_article_body(url: str) -> str:
    """Fetch an individual Apple article page and return body text (up to 2000 chars)."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Try common Apple article body selectors
        for selector in [
            "div.article-body",
            "section.article-body",
            "div.content-body",
            "main article",
            "div[class*='article']",
            "div.post-content",
            "main",
        ]:
            body = soup.select_one(selector)
            if body:
                text = body.get_text(separator=" ", strip=True)
                if len(text) > 100:
                    return text[:2000]

        # Fallback: grab all <p> tags from main content
        paragraphs = soup.select("main p, article p")
        if paragraphs:
            text = " ".join(p.get_text(strip=True) for p in paragraphs)
            if len(text) > 50:
                return text[:2000]

    except Exception as e:
        print(f"  [Apple] Body fetch error for {url}: {e}")

    return ""
