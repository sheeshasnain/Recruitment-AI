from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.agents.scheduling_agent import (
    prepare_calendar_event,
)
from backend.core.database import get_db
from backend.core.logger import setup_logger
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


# --------------------------------------------------
# Application Logger
# --------------------------------------------------

logger = setup_logger(__name__)


# ==================================================
# PROPOSE INTERVIEW SCHEDULE
# ==================================================

@router.post("/interviews/{interview_id}/propose")
async def propose_schedule(
    interview_id: int,
    payload: ScheduleProposalRequest,
    db: Session = Depends(get_db),
):

    logger.info(
        "Schedule proposal requested | "
        "interview_id=%s",
        interview_id,
    )

    interview = db.get(
        Interview,
        interview_id,
    )

    if not interview:
        logger.warning(
            "Schedule proposal failed | "
            "interview_id=%s | "
            "reason=interview_not_found",
            interview_id,
        )

        raise HTTPException(
            status_code=404,
            detail="Interview not found.",
        )

    application = db.get(
        Application,
        interview.application_id,
    )

    if not application:
        logger.warning(
            "Schedule proposal failed | "
            "interview_id=%s | "
            "reason=application_not_found",
            interview_id,
        )

        raise HTTPException(
            status_code=404,
            detail="Application not found.",
        )

    if not application.approved_for_interview:
        logger.warning(
            "Schedule proposal blocked | "
            "interview_id=%s | "
            "application_id=%s | "
            "reason=recruiter_approval_required",
            interview_id,
            application.id,
        )

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

    if (
        existing
        and existing.status != "rejected"
    ):
        logger.warning(
            "Schedule proposal conflict | "
            "interview_id=%s | "
            "existing_schedule_id=%s | "
            "status=%s",
            interview.id,
            existing.id,
            existing.status,
        )

        raise HTTPException(
            status_code=409,
            detail=(
                "An active schedule already exists "
                "for this interview."
            ),
        )

    candidate = db.get(
        Candidate,
        application.candidate_id,
    )

    if not candidate:
        logger.error(
            "Schedule proposal failed | "
            "application_id=%s | "
            "reason=candidate_not_found",
            application.id,
        )

        raise HTTPException(
            status_code=404,
            detail="Candidate not found.",
        )

    job = db.get(
        Job,
        application.job_id,
    )

    if not job:
        logger.error(
            "Schedule proposal failed | "
            "application_id=%s | "
            "reason=job_not_found",
            application.id,
        )

        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    # --------------------------------------------------
    # AI Scheduling Agent
    #
    # This only prepares content.
    # No Google Calendar event is created here.
    # --------------------------------------------------

    try:
        draft = await prepare_calendar_event(
            candidate_name=candidate.name,
            job_title=job.title,
            scheduled_start=(
                payload.scheduled_start.isoformat()
            ),
            scheduled_end=(
                payload.scheduled_end.isoformat()
            ),
            timezone=payload.timezone,
        )

    except Exception:
        logger.exception(
            "Scheduling agent failed | "
            "interview_id=%s | "
            "application_id=%s",
            interview.id,
            application.id,
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "Unable to prepare interview "
                "schedule draft."
            ),
        )

    # --------------------------------------------------
# CREATE OR REUSE SCHEDULE
# --------------------------------------------------

    if existing:

        logger.info(
            "Re-proposing rejected schedule | "
            "schedule_id=%s | "
            "interview_id=%s",
            existing.id,
            interview.id,
        )

        schedule = existing

        schedule.scheduled_start = (
            payload.scheduled_start
        )

        schedule.scheduled_end = (
            payload.scheduled_end
        )

        schedule.timezone = (
            payload.timezone
        )

        schedule.status = (
            "pending_approval"
        )

        schedule.event_title = (
            draft.title
        )

        schedule.event_description = (
            draft.description
        )

        schedule.candidate_message = (
            draft.candidate_message
        )


        schedule.google_event_id = None
        schedule.meeting_link = None

    else:

        schedule = InterviewSchedule(
            interview_id=interview.id,
            scheduled_start=(
                payload.scheduled_start
            ),
            scheduled_end=(
                payload.scheduled_end
            ),
            timezone=payload.timezone,
            status="pending_approval",
            event_title=draft.title,
            event_description=(
                draft.description
            ),
            candidate_message=(
                draft.candidate_message
            ),
        )

    try:
        db.add(schedule)
        db.commit()
        db.refresh(schedule)

    except Exception:
        db.rollback()

        logger.exception(
            "Schedule database save failed | "
            "interview_id=%s",
            interview.id,
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to save schedule.",
        )

    logger.info(
        "Schedule proposed | "
        "interview_id=%s | "
        "application_id=%s | "
        "schedule_id=%s | "
        "status=%s",
        interview.id,
        application.id,
        schedule.id,
        schedule.status,
    )

    return {
        "schedule_id": schedule.id,
        "interview_id": interview.id,
        "status": schedule.status,
        "title": draft.title,
        "description": draft.description,
        "candidate_message": (
            draft.candidate_message
        ),
        "scheduled_start": (
            schedule.scheduled_start
        ),
        "scheduled_end": (
            schedule.scheduled_end
        ),
        "timezone": schedule.timezone,
    }


# ==================================================
# APPROVE / REJECT INTERVIEW SCHEDULE
# ==================================================

@router.post("/schedules/{schedule_id}/approve")
def approve_schedule(
    schedule_id: int,
    payload: ScheduleApprovalRequest,
    db: Session = Depends(get_db),
):

    logger.info(
        "Schedule approval action requested | "
        "schedule_id=%s | "
        "approved=%s",
        schedule_id,
        payload.approved,
    )

    schedule = db.get(
        InterviewSchedule,
        schedule_id,
    )

    if not schedule:
        logger.warning(
            "Schedule approval failed | "
            "schedule_id=%s | "
            "reason=schedule_not_found",
            schedule_id,
        )

        raise HTTPException(
            status_code=404,
            detail="Schedule not found.",
        )

    if schedule.status != "pending_approval":
        logger.warning(
            "Schedule approval conflict | "
            "schedule_id=%s | "
            "current_status=%s",
            schedule.id,
            schedule.status,
        )

        raise HTTPException(
            status_code=409,
            detail=(
                "Schedule is not awaiting "
                "approval."
            ),
        )

    # --------------------------------------------------
    # Recruiter rejected the proposed schedule.
    # No Google Calendar call is made.
    # --------------------------------------------------

    if not payload.approved:
        schedule.status = "rejected"

        db.commit()

        logger.info(
            "Schedule rejected by recruiter | "
            "schedule_id=%s",
            schedule.id,
        )

        return {
            "schedule_id": schedule.id,
            "status": "rejected",
        }

    interview = db.get(
        Interview,
        schedule.interview_id,
    )

    if not interview:
        logger.error(
            "Schedule approval failed | "
            "schedule_id=%s | "
            "reason=interview_not_found",
            schedule.id,
        )

        raise HTTPException(
            status_code=404,
            detail="Interview not found.",
        )

    application = db.get(
        Application,
        interview.application_id,
    )

    if not application:
        logger.error(
            "Schedule approval failed | "
            "schedule_id=%s | "
            "reason=application_not_found",
            schedule.id,
        )

        raise HTTPException(
            status_code=404,
            detail="Application not found.",
        )

    candidate = db.get(
        Candidate,
        application.candidate_id,
    )

    if not candidate:
        logger.error(
            "Schedule approval failed | "
            "schedule_id=%s | "
            "reason=candidate_not_found",
            schedule.id,
        )

        raise HTTPException(
            status_code=404,
            detail="Candidate not found.",
        )

    # --------------------------------------------------
    # EXTERNAL SIDE EFFECT
    #
    # Google Calendar is called ONLY after recruiter
    # approval.
    # --------------------------------------------------

    try:
        result = create_interview_calendar_event(
            title=schedule.event_title,
            description=schedule.event_description,
            start_datetime=(
                schedule.scheduled_start.isoformat()
            ),
            end_datetime=(
                schedule.scheduled_end.isoformat()
            ),
            timezone=schedule.timezone,
            candidate_email=candidate.email,
        )

        schedule.google_event_id = (
            result["event_id"]
        )

        schedule.meeting_link = (
            result["meeting_link"]
        )

        schedule.status = "scheduled"

        # --------------------------------------------------
        # Persistent audit log for external tool action
        # --------------------------------------------------

        tool_log = ToolActionLog(
            tool_name="google_calendar",
            action="create_event",
            entity_type="interview_schedule",
            entity_id=schedule.id,
            status="success",
            request_payload={
                "scheduled_start": (
                    schedule
                    .scheduled_start
                    .isoformat()
                ),
                "scheduled_end": (
                    schedule
                    .scheduled_end
                    .isoformat()
                ),
                "timezone": (
                    schedule.timezone
                ),
            },
            response_payload={
                "event_id": (
                    result["event_id"]
                ),
                "meeting_link": (
                    result["meeting_link"]
                ),
            },
        )

        db.add(tool_log)

        update_application_status(
            db=db,
            application=application,
            new_status=(
                "interview_scheduled"
            ),
            reason=(
                "Recruiter approved "
                "interview schedule."
            ),
        )

        db.commit()
        db.refresh(schedule)

        logger.info(
            "Calendar event created | "
            "schedule_id=%s | "
            "interview_id=%s | "
            "application_id=%s | "
            "status=%s",
            schedule.id,
            interview.id,
            application.id,
            schedule.status,
        )

        return {
            "schedule_id": schedule.id,
            "status": schedule.status,
            "google_event_id": (
                schedule.google_event_id
            ),
            "meeting_link": (
                schedule.meeting_link
            ),
        }

    except Exception as exc:

        db.rollback()

        logger.exception(
            "Calendar creation failed | "
            "schedule_id=%s | "
            "interview_id=%s",
            schedule.id,
            interview.id,
        )

        # --------------------------------------------------
        # Store failure in persistent audit table.
        # --------------------------------------------------

        try:
            failure_log = ToolActionLog(
                tool_name="google_calendar",
                action="create_event",
                entity_type=(
                    "interview_schedule"
                ),
                entity_id=schedule.id,
                status="failed",
                error_message=str(exc),
            )

            db.add(failure_log)
            db.commit()

        except Exception:
            db.rollback()

            logger.exception(
                "Unable to save Calendar "
                "failure audit log | "
                "schedule_id=%s",
                schedule.id,
            )

        raise HTTPException(
            status_code=502,
            detail=(
                "Google Calendar event "
                "creation failed."
            ),
        )


# ==================================================
# LIST INTERVIEW SCHEDULES
# ==================================================

@router.get("")
def list_schedules(
    db: Session = Depends(get_db),
):

    schedules = (
        db.query(InterviewSchedule)
        .order_by(
            InterviewSchedule.created_at.desc()
        )
        .all()
    )

    results = []

    for schedule in schedules:

        interview = db.get(
            Interview,
            schedule.interview_id,
        )

        application = None
        candidate = None
        job = None

        if interview:

            application = db.get(
                Application,
                interview.application_id,
            )

        if application:

            candidate = db.get(
                Candidate,
                application.candidate_id,
            )

            job = db.get(
                Job,
                application.job_id,
            )

        results.append(
            {
                "schedule_id": schedule.id,
                "interview_id": (
                    schedule.interview_id
                ),
                "application_id": (
                    application.id
                    if application
                    else None
                ),
                "candidate_name": (
                    candidate.name
                    if candidate
                    else "Unknown Candidate"
                ),
                "candidate_email": (
                    candidate.email
                    if candidate
                    else None
                ),
                "job_title": (
                    job.title
                    if job
                    else "Unknown Job"
                ),
                "scheduled_start": (
                    schedule.scheduled_start
                ),
                "scheduled_end": (
                    schedule.scheduled_end
                ),
                "timezone": (
                    schedule.timezone
                ),
                "meeting_type": (
                    schedule.meeting_type
                ),
                "status": (
                    schedule.status
                ),
                "event_title": (
                    schedule.event_title
                ),
                "event_description": (
                    schedule.event_description
                ),
                "candidate_message": (
                    schedule.candidate_message
                ),
                "google_event_id": (
                    schedule.google_event_id
                ),
                "meeting_link": (
                    schedule.meeting_link
                ),
                "created_at": (
                    schedule.created_at
                ),
            }
        )

    return results


# ==================================================
# GET INTERVIEW SCHEDULE
# ==================================================

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
        "interview_id": (
            schedule.interview_id
        ),
        "scheduled_start": (
            schedule.scheduled_start
        ),
        "scheduled_end": (
            schedule.scheduled_end
        ),
        "timezone": schedule.timezone,
        "status": schedule.status,
        "meeting_link": (
            schedule.meeting_link
        ),
        "google_event_id": (
            schedule.google_event_id
        ),
        "event_title": (
            schedule.event_title
        ),
        "event_description": (
            schedule.event_description
        ),
        "candidate_message": (
            schedule.candidate_message
        ),
    }