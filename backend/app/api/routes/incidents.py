import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    ActivityLog,
    Incident,
    IncidentCreate,
    IncidentPublic,
    IncidentsPublic,
    IncidentUpdate,
    IncidentStatus,
    Message,
)

router = APIRouter(prefix="/incidents", tags=["incidents"])


def _log(session: SessionDep, entity_id: uuid.UUID, action: str, user_id: uuid.UUID, detail: str | None = None) -> None:
    session.add(ActivityLog(entity_type="incident", entity_id=entity_id, action=action, user_id=user_id, detail=detail, timestamp=datetime.now(timezone.utc)))


@router.get("/", response_model=IncidentsPublic)
def read_incidents(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    project_id: uuid.UUID | None = None,
    status: IncidentStatus | None = None,
) -> Any:
    """Lấy danh sách incident, filter theo project_id / status."""
    stmt = select(Incident)
    count_stmt = select(func.count()).select_from(Incident)
    if project_id:
        stmt = stmt.where(Incident.project_id == project_id)
        count_stmt = count_stmt.where(Incident.project_id == project_id)
    if status:
        stmt = stmt.where(Incident.status == status)
        count_stmt = count_stmt.where(Incident.status == status)
    count = session.exec(count_stmt).one()
    incidents = session.exec(stmt.order_by(col(Incident.opened_at).desc()).offset(skip).limit(limit)).all()
    return IncidentsPublic(data=[IncidentPublic.model_validate(i) for i in incidents], count=count)


@router.get("/{id}", response_model=IncidentPublic)
def read_incident(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """Lấy chi tiết incident."""
    incident = session.get(Incident, id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.post("/", response_model=IncidentPublic)
def create_incident(*, session: SessionDep, current_user: CurrentUser, incident_in: IncidentCreate) -> Any:
    """Tạo incident mới."""
    incident = Incident.model_validate(incident_in)
    session.add(incident)
    session.flush()
    _log(session, incident.id, "created", current_user.id, f"Incident '{incident.title}' opened, severity={incident.severity.value}")
    session.commit()
    session.refresh(incident)
    return incident


@router.patch("/{id}", response_model=IncidentPublic)
def update_incident(
    *, session: SessionDep, current_user: CurrentUser, id: uuid.UUID, incident_in: IncidentUpdate
) -> Any:
    """Cập nhật incident."""
    incident = session.get(Incident, id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    update_data = incident_in.model_dump(exclude_unset=True)
    incident.sqlmodel_update(update_data)
    session.add(incident)
    _log(session, incident.id, "updated", current_user.id, f"Incident '{incident.title}' updated")
    session.commit()
    session.refresh(incident)
    return incident


@router.post("/{id}/resolve", response_model=IncidentPublic)
def resolve_incident(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """Resolve incident — ghi thời gian resolved_at."""
    incident = session.get(Incident, id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if incident.status == IncidentStatus.resolved:
        raise HTTPException(status_code=400, detail="Incident is already resolved")
    incident.status = IncidentStatus.resolved
    incident.resolved_at = datetime.now(timezone.utc)
    session.add(incident)
    mttr_seconds = None
    if incident.opened_at:
        delta = incident.resolved_at - incident.opened_at
        mttr_seconds = int(delta.total_seconds())
    _log(session, incident.id, "resolved", current_user.id, f"Incident resolved. MTTR: {mttr_seconds}s" if mttr_seconds else "Incident resolved")
    session.commit()
    session.refresh(incident)
    return incident


@router.delete("/{id}")
def delete_incident(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Message:
    """Xóa incident."""
    incident = session.get(Incident, id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    session.delete(incident)
    session.commit()
    return Message(message="Incident deleted successfully")
