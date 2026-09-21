from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from backend.agents.graph import (
    recruitment_graph,
)
from backend.core.database import get_db

from backend.models.application import (
    Application,
)
from backend.models.candidate import (
    Candidate,
)
from backend.models.job import Job
from backend.models.status_history import (
    ApplicationStatusHistory,
)

from backend.schemas.application import (
    ApplicationRead,
    ApplicationScreenRequest,
)

from backend.schemas.job import (
    JobInput,
)
# import logging

# logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/api/v1/applications",
    tags=["Applications"],
)


@router.post(
    "/screen",
    response_model=ApplicationRead,
)
async def screen_application(
    request: ApplicationScreenRequest,
    db: Session = Depends(get_db),
):

    candidate = db.get(
        Candidate,
        request.candidate_id,
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found.",
        )


    job = db.get(
        Job,
        request.job_id,
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )


    existing_application = (
        db.query(Application)
        .filter(
            Application.candidate_id
            == candidate.id,
            Application.job_id
            == job.id,
        )
        .first()
    )

    if existing_application:
        raise HTTPException(
            status_code=409,
            detail=(
                "Candidate has already been "
                "screened for this job."
            ),
        )


    job_input = JobInput(
        title=job.title,
        description=job.description,
        required_skills=(
            job.required_skills or []
        ),
        minimum_experience=(
            job.minimum_experience
        ),
    )


    initial_state = {

        "candidate_name":
            candidate.name,

        "candidate_email":
            candidate.email,

        "candidate_phone":
            candidate.phone,

        "resume_text":
            candidate.resume_text,

        "job":
            job_input,
    }


    result = await recruitment_graph.ainvoke(
        initial_state
    )


    profile = result[
        "candidate_profile"
    ]

    screening = result[
        "screening_result"
    ]

    route = result["route"]


    # --------------------------------
    # Update candidate profile
    # --------------------------------

    candidate.current_role = (
        profile.current_role
    )

    candidate.years_experience = (
        profile.years_experience
    )

    candidate.skills = (
        profile.skills
    )

    candidate.education = (
        profile.education
    )

    candidate.experience_summary = (
        profile.experience_summary
    )

    candidate.strengths = (
        profile.strengths
    )


    # --------------------------------
    # Create application
    # --------------------------------

    application = Application(

        candidate_id=candidate.id,

        job_id=job.id,

        status="screening_complete",

        screening_route=route,

        matched_skills=(
            screening.matched_skills
        ),

        missing_skills=(
            screening.missing_skills
        ),

        strengths=(
            screening.strengths
        ),

        concerns=(
            screening.concerns
        ),

        skills_score=(
            screening.skills_score
        ),

        experience_score=(
            screening.experience_score
        ),

        overall_score=(
            screening.overall_score
        ),

        reasoning=(
            screening.reasoning
        ),
    )


    db.add(application)

    db.flush()


    history = (
        ApplicationStatusHistory(

            application_id=(
                application.id
            ),

            previous_status="new",

            new_status=(
                "screening_complete"
            ),

            reason=(
                "AI screening completed. "
                "Recruiter review pending."
            ),
        )
    )


    db.add(history)

    db.commit()

    db.refresh(application)

    return application



@router.get(
    "/{application_id}",
    response_model=ApplicationRead,
)
def get_application(
    application_id: int,
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

    return application

@router.get("")
def list_applications(
    db: Session = Depends(get_db),
):
    applications = (
        db.query(Application)
        .order_by(
            Application.created_at.desc()
        )
        .all()
    )

    results = []

    for application in applications:

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
                # ==================================
                # APPLICATION
                # ==================================

                "id": application.id,

                "candidate_id": (
                    application.candidate_id
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

                "job_id": (
                    application.job_id
                ),

                "job_title": (
                    job.title
                    if job
                    else "Unknown Job"
                ),

                "status": (
                    application.status
                ),

                # ==================================
                # AI SCREENING
                # ==================================

                "screening_route": (
                    application.screening_route
                ),

                "matched_skills": (
                    application.matched_skills
                    or []
                ),

                "missing_skills": (
                    application.missing_skills
                    or []
                ),

                "strengths": (
                    application.strengths
                    or []
                ),

                "concerns": (
                    application.concerns
                    or []
                ),

                "skills_score": (
                    application.skills_score
                ),

                "experience_score": (
                    application.experience_score
                ),

                "overall_score": (
                    application.overall_score
                ),

                "reasoning": (
                    application.reasoning
                ),

                # ==================================
                # RECRUITER SCREENING DECISION
                # ==================================

                "recruiter_decision": (
                    application.recruiter_decision
                ),

                "recruiter_notes": (
                    application.recruiter_notes
                ),

                "approved_for_interview": (
                    application.approved_for_interview
                ),

                # ==================================
                # FINAL RECRUITER DECISION
                # ==================================

                "final_decision": (
                    application.final_decision
                ),

                "final_decision_notes": (
                    application.final_decision_notes
                ),

                "final_decision_at": (
                    application.final_decision_at
                ),

                # ==================================
                # TIMESTAMPS
                # ==================================

                "created_at": (
                    application.created_at
                ),

                "updated_at": (
                    application.updated_at
                ),
            }
        )

    return results