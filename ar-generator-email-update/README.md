# AR Generator Email Update

Overlay image for `ar-generator` that changes the accomplishment report email flow.

Behavior:

- Sends the AR PDF to `andrew.mendoza@dict.gov.ph` for review and cosign.
- Sets `reply_to` to `matthewjericho.silva@dict.gov.ph`.
- Sends a Telegram confirmation to the configured `AR_TELEGRAM_CHAT_ID` after Resend accepts the email.
- Falls back to `TELEGRAM_CHAT_ID` only if the AR-specific Telegram variables are not configured.

This overlay does not change the scheduler or the report generation routes.
