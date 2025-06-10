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


StatusType = Literal["not_started", "pending", "running", "completed", "failed"]


class TaskStatus(Model):
    __collection__ = "task_status"
    status: StatusType = "not_started"
    error: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def get_status(id: str) -> TaskStatus:
    return TaskStatus.get_by_id(id)


def upsert_status(id: str, status: StatusType, error: str | None = None) -> TaskStatus:
    try:
        task_status = TaskStatus.get_by_id(id)
    except Exception as e:
        logger.info("Not found task status, create new one")
        task_status = None

    if task_status is None:
        task_status = TaskStatus(id=id)
    task_status.status = status
    task_status.error = error
    task_status.updated_at = datetime.now(timezone.utc)
    task_status.save()
    return task_status
