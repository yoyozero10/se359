import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    ActivityLog,
    Task,
    TaskCreate,
    TaskPublic,
    TasksPublic,
    TaskUpdate,
    TaskStatus,
    Message,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _log(session: SessionDep, entity_id: uuid.UUID, action: str, user_id: uuid.UUID, detail: str | None = None) -> None:
    session.add(ActivityLog(entity_type="task", entity_id=entity_id, action=action, user_id=user_id, detail=detail, timestamp=datetime.now(timezone.utc)))


@router.get("/", response_model=TasksPublic)
def read_tasks(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    project_id: uuid.UUID | None = None,
    status: TaskStatus | None = None,
) -> Any:
    """Lấy danh sách task, có thể filter theo project_id và status."""
    stmt = select(Task)
    count_stmt = select(func.count()).select_from(Task)
    if project_id:
        stmt = stmt.where(Task.project_id == project_id)
        count_stmt = count_stmt.where(Task.project_id == project_id)
    if status:
        stmt = stmt.where(Task.status == status)
        count_stmt = count_stmt.where(Task.status == status)
    count = session.exec(count_stmt).one()
    tasks = session.exec(stmt.order_by(col(Task.created_at).desc()).offset(skip).limit(limit)).all()
    return TasksPublic(data=[TaskPublic.model_validate(t) for t in tasks], count=count)


@router.get("/{id}", response_model=TaskPublic)
def read_task(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """Lấy chi tiết task."""
    task = session.get(Task, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/", response_model=TaskPublic)
def create_task(*, session: SessionDep, current_user: CurrentUser, task_in: TaskCreate) -> Any:
    """Tạo task mới."""
    task = Task.model_validate(task_in)
    session.add(task)
    session.flush()
    _log(session, task.id, "created", current_user.id, f"Task '{task.title}' created with status={task.status.value}")
    session.commit()
    session.refresh(task)
    return task


@router.patch("/{id}", response_model=TaskPublic)
def update_task(
    *, session: SessionDep, current_user: CurrentUser, id: uuid.UUID, task_in: TaskUpdate
) -> Any:
    """Cập nhật task."""
    task = session.get(Task, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    old_status = task.status
    update_data = task_in.model_dump(exclude_unset=True)
    task.sqlmodel_update(update_data)
    task.updated_at = datetime.now(timezone.utc)
    session.add(task)
    detail = f"Updated task '{task.title}'"
    if "status" in update_data and update_data["status"] != old_status:
        detail = f"Status changed: {old_status.value} → {task.status.value}"
        _log(session, task.id, "status_changed", current_user.id, detail)
    else:
        _log(session, task.id, "updated", current_user.id, detail)
    session.commit()
    session.refresh(task)
    return task


@router.patch("/{id}/status", response_model=TaskPublic)
def update_task_status(
    *, session: SessionDep, current_user: CurrentUser, id: uuid.UUID, status: TaskStatus
) -> Any:
    """Đổi trạng thái task nhanh."""
    task = session.get(Task, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    old_status = task.status
    task.status = status
    task.updated_at = datetime.now(timezone.utc)
    session.add(task)
    _log(session, task.id, "status_changed", current_user.id, f"{old_status.value} → {status.value}")
    session.commit()
    session.refresh(task)
    return task


@router.delete("/{id}")
def delete_task(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Message:
    """Xóa task."""
    task = session.get(Task, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return Message(message="Task deleted successfully")
