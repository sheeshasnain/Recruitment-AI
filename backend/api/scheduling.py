from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.agents.scheduling_agent import (
    prepare_calendar_event,
)
from backend.core.database import get_db
from backend.models.application import Application
from backend.models.candidate import Candidate
from backend.models.interview import Interview
from backend.models.interview_schedule import (
    InterviewSchedule,
)
from backend.models.job import Job
from backend.models.tool_action_log import ToolActionLog
from backend.schemas.scheduling import (
    ScheduleApprovalRequest,
    ScheduleProposalRequest,
)
from backend.services.status_service import (
    update_application_status,
)
from backend.tools.calendar_tool import (
    create_interview_calendar_event,
)


router = APIRouter(
    prefix="/api/v1/scheduling",
    tags=["Scheduling"],
)

@router.post("/interviews/{interview_id}/propose")
async def propose_schedule(
    interview_id: int,
    payload: ScheduleProposalRequest,
    db: Session = Depends(get_db),
):

    interview = db.get(
        Interview,
        interview_id,
    )

    if not interview:
        raise HTTPException(
            status_code=404,
            detail="Interview not found.",
        )

    application = db.get(
        Application,
        interview.application_id,
    )

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found.",
        )

    if not application.approved_for_interview:
        raise HTTPException(
            status_code=403,
            detail="Recruiter approval is required.",
        )

    existing = (
        db.query(InterviewSchedule)
        .filter(
            InterviewSchedule.interview_id
            == interview.id
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="A schedule already exists for this interview.",
        )

    candidate = db.get(
        Candidate,
        application.candidate_id,
    )

    job = db.get(
        Job,
        application.job_id,
    )

    draft = await prepare_calendar_event(
        candidate_name=candidate.name,
        job_title=job.title,
        scheduled_start=payload.scheduled_start.isoformat(),
        scheduled_end=payload.scheduled_end.isoformat(),
        timezone=payload.timezone,
    )

    schedule = InterviewSchedule(
        interview_id=interview.id,
        scheduled_start=payload.scheduled_start,
        scheduled_end=payload.scheduled_end,
        timezone=payload.timezone,
        status="pending_approval",

        event_title=draft.title,
        event_description=draft.description,
        candidate_message=draft.candidate_message,
    )

    db.add(schedule)
    db.commit()
    db.refresh(schedule)

    return {
        "schedule_id": schedule.id,
        "interview_id": interview.id,
        "status": schedule.status,
        "title": draft.title,
        "description": draft.description,
        "candidate_message": draft.candidate_message,
        "scheduled_start": schedule.scheduled_start,
        "scheduled_end": schedule.scheduled_end,
        "timezone": schedule.timezone,
    }

@router.post("/schedules/{schedule_id}/approve")
def approve_schedule(
    schedule_id: int,
    payload: ScheduleApprovalRequest,
    db: Session = Depends(get_db),
):

    schedule = db.get(
        InterviewSchedule,
        schedule_id,
    )

    if not schedule:
        raise HTTPException(
            status_code=404,
            detail="Schedule not found.",
        )

    if schedule.status != "pending_approval":
        raise HTTPException(
            status_code=409,
            detail="Schedule is not awaiting approval.",
        )

    if not payload.approved:
        schedule.status = "rejected"
        db.commit()

        return {
            "schedule_id": schedule.id,
            "status": "rejected",
        }

    interview = db.get(
        Interview,
        schedule.interview_id,
    )

    application = db.get(
        Application,
        interview.application_id,
    )

    candidate = db.get(
        Candidate,
        application.candidate_id,
    )

    try:
        result = create_interview_calendar_event(
            title=schedule.event_title,
            description=schedule.event_description,
            start_datetime=schedule.scheduled_start.isoformat(),
            end_datetime=schedule.scheduled_end.isoformat(),
            timezone=schedule.timezone,
            candidate_email=candidate.email,
        )

        schedule.google_event_id = result["event_id"]
        schedule.meeting_link = result["meeting_link"]
        schedule.status = "scheduled"

        log = ToolActionLog(
            tool_name="google_calendar",
            action="create_event",
            entity_type="interview_schedule",
            entity_id=schedule.id,
            status="success",
            request_payload={
                "scheduled_start":
                    schedule.scheduled_start.isoformat(),
                "scheduled_end":
                    schedule.scheduled_end.isoformat(),
                "timezone":
                    schedule.timezone,
            },
            response_payload={
                "event_id":
                    result["event_id"],
                "meeting_link":
                    result["meeting_link"],
            },
        )

        db.add(log)

        update_application_status(
            db=db,
            application=application,
            new_status="interview_scheduled",
            reason="Recruiter approved interview schedule.",
        )

        db.commit()

        return {
            "schedule_id": schedule.id,
            "status": schedule.status,
            "google_event_id": schedule.google_event_id,
            "meeting_link": schedule.meeting_link,
        }

    except Exception as exc:

        db.rollback()

        failure_log = ToolActionLog(
            tool_name="google_calendar",
            action="create_event",
            entity_type="interview_schedule",
            entity_id=schedule.id,
            status="failed",
            error_message=str(exc),
        )

        db.add(failure_log)
        db.commit()

        raise HTTPException(
            status_code=502,
            detail="Google Calendar event creation failed.",
        )

@router.get("/interviews/{interview_id}")
def get_schedule(
    interview_id: int,
    db: Session = Depends(get_db),
):

    schedule = (
        db.query(InterviewSchedule)
        .filter(
            InterviewSchedule.interview_id
            == interview_id
        )
        .first()
    )

    if not schedule:
        raise HTTPException(
            status_code=404,
            detail="Schedule not found.",
        )

    return {
        "schedule_id": schedule.id,
        "interview_id": schedule.interview_id,
        "scheduled_start": schedule.scheduled_start,
        "scheduled_end": schedule.scheduled_end,
        "timezone": schedule.timezone,
        "status": schedule.status,
        "meeting_link": schedule.meeting_link,
        "google_event_id": schedule.google_event_id,
    }