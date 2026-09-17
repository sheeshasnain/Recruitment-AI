from backend.services.calendar_service import (
    create_calendar_event,
)


def create_interview_calendar_event(
    *,
    title: str,
    description: str,
    start_datetime: str,
    end_datetime: str,
    timezone: str,
    candidate_email: str,
) -> dict:

    return create_calendar_event(
        summary=title,
        description=description,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        timezone=timezone,
        attendee_email=candidate_email,
    )