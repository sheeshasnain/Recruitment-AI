from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
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


class Interview(Base):

    __tablename__ = "interviews"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id"),
        nullable=False,
        unique=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="prepared",
    )

    interview_type: Mapped[str] = mapped_column(
        String(50),
        default="structured",
    )

    recruiter_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    questions = relationship(
        "InterviewQuestion",
        back_populates="interview",
        cascade="all, delete-orphan",
    )

    evaluation = relationship(
        "InterviewEvaluation",
        back_populates="interview",
        uselist=False,
        cascade="all, delete-orphan",
    )