from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import settings

from backend.api.llm import (
    router as llm_router,
)
from backend.api.screening import (
    router as screening_router,
)
from backend.api.applications import (
    router as applications_router,
)
from backend.api.candidates import (
    router as candidates_router,
)
from backend.api.jobs import (
    router as jobs_router,
)
from backend.api.interviews import (
    router as interviews_router,
)
from backend.api.recruiter import (
    router as recruiter_router,
)
from backend.api.communications import (
    router as communications_router,
)
from backend.api.scheduling import (
    router as scheduling_router,
)
from backend.api.tool_logs import (
    router as tool_logs_router,
)


app = FastAPI(
    title=settings.app_name,
    description=(
        "AI-powered recruitment and "
        "interview operations platform"
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(llm_router)
app.include_router(screening_router)
app.include_router(candidates_router)
app.include_router(jobs_router)
app.include_router(applications_router)
app.include_router(recruiter_router)
app.include_router(interviews_router)
app.include_router(scheduling_router)
app.include_router(communications_router)
app.include_router(tool_logs_router)


@app.get("/")
async def root():
    return {
        "message": (
            "Recruitment AI API is running"
        ),
        "environment": settings.app_env,
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": settings.app_name,
    }