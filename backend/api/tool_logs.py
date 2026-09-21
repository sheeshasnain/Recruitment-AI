from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.tool_action_log import ToolActionLog


router = APIRouter(
    prefix="/api/v1/tool-logs",
    tags=["Tool Logs"],
)


@router.get("")
def get_tool_logs(
    db: Session = Depends(get_db),
):

    logs = (
        db.query(ToolActionLog)
        .order_by(
            ToolActionLog.created_at.desc()
        )
        .limit(100)
        .all()
    )

    return [
        {
            "id": log.id,
            "tool": log.tool_name,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "status": log.status,
            "request_payload": (
                log.request_payload
            ),
            "response_payload": (
                log.response_payload
            ),
            "error": log.error_message,
            "created_at": log.created_at,
        }
        for log in logs
    ]