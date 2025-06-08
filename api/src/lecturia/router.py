import base64
import os
import uuid

import fastapi
import grpc
from fastapi import Body
from google.cloud import tasks_v2
from google.cloud.tasks_v2.services.cloud_tasks.transports import CloudTasksGrpcTransport
from google.protobuf import duration_pb2
from loguru import logger
from pydantic import BaseModel

from .models import Manifest, MovieConfig
from .storage import download_data_from_public_bucket, ls_public_bucket


class LectureInfo(BaseModel):
    id: str
    title: str
    topic: str
    created_at: str


router = fastapi.APIRouter()


@router.get("/lectures")
async def list_lectures() -> list[LectureInfo]:
    lectures = ls_public_bucket("lectures")
    logger.info(f"Lectures: {lectures}")
    return [
        LectureInfo(
            id=lecture,
            title="サンプル講義",
            topic="テストトピック",
            created_at="2025-06-07"
        )
        for lecture in lectures
    ]


@router.get("/lectures/{lecture_id}/manifest")
async def get_lecture_manifest(lecture_id: str) -> Manifest:
    sprite_right_bytes = download_data_from_public_bucket(f"/{lecture_id}/sprites/right.png")
    sprite_left_bytes = download_data_from_public_bucket(f"/{lecture_id}/sprites/left.png")
    sprites: dict[str, str] = {}
    if sprite_left_bytes:
        sprites["left"] = f"data:image/png;base64,{base64.b64encode(sprite_left_bytes).decode('utf-8')}"
    if sprite_right_bytes:
        sprites["right"] = f"data:image/png;base64,{base64.b64encode(sprite_right_bytes).decode('utf-8')}"

    return Manifest(
        id=lecture_id,
        title="test",
        slide_url=f"/static/lectures/{lecture_id}/result_slide.html",
        audio_urls=[f"/static/lectures/{lecture_id}/audio_{i + 1}.mp3" for i in range(8)],
        events_url=f"/static/lectures/{lecture_id}/events.json",
        sprites=sprites,
        slide_width=1280,
        slide_height=720,
    )


@router.post("/create-lecture")
async def create_lecture(config: MovieConfig = Body(...)):
    logger.info(f"Creating lecture: {config}")
    task_id = str(uuid.uuid4())

    channel = grpc.insecure_channel("gcloud-tasks-emulator:8123")
    transport = CloudTasksGrpcTransport(channel=channel)
    client = tasks_v2.CloudTasksClient(transport=transport)
    parent = client.queue_path(os.environ["PROJECT_ID"], "asia-northeast1", "lecture-queue")
    logger.info(f"Parent: {parent}")
    task = tasks_v2.Task(
        http_request=tasks_v2.HttpRequest(
            http_method=tasks_v2.HttpMethod.POST,
            url=f"{os.environ['WORKER_URL']}/tasks/create-lecture",
            headers={"Content-Type": "application/json"},
            body=config.model_dump_json().encode(),
        )
    )
    # dispatch_deadline を 10 分（600 秒）に設定
    task.dispatch_deadline = duration_pb2.Duration(seconds=600)
    client.create_task(parent=parent, task=task)
    return {"task_id": task_id}
