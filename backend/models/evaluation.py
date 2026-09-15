from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from backend.models.base import Base


class InterviewEvaluation(Base):

    __tablename__ = "interview_evaluations"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    interview_id: Mapped[int] = mapped_column(
        ForeignKey("interviews.id"),
        unique=True,
        nullable=False,
    )

    technical_score: Mapped[float] = mapped_column(
        Float,
        default=0,
    )

    communication_score: Mapped[float] = mapped_column(
        Float,
        default=0,
    )

    problem_solving_score: Mapped[float] = mapped_column(
        Float,
        default=0,
    )

    experience_score: Mapped[float] = mapped_column(
        Float,
        default=0,
    )

    overall_score: Mapped[float] = mapped_column(
        Float,
        default=0,
    )

    recommendation: Mapped[str] = mapped_column(
        String(50),
    )

    strengths: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )

    concerns: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    interview = relationship(
        "Interview",
        back_populates="evaluation",
    )