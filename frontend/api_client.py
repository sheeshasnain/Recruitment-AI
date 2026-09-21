import os

import requests
import httpx


API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
)


def api_get(
    endpoint: str,
):
    response = requests.get(
        f"{API_BASE_URL}{endpoint}",
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def api_post(
    endpoint: str,
    *,
    json: dict | None = None,
    files=None,
    data=None,
):
    response = requests.post(
        f"{API_BASE_URL}{endpoint}",
        json=json,
        files=files,
        data=data,
        timeout=120,
    )

    response.raise_for_status()

    return response.json()

def get_applications():
    response = httpx.get(
        f"{API_BASE_URL}/api/v1/applications",
        timeout=30,
    )

    response.raise_for_status()

    return response.json()

# ==================================================
# JOBS
# ==================================================


def get_jobs():
    response = httpx.get(
        f"{API_BASE_URL}/api/v1/jobs",
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def get_job(job_id: int):
    response = httpx.get(
        f"{API_BASE_URL}/api/v1/jobs/{job_id}",
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def create_job(
    *,
    title: str,
    description: str,
    required_skills: list[str],
    minimum_experience: float,
):
    response = httpx.post(
        f"{API_BASE_URL}/api/v1/jobs",
        json={
            "title": title,
            "description": description,
            "required_skills": required_skills,
            "minimum_experience": (
                minimum_experience
            ),
        },
        timeout=30,
    )

    response.raise_for_status()

    return response.json()

# ==================================================
# CANDIDATES
# ==================================================


def get_candidates():
    response = httpx.get(
        f"{API_BASE_URL}/api/v1/candidates",
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def get_candidate(candidate_id: int):
    response = httpx.get(
        f"{API_BASE_URL}/api/v1/candidates/{candidate_id}",
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def create_candidate(
    *,
    name: str,
    email: str,
    phone: str | None,
    resume_name: str,
    resume_bytes: bytes,
    resume_content_type: str,
):
    data = {
        "name": name,
        "email": email,
    }

    if phone:
        data["phone"] = phone

    files = {
        "resume": (
            resume_name,
            resume_bytes,
            resume_content_type,
        )
    }

    response = httpx.post(
        f"{API_BASE_URL}/api/v1/candidates",
        data=data,
        files=files,
        timeout=60,
    )

    response.raise_for_status()

    return response.json()

# ==================================================
# INTERVIEWS
# ==================================================


def get_interviews():
    response = httpx.get(
        f"{API_BASE_URL}/api/v1/interviews",
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def get_interview(interview_id: int):
    response = httpx.get(
        f"{API_BASE_URL}/api/v1/interviews/{interview_id}",
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def prepare_interview(
    application_id: int,
    number_of_questions: int = 8,
):
    response = httpx.post(
        (
            f"{API_BASE_URL}/api/v1/interviews/"
            f"applications/{application_id}/prepare"
        ),
        json={
            "number_of_questions": number_of_questions,
        },
        timeout=120,
    )

    response.raise_for_status()

    return response.json()


def get_interview_questions(
    interview_id: int,
):
    response = httpx.get(
        (
            f"{API_BASE_URL}/api/v1/interviews/"
            f"{interview_id}/questions"
        ),
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def start_interview(
    interview_id: int,
):
    response = httpx.post(
        (
            f"{API_BASE_URL}/api/v1/interviews/"
            f"{interview_id}/start"
        ),
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def submit_interview_answer(
    interview_id: int,
    question_id: int,
    answer: str,
):
    response = httpx.post(
        (
            f"{API_BASE_URL}/api/v1/interviews/"
            f"{interview_id}/questions/"
            f"{question_id}/answer"
        ),
        json={
            "answer": answer,
        },
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def generate_interview_followup(
    interview_id: int,
    question_id: int,
):
    response = httpx.post(
        (
            f"{API_BASE_URL}/api/v1/interviews/"
            f"{interview_id}/questions/"
            f"{question_id}/followup"
        ),
        timeout=120,
    )

    response.raise_for_status()

    return response.json()


def complete_interview(
    interview_id: int,
):
    response = httpx.post(
        (
            f"{API_BASE_URL}/api/v1/interviews/"
            f"{interview_id}/complete"
        ),
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def evaluate_interview(
    interview_id: int,
):
    response = httpx.post(
        (
            f"{API_BASE_URL}/api/v1/interviews/"
            f"{interview_id}/evaluate"
        ),
        timeout=120,
    )

    response.raise_for_status()

    return response.json()


# ==================================================
# SCHEDULING
# ==================================================


def get_schedules():
    response = httpx.get(
        f"{API_BASE_URL}/api/v1/scheduling",
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def get_interview_schedule(
    interview_id: int,
):
    response = httpx.get(
        (
            f"{API_BASE_URL}/api/v1/scheduling/"
            f"interviews/{interview_id}"
        ),
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def propose_interview_schedule(
    *,
    interview_id: int,
    scheduled_start: str,
    scheduled_end: str,
    timezone: str,
):
    response = httpx.post(
        (
            f"{API_BASE_URL}/api/v1/scheduling/"
            f"interviews/{interview_id}/propose"
        ),
        json={
            "scheduled_start": scheduled_start,
            "scheduled_end": scheduled_end,
            "timezone": timezone,
        },
        timeout=120,
    )

    response.raise_for_status()

    return response.json()


def approve_interview_schedule(
    *,
    schedule_id: int,
    approved: bool,
):
    response = httpx.post(
        (
            f"{API_BASE_URL}/api/v1/scheduling/"
            f"schedules/{schedule_id}/approve"
        ),
        json={
            "approved": approved,
        },
        timeout=120,
    )

    response.raise_for_status()

    return response.json()


# ==================================================
# COMMUNICATIONS
# ==================================================


def get_communications():
    response = httpx.get(
        (
            f"{API_BASE_URL}"
            f"/api/v1/communications"
        ),
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def get_application_communications(
    application_id: int,
):
    response = httpx.get(
        (
            f"{API_BASE_URL}"
            f"/api/v1/communications/"
            f"applications/{application_id}"
        ),
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def create_communication_draft(
    *,
    application_id: int,
    communication_type: str,
):
    response = httpx.post(
        (
            f"{API_BASE_URL}"
            f"/api/v1/communications/"
            f"applications/{application_id}/draft"
        ),
        json={
            "communication_type":
                communication_type,
        },
        timeout=120,
    )

    response.raise_for_status()

    return response.json()


def approve_communication(
    *,
    communication_id: int,
    approved: bool,
):
    response = httpx.post(
        (
            f"{API_BASE_URL}"
            f"/api/v1/communications/"
            f"{communication_id}/approve"
        ),
        json={
            "approved": approved,
        },
        timeout=120,
    )

    response.raise_for_status()

    return response.json()

def update_communication_draft(
    *,
    communication_id: int,
    subject: str,
    body: str,
):
    response = httpx.put(
        (
            f"{API_BASE_URL}"
            f"/api/v1/communications/"
            f"{communication_id}"
        ),
        json={
            "subject": subject,
            "body": body,
        },
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


# ==================================================
# RECRUITER DECISIONS
# ==================================================


def make_recruiter_decision(
    *,
    application_id: int,
    decision: str,
    notes: str | None = None,
):
    response = httpx.post(
        (
            f"{API_BASE_URL}"
            f"/api/v1/recruiter/"
            f"applications/{application_id}/decision"
        ),
        json={
            "decision": decision,
            "notes": notes,
        },
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def make_final_recruiter_decision(
    *,
    application_id: int,
    decision: str,
    notes: str | None = None,
):
    response = httpx.post(
        (
            f"{API_BASE_URL}"
            f"/api/v1/recruiter/"
            f"applications/{application_id}/"
            f"final-decision"
        ),
        json={
            "decision": decision,
            "notes": notes,
        },
        timeout=30,
    )

    response.raise_for_status()

    return response.json()

# ==================================================
# AUDIT LOGS
# ==================================================


def get_tool_logs():
    response = httpx.get(
        f"{API_BASE_URL}/api/v1/tool-logs",
        timeout=30,
    )

    response.raise_for_status()

    return response.json()