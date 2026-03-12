import os
import anthropic
from crawlers.base import Article

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def summarize(article: Article) -> Article:
    """Fill in ai_summary_en and ai_summary_ko on the article."""
    client = _get_client()
    content = f"Title: {article.title}\n\n{article.summary}"

    if article.language == "ko":
        prompt = (
            "다음 한국어 기술 블로그 글을 3문장으로 간결하게 요약해줘. "
            "불릿 포인트 없이 자연스러운 문장으로 작성해.\n\n"
            f"{content}"
        )
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        article.ai_summary_ko = msg.content[0].text.strip()
    else:
        prompt = (
            "Summarize the following tech blog article in 2-3 concise English sentences. "
            "Then provide a Korean translation of your summary. "
            "Format your response exactly as:\n"
            "EN: <English summary>\nKO: <Korean translation>\n\n"
            f"{content}"
        )
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        text = msg.content[0].text.strip()
        en_line = _extract_line(text, "EN:")
        ko_line = _extract_line(text, "KO:")
        article.ai_summary_en = en_line
        article.ai_summary_ko = ko_line

    return article


def _extract_line(text: str, prefix: str) -> str:
    for line in text.splitlines():
        if line.startswith(prefix):
            return line[len(prefix):].strip()
    return text  # fallback: return full text
