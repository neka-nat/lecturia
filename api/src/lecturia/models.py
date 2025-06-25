import datetime
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
            イベントがposeの場合はキャラクターの動作名("idle", "talk", "point")が入る
            イベントがquiizの場合はクイズ名が入る
        target: イベントの対象となるキャラクター
    """
    type: Literal["start", "pose", "slideNext", "slidePrev", "slideStep", "sprite", "quiz", "end"]
    time_sec: float
    name: str | None = None
    target: Literal["left", "right"] | None = None   # イベントの対象となるキャラクター


class Quiz(BaseModel):
    question: str
    choices: list[str]
    answer_index: int


class QuizSection(BaseModel):
    name: str
    slide_no: int
    quizzes: list[Quiz]


class EventList(BaseModel):
    events: list[Event]


class QuizSectionList(BaseModel):
    quiz_sections: list[QuizSection]


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
    created_at: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)

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
    """
    講義のマニフェスト

    Args:
        id: 講義のID
        title: 講義のタイトル
    """
    id: uuid.UUID
    title: str
    slide_url: str
    quiz_url: str
    audio_urls: list[str]
    quiz_sfx_url: str
    events_url: str
    sprites: dict[str, str]  # base64 encoded image
    slide_width: int
    slide_height: int
    created_at: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
