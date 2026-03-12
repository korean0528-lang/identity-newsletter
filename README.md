# Identity Tech Newsletter Bot

Google / Meta / Apple / Kakao / Toss의 기술 블로그 및 개발자 센터에서
**인증·로그인·개인정보** 관련 새 글을 감지하여 이메일로 발송하는 뉴스레터 봇.

---

## 주요 기능

- 다섯 개 소스 크롤링 (RSS + 스크래핑)
- 키워드 자동 필터링 (passkey, FIDO, OAuth, 소셜 로그인, 개인정보 등)
- Claude API로 영문 글 자동 요약 + 한국어 번역 (한국어 글은 요약만)
- GitHub Gist로 중복 발송 방지 (이미 보낸 글 기록)
- GitHub Actions 평일 09:00 KST 자동 실행

---

## 설정 방법

### 1. Gist 생성 (최초 1회)

1. https://gist.github.com 접속
2. 파일명: `identity_newsletter_seen.json`
3. 내용: `{"ids": []}`
4. **Secret gist** 로 생성
5. URL에서 Gist ID 복사 (`gist.github.com/{user}/{GIST_ID}`)

### 2. GitHub Secrets 설정

레포지토리 → Settings → Secrets and variables → Actions → New repository secret

| Secret 이름 | 값 |
|------------|---|
| `ANTHROPIC_API_KEY` | [Anthropic Console](https://console.anthropic.com) 에서 발급 |
| `GIST_ID` | 위에서 복사한 Gist ID |
| `SMTP_USER` | Gmail 주소 (예: yourname@gmail.com) |
| `SMTP_PASS` | Gmail **앱 비밀번호** (2단계 인증 필요, [여기서 발급](https://myaccount.google.com/apppasswords)) |
| `EMAIL_TO` | 수신 주소 (콤마로 여러 명 가능) |

> `GITHUB_TOKEN`은 Actions에서 자동 제공되므로 별도 설정 불필요

### 3. 로컬 테스트

```bash
pip install -r requirements.txt

# .env 파일 생성 (로컬 테스트용)
export ANTHROPIC_API_KEY=sk-ant-...
export GIST_ID=your_gist_id
export GITHUB_TOKEN=ghp_...
export SMTP_USER=your@gmail.com
export SMTP_PASS=xxxx-xxxx-xxxx-xxxx
export EMAIL_TO=recipient@example.com

# Dry run (이메일 발송 없이 터미널 출력)
python main.py --dry-run

# 이미 본 글도 다시 처리하고 싶을 때
python main.py --dry-run --force
```

### 4. GitHub Actions 수동 실행

Actions 탭 → Identity Tech Newsletter → Run workflow

- `dry_run: true` → 이메일 없이 로그만 확인
- `force: true` → 이미 발송된 글도 재처리

---

## 프로젝트 구조

```
identity-newsletter/
├── .github/workflows/newsletter.yml  # Actions 스케줄
├── crawlers/
│   ├── base.py        # Article 데이터클래스, BaseCrawler
│   ├── google.py      # RSS (Developers Blog, Security, Android)
│   ├── meta.py        # RSS (Engineering, About)
│   ├── apple.py       # Scraping (developer.apple.com/news)
│   ├── kakao.py       # Scraping (tech.kakao.com)
│   └── toss.py        # Scraping (toss.tech)
├── core/
│   ├── filters.py     # 키워드 필터링
│   ├── summarizer.py  # Claude API 요약+번역
│   ├── state.py       # GitHub Gist 상태 관리
│   └── mailer.py      # HTML 이메일 발송
├── main.py            # 실행 엔트리포인트
└── requirements.txt
```

---

## 이메일 출력 예시

```
[Google] Sign in with Google: Passkey Support for Enterprise
링크: https://developers.googleblog.com/...
EN: Google has expanded passkey support to enterprise accounts...
KO: 구글이 기업 계정에 대한 패스키 지원을 확대했습니다...
키워드: passkey, sign in with, authentication

[Toss] 토스의 생체인증 기반 간편 로그인 개선
링크: https://toss.tech/...
KO: 토스는 이번 업데이트에서 Face ID 기반 로그인을 전면 적용했습니다...
키워드: 간편 로그인, 생체인증
```

---

## 키워드 목록

`core/filters.py`의 `KEYWORDS` 리스트를 수정하여 추가/제거 가능.

현재 키워드: `passkey`, `fido`, `webauthn`, `oauth`, `sso`, `social login`,
`privacy`, `gdpr`, `identity`, `2fa`, `mfa`, `biometric`, `패스키`, `소셜 로그인`,
`개인정보`, `간편 로그인`, `본인인증`, `이중인증` 등
