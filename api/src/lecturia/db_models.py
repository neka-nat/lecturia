from datetime import datetime, timezone
from enum import Enum
from typing import Any

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class StatusType(str, Enum):
    NOT_STARTED = "not_started"
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    DELETED = "deleted"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class LectureRecord(SQLModel, table=True):
    __tablename__ = "lectures"

    id: str = Field(primary_key=True)
    topic: str
    detail: str | None = None
    config_json: dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False))
    status: StatusType = Field(default=StatusType.NOT_STARTED, index=True)
    progress_percentage: int = Field(default=0, ge=0, le=100)
    current_phase: str | None = None
    error: str | None = None
    created_at: datetime = Field(default_factory=utc_now, index=True)
    updated_at: datetime = Field(default_factory=utc_now)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    deleted_at: datetime | None = Field(default=None, index=True)


class TaskStatusResponse(SQLModel):
    id: str
    status: StatusType
    progress_percentage: int = 0
    current_phase: str | None = None
    error: str | None = None
    created_at: datetime
    updated_at: datetime
