from .google import GoogleCrawler
from .meta import MetaCrawler
from .apple import AppleCrawler
from .kakao import KakaoCrawler
from .toss import TossCrawler

ALL_CRAWLERS = [
    GoogleCrawler,
    MetaCrawler,
    AppleCrawler,
    KakaoCrawler,
    TossCrawler,
]
