from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Article:
    id: str           # unique identifier (URL or GUID)
    source: str       # e.g. "Google", "Toss"
    title: str
    url: str
    summary: str      # first ~500 chars of body, used for keyword matching
    language: str     # "en" or "ko"
    published: str    # ISO date string or empty
    keywords_found: list[str] = field(default_factory=list)
    # Filled in by summarizer
    ai_summary_en: str = ""
    ai_summary_ko: str = ""


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


class BaseCrawler(ABC):
    source_name: str = ""
    language: str = "en"

    @abstractmethod
    def fetch(self) -> list[Article]:
        """Return a list of recently published articles."""
        ...
