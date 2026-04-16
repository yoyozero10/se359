import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    ActivityLog,
    Bug,
    BugCreate,
    BugPublic,
    BugsPublic,
    BugUpdate,
    BugStatus,
    BugSeverity,
    Message,
)

router = APIRouter(prefix="/bugs", tags=["bugs"])


def _log(session: SessionDep, entity_id: uuid.UUID, action: str, user_id: uuid.UUID, detail: str | None = None) -> None:
    session.add(ActivityLog(entity_type="bug", entity_id=entity_id, action=action, user_id=user_id, detail=detail, timestamp=datetime.now(timezone.utc)))


@router.get("/", response_model=BugsPublic)
def read_bugs(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    project_id: uuid.UUID | None = None,
    status: BugStatus | None = None,
    severity: BugSeverity | None = None,
) -> Any:
    """Lấy danh sách bug, filter theo project_id / status / severity."""
    stmt = select(Bug)
    count_stmt = select(func.count()).select_from(Bug)
    if project_id:
        stmt = stmt.where(Bug.project_id == project_id)
        count_stmt = count_stmt.where(Bug.project_id == project_id)
    if status:
        stmt = stmt.where(Bug.status == status)
        count_stmt = count_stmt.where(Bug.status == status)
    if severity:
        stmt = stmt.where(Bug.severity == severity)
        count_stmt = count_stmt.where(Bug.severity == severity)
    count = session.exec(count_stmt).one()
    bugs = session.exec(stmt.order_by(col(Bug.created_at).desc()).offset(skip).limit(limit)).all()
    return BugsPublic(data=[BugPublic.model_validate(b) for b in bugs], count=count)


@router.get("/{id}", response_model=BugPublic)
def read_bug(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """Lấy chi tiết bug."""
    bug = session.get(Bug, id)
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    return bug


@router.post("/", response_model=BugPublic)
def create_bug(*, session: SessionDep, current_user: CurrentUser, bug_in: BugCreate) -> Any:
    """Tạo bug mới."""
    bug = Bug.model_validate(bug_in)
    session.add(bug)
    session.flush()
    _log(session, bug.id, "created", current_user.id, f"Bug '{bug.title}' created, severity={bug.severity.value}")
    session.commit()
    session.refresh(bug)
    return bug


@router.patch("/{id}", response_model=BugPublic)
def update_bug(
    *, session: SessionDep, current_user: CurrentUser, id: uuid.UUID, bug_in: BugUpdate
) -> Any:
    """Cập nhật bug."""
    bug = session.get(Bug, id)
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    old_status = bug.status
    update_data = bug_in.model_dump(exclude_unset=True)
    bug.sqlmodel_update(update_data)
    bug.updated_at = datetime.now(timezone.utc)
    session.add(bug)
    if "status" in update_data and update_data["status"] != old_status:
        _log(session, bug.id, "status_changed", current_user.id, f"{old_status.value} → {bug.status.value}")
    else:
        _log(session, bug.id, "updated", current_user.id, f"Bug '{bug.title}' updated")
    session.commit()
    session.refresh(bug)
    return bug


@router.delete("/{id}")
def delete_bug(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Message:
    """Xóa bug."""
    bug = session.get(Bug, id)
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    session.delete(bug)
    session.commit()
    return Message(message="Bug deleted successfully")
