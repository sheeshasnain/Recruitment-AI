import base64
from email.message import EmailMessage

from googleapiclient.discovery import build

from backend.services.google_auth_service import (
    get_google_credentials,
)


def send_email(
    *,
    recipient: str,
    subject: str,
    body: str,
) -> dict:

    credentials = get_google_credentials()

    service = build(
        "gmail",
        "v1",
        credentials=credentials,
    )

    message = EmailMessage()

    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    result = (
        service.users()
        .messages()
        .send(
            userId="me",
            body={
                "raw": encoded_message,
            },
        )
        .execute()
    )

    return {
        "message_id": result.get("id"),
        "thread_id": result.get("threadId"),
    }