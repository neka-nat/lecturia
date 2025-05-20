from typing import Literal

from pydantic import BaseModel

from .chains.tts import VoiceTypes


class Event(BaseModel):
    type: Literal["start", "pose", "slideNext", "slidePrev", "slideStep", "end"]
    time_sec: float
    name: str | None = None


class EventList(BaseModel):
    events: list[Event]


class MovieConfig(BaseModel):
    topic: str
    detail: str | None = None
    extra_slide_rules: list[str]  = []
    fps: int = 30
    num_slides: int | None = None
    page_transition_duration_sec: float = 0.5
    sprite_name: str | None = None
    voice_type: VoiceTypes | None = None
    web_search: bool = False
