import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from .chains.slide_to_script import Speaker
from .chains.tts import VoiceTypes


class Event(BaseModel):
    """
    イベントは、スライドの表示、キャラクターの表情やポーズ、音声の再生などを表す。

    Args:
        type: イベントの種類
        time_sec: イベントの発生時間（秒）
        name: イベントの名前
        target: イベントの対象となるキャラクター
    """
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
    def speakers(self) -> list[Speaker]:
        return [Speaker(name=c.name, role=c.role) for c in self.characters]

    def get_voice_type(self, name: str) -> VoiceTypes:
        for c in self.characters:
            if c.name == name:
                return c.voice_type
        raise ValueError(f"Voice type not found: {name}")


class Manifest(BaseModel):
    id: uuid.UUID
    title: str
    slide_url: str
    audio_url: str
    events_url: str
    sprites: dict[str, str]  # base64 encoded image
    slide_width: int
    slide_height: int

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )