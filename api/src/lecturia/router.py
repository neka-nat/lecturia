import base64
from pathlib import Path

import fastapi

from lecturia.models import Manifest


router = fastapi.APIRouter()


@router.get("/lectures/{lecture_id}/manifest")
async def get_lecture_manifest(lecture_id: str) -> Manifest:
    test_id = "c527e23f-ca9a-4d84-ac83-72b877be5a6b"
    sprites_dir = Path(__file__).resolve().parents[2] / "results" / test_id / "sprites"
    sprites: dict[str, str] = {}
    if (sprites_dir / "left.png").exists():
        with open(sprites_dir / "left.png", "rb") as f:
            sprites["left"] = base64.b64encode(f.read()).decode("utf-8")
    if (sprites_dir / "right.png").exists():
        with open(sprites_dir / "right.png", "rb") as f:
            sprites["right"] = base64.b64encode(f.read()).decode("utf-8")

    return Manifest(
        id=test_id,
        title="test",
        slide_url=f"/results/{test_id}/result_slide.html",
        audio_url=f"/results/{test_id}/audio_1.mp3",
        events_url=f"/results/{test_id}/events.json",
        sprites=sprites,
    )
