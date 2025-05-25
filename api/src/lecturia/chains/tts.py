from typing import Literal

from langchain_core.runnables import Runnable
from openai import OpenAI
from pydantic import BaseModel
from tts_clients.google.client import GoogleTTSClient
from tts_clients.google.models import (
    MultiSpeakerTextToAudioRequest,
    SpeakerTextToAudioRequest,
    TextToAudioRequest,
    TextToAudioResponse,
)

class VoiceType(BaseModel):
    name: str
    instructions: str


_instructions_woman = """Voice - Warm, upbeat, and reassuring, with a steady and confident cadence that keeps the conversation calm and productive.
Tone - Positive and solution-oriented, always focusing on the next steps rather than dwelling on the problem.
Dialect - Neutral and professional, avoiding overly casual speech but maintaining a friendly and approachable style.

"""


_instructions_cat = """Voice - High-energy, upbeat, and encouraging, projecting enthusiasm and motivation.
Punctuation - Short, punchy sentences with strategic pauses to maintain excitement and clarity.
Delivery - Fast-paced and dynamic, with rising intonation to build momentum and keep engagement high.

"""


_instructions_senior_male = """Tone - The voice should be refined, formal, and delightfully theatrical, reminiscent of a charming radio announcer from the early 20th century.
Pacing - The speech should flow smoothly at a steady cadence, neither rushed nor sluggish, allowing for clarity and a touch of grandeur.
Pronunciation - Words should be enunciated crisply and elegantly, with an emphasis on vintage expressions and a slight flourish on key phrases.

"""


_voice_types_map = {
    "woman": VoiceType(name="Autonoe", instructions=_instructions_woman),
    "cat": VoiceType(name="Orus", instructions=_instructions_cat),
    "senior_male": VoiceType(name="Charon", instructions=_instructions_senior_male),
    "man": VoiceType(name="Rasalgethi", instructions=""),
}


VoiceTypes = Literal["woman", "cat", "senior_male", "man"]


class Talk(BaseModel):
    speaker_name: str
    text: str
    voice_type: VoiceTypes


class TTS(Runnable):
    def __init__(self):
        self.client = OpenAI()

    def invoke(self, text: str, voice_type: VoiceTypes | None = None) -> TextToAudioResponse:
        voice_type = voice_type or "woman"
        req = TextToAudioRequest(
            text=text,
            voice_name=_voice_types_map[voice_type].name,
            instructions=_voice_types_map[voice_type].instructions,
        )
        client = GoogleTTSClient()
        response = client.text_to_audio(req)
        return response

    def multi_speaker_invoke(self, talks: list[Talk]) -> TextToAudioResponse:
        req = MultiSpeakerTextToAudioRequest(
            speakers=[
                SpeakerTextToAudioRequest(
                    speaker_name=talk.speaker_name,
                    text=talk.text,
                    voice_name=_voice_types_map[talk.voice_type].name,
                )
                for talk in talks
            ],
            instructions="TTS the following conversation between two speakers, " + "and ".join([f"{talk.speaker_name}" for talk in talks]) + ".",
        )
        client = GoogleTTSClient()
        response = client.multi_speaker_text_to_audio(req)
        return response



def create_tts_chain() -> Runnable:
    return TTS()
