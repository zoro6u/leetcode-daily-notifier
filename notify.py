"""Fetch today's LeetCode daily question and send it to Telegram."""
import os
import sys

import requests

LEETCODE_GRAPHQL = "https://leetcode.com/graphql"
QUERY = """
query questionOfToday {
  activeDailyCodingChallengeQuestion {
    date
    link
    question {
      title
      difficulty
      acRate
      topicTags { name }
    }
  }
}
"""

DIFFICULTY_EMOJI = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}


def send_telegram(text: str) -> None:
    token = os.environ["TG_TOKEN"]
    chat_id = os.environ["TG_CHAT_ID"]
    r = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data={"chat_id": chat_id, "text": text, "disable_web_page_preview": False},
        timeout=15,
    )
    r.raise_for_status()


def fetch_daily() -> dict:
    r = requests.post(
        LEETCODE_GRAPHQL,
        json={"query": QUERY, "operationName": "questionOfToday"},
        headers={"Content-Type": "application/json", "Referer": "https://leetcode.com"},
        timeout=15,
    )
    r.raise_for_status()
    data = r.json()["data"]["activeDailyCodingChallengeQuestion"]
    if not data:
        raise ValueError("Empty response from LeetCode")
    return data


def format_message(d: dict) -> str:
    q = d["question"]
    emoji = DIFFICULTY_EMOJI.get(q["difficulty"], "⚪")
    tags = ", ".join(t["name"] for t in q["topicTags"]) or "—"
    return (
        f"📅 LeetCode Daily — {d['date']}\n\n"
        f"{emoji} {q['title']} ({q['difficulty']})\n"
        f"🏷 {tags}\n"
        f"✅ Acceptance: {q['acRate']:.1f}%\n\n"
        f"https://leetcode.com{d['link']}"
    )


def main() -> None:
    try:
        msg = format_message(fetch_daily())
    except Exception as e:  # LeetCode endpoint is unofficial and may change
        send_telegram(f"⚠️ Failed to fetch LeetCode daily question:\n{e}")
        sys.exit(1)
    send_telegram(msg)
    print("Sent:\n" + msg)


if __name__ == "__main__":
    main()
