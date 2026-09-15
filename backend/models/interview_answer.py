from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    JSON,
    Text,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from backend.models.base import Base


class InterviewAnswer(Base):

    __tablename__ = "interview_answers"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    question_id: Mapped[int] = mapped_column(
        ForeignKey("interview_questions.id"),
        nullable=False,
    )

    answer_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    semantic_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    strengths: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )

    concerns: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )

    evaluator_reasoning: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    question = relationship(
        "InterviewQuestion",
        back_populates="answers",
    )