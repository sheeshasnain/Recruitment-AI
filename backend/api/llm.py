from fastapi import APIRouter, HTTPException

from backend.schemas.chat import ChatRequest, ChatResponse
from backend.services.llm_service import get_llm


router = APIRouter(
    prefix="/api/v1/llm",
    tags=["LLM"],
)


@router.post(
    "/test",
    response_model=ChatResponse,
)
async def test_llm(request: ChatRequest):
    try:
        llm = get_llm()

        result = await llm.ainvoke(request.message)

        return ChatResponse(
            response=result.content
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to process LLM request.",
        ) from exc