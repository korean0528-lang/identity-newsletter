import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from crawlers.base import Article

SOURCE_COLORS = {
    "Google": "#4285F4",
    "Meta": "#1877F2",
    "Apple": "#555555",
    "Kakao": "#FEE500",
    "Toss": "#0064FF",
}


def send_newsletter(articles: list[Article]) -> None:
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASS", "")
    email_from = os.environ.get("EMAIL_FROM", smtp_user)
    email_to_raw = os.environ.get("EMAIL_TO", "")
    recipients = [r.strip() for r in email_to_raw.split(",") if r.strip()]

    if not recipients:
        print("  [mailer] EMAIL_TO not set — skipping send")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    subject = f"[Identity Tech Newsletter] {today} — {len(articles)}건 새 소식"

    html_body = _build_html(articles, today)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = email_from
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(email_from, recipients, msg.as_string())

    print(f"  [mailer] Email sent to {recipients}")


def _build_html(articles: list[Article], today: str) -> str:
    # Group by source
    grouped: dict[str, list[Article]] = {}
    for art in articles:
        grouped.setdefault(art.source, []).append(art)

    sections = ""
    for source, items in grouped.items():
        color = SOURCE_COLORS.get(source, "#333333")
        cards = ""
        for art in items:
            kw_badges = " ".join(
                f'<span style="background:#f0f0f0;padding:2px 6px;border-radius:4px;font-size:11px">{kw}</span>'
                for kw in art.keywords_found[:5]
            )
            summary_block = ""
            if art.ai_summary_en:
                summary_block += (
                    f'<p style="margin:6px 0;font-size:13px;color:#333">'
                    f'<strong>EN</strong> {art.ai_summary_en}</p>'
                )
            if art.ai_summary_ko:
                summary_block += (
                    f'<p style="margin:6px 0;font-size:13px;color:#333">'
                    f'<strong>KO</strong> {art.ai_summary_ko}</p>'
                )

            cards += f"""
            <div style="border:1px solid #e0e0e0;border-radius:8px;padding:14px;margin-bottom:12px;background:#fff">
              <a href="{art.url}" style="font-size:15px;font-weight:bold;color:#1a1a1a;text-decoration:none">
                {art.title}
              </a>
              <div style="margin:4px 0 8px;font-size:11px;color:#888">{art.published}</div>
              {summary_block}
              <div style="margin-top:8px">{kw_badges}</div>
              <div style="margin-top:8px">
                <a href="{art.url}" style="font-size:12px;color:{color}">원문 보기 →</a>
              </div>
            </div>
            """

        sections += f"""
        <div style="margin-bottom:32px">
          <h2 style="margin:0 0 12px;padding:8px 12px;background:{color};color:{'#000' if source == 'Kakao' else '#fff'};
                     border-radius:6px;font-size:16px">{source}</h2>
          {cards}
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
    <body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f5f5f5;margin:0;padding:0">
      <div style="max-width:640px;margin:24px auto;background:#f5f5f5">
        <div style="background:#1a1a1a;color:#fff;padding:20px 24px;border-radius:8px 8px 0 0">
          <h1 style="margin:0;font-size:20px">Identity Tech Newsletter</h1>
          <p style="margin:4px 0 0;font-size:13px;color:#aaa">{today} — 인증/로그인/개인정보 동향</p>
        </div>
        <div style="padding:20px 0">
          {sections}
        </div>
        <div style="padding:12px 0;text-align:center;font-size:11px;color:#aaa">
          자동 생성된 뉴스레터입니다 · powered by Claude API
        </div>
      </div>
    </body>
    </html>
    """
