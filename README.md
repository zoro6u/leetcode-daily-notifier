# LeetCode Daily Notifier

Sends today's LeetCode daily question to Telegram every morning via GitHub Actions.

## Setup
1. Create a bot with @BotFather on Telegram → copy the token.
2. Send any message to your bot, then open
   `https://api.telegram.org/bot<TOKEN>/getUpdates` and copy `chat.id`.
3. In the repo: Settings → Secrets and variables → Actions → add
   `TG_TOKEN` and `TG_CHAT_ID`.
4. Actions tab → "Daily LeetCode Notifier" → Run workflow (to test).

## Notes
- Uses LeetCode's unofficial GraphQL endpoint; it may change without notice.
  On failure, the script sends you a warning message instead of failing silently.
- Scheduled runs can be delayed by GitHub during busy periods.
- GitHub may disable scheduled workflows in repos with no activity for a long time;
  re-enable from the Actions tab if that happens.
