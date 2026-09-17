from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import Base


class InterviewSchedule(Base):
    __tablename__ = "interview_schedules"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    interview_id: Mapped[int] = mapped_column(
        ForeignKey("interviews.id"),
        nullable=False,
        unique=True,
    )

    scheduled_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    scheduled_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    timezone: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    meeting_type: Mapped[str] = mapped_column(
        String(50),
        default="google_meet",
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="pending_approval",
    )

    # AI-generated calendar title
    event_title: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # AI-generated calendar description
    event_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # AI-generated candidate-facing message
    candidate_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    google_event_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    meeting_link: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )