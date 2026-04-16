import uuid
from datetime import datetime, timezone
from enum import Enum

from pydantic import EmailStr
from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore[assignment]
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    projects: list["Project"] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore[assignment]


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime | None = None


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


# ==============================================================
# DOMAIN MODELS — SE359 Project
# ==============================================================


# ---- Enums ----
class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"
    cancelled = "cancelled"


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class BugSeverity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class BugStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    fixed = "fixed"
    closed = "closed"


class IncidentStatus(str, Enum):
    open = "open"
    investigating = "investigating"
    resolved = "resolved"


class DeploymentStatus(str, Enum):
    success = "success"
    failed = "failed"
    in_progress = "in_progress"


# ---- Project ----
class ProjectBase(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)


class Project(ProjectBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    owner: User | None = Relationship(back_populates="projects")
    tasks: list["Task"] = Relationship(back_populates="project", cascade_delete=True)
    bugs: list["Bug"] = Relationship(back_populates="project", cascade_delete=True)
    incidents: list["Incident"] = Relationship(back_populates="project", cascade_delete=True)


class ProjectPublic(ProjectBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime | None = None


class ProjectsPublic(SQLModel):
    data: list[ProjectPublic]
    count: int


# ---- Task ----
class TaskCreate(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    status: TaskStatus = TaskStatus.todo
    priority: Priority = Priority.medium
    assignee_id: uuid.UUID | None = None
    project_id: uuid.UUID


class TaskUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus | None = None
    priority: Priority | None = None
    assignee_id: uuid.UUID | None = None


class Task(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    status: TaskStatus = TaskStatus.todo
    priority: Priority = Priority.medium
    assignee_id: uuid.UUID | None = Field(default=None, foreign_key="user.id", nullable=True)
    project_id: uuid.UUID = Field(foreign_key="project.id", nullable=False, ondelete="CASCADE")
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    project: Project | None = Relationship(back_populates="tasks")


class TaskPublic(SQLModel):
    id: uuid.UUID
    title: str
    description: str | None = None
    status: TaskStatus
    priority: Priority
    assignee_id: uuid.UUID | None = None
    project_id: uuid.UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None


class TasksPublic(SQLModel):
    data: list[TaskPublic]
    count: int


# ---- Bug ----
class BugCreate(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    severity: BugSeverity = BugSeverity.medium
    status: BugStatus = BugStatus.open
    assignee_id: uuid.UUID | None = None
    project_id: uuid.UUID


class BugUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    severity: BugSeverity | None = None
    status: BugStatus | None = None
    assignee_id: uuid.UUID | None = None


class Bug(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    severity: BugSeverity = BugSeverity.medium
    status: BugStatus = BugStatus.open
    assignee_id: uuid.UUID | None = Field(default=None, foreign_key="user.id", nullable=True)
    project_id: uuid.UUID = Field(foreign_key="project.id", nullable=False, ondelete="CASCADE")
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    project: Project | None = Relationship(back_populates="bugs")


class BugPublic(SQLModel):
    id: uuid.UUID
    title: str
    description: str | None = None
    severity: BugSeverity
    status: BugStatus
    assignee_id: uuid.UUID | None = None
    project_id: uuid.UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None


class BugsPublic(SQLModel):
    data: list[BugPublic]
    count: int


# ---- Incident ----
class IncidentCreate(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    severity: BugSeverity = BugSeverity.high
    assignee_id: uuid.UUID | None = None
    project_id: uuid.UUID


class IncidentUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    severity: BugSeverity | None = None
    status: IncidentStatus | None = None
    assignee_id: uuid.UUID | None = None


class Incident(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    severity: BugSeverity = BugSeverity.high
    status: IncidentStatus = IncidentStatus.open
    assignee_id: uuid.UUID | None = Field(default=None, foreign_key="user.id", nullable=True)
    project_id: uuid.UUID = Field(foreign_key="project.id", nullable=False, ondelete="CASCADE")
    opened_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    resolved_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    project: Project | None = Relationship(back_populates="incidents")


class IncidentPublic(SQLModel):
    id: uuid.UUID
    title: str
    description: str | None = None
    severity: BugSeverity
    status: IncidentStatus
    assignee_id: uuid.UUID | None = None
    project_id: uuid.UUID
    opened_at: datetime | None = None
    resolved_at: datetime | None = None


class IncidentsPublic(SQLModel):
    data: list[IncidentPublic]
    count: int


# ---- ActivityLog ----
class ActivityLog(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    entity_type: str = Field(max_length=50)   # "task" | "bug" | "incident" | "project"
    entity_id: uuid.UUID
    action: str = Field(max_length=100)        # "created" | "status_changed" | "resolved" ...
    user_id: uuid.UUID | None = Field(default=None, foreign_key="user.id", nullable=True)
    detail: str | None = Field(default=None, max_length=500)
    timestamp: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class ActivityLogPublic(SQLModel):
    id: uuid.UUID
    entity_type: str
    entity_id: uuid.UUID
    action: str
    user_id: uuid.UUID | None = None
    detail: str | None = None
    timestamp: datetime | None = None


class ActivityLogsPublic(SQLModel):
    data: list[ActivityLogPublic]
    count: int


# ---- DeploymentInfo ----
class DeploymentInfo(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    version: str = Field(max_length=50)
    commit_sha: str | None = Field(default=None, max_length=100)
    environment: str = Field(default="production", max_length=50)
    status: DeploymentStatus = DeploymentStatus.success
    deployed_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class DeploymentInfoPublic(SQLModel):
    id: uuid.UUID
    version: str
    commit_sha: str | None = None
    environment: str
    status: DeploymentStatus
    deployed_at: datetime | None = None


class DeploymentsPublic(SQLModel):
    data: list[DeploymentInfoPublic]
    count: int
