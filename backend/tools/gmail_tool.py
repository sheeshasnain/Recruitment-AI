from backend.services.gmail_service import (
    send_email,
)


def send_candidate_email(
    *,
    recipient: str,
    subject: str,
    body: str,
) -> dict:

    return send_email(
        recipient=recipient,
        subject=subject,
        body=body,
    )