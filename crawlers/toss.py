import re
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

            for a in soup.find_all("a", href=ARTICLE_PATTERN):
                href = a["href"]
                url = BASE_URL + href
                if url in seen:
                    continue
                seen.add(url)

                # Title is stored in data attribute; excerpt in the last div
                title = a.get("data-log-item_title", "").strip()
                if not title:
                    # fallback: longest text node > 10 chars
                    lines = [t.strip() for t in a.stripped_strings]
                    title = next((l for l in lines if len(l) > 10), "")
                if not title:
                    continue

                # Excerpt lives in the last content div (class ending in b8)
                divs = a.find_all("div")
                desc_div = divs[-1] if divs else None
                summary = desc_div.get_text(strip=True)[:500] if desc_div else title

                articles.append(Article(
                    id=url,
                    source=self.source_name,
                    title=title,
                    url=url,
                    summary=summary,
                    language=self.language,
                    published="",
                ))
        except Exception as e:
            print(f"  [Toss] Scraping error: {e}")

        return articles
