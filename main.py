#!/usr/bin/env python3
"""
Identity Tech Newsletter Bot
크롤링 → 필터링 → Claude 요약/번역 → 이메일 발송

Usage:
  python main.py              # 정상 실행
  python main.py --dry-run    # 이메일 발송 없이 터미널 출력만
  python main.py --force      # Gist 상태 무시하고 모든 매칭 글 처리
"""
import argparse
import sys
import time

from crawlers import ALL_CRAWLERS
from core.filters import filter_articles
from core.mailer import send_newsletter
from core.state import load_seen_ids, save_seen_ids
from core.summarizer import summarize


def main(dry_run: bool = False, force: bool = False) -> None:
    print("=" * 60)
    print("Identity Tech Newsletter Bot")
    print("=" * 60)

    # 1. Load seen IDs from Gist
    seen_ids = set() if force else load_seen_ids()
    print(f"\n[1] 이미 처리된 글: {len(seen_ids)}건")

    # 2. Crawl all sources
    print("\n[2] 크롤링 시작...")
    all_articles = []
    for CrawlerClass in ALL_CRAWLERS:
        crawler = CrawlerClass()
        try:
            items = crawler.fetch()
            print(f"  [{crawler.source_name}] {len(items)}건 수집")
            all_articles.extend(items)
        except Exception as e:
            print(f"  [{crawler.source_name}] 오류: {e}")
        time.sleep(1)

    print(f"\n  총 {len(all_articles)}건 수집 완료")

    # 3. Keyword filtering
    print("\n[3] 키워드 필터링...")
    matched = filter_articles(all_articles)
    print(f"  키워드 매칭: {len(matched)}건")

    # 4. Exclude already-seen articles
    new_articles = [a for a in matched if a.id not in seen_ids]
    print(f"  신규 (미발송): {len(new_articles)}건")

    if not new_articles:
        print("\n새로운 글이 없습니다. 종료합니다.")
        return

    # 5. Summarize & translate with Claude
    print(f"\n[4] Claude API 요약/번역 중... ({len(new_articles)}건)")
    summarized = []
    for i, article in enumerate(new_articles, 1):
        print(f"  ({i}/{len(new_articles)}) {article.source}: {article.title[:60]}...")
        try:
            summarized.append(summarize(article))
        except Exception as e:
            print(f"    요약 실패: {e}")
            summarized.append(article)  # include even without summary

    # 6. Send or dry-run
    if dry_run:
        print("\n[DRY RUN] 이메일 발송 없이 결과 출력:")
        print("-" * 60)
        for art in summarized:
            print(f"\n[{art.source}] {art.title}")
            print(f"  URL: {art.url}")
            if art.ai_summary_en:
                print(f"  EN: {art.ai_summary_en}")
            if art.ai_summary_ko:
                print(f"  KO: {art.ai_summary_ko}")
            print(f"  키워드: {', '.join(art.keywords_found)}")
    else:
        print("\n[5] 이메일 발송 중...")
        send_newsletter(summarized)

    # 7. Update seen IDs
    if not dry_run:
        new_seen = seen_ids | {a.id for a in new_articles}
        save_seen_ids(new_seen)
    else:
        print("\n[DRY RUN] Gist 상태 업데이트 생략")

    print(f"\n완료! 처리된 글: {len(summarized)}건")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Identity Tech Newsletter Bot")
    parser.add_argument("--dry-run", action="store_true", help="이메일 발송 없이 터미널 출력만")
    parser.add_argument("--force", action="store_true", help="Gist 상태 무시, 모든 매칭 글 처리")
    args = parser.parse_args()

    try:
        main(dry_run=args.dry_run, force=args.force)
    except KeyboardInterrupt:
        print("\n중단됨")
        sys.exit(0)
