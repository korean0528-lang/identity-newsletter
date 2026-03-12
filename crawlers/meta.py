import feedparser
from .base import Article, BaseCrawler

FEEDS = [
    "https://engineering.fb.com/feed/",
    "https://about.fb.com/news/feed/",
]


class MetaCrawler(BaseCrawler):
    source_name = "Meta"
    language = "en"

    def fetch(self) -> list[Article]:
        articles = []
        seen_urls: set[str] = set()

        for feed_url in FEEDS:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries:
                    url = entry.get("link", "")
                    if not url or url in seen_urls:
                        continue
                    seen_urls.add(url)

                    summary = entry.get("summary", "") or ""
                    summary = _strip_tags(summary)[:500]

                    articles.append(Article(
                        id=url,
                        source=self.source_name,
                        title=entry.get("title", ""),
                        url=url,
                        summary=summary,
                        language=self.language,
                        published=entry.get("published", ""),
                    ))
            except Exception as e:
                print(f"  [Meta] Feed error ({feed_url}): {e}")

        return articles


def _strip_tags(html: str) -> str:
    import re
    return re.sub(r"<[^>]+>", " ", html).strip()
