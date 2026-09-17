from uuid import uuid4

from googleapiclient.discovery import build

from backend.services.google_auth_service import (
    get_google_credentials,
)


def create_calendar_event(
    *,
    summary: str,
    description: str,
    start_datetime: str,
    end_datetime: str,
    timezone: str,
    attendee_email: str,
) -> dict:

    credentials = get_google_credentials()

    service = build(
        "calendar",
        "v3",
        credentials=credentials,
    )

    event = {
        "summary": summary,
        "description": description,
        "start": {
            "dateTime": start_datetime,
            "timeZone": timezone,
        },
        "end": {
            "dateTime": end_datetime,
            "timeZone": timezone,
        },
        "attendees": [
            {
                "email": attendee_email,
            }
        ],
        "conferenceData": {
            "createRequest": {
                "requestId": str(uuid4()),
                "conferenceSolutionKey": {
                    "type": "hangoutsMeet"
                },
            }
        },
    }

    created_event = (
        service.events()
        .insert(
            calendarId="primary",
            body=event,
            conferenceDataVersion=1,
            sendUpdates="none",
        )
        .execute()
    )

    meeting_link = (
        created_event
        .get("conferenceData", {})
        .get("entryPoints", [{}])[0]
        .get("uri")
    )

    return {
        "event_id": created_event.get("id"),
        "html_link": created_event.get("htmlLink"),
        "meeting_link": meeting_link,
    }