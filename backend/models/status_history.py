from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base


class ApplicationStatusHistory(Base):
    __tablename__ = "application_status_history"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id"),
        nullable=False,
    )

    previous_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    new_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    application = relationship(
        "Application",
        back_populates="status_history",
    )