import fastapi

from lecturia.models import Manifest


router = fastapi.APIRouter()


@router.get("/lectures/{lecture_id}/manifest")
async def get_lecture_manifest(lecture_id: str) -> Manifest:
    test_id = "4788060d-7142-4d67-b47b-36b94f807af9"
    return Manifest(
        id=test_id,
        title="test",
        slide_url=f"/api/lectures/{test_id}/slide.html",
        audio_url=f"/api/lectures/{test_id}/audio.mp3",
        events_url=f"/api/lectures/{test_id}/events.json",
        sprites_url={
            "left": f"/api/lectures/{test_id}/sprites/left.png",
            "right": f"/api/lectures/{test_id}/sprites/right.png",
        },
    )
