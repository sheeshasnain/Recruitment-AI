from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.agents.communication_agent import (
    generate_candidate_email,
)
from backend.core.database import get_db
from backend.models.application import Application
from backend.models.candidate import Candidate
from backend.models.communication import (
    CandidateCommunication,
)
from backend.models.interview import Interview
from backend.models.interview_schedule import (
    InterviewSchedule,
)
from backend.models.job import Job
from backend.models.tool_action_log import ToolActionLog
from backend.schemas.communication import (
    CommunicationApprovalRequest,
    CommunicationDraftRequest,
    CommunicationUpdateRequest,
)
from backend.tools.gmail_tool import (
    send_candidate_email,
)


router = APIRouter(
    prefix="/api/v1/communications",
    tags=["Communications"],
)

@router.post("/applications/{application_id}/draft")
async def create_communication_draft(
    application_id: int,
    payload: CommunicationDraftRequest,
    db: Session = Depends(get_db),
):

    application = db.get(
        Application,
        application_id,
    )

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found.",
        )

    candidate = db.get(
        Candidate,
        application.candidate_id,
    )

    job = db.get(
        Job,
        application.job_id,
    )

    scheduled_start = None
    schedule_timezone = None
    meeting_link = None

    if payload.communication_type in {
        "interview_invitation",
        "interview_reminder",
    }:

        interview = (
            db.query(Interview)
            .filter(
                Interview.application_id
                == application.id
            )
            .first()
        )

        if not interview:
            raise HTTPException(
                status_code=409,
                detail="No interview exists for this application.",
            )

        schedule = (
            db.query(InterviewSchedule)
            .filter(
                InterviewSchedule.interview_id
                == interview.id
            )
            .first()
        )

        if not schedule or schedule.status != "scheduled":
            raise HTTPException(
                status_code=409,
                detail="Interview must be scheduled first.",
            )

        scheduled_start = (
            schedule.scheduled_start.isoformat()
        )

        schedule_timezone = schedule.timezone
        meeting_link = schedule.meeting_link

    draft = await generate_candidate_email(
        communication_type=payload.communication_type,
        candidate_name=candidate.name,
        job_title=job.title,
        scheduled_start=scheduled_start,
        timezone=schedule_timezone,
        meeting_link=meeting_link,
    )

    communication = CandidateCommunication(
        application_id=application.id,
        communication_type=payload.communication_type,
        recipient_email=candidate.email,
        subject=draft.subject,
        body=draft.body,
        status="draft",
    )

    db.add(communication)
    db.commit()
    db.refresh(communication)

    return {
        "communication_id": communication.id,
        "status": communication.status,
        "recipient": communication.recipient_email,
        "subject": communication.subject,
        "body": communication.body,
    }


# ==================================================
# UPDATE COMMUNICATION DRAFT
# ==================================================

@router.put("/{communication_id}")
def update_communication_draft(
    communication_id: int,
    payload: CommunicationUpdateRequest,
    db: Session = Depends(get_db),
):

    clean_subject = (
        payload.subject.strip()
    )

    clean_body = (
        payload.body.strip()
    )


    if len(clean_subject) < 3:

        raise HTTPException(
            status_code=422,
            detail=(
                "Subject must contain at least "
                "3 non-whitespace characters."
            ),
        )


    if len(clean_body) < 10:
    
        raise HTTPException(
            status_code=422,
            detail=(
                "Email body must contain at least "
                "10 non-whitespace characters."
            ),
        )

    communication = db.get(
        CandidateCommunication,
        communication_id,
    )

    if not communication:
        raise HTTPException(
            status_code=404,
            detail="Communication not found.",
        )

    # Only unsent drafts can be edited.
    if communication.status != "draft":
        raise HTTPException(
            status_code=409,
            detail=(
                "Only draft communications "
                "can be edited."
            ),
        )

    communication.subject = (
        clean_subject
    )

    communication.body = (
        clean_body
    )

    try:

        db.commit()
        db.refresh(
            communication
        )

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to update "
                "communication draft."
            ),
        )

    return {
        "communication_id": (
            communication.id
        ),
        "status": (
            communication.status
        ),
        "recipient": (
            communication.recipient_email
        ),
        "subject": (
            communication.subject
        ),
        "body": (
            communication.body
        ),
    }


@router.post("/{communication_id}/approve")
def approve_communication(
    communication_id: int,
    payload: CommunicationApprovalRequest,
    db: Session = Depends(get_db),
):

    communication = db.get(
        CandidateCommunication,
        communication_id,
    )

    if not communication:
        raise HTTPException(
            status_code=404,
            detail="Communication not found.",
        )

    if communication.status != "draft":
        raise HTTPException(
            status_code=409,
            detail="Communication is not awaiting approval.",
        )

    if not payload.approved:

        communication.status = "rejected"

        db.commit()

        return {
            "communication_id":
                communication.id,
            "status":
                communication.status,
        }

    try:

        result = send_candidate_email(
            recipient=communication.recipient_email,
            subject=communication.subject,
            body=communication.body,
        )

        communication.status = "sent"

        communication.provider_message_id = (
            result["message_id"]
        )

        communication.sent_at = (
            datetime.now(timezone.utc)
        )

        log = ToolActionLog(
            tool_name="gmail",
            action="send_email",
            entity_type="candidate_communication",
            entity_id=communication.id,
            status="success",
            request_payload={
                "recipient":
                    communication.recipient_email,
                "subject":
                    communication.subject,
            },
            response_payload={
                "message_id":
                    result["message_id"],
            },
        )

        db.add(log)
        db.commit()

        return {
            "communication_id":
                communication.id,
            "status":
                communication.status,
            "message_id":
                communication.provider_message_id,
        }

    except Exception as exc:

        db.rollback()

        failure_log = ToolActionLog(
            tool_name="gmail",
            action="send_email",
            entity_type="candidate_communication",
            entity_id=communication.id,
            status="failed",
            error_message=str(exc),
        )

        db.add(failure_log)
        db.commit()

        raise HTTPException(
            status_code=502,
            detail="Email delivery failed.",
        )


# ==================================================
# LIST ALL COMMUNICATIONS
# ==================================================

@router.get("")
def list_communications(
    db: Session = Depends(get_db),
):

    communications = (
        db.query(
            CandidateCommunication
        )
        .order_by(
            CandidateCommunication
            .created_at
            .desc()
        )
        .all()
    )

    results = []

    for communication in communications:

        application = db.get(
            Application,
            communication.application_id,
        )

        candidate = None
        job = None

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
                "communication_id": (
                    communication.id
                ),
                "application_id": (
                    communication.application_id
                ),
                "candidate_id": (
                    candidate.id
                    if candidate
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
                    else communication.recipient_email
                ),
                "job_title": (
                    job.title
                    if job
                    else "Unknown Job"
                ),
                "communication_type": (
                    communication.communication_type
                ),
                "recipient": (
                    communication.recipient_email
                ),
                "subject": (
                    communication.subject
                ),
                "body": (
                    communication.body
                ),
                "status": (
                    communication.status
                ),
                "provider_message_id": (
                    communication.provider_message_id
                ),
                "created_at": (
                    communication.created_at
                ),
                "sent_at": (
                    communication.sent_at
                ),
            }
        )

    return results


@router.get("/applications/{application_id}")
def get_communications(
    application_id: int,
    db: Session = Depends(get_db),
):

    communications = (
        db.query(CandidateCommunication)
        .filter(
            CandidateCommunication.application_id
            == application_id
        )
        .order_by(
            CandidateCommunication.created_at.desc()
        )
        .all()
    )

    return [
        {
            "communication_id": item.id,
            "type": item.communication_type,
            "recipient": item.recipient_email,
            "subject": item.subject,
            "body": item.body,
            "status": item.status,
            "sent_at": item.sent_at,
        }
        for item in communications
    ]