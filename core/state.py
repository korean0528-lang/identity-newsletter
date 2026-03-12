"""
GitHub Gist-based state management for tracking seen article IDs.

Gist file layout:
  seen_ids.json  →  {"ids": ["url1", "url2", ...]}
"""
import json
import os
import requests

GIST_FILENAME = "identity_newsletter_seen.json"


def load_seen_ids() -> set[str]:
    gist_id = os.environ.get("GIST_ID", "")
    token = os.environ.get("GITHUB_TOKEN", "")
    if not gist_id or not token:
        print("  [state] GIST_ID or GITHUB_TOKEN not set — starting fresh")
        return set()

    try:
        resp = requests.get(
            f"https://api.github.com/gists/{gist_id}",
            headers=_auth_headers(token),
            timeout=15,
        )
        resp.raise_for_status()
        files = resp.json().get("files", {})
        file_data = files.get(GIST_FILENAME, {})
        content = file_data.get("content", "{}")
        data = json.loads(content)
        return set(data.get("ids", []))
    except Exception as e:
        print(f"  [state] Failed to load Gist state: {e}")
        return set()


def save_seen_ids(ids: set[str]) -> None:
    gist_id = os.environ.get("GIST_ID", "")
    token = os.environ.get("GITHUB_TOKEN", "")
    if not gist_id or not token:
        print("  [state] GIST_ID or GITHUB_TOKEN not set — state not saved")
        return

    payload = {
        "files": {
            GIST_FILENAME: {
                "content": json.dumps({"ids": sorted(ids)}, ensure_ascii=False, indent=2)
            }
        }
    }
    try:
        resp = requests.patch(
            f"https://api.github.com/gists/{gist_id}",
            headers=_auth_headers(token),
            json=payload,
            timeout=15,
        )
        resp.raise_for_status()
        print(f"  [state] Saved {len(ids)} seen IDs to Gist")
    except Exception as e:
        print(f"  [state] Failed to save Gist state: {e}")


def _auth_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
