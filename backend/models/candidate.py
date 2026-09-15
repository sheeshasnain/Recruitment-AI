from datetime import datetime

from sqlalchemy import DateTime, Float, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    phone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    resume_filename: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    resume_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    current_role: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    years_experience: Mapped[float] = mapped_column(
        Float,
        default=0,
    )

    skills: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )

    education: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )

    experience_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    strengths: Mapped[list] = mapped_column(
        JSON,
        default=list,
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

    applications = relationship(
        "Application",
        back_populates="candidate",
        cascade="all, delete-orphan",
    )