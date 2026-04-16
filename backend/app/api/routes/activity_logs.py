from typing import Any

from fastapi import APIRouter
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import ActivityLog, ActivityLogPublic, ActivityLogsPublic

router = APIRouter(prefix="/activity-logs", tags=["activity-logs"])


@router.get("/", response_model=ActivityLogsPublic)
def read_activity_logs(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    entity_type: str | None = None,
) -> Any:
    """Lấy lịch sử hoạt động (audit trail). Filter tuỳ chọn theo entity_type."""
    stmt = select(ActivityLog)
    count_stmt = select(func.count()).select_from(ActivityLog)
    if entity_type:
        stmt = stmt.where(ActivityLog.entity_type == entity_type)
        count_stmt = count_stmt.where(ActivityLog.entity_type == entity_type)
    count = session.exec(count_stmt).one()
    logs = session.exec(
        stmt.order_by(col(ActivityLog.timestamp).desc()).offset(skip).limit(limit)
    ).all()
    return ActivityLogsPublic(data=[ActivityLogPublic.model_validate(log) for log in logs], count=count)
