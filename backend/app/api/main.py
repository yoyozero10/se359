from fastapi import APIRouter

from app.api.routes import (
    activity_logs,
    bugs,
    devops,
    incidents,
    items,
    login,
    private,
    projects,
    tasks,
    users,
    utils,
)
from app.core.config import settings

api_router = APIRouter()

# Template routes (giữ lại)
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)

# SE359 Domain routes
api_router.include_router(projects.router)
api_router.include_router(tasks.router)
api_router.include_router(bugs.router)
api_router.include_router(incidents.router)
api_router.include_router(activity_logs.router)

# DevOps endpoints (không cần prefix /api/v1)
api_router.include_router(devops.router)

if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
