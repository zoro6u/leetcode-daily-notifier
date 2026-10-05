"""LeetCode daily notifier for Telegram.

Usage:
  python notify.py morning   # send today's question
  python notify.py evening   # remind if today's question isn't solved yet
"""
import os
import sys
from datetime import datetime, timezone

import requests

LEETCODE_GRAPHQL = "https://leetcode.com/graphql"
HEADERS = {"Content-Type": "application/json", "Referer": "https://leetcode.com"}
DIFFICULTY_EMOJI = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}

DAILY_QUERY = """
query questionOfToday {
  activeDailyCodingChallengeQuestion {
    date
    link
    question { title titleSlug difficulty acRate topicTags { name } }
  }
}
"""

RECENT_AC_QUERY = """
query recentAcSubmissions($username: String!, $limit: Int!) {
  recentAcSubmissionList(username: $username, limit: $limit) {
    titleSlug
    timestamp
  }
}
"""


def gql(query: str, variables: dict | None = None) -> dict:
    r = requests.post(
        LEETCODE_GRAPHQL,
        json={"query": query, "variables": variables or {}},
        headers=HEADERS,
        timeout=15,
    )
    r.raise_for_status()
    body = r.json()
    if body.get("errors"):
        raise ValueError(body["errors"])
    return body["data"]


def send_telegram(text: str) -> None:
    r = requests.post(
        f"https://api.telegram.org/bot{os.environ['TG_TOKEN']}/sendMessage",
        data={"chat_id": os.environ["TG_CHAT_ID"], "text": text},
        timeout=15,
    )
    r.raise_for_status()


def fetch_daily() -> dict:
    data = gql(DAILY_QUERY)["activeDailyCodingChallengeQuestion"]
    if not data:
        raise ValueError("Empty daily question response")
    return data


def solved_today(username: str, slug: str) -> bool:
    """True if `slug` has an accepted submission since 00:00 UTC today."""
    subs = gql(RECENT_AC_QUERY, {"username": username, "limit": 20})
    subs = subs.get("recentAcSubmissionList") or []
    start_of_day = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    ).timestamp()
    return any(
        s["titleSlug"] == slug and int(s["timestamp"]) >= start_of_day for s in subs
    )


def morning() -> None:
    d = fetch_daily()
    q = d["question"]
    tags = ", ".join(t["name"] for t in q["topicTags"]) or "—"
    send_telegram(
        f"📅 LeetCode Daily — {d['date']}\n\n"
        f"{DIFFICULTY_EMOJI.get(q['difficulty'], '⚪')} {q['title']} ({q['difficulty']})\n"
        f"🏷 {tags}\n"
        f"✅ Acceptance: {q['acRate']:.1f}%\n\n"
        f"https://leetcode.com{d['link']}"
    )


def evening() -> None:
    d = fetch_daily()
    q = d["question"]
    if solved_today(os.environ["LC_USERNAME"], q["titleSlug"]):
        send_telegram(f"🔥 Done for today — you solved “{q['title']}”. Nice work!")
    else:
        send_telegram(
            f"⏰ You haven't solved today's question yet!\n\n"
            f"{q['title']} ({q['difficulty']})\n"
            f"https://leetcode.com{d['link']}"
        )


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "morning"
    handlers = {"morning": morning, "evening": evening}
    if mode not in handlers:
        sys.exit(f"Unknown mode: {mode}")
    try:
        handlers[mode]()
    except Exception as e:  # LeetCode's GraphQL is unofficial and may change
        send_telegram(f"⚠️ LeetCode notifier ({mode}) failed:\n{e}")
        sys.exit(1)
    print(f"{mode}: sent")


if __name__ == "__main__":
    main()
