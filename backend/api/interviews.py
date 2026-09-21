from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from backend.agents.interview_graph import (
    interview_preparation_graph,
)
from backend.core.database import get_db
from backend.models.application import Application
from backend.models.candidate import Candidate
from backend.models.interview import Interview
from backend.models.interview_question import (
    InterviewQuestion,
)
from backend.models.job import Job

from datetime import datetime, timezone

from backend.models.interview_answer import (
    InterviewAnswer,
)
from backend.schemas.interview import (
    AnswerSubmitRequest,
    PrepareInterviewRequest,
)
from backend.agents.followup_agent import (
    generate_followup_question,
)

from backend.agents.evaluation_agent import (
    evaluate_interview,
)
from backend.models.evaluation import (
    InterviewEvaluation,
)
from backend.services.interview_scoring_service import (
    calculate_interview_score,
)

from backend.services.status_service import update_application_status


router = APIRouter(
    prefix="/api/v1/interviews",
    tags=["Interviews"],
)


@router.post(
    "/applications/{application_id}/prepare"
)
async def prepare_interview(
    application_id: int,
    payload: PrepareInterviewRequest,
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

    if not application.approved_for_interview:
        raise HTTPException(
            status_code=403,
            detail=(
                "Recruiter approval is required "
                "before preparing an interview."
            ),
        )

    existing = (
        db.query(Interview)
        .filter(
            Interview.application_id
            == application.id
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail=(
                "Interview already exists for "
                "this application."
            ),
        )

    candidate = db.get(
        Candidate,
        application.candidate_id,
    )

    job = db.get(
        Job,
        application.job_id,
    )

    state = {
        "application_id": application.id,

        "job_title": job.title,

        "job_description":
            job.description,

        "required_skills":
            job.required_skills or [],

        "candidate_skills":
            candidate.skills or [],

        "candidate_summary":
            candidate.experience_summary or "",

        "screening_strengths":
            application.strengths or [],

        "screening_concerns":
            application.concerns or [],

        "number_of_questions":
            payload.number_of_questions,
    }

    result = (
        await interview_preparation_graph.ainvoke(
            state
        )
    )

    interview = Interview(
        application_id=application.id,
        status="prepared",
    )

    db.add(interview)
    db.flush()

    generated = result[
        "generated_questions"
    ]

    for index, item in enumerate(
        generated.questions,
        start=1,
    ):

        question = InterviewQuestion(
            interview_id=interview.id,
            question_text=item.question,
            category=item.category,
            difficulty=item.difficulty,
            expected_points=(
                item.expected_points
            ),
            weight=item.weight,
            sequence=index,
        )

        db.add(question)

    update_application_status(
        db=db,
        application=application,
        new_status="interview_prepared",
        reason="Interview questions prepared.",
    )

    db.commit()
    db.refresh(interview)

    return {
        "interview_id": interview.id,
        "application_id": application.id,
        "status": interview.status,
        "questions_created": len(
            generated.questions
        ),
    }

@router.get(
    "/{interview_id}/questions"
)
def get_interview_questions(
    interview_id: int,
    db: Session = Depends(get_db),
):

    interview = db.get(
        Interview,
        interview_id,
    )

    if not interview:
        raise HTTPException(
            status_code=404,
            detail="Interview not found.",
        )

    questions = (
        db.query(InterviewQuestion)
        .filter(
            InterviewQuestion.interview_id
            == interview_id
        )
        .order_by(
            InterviewQuestion.sequence
        )
        .all()
    )

    return [
        {
            "id": question.id,
            "sequence": question.sequence,
            "question":
                question.question_text,
            "category":
                question.category,
            "difficulty":
                question.difficulty,
            "expected_points":
                question.expected_points,
            "weight":
                question.weight,
            "is_followup":
                question.is_followup,
        }
        for question in questions
    ]

@router.post("/{interview_id}/start")
def start_interview(
    interview_id: int,
    db: Session = Depends(get_db),
):
    interview = db.get(
        Interview,
        interview_id,
    )

    if not interview:
        raise HTTPException(
            status_code=404,
            detail="Interview not found.",
        )

    if interview.status != "prepared":
        raise HTTPException(
            status_code=409,
            detail="Only prepared interviews can be started.",
        )

    # Update interview itself
    interview.status = "in_progress"
    interview.started_at = datetime.now(timezone.utc)

    # STEP 40:
    # Synchronize the parent application's status
    application = db.get(
        Application,
        interview.application_id,
    )

    update_application_status(
        db=db,
        application=application,
        new_status="interview_in_progress",
        reason="Interview started.",
    )

    db.commit()

    return {
        "interview_id": interview.id,
        "status": interview.status,
    }

@router.post(
    "/{interview_id}/questions/{question_id}/answer"
)
def submit_answer(
    interview_id: int,
    question_id: int,
    payload: AnswerSubmitRequest,
    db: Session = Depends(get_db),
):

    interview = db.get(
        Interview,
        interview_id,
    )

    if not interview:
        raise HTTPException(
            status_code=404,
            detail="Interview not found.",
        )

    if interview.status != "in_progress":
        raise HTTPException(
            status_code=409,
            detail="Interview is not in progress.",
        )

    question = db.get(
        InterviewQuestion,
        question_id,
    )

    if (
        not question
        or question.interview_id
        != interview.id
    ):
        raise HTTPException(
            status_code=404,
            detail="Question not found.",
        )

    existing_answer = (
        db.query(InterviewAnswer)
        .filter(
            InterviewAnswer.question_id
            == question.id
        )
        .first()
    )

    if existing_answer:

        existing_answer.answer_text = (
            payload.answer
        )

        db.commit()

        return {
            "answer_id":
                existing_answer.id,
            "updated": True,
        }

    answer = InterviewAnswer(
        question_id=question.id,
        answer_text=payload.answer,
    )

    db.add(answer)
    db.commit()
    db.refresh(answer)

    return {
        "answer_id": answer.id,
        "updated": False,
    }

@router.post(
    "/{interview_id}/questions/{question_id}/followup"
)
async def create_followup(
    interview_id: int,
    question_id: int,
    db: Session = Depends(get_db),
):

    interview = db.get(
        Interview,
        interview_id,
    )

    if not interview:
        raise HTTPException(
            status_code=404,
            detail="Interview not found.",
        )

    if interview.status != "in_progress":
        raise HTTPException(
            status_code=409,
            detail="Interview is not in progress.",
        )

    question = db.get(
        InterviewQuestion,
        question_id,
    )

    if (
        not question
        or question.interview_id
        != interview.id
    ):
        raise HTTPException(
            status_code=404,
            detail="Question not found.",
        )

    answer = (
        db.query(InterviewAnswer)
        .filter(
            InterviewAnswer.question_id
            == question.id
        )
        .first()
    )

    if not answer:
        raise HTTPException(
            status_code=409,
            detail=(
                "Candidate must answer the "
                "question before a follow-up "
                "can be generated."
            ),
        )

    result = await generate_followup_question(
        original_question=(
            question.question_text
        ),
        candidate_answer=(
            answer.answer_text
        ),
        expected_points=(
            question.expected_points or []
        ),
    )

    max_sequence = (
        db.query(InterviewQuestion)
        .filter(
            InterviewQuestion.interview_id
            == interview.id
        )
        .count()
    )

    followup = InterviewQuestion(
        interview_id=interview.id,
        question_text=result.question,
        category=question.category,
        difficulty=question.difficulty,
        expected_points=(
            question.expected_points
        ),
        weight=question.weight,
        sequence=max_sequence + 1,
        is_followup=True,
        parent_question_id=question.id,
    )

    db.add(followup)
    db.commit()
    db.refresh(followup)

    return {
        "question_id": followup.id,
        "question": followup.question_text,
        "reason": result.reason,
    }

@router.post(
    "/{interview_id}/complete"
)
def complete_interview(
    interview_id: int,
    db: Session = Depends(get_db),
):

    interview = db.get(
        Interview,
        interview_id,
    )

    if not interview:
        raise HTTPException(
            status_code=404,
            detail="Interview not found.",
        )

    if interview.status != "in_progress":
        raise HTTPException(
            status_code=409,
            detail="Interview is not in progress.",
        )

    questions = (
        db.query(InterviewQuestion)
        .filter(
            InterviewQuestion.interview_id
            == interview.id,
            InterviewQuestion.is_followup
            == False,  # noqa: E712
        )
        .all()
    )

    unanswered = []

    for question in questions:

        answer = (
            db.query(InterviewAnswer)
            .filter(
                InterviewAnswer.question_id
                == question.id
            )
            .first()
        )

        if not answer:
            unanswered.append(
                question.id
            )

    if unanswered:
        raise HTTPException(
            status_code=409,
            detail={
                "message":
                    "Required questions remain unanswered.",
                "question_ids":
                    unanswered,
            },
        )

    interview.status = "completed"

    interview.completed_at = (
        datetime.now(timezone.utc)
    )

    application = db.get(
        Application,
        interview.application_id,
    )

    update_application_status(
        db=db,
        application=application,
        new_status="interview_completed",
        reason="Interview completed.",
    )

    db.commit()

    return {
        "interview_id": interview.id,
        "status": interview.status,
    }

@router.post(
    "/{interview_id}/evaluate"
)
async def evaluate_completed_interview(
    interview_id: int,
    db: Session = Depends(get_db),
):

    interview = db.get(
        Interview,
        interview_id,
    )

    if not interview:
        raise HTTPException(
            status_code=404,
            detail="Interview not found.",
        )

    if interview.status != "completed":
        raise HTTPException(
            status_code=409,
            detail=(
                "Interview must be completed "
                "before evaluation."
            ),
        )

    existing = (
        db.query(InterviewEvaluation)
        .filter(
            InterviewEvaluation.interview_id
            == interview.id
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail=(
                "Interview has already been evaluated."
            ),
        )

    application = db.get(
        Application,
        interview.application_id,
    )

    job = db.get(
        Job,
        application.job_id,
    )

    questions = (
        db.query(InterviewQuestion)
        .filter(
            InterviewQuestion.interview_id
            == interview.id
        )
        .order_by(
            InterviewQuestion.sequence
        )
        .all()
    )

    transcript_parts = []

    for question in questions:

        answer = (
            db.query(InterviewAnswer)
            .filter(
                InterviewAnswer.question_id
                == question.id
            )
            .first()
        )

        if not answer:
            continue

        transcript_parts.append(
            f"""
Question:
{question.question_text}

Candidate Answer:
{answer.answer_text}
"""
        )

    transcript = "\n".join(
        transcript_parts
    )

    semantic = await evaluate_interview(
        job_title=job.title,
        required_skills=(
            job.required_skills or []
        ),
        interview_transcript=transcript,
    )

    overall_score, recommendation = (
        calculate_interview_score(
            semantic
        )
    )

    evaluation = InterviewEvaluation(
        interview_id=interview.id,

        technical_score=(
            semantic.technical
        ),

        communication_score=(
            semantic.communication
        ),

        problem_solving_score=(
            semantic.problem_solving
        ),

        experience_score=(
            semantic.experience
        ),

        overall_score=overall_score,

        recommendation=recommendation,

        strengths=semantic.strengths,

        concerns=semantic.concerns,

        summary=semantic.summary,
    )

    db.add(evaluation)

    update_application_status(
        db=db,
        application=application,
        new_status="evaluation_complete",
        reason="AI-assisted interview evaluation completed.",
    )

    db.commit()
    db.refresh(evaluation)

    return {
        "evaluation_id": evaluation.id,

        "interview_id": interview.id,

        "technical_score":
            evaluation.technical_score,

        "problem_solving_score":
            evaluation.problem_solving_score,

        "experience_score":
            evaluation.experience_score,

        "communication_score":
            evaluation.communication_score,

        "overall_score":
            evaluation.overall_score,

        "recommendation":
            evaluation.recommendation,

        "strengths":
            evaluation.strengths,

        "concerns":
            evaluation.concerns,

        "summary":
            evaluation.summary,
    }

@router.get("")
def list_interviews(
    db: Session = Depends(get_db),
):
    interviews = (
        db.query(Interview)
        .order_by(Interview.id.desc())
        .all()
    )

    results = []

    for interview in interviews:
        application = db.get(
            Application,
            interview.application_id,
        )

        candidate = None
        job = None

        if application:
            candidate = db.get(
                Candidate,
                application.candidate_id,
            )

            job = db.get(
                Job,
                application.job_id,
            )

        evaluation = (
            db.query(InterviewEvaluation)
            .filter(
                InterviewEvaluation.interview_id
                == interview.id
            )
            .first()
        )

        results.append(
            {
                "interview_id": interview.id,
                "application_id": (
                    interview.application_id
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
                "job_title": (
                    job.title
                    if job
                    else "Unknown Job"
                ),
                "status": interview.status,
                "interview_type": (
                    interview.interview_type
                ),
                "created_at": interview.created_at,
                "started_at": interview.started_at,
                "completed_at": interview.completed_at,
                "overall_score": (
                    evaluation.overall_score
                    if evaluation
                    else None
                ),
                "recommendation": (
                    evaluation.recommendation
                    if evaluation
                    else None
                ),
            }
        )

    return results

@router.get(
    "/{interview_id}"
)
def get_interview(
    interview_id: int,
    db: Session = Depends(get_db),
):

    interview = db.get(
        Interview,
        interview_id,
    )

    if not interview:
        raise HTTPException(
            status_code=404,
            detail="Interview not found.",
        )

    questions = (
        db.query(InterviewQuestion)
        .filter(
            InterviewQuestion.interview_id
            == interview.id
        )
        .order_by(
            InterviewQuestion.sequence
        )
        .all()
    )

    question_data = []

    for question in questions:

        answer = (
            db.query(InterviewAnswer)
            .filter(
                InterviewAnswer.question_id
                == question.id
            )
            .first()
        )

        question_data.append(
            {
                "question_id":
                    question.id,

                "sequence":
                    question.sequence,

                "question":
                    question.question_text,

                "category":
                    question.category,

                "is_followup":
                    question.is_followup,

                "answer":
                    (
                        answer.answer_text
                        if answer
                        else None
                    ),
            }
        )

    evaluation = (
        db.query(InterviewEvaluation)
        .filter(
            InterviewEvaluation.interview_id
            == interview.id
        )
        .first()
    )

    return {
        "interview_id":
            interview.id,

        "application_id":
            interview.application_id,

        "status":
            interview.status,

        "started_at":
            interview.started_at,

        "completed_at":
            interview.completed_at,

        "questions":
            question_data,

        "evaluation":
        (
            {
                "evaluation_id":
                    evaluation.id,

                "technical_score":
                    evaluation.technical_score,

                "communication_score":
                    evaluation.communication_score,

                "problem_solving_score":
                    evaluation.problem_solving_score,

                "experience_score":
                    evaluation.experience_score,

                "overall_score":
                    evaluation.overall_score,

                "recommendation":
                    evaluation.recommendation,

                "strengths":
                    evaluation.strengths,

                "concerns":
                    evaluation.concerns,

                "summary":
                    evaluation.summary,

                "created_at":
                    evaluation.created_at,
            }
            if evaluation
            else None
        ),
    }