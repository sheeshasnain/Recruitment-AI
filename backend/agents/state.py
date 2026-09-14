from typing import TypedDict

from backend.schemas.candidate import CandidateProfile
from backend.schemas.job import JobInput
from backend.schemas.screening import ScreeningResult


class RecruitmentState(TypedDict, total=False):
    candidate_name: str
    candidate_email: str
    candidate_phone: str | None
    resume_text: str

    job: JobInput

    candidate_profile: CandidateProfile

    screening_result: ScreeningResult

    route: str
    error: str | None