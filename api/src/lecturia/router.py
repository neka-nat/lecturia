import base64
import os
import uuid
import datetime
from pathlib import Path

import fastapi
from fastapi import Body
from google.cloud import tasks_v2

from lecturia.models import Manifest, MovieConfig
from pydantic import BaseModel


class LectureInfo(BaseModel):
    id: str
    title: str
    topic: str
    created_at: str


router = fastapi.APIRouter()
client = tasks_v2.CloudTasksClient()
parent = client.queue_path(os.environ["PROJECT_ID"], "us-central1", "lecture-queue")


@router.get("/lectures")
async def list_lectures() -> list[LectureInfo]:
    # For now, return the test lecture
    # TODO: Replace with actual database/file system lookup
    return [
        LectureInfo(
            id="c527e23f-ca9a-4d84-ac83-72b877be5a6b",
            title="サンプル講義",
            topic="テストトピック",
            created_at="2025-06-07"
        )
    ]


@router.get("/lectures/{lecture_id}/manifest")
async def get_lecture_manifest(lecture_id: str) -> Manifest:
    test_id = "c527e23f-ca9a-4d84-ac83-72b877be5a6b"
    sprites_dir = Path(__file__).resolve().parents[2] / "results" / test_id / "sprites"
    sprites: dict[str, str] = {}
    if (sprites_dir / "left.png").exists():
        with open(sprites_dir / "left.png", "rb") as f:
            sprites["left"] = f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"
    if (sprites_dir / "right.png").exists():
        with open(sprites_dir / "right.png", "rb") as f:
            sprites["right"] = f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"

    return Manifest(
        id=test_id,
        title="test",
        slide_url=f"/results/{test_id}/result_slide.html",
        audio_urls=[f"/results/{test_id}/audio_{i + 1}.mp3" for i in range(8)],
        events_url=f"/results/{test_id}/events.json",
        sprites=sprites,
        slide_width=1280,
        slide_height=720,
    )


@router.post("/create-lecture")
async def create_lecture(config: MovieConfig = Body(...)):
    task_id = str(uuid.uuid4())
    task = tasks_v2.Task(
        parent=parent,
        task_id=str(uuid.uuid4()),
        schedule_time=datetime.datetime.now(datetime.timezone.utc),
        dispatch_count=0,
        dispatch_deadline=datetime.timedelta(seconds=600),
    )
    client.create_task(task)
    return {"task_id": task_id}
