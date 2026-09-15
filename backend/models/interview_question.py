from sqlalchemy import (
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from backend.models.base import Base


class InterviewQuestion(Base):

    __tablename__ = "interview_questions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    interview_id: Mapped[int] = mapped_column(
        ForeignKey("interviews.id"),
        nullable=False,
    )

    question_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    difficulty: Mapped[str] = mapped_column(
        String(30),
        default="medium",
    )

    expected_points: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )

    weight: Mapped[float] = mapped_column(
        Float,
        default=1.0,
    )

    sequence: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    is_followup: Mapped[bool] = mapped_column(
        default=False,
    )

    parent_question_id: Mapped[int | None] = mapped_column(
        ForeignKey("interview_questions.id"),
        nullable=True,
    )

    interview = relationship(
        "Interview",
        back_populates="questions",
    )

    answers = relationship(
        "InterviewAnswer",
        back_populates="question",
        cascade="all, delete-orphan",
    )