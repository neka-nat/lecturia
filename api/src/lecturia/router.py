import base64
import os
import uuid
from typing import Literal

import fastapi
import grpc
from fastapi import Body
from google.cloud import tasks_v2
from google.cloud.tasks_v2.services.cloud_tasks.transports import CloudTasksGrpcTransport
from google.protobuf import duration_pb2
from loguru import logger
from pydantic import BaseModel

from .database import session_scope
from .db_models import TaskStatusResponse
from .lecture_repository import (
    get_lecture,
    list_active_lectures,
    load_movie_config,
    mark_lecture_deleted,
    to_task_status_response,
    upsert_lecture,
)
from .models import Manifest, MovieConfig
from .storage import (
    count_public_bucket,
    delete_data_from_public_bucket,
    download_data_from_public_bucket,
    is_exists_in_public_bucket,
    get_public_storage_url,
)


class LectureInfo(BaseModel):
    id: str
    topic: str
    detail: str | None = None
    created_at: str
    status: Literal["completed", "failed", "running", "pending", "deleted"] = "completed"
    progress_percentage: int | None = None
    current_phase: str | None = None


router = fastapi.APIRouter()


@router.get("/lectures")
async def list_lectures() -> list[LectureInfo]:
    lecture_infos: list[LectureInfo] = []
    with session_scope() as session:
        lecture_records = list_active_lectures(session)

    for lecture in lecture_records:
        lecture_id = lecture.id
        # Determine lecture status
        lecture_status = lecture.status
        created_at = lecture.created_at.strftime("%Y-%m-%d %H:%M:%S")
        progress = lecture.progress_percentage
        phase = lecture.current_phase
        has_events = is_exists_in_public_bucket(f"lectures/{lecture_id}/events.json")
        if (lecture.status == "completed" and not has_events) \
            or lecture.status not in ("pending", "running", "completed", "failed"):
            logger.warning(f"Inconsistent lecture data: {lecture_id}")
            lecture_status = "failed"

        lecture_infos.append(LectureInfo(
            id=lecture_id,
            topic=lecture.topic,
            detail=lecture.detail,
            created_at=created_at,
            status=lecture_status,
            progress_percentage=progress,
            current_phase=phase,
        ))
    return lecture_infos


@router.get("/lectures/{lecture_id}/manifest")
async def get_lecture_manifest(lecture_id: str) -> Manifest:
    sprite_right_bytes = download_data_from_public_bucket(f"lectures/{lecture_id}/sprites/right.png")
    sprite_left_bytes = download_data_from_public_bucket(f"lectures/{lecture_id}/sprites/left.png")
    sprites: dict[str, str] = {}
    if sprite_left_bytes:
        sprites["left"] = f"data:image/png;base64,{base64.b64encode(sprite_left_bytes).decode('utf-8')}"
    if sprite_right_bytes:
        sprites["right"] = f"data:image/png;base64,{base64.b64encode(sprite_right_bytes).decode('utf-8')}"

    audio_count = count_public_bucket(f"lectures/{lecture_id}/audio_")
    return Manifest(
        id=lecture_id,
        title=str(lecture_id),  # 現状使用してないので、仮で入れておく
        slide_url=f"/static/lectures/{lecture_id}/result_slide.html",
        quiz_url=f"/static/lectures/{lecture_id}/result_quiz.json",
        audio_urls=[
            get_public_storage_url(f"lectures/{lecture_id}/audio_{i + 1}.mp3")  # リダイレクトでOriginがnullになるので、storage.googleapis.com を直接指定
            for i in range(audio_count)
        ],
        quiz_sfx_url=get_public_storage_url(f"lectures/{lecture_id}/quiz.mp3"),
        events_url=f"/static/lectures/{lecture_id}/events.json",
        sprites=sprites,
        slide_width=1280,
        slide_height=720,
    )


@router.get("/tasks/{task_id}/status")
async def get_task_status(task_id: str) -> TaskStatusResponse:
    with session_scope() as session:
        lecture = get_lecture(session, task_id)
    if lecture is None or lecture.deleted_at is not None:
        raise fastapi.HTTPException(status_code=404, detail="Task not found")
    return to_task_status_response(lecture)


async def _create_lecture_task(lecture_id: str, config: MovieConfig) -> dict[str, str]:
    if os.getenv("LECTURIA_WORKER_URL") and os.getenv("LECTURIA_WORKER_URL") not in ["http://localhost:8001", "http://worker:8001"]:
        client = tasks_v2.CloudTasksClient()
    else:
        channel = grpc.insecure_channel("gcloud-tasks-emulator:8123")
        transport = CloudTasksGrpcTransport(channel=channel)
        client = tasks_v2.CloudTasksClient(transport=transport)
    parent = client.queue_path(os.environ["GOOGLE_CLOUD_PROJECT"], os.environ["GOOGLE_CLOUD_LOCATION"], "lecture-queue")
    logger.info(f"Parent: {parent}")
    task = tasks_v2.Task(
        http_request=tasks_v2.HttpRequest(
            http_method=tasks_v2.HttpMethod.POST,
            url=f"{os.environ['LECTURIA_WORKER_URL']}/tasks/create-lecture?lecture_id={lecture_id}",
            headers={"Content-Type": "application/json"},
            body=config.model_dump_json().encode(),
        )
    )
    # dispatch_deadline を 15 分（900 秒）に設定
    task.dispatch_deadline = duration_pb2.Duration(seconds=900)
    client.create_task(parent=parent, task=task)
    return {"task_id": lecture_id}


@router.post("/create-lecture")
async def create_lecture(config: MovieConfig = Body(...)):
    logger.info(f"Creating lecture: {config}")
    lecture_id = str(uuid.uuid4())
    with session_scope() as session:
        upsert_lecture(
            session,
            lecture_id,
            "pending",
            config=config,
            progress_percentage=0,
            current_phase="待機中",
        )
    try:
        return await _create_lecture_task(lecture_id, config)
    except Exception as exc:
        with session_scope() as session:
            upsert_lecture(
                session,
                lecture_id,
                "failed",
                error=str(exc),
                current_phase="キュー投入エラー",
            )
        raise


@router.post("/lectures/{lecture_id}/regenerate")
async def regenerate_lecture(lecture_id: str):
    """
    講義の再生成を行う。失敗した講義IDで新たに生成処理を開始する。
    """
    logger.info(f"Regenerating lecture: {lecture_id}")

    with session_scope() as session:
        lecture = get_lecture(session, lecture_id)
        if lecture is None or lecture.deleted_at is not None:
            raise fastapi.HTTPException(status_code=404, detail="Task not found")
        if lecture.status == "completed":
            raise fastapi.HTTPException(status_code=400, detail="Lecture is already completed")
        if lecture.status in ("pending", "running"):
            raise fastapi.HTTPException(status_code=400, detail="Lecture is already running")
        config = load_movie_config(lecture)
        upsert_lecture(
            session,
            lecture_id,
            "pending",
            error=None,
            progress_percentage=0,
            current_phase="待機中",
        )
    try:
        return await _create_lecture_task(lecture_id, config)
    except Exception as exc:
        with session_scope() as session:
            upsert_lecture(
                session,
                lecture_id,
                "failed",
                error=str(exc),
                current_phase="キュー投入エラー",
            )
        raise


@router.delete("/lectures/{lecture_id}")
async def delete_lecture(lecture_id: str):
    delete_data_from_public_bucket(f"lectures/{lecture_id}")
    with session_scope() as session:
        mark_lecture_deleted(session, lecture_id)
    return {"message": "Lecture deleted"}
