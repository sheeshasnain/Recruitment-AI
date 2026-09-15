from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.job import Job
from backend.schemas.job import (
    JobCreate,
    JobRead,
)


router = APIRouter(
    prefix="/api/v1/jobs",
    tags=["Jobs"],
)


@router.post(
    "",
    response_model=JobRead,
    status_code=201,
)
def create_job(
    payload: JobCreate,
    db: Session = Depends(get_db),
):

    job = Job(
        title=payload.title,
        description=payload.description,
        required_skills=(
            payload.required_skills
        ),
        minimum_experience=(
            payload.minimum_experience
        ),
    )

    db.add(job)

    db.commit()

    db.refresh(job)

    return job


@router.get(
    "",
    response_model=list[JobRead],
)
def list_jobs(
    db: Session = Depends(get_db),
):

    return (
        db.query(Job)
        .order_by(
            Job.created_at.desc()
        )
        .all()
    )


@router.get(
    "/{job_id}",
    response_model=JobRead,
)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
):

    job = db.get(
        Job,
        job_id,
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    return job