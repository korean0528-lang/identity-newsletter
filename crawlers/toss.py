import re
import time
import requests
from bs4 import BeautifulSoup
from .base import Article, BaseCrawler, HEADERS

BASE_URL = "https://toss.tech"
BLOG_URL = f"{BASE_URL}/"

# toss.tech article URLs look like /article/{slug} or /article/{number}
ARTICLE_PATTERN = re.compile(r"^/article/[^/]+$")


class TossCrawler(BaseCrawler):
    source_name = "Toss"
    language = "ko"

    def fetch(self) -> list[Article]:
        articles = []
        seen: set[str] = set()

        try:
            resp = requests.get(BLOG_URL, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            candidates = []
            for a in soup.find_all("a", href=ARTICLE_PATTERN):
                href = a["href"]
                url = BASE_URL + href
                if url in seen:
                    continue
                seen.add(url)

                title = a.get("data-log-item_title", "").strip()
                if not title:
                    lines = [t.strip() for t in a.stripped_strings]
                    title = next((l for l in lines if len(l) > 10), "")
                if not title:
                    continue

                candidates.append((title, url))

            for i, (title, url) in enumerate(candidates):
                summary = _fetch_article_body(url)
                articles.append(Article(
                    id=url,
                    source=self.source_name,
                    title=title,
                    url=url,
                    summary=summary,
                    language=self.language,
                    published="",
                ))
                if i < len(candidates) - 1:
                    time.sleep(0.3)

        except Exception as e:
            print(f"  [Toss] Scraping error: {e}")

        return articles


def _fetch_article_body(url: str) -> str:
    """Fetch a Toss article page and return body text (up to 2000 chars)."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Try common article body selectors for Next.js sites
        for selector in [
            "article",
            "div.article-content",
            "div.post-content",
            "div[class*='content']",
            "main",
        ]:
            body = soup.select_one(selector)
            if body:
                text = body.get_text(separator=" ", strip=True)
                if len(text) > 100:
                    return text[:2000]

        # Fallback: all paragraphs
        paragraphs = soup.select("p")
        if paragraphs:
            text = " ".join(p.get_text(strip=True) for p in paragraphs)
            if len(text) > 50:
                return text[:2000]

    except Exception as e:
        print(f"  [Toss] Body fetch error for {url}: {e}")

    return ""
