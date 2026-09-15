from sqlalchemy.orm import Session

from backend.models.application import (
    Application,
)
from backend.models.status_history import (
    ApplicationStatusHistory,
)


def update_application_status(
    *,
    db: Session,
    application: Application,
    new_status: str,
    reason: str | None = None,
) -> None:

    previous_status = (
        application.status
    )

    application.status = new_status

    history = (
        ApplicationStatusHistory(
            application_id=(
                application.id
            ),
            previous_status=(
                previous_status
            ),
            new_status=new_status,
            reason=reason,
        )
    )

    db.add(history)