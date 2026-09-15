from datetime import datetime

from sqlalchemy import DateTime, Float, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    required_skills: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )

    minimum_experience: Mapped[float] = mapped_column(
        Float,
        default=0,
    )

    is_active: Mapped[bool] = mapped_column(
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    applications = relationship(
        "Application",
        back_populates="job",
        cascade="all, delete-orphan",
    )