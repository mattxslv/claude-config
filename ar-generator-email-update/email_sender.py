import os

import requests
import resend

REVIEWER_EMAIL = os.environ.get("AR_REVIEWER_EMAIL", "andrew.mendoza@dict.gov.ph")
REPORT_OWNER_EMAIL = os.environ.get("AR_OWNER_EMAIL", "matthewjericho.silva@dict.gov.ph")
SENDER = os.environ.get("AR_SENDER_EMAIL", "noreply@dict.gov.ph")
REVIEWER_NAME = os.environ.get("AR_REVIEWER_NAME", "Sir Andrew")
REPORT_OWNER_NAME = os.environ.get("AR_OWNER_NAME", "Matthew Jericho Silva")


def send_telegram_confirmation(period: str, resend_response: dict | None) -> None:
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        return

    resend_id = resend_response.get("id") if isinstance(resend_response, dict) else None
    message = (
        "Accomplishment Report emailed for review.\n\n"
        f"Period: {period}\n"
        f"Sent to: {REVIEWER_EMAIL}\n"
        f"Instruction: Please review and cosign first, then send the finalized copy back to {REPORT_OWNER_EMAIL} for upload."
    )
    if resend_id:
        message += f"\nResend ID: {resend_id}"

    try:
        requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={"chat_id": chat_id, "text": message, "disable_web_page_preview": True},
            timeout=30,
        ).raise_for_status()
    except Exception as error:
        print(f"telegram_confirmation_failed error={error}", flush=True)


def send_report_email(api_key: str, pdf_bytes: bytes, period: str) -> None:
    resend.api_key = api_key

    filename = f"AR - Silva, Matthew Jericho - {period}.pdf"
    response = resend.Emails.send({
        "from": SENDER,
        "to": [REVIEWER_EMAIL],
        "reply_to": [REPORT_OWNER_EMAIL],
        "subject": f"Accomplishment Report for Review and Cosign - {period}",
        "text": (
            f"Good day {REVIEWER_NAME},\n\n"
            f"Please find attached the Accomplishment Report of {REPORT_OWNER_NAME} for the period of {period}.\n\n"
            "Kindly review and cosign the report first. Once signed, please send the finalized copy "
            f"back to {REPORT_OWNER_NAME} at {REPORT_OWNER_EMAIL} so he can upload it to the required system.\n\n"
            "Thank you.\n\n"
            "This was generated automatically."
        ),
        "attachments": [
            {
                "filename": filename,
                "content": list(pdf_bytes),
            }
        ],
    })
    send_telegram_confirmation(period, response)
