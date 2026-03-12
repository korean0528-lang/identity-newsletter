import re
import requests
from bs4 import BeautifulSoup
from .base import Article, BaseCrawler, HEADERS

BASE_URL = "https://developer.apple.com"
NEWS_URL = f"{BASE_URL}/news/"


class AppleCrawler(BaseCrawler):
    source_name = "Apple"
    language = "en"

    def fetch(self) -> list[Article]:
        articles = []
        try:
            resp = requests.get(NEWS_URL, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # Apple developer news uses article cards
            for item in soup.select("a.news-index-item, li.news-item, article"):
                title_tag = item.find(["h2", "h3", "h4"])
                title = title_tag.get_text(strip=True) if title_tag else ""
                if not title:
                    # fallback: use link text
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

                desc_tag = item.find("p")
                summary = desc_tag.get_text(strip=True)[:500] if desc_tag else title

                articles.append(Article(
                    id=url,
                    source=self.source_name,
                    title=title,
                    url=url,
                    summary=summary,
                    language=self.language,
                    published=published,
                ))
        except Exception as e:
            print(f"  [Apple] Scraping error: {e}")

        return articles
