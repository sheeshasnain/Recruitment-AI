from fastapi import APIRouter, HTTPException

from backend.agents.graph import recruitment_graph
from backend.schemas.screening import (
    ScreeningRequest,
    ScreeningResponse,
)


router = APIRouter(
    prefix="/api/v1/screening",
    tags=["Screening"],
)


@router.post(
    "/run",
    response_model=ScreeningResponse,
)
async def run_screening(
    request: ScreeningRequest,
):
    try:
        initial_state = {
            "candidate_name": request.candidate.name,
            "candidate_email": request.candidate.email,
            "candidate_phone": request.candidate.phone,
            "resume_text": request.candidate.resume_text,
            "job": request.job,
        }

        result = await recruitment_graph.ainvoke(
            initial_state
        )

        return ScreeningResponse(
            candidate_profile=(
                result["candidate_profile"].model_dump()
            ),
            screening_result=(
                result["screening_result"].model_dump()
            ),
            route=result["route"],
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Candidate screening failed.",
        ) from exc