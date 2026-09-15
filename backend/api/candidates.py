from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.candidate import Candidate
from backend.schemas.candidate import CandidateRead
from backend.tools.resume_parser import (
    extract_resume_text,
)


router = APIRouter(
    prefix="/api/v1/candidates",
    tags=["Candidates"],
)


@router.post(
    "",
    response_model=CandidateRead,
    status_code=201,
)
async def create_candidate(
    name: str = Form(...),
    email: EmailStr = Form(...),
    phone: str | None = Form(None),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db),
):

    resume_text = await extract_resume_text(
        resume
    )

    candidate = Candidate(
        name=name.strip(),
        email=str(email).lower(),
        phone=phone,
        resume_filename=resume.filename,
        resume_text=resume_text,
    )

    db.add(candidate)

    try:
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail=(
                "A candidate with this email "
                "already exists."
            ),
        )

    db.refresh(candidate)

    return candidate


@router.get(
    "",
    response_model=list[CandidateRead],
)
def list_candidates(
    db: Session = Depends(get_db),
):

    return (
        db.query(Candidate)
        .order_by(
            Candidate.created_at.desc()
        )
        .all()
    )


@router.get(
    "/{candidate_id}",
    response_model=CandidateRead,
)
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
):

    candidate = db.get(
        Candidate,
        candidate_id,
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found.",
        )

    return candidate