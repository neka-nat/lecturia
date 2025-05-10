from typing import Literal

from pydantic import BaseModel


class Event(BaseModel):
    type: Literal["start", "pose", "slideNext", "slidePrev", "slideStep", "end"]
    time_sec: float
    name: str | None = None


class EventList(BaseModel):
    events: list[Event]


class MovieConfig(BaseModel):
    topic: str
    detail: str | None = None
    fps: int = 30
    num_slides: int | None = None
    page_transition_duration_sec: float = 0.5
