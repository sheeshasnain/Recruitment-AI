from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    JSON,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base


class Application(Base):
    __tablename__ = "applications"

    __table_args__ = (
        UniqueConstraint(
            "candidate_id",
            "job_id",
            name="uq_candidate_job",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id"),
        nullable=False,
    )

    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="new",
    )

    screening_route: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    matched_skills: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )

    missing_skills: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )

    strengths: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )

    concerns: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )

    skills_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    experience_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    overall_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    reasoning: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    candidate = relationship(
        "Candidate",
        back_populates="applications",
    )

    job = relationship(
        "Job",
        back_populates="applications",
    )

    status_history = relationship(
        "ApplicationStatusHistory",
        back_populates="application",
        cascade="all, delete-orphan",
    )