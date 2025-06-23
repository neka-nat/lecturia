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

from .models import Manifest, MovieConfig
from .storage import (
    count_public_bucket,
    delete_data_from_public_bucket,
    download_data_from_public_bucket,
    is_exists_in_public_bucket,
    get_public_storage_url,
)
from .firestore import TaskStatus, get_all_active_status, get_status, upsert_status


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
    status_list = get_all_active_status()
    for task_status in status_list:
        lecture_id = task_status.id
        # Determine lecture status
        lecture_status = task_status.status
        created_at = task_status.created_at.isoformat()
        progress = task_status.progress_percentage
        phase = task_status.current_phase
        has_events = is_exists_in_public_bucket(f"lectures/{lecture_id}/events.json")
        if not has_events:
            logger.info(f"Find incomplete lecture without task status: {lecture_id}")
            lecture_status = "failed"

        json_str = download_data_from_public_bucket(f"lectures/{lecture_id}/movie_config.json")
        if json_str is None:
            lecture_infos.append(LectureInfo(
                id=lecture_id,
                topic="<無題>",
                detail="無し",
                created_at="",
                status=lecture_status,
            ))
        else:
            movie_config = MovieConfig.model_validate_json(json_str)
            lecture_infos.append(LectureInfo(
                id=lecture_id,
                topic=movie_config.topic,
                detail=movie_config.detail,
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
        events_url=f"/static/lectures/{lecture_id}/events.json",
        sprites=sprites,
        slide_width=1280,
        slide_height=720,
    )


@router.get("/tasks/{task_id}/status")
async def get_task_status(task_id: str) -> TaskStatus:
    task_status = get_status(task_id)
    if task_status is None:
        raise fastapi.HTTPException(status_code=404, detail="Task not found")
    return task_status


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
    # Initialize task status in Firestore
    upsert_status(lecture_id, "pending")
    return await _create_lecture_task(lecture_id, config)


@router.post("/lectures/{lecture_id}/regenerate")
async def regenerate_lecture(lecture_id: str):
    """
    講義の再生成を行う。失敗した講義IDで新たに生成処理を開始する。
    """
    logger.info(f"Regenerating lecture: {lecture_id}")

    # Get original movie config
    json_str = download_data_from_public_bucket(f"lectures/{lecture_id}/movie_config.json")
    if json_str is None:
        raise fastapi.HTTPException(status_code=404, detail="Original lecture config not found")
    config = MovieConfig.model_validate_json(json_str)

    # Reset task status to pending
    upsert_status(lecture_id, "pending")
    return await _create_lecture_task(lecture_id, config)


@router.delete("/lectures/{lecture_id}")
async def delete_lecture(lecture_id: str):
    delete_data_from_public_bucket(f"lectures/{lecture_id}")
    upsert_status(lecture_id, "deleted")
    return {"message": "Lecture deleted"}
