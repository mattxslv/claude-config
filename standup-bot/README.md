# Telegram Daily Standup Bot

Sends a daily standup draft to Telegram every Monday to Thursday at 9:00 AM PHT.

Message format:

```text
Monday, May 18, 2026

PEMEDES
Yesterday:
- ...
Today:
- ...
Blockers:
- None at the moment.

DTAP
Yesterday:
- ...
Today:
- ...
Blockers:
- None at the moment.

Startup PH
Yesterday:
- ...
Today:
- ...
Blockers:
- None at the moment.
```

Required environment variables:

```env
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
GITHUB_TOKEN=
GEMINI_API_KEY=
GITHUB_AUTHOR=mattxslv
```

Optional environment variables:

```env
TIMEZONE=Asia/Manila
LOOKBACK_DAYS=3
```

Schedule for Cloud Scheduler in UTC:

```cron
0 1 * * 1-4
```
