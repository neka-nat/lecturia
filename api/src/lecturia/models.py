from pydantic import BaseModel


class MovieConfig(BaseModel):
    topic: str
    detail: str | None = None
    fps: int = 30
    num_slides: int | None = None
    page_transition_duration_sec: float = 0.5
