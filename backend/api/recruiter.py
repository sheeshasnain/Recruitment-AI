from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.application import Application
from backend.models.status_history import ApplicationStatusHistory
from backend.schemas.interview import RecruiterDecisionRequest

from datetime import (
    datetime,
    timezone,
)

from backend.schemas.final_decision import (
    FinalDecisionRequest,
)
from backend.models.interview import (
    Interview,
)
from backend.models.evaluation import (
    InterviewEvaluation,
)
from backend.services.status_service import (
    update_application_status,
)


router = APIRouter(
    prefix="/api/v1/recruiter",
    tags=["Recruiter"],
)


@router.post(
    "/applications/{application_id}/decision"
)
def make_recruiter_decision(
    application_id: int,
    payload: RecruiterDecisionRequest,
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

    if application.status != "screening_complete":
        raise HTTPException(
            status_code=409,
            detail=(
                "Application must complete screening "
                "before recruiter review."
            ),
        )

    previous_status = application.status

    application.recruiter_decision = (
        payload.decision
    )

    application.recruiter_notes = (
        payload.notes
    )

    if payload.decision == "approve":

        application.approved_for_interview = True
        application.status = "interview_approved"

    elif payload.decision == "hold":

        application.approved_for_interview = False
        application.status = "recruiter_hold"

    else:

        application.approved_for_interview = False
        application.status = "recruiter_rejected"

    history = ApplicationStatusHistory(
        application_id=application.id,
        previous_status=previous_status,
        new_status=application.status,
        reason=payload.notes or (
            f"Recruiter decision: {payload.decision}"
        ),
    )

    db.add(history)
    db.commit()
    db.refresh(application)

    return {
        "application_id": application.id,
        "decision": application.recruiter_decision,
        "status": application.status,
        "approved_for_interview":
            application.approved_for_interview,
    }

@router.post(
    "/applications/{application_id}/final-decision"
)
def final_recruiter_decision(
    application_id: int,
    payload: FinalDecisionRequest,
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

    if application.final_decision:
        raise HTTPException(
            status_code=409,
            detail=(
                "A final recruiter decision "
                "has already been recorded."
            ),
        )

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
            detail=(
                "An interview does not exist "
                "for this application."
            ),
        )

    if interview.status != "completed":
        raise HTTPException(
            status_code=409,
            detail=(
                "Interview must be completed "
                "before a final decision."
            ),
        )
    

    evaluation = (
        db.query(InterviewEvaluation)
        .filter(
            InterviewEvaluation.interview_id
            == interview.id
        )
        .first()
    )

    if not evaluation:
        raise HTTPException(
            status_code=409,
            detail=(
                "Interview evaluation "
                "must be completed first."
            ),
        )

    application.final_decision = (
        payload.decision
    )

    application.final_decision_notes = (
        payload.notes
    )

    application.final_decision_at = (
        datetime.now(timezone.utc)
    )

    status_map = {
        "hire": "hired",
        "reject": "rejected",
        "hold": "final_review_hold",
    }

    update_application_status(
        db=db,
        application=application,
        new_status=status_map[
            payload.decision
        ],
        reason=(
            payload.notes
            or (
                "Final recruiter decision: "
                f"{payload.decision}"
            )
        ),
    )

    db.commit()
    db.refresh(application)

    return {
        "application_id": (
            application.id
        ),
        "final_decision": (
            application.final_decision
        ),
        "notes": (
            application.final_decision_notes
        ),
        "status": application.status,
        "decided_at": (
            application.final_decision_at
        ),
    }