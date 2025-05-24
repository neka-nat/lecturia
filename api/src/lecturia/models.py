from typing import Literal

from pydantic import BaseModel

from .chains.tts import VoiceTypes


class Event(BaseModel):
    type: Literal["start", "pose", "slideNext", "slidePrev", "slideStep", "end"]
    time_sec: float
    name: str | None = None
    target: Literal["left", "right"] | None = None   # イベントの対象となるキャラクター


class EventList(BaseModel):
    events: list[Event]


class Character(BaseModel):
    name: str
    role: str | None = None
    sprite_name: str
    voice_type: VoiceTypes | None = None


class MovieConfig(BaseModel):
    topic: str
    detail: str | None = None
    extra_slide_rules: list[str]  = []
    fps: int = 30
    num_slides: int | None = None
    page_transition_duration_sec: float = 0.5
    characters: list[Character] = [
        Character(name="speaker1", role="講師", sprite_name="sprite_woman.png", voice_type="woman")
    ]
    web_search: bool = False

    @property
    def sprite_names(self) -> list[str]:
        return [c.sprite_name for c in self.characters]

    @property
    def speaker_names(self) -> list[str]:
        return [c.name for c in self.characters]

    def get_voice_type(self, name: str) -> VoiceTypes:
        for c in self.characters:
            if c.name == name:
                return c.voice_type
        raise ValueError(f"Voice type not found: {name}")
