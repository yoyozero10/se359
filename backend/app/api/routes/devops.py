import os
from typing import Any

from fastapi import APIRouter
from sqlmodel import select

from app.api.deps import SessionDep
from app.models import DeploymentInfo, DeploymentInfoPublic, DeploymentsPublic

router = APIRouter(tags=["devops"])


@router.get("/healthz", include_in_schema=True)
def healthz() -> dict:
    """Liveness probe — app còn sống không."""
    return {"status": "ok"}


@router.get("/readyz", include_in_schema=True)
def readyz(session: SessionDep) -> dict:
    """Readiness probe — app sẵn sàng nhận request (kiểm tra DB)."""
    try:
        session.exec(select(1))  # type: ignore
        db_ok = True
    except Exception:
        db_ok = False
    return {"status": "ok" if db_ok else "degraded", "db": "ok" if db_ok else "error"}


@router.get("/version", include_in_schema=True)
def version() -> dict:
    """Trả về version và commit SHA đang chạy."""
    return {
        "version": os.getenv("APP_VERSION", "0.1.0"),
        "commit_sha": os.getenv("GIT_COMMIT_SHA", "local"),
        "environment": os.getenv("ENVIRONMENT", "local"),
    }


@router.get("/deployments", response_model=DeploymentsPublic, tags=["devops"])
def read_deployments(session: SessionDep, skip: int = 0, limit: int = 20) -> Any:
    """Lịch sử deployment."""
    from sqlmodel import col, func
    count = session.exec(select(func.count()).select_from(DeploymentInfo)).one()
    deployments = session.exec(
        select(DeploymentInfo).order_by(col(DeploymentInfo.deployed_at).desc()).offset(skip).limit(limit)
    ).all()
    return DeploymentsPublic(data=[DeploymentInfoPublic.model_validate(d) for d in deployments], count=count)
