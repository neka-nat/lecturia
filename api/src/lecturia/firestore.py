from os import environ
from datetime import datetime
from typing import Literal

import google.auth.credentials
from firedantic import configure, Model, Field
from google.cloud import firestore
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
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


def get_status(id: str) -> TaskStatus:
    return TaskStatus.get_by_id(id)


def upsert_status(id: str, status: StatusType, error: str | None = None) -> TaskStatus:
    status = TaskStatus.get_by_id(id)
    if status is None:
        status = TaskStatus(id=id)
    status.status = status
    status.error = error
    status.save()
    return status
