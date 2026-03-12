import feedparser
from .base import Article, BaseCrawler

FEED_URL = "https://tech.kakao.com/feed/"


class KakaoCrawler(BaseCrawler):
    source_name = "Kakao"
    language = "ko"

    def fetch(self) -> list[Article]:
        articles = []
        try:
            feed = feedparser.parse(FEED_URL)
            for entry in feed.entries:
                url = entry.get("link", "")
                if not url:
                    continue

                summary = entry.get("description", "") or entry.get("summary", "")
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
            print(f"  [Kakao] Feed error: {e}")

        return articles


def _strip_tags(html: str) -> str:
    import re
    return re.sub(r"<[^>]+>", " ", html).strip()
