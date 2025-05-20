from typing import Literal

from langchain_core.runnables import Runnable
from openai import OpenAI
from openai import APIResponse
from pydantic import BaseModel


class VoiceType(BaseModel):
    name: str
    instructions: str


_instructions_woman = """Voice: Warm, upbeat, and reassuring, with a steady and confident cadence that keeps the conversation calm and productive.

Tone: Positive and solution-oriented, always focusing on the next steps rather than dwelling on the problem.

Dialect: Neutral and professional, avoiding overly casual speech but maintaining a friendly and approachable style.
"""


_instructions_cat = """Voice: High-energy, upbeat, and encouraging, projecting enthusiasm and motivation.

Punctuation: Short, punchy sentences with strategic pauses to maintain excitement and clarity.

Delivery: Fast-paced and dynamic, with rising intonation to build momentum and keep engagement high.
"""


_instructions_senior_male = """Tone: The voice should be refined, formal, and delightfully theatrical, reminiscent of a charming radio announcer from the early 20th century.

Pacing: The speech should flow smoothly at a steady cadence, neither rushed nor sluggish, allowing for clarity and a touch of grandeur.

Pronunciation: Words should be enunciated crisply and elegantly, with an emphasis on vintage expressions and a slight flourish on key phrases.
"""


_voice_types_map = {
    "woman": VoiceType(name="sage", instructions=_instructions_woman),
    "cat": VoiceType(name="onyx", instructions=_instructions_cat),
    "senior_male": VoiceType(name="ash", instructions=_instructions_senior_male),
}


VoiceTypes = Literal["woman", "cat", "senior_male"]


class TTS(Runnable):
    def __init__(self):
        self.client = OpenAI()

    def invoke(self, text: str, voice_type: VoiceTypes | None = None) -> APIResponse:
        voice_type = voice_type or "woman"

        response = self.client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice=_voice_types_map[voice_type].name,
            input=text,
            instructions=_voice_types_map[voice_type].instructions,
            speed=2.0,
        )
        return response


def create_tts_chain() -> Runnable:
    return TTS()
