from os import environ
from datetime import datetime, timezone
from typing import Literal

import google.auth.credentials
from firedantic import configure, Model
from pydantic import Field
from google.cloud import firestore
from loguru import logger
from unittest.mock import Mock


if environ.get("FIRESTORE_EMULATOR_HOST"):
    client = firestore.Client(
        project="firedantic-test",
        credentials=Mock(spec=google.auth.credentials.Credentials)
    )
else:
    client = firestore.Client()

configure(client, prefix="firedantic-test-")


StatusType = Literal["not_started", "pending", "running", "completed", "failed", "deleted"]


class TaskStatus(Model):
    """
    講義作成タスクの状態を管理するモデル
    """

    __collection__ = "task_status"
    status: StatusType = "not_started"
    progress_percentage: int = 0
    current_phase: str | None = None
    error: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def get_status(id: str) -> TaskStatus | None:
    try:
        return TaskStatus.get_by_id(id)
    except Exception as e:
        logger.info(f"Not found task status: {e}")
        return None


def get_all_active_status() -> list[TaskStatus]:
    return TaskStatus.find({"status": {"not-in": ["deleted"]}})


def upsert_status(
    id: str,
    status: StatusType,
    error: str | None = None,
    progress_percentage: int | None = None,
    current_phase: str | None = None,
) -> TaskStatus:
    try:
        task_status = TaskStatus.get_by_id(id)
    except Exception as e:
        logger.info("Not found task status, create new one")
        task_status = None

    if task_status is None:
        task_status = TaskStatus(id=id)
    task_status.status = status
    task_status.error = error
    if progress_percentage is not None:
        task_status.progress_percentage = progress_percentage
    if current_phase is not None:
        task_status.current_phase = current_phase
    task_status.updated_at = datetime.now(timezone.utc)
    task_status.save()
    return task_status
