import re
from crawlers.base import Article

# 단어 경계가 필요한 키워드 (부분 문자열 오탐 방지)
WORD_BOUNDARY_KEYWORDS = [
    "passkey", "fido", "webauthn", "oauth", "sso",
    "openid", "pkce", "2fa", "mfa",
]

# 부분 포함으로 매칭하는 키워드
SUBSTRING_KEYWORDS = [
    # Authentication / Login
    "sign in with", "social login", "biometric",
    "two-factor", "multi-factor", "authentication", "sign-on",
    "login", "sign-in", "sign in", "passwordless",
    # Privacy / Security
    "privacy", "gdpr", "ccpa", "account security", "identity",
    "data protection", "user data", "consent",
    # Account / Member
    "account", "membership", "profile", "credential",
    # Korean
    "패스키", "파이도", "인증", "소셜 로그인", "개인정보",
    "간편 로그인", "본인인증", "이중인증", "계정 보안", "로그인",
    "회원", "생체인증", "비밀번호", "아이디", "계정",
    # 문서 / 신원
    "인증서", "신분증", "전자문서", "지갑", "전자지갑",
]


def filter_articles(articles: list[Article]) -> list[Article]:
    matched = []
    for article in articles:
        found = _find_keywords(article.title + " " + article.summary)
        if found:
            article.keywords_found = found
            matched.append(article)
    return matched


def _find_keywords(text: str) -> list[str]:
    lower = text.lower()
    found = []
    for kw in WORD_BOUNDARY_KEYWORDS:
        pattern = r"\b" + re.escape(kw) + r"\b"
        if re.search(pattern, lower):
            found.append(kw)
    for kw in SUBSTRING_KEYWORDS:
        if kw in lower:
            found.append(kw)
    return found
