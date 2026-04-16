import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    ActivityLog,
    Project,
    ProjectCreate,
    ProjectPublic,
    ProjectsPublic,
    ProjectUpdate,
    Message,
)

router = APIRouter(prefix="/projects", tags=["projects"])


def _log_action(
    session: SessionDep,
    entity_type: str,
    entity_id: uuid.UUID,
    action: str,
    user_id: uuid.UUID,
    detail: str | None = None,
) -> None:
    log = ActivityLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        user_id=user_id,
        detail=detail,
        timestamp=datetime.now(timezone.utc),
    )
    session.add(log)


@router.get("/", response_model=ProjectsPublic)
def read_projects(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """Lấy danh sách project."""
    if current_user.is_superuser:
        count = session.exec(select(func.count()).select_from(Project)).one()
        projects = session.exec(
            select(Project).order_by(col(Project.created_at).desc()).offset(skip).limit(limit)
        ).all()
    else:
        count = session.exec(
            select(func.count()).select_from(Project).where(Project.owner_id == current_user.id)
        ).one()
        projects = session.exec(
            select(Project)
            .where(Project.owner_id == current_user.id)
            .order_by(col(Project.created_at).desc())
            .offset(skip)
            .limit(limit)
        ).all()
    return ProjectsPublic(data=[ProjectPublic.model_validate(p) for p in projects], count=count)


@router.get("/{id}", response_model=ProjectPublic)
def read_project(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """Lấy chi tiết một project."""
    project = session.get(Project, id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not current_user.is_superuser and project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return project


@router.post("/", response_model=ProjectPublic)
def create_project(
    *, session: SessionDep, current_user: CurrentUser, project_in: ProjectCreate
) -> Any:
    """Tạo project mới."""
    project = Project.model_validate(project_in, update={"owner_id": current_user.id})
    session.add(project)
    session.flush()
    _log_action(session, "project", project.id, "created", current_user.id, f"Project '{project.name}' created")
    session.commit()
    session.refresh(project)
    return project


@router.patch("/{id}", response_model=ProjectPublic)
def update_project(
    *, session: SessionDep, current_user: CurrentUser, id: uuid.UUID, project_in: ProjectUpdate
) -> Any:
    """Cập nhật project."""
    project = session.get(Project, id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not current_user.is_superuser and project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    project.sqlmodel_update(project_in.model_dump(exclude_unset=True))
    session.add(project)
    _log_action(session, "project", project.id, "updated", current_user.id, f"Project '{project.name}' updated")
    session.commit()
    session.refresh(project)
    return project


@router.delete("/{id}")
def delete_project(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """Xóa project."""
    project = session.get(Project, id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not current_user.is_superuser and project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    session.delete(project)
    session.commit()
    return Message(message="Project deleted successfully")
