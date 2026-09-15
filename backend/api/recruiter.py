from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.application import Application
from backend.models.status_history import ApplicationStatusHistory
from backend.schemas.interview import RecruiterDecisionRequest


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