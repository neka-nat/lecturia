from langchain_core.runnables import Runnable
from openai import OpenAI
from openai import APIResponse


_instructions = """Voice: Warm, upbeat, and reassuring, with a steady and confident cadence that keeps the conversation calm and productive.

Tone: Positive and solution-oriented, always focusing on the next steps rather than dwelling on the problem.

Dialect: Neutral and professional, avoiding overly casual speech but maintaining a friendly and approachable style.
"""


class TTS(Runnable):
    def __init__(self):
        self.client = OpenAI()

    def invoke(self, text: str) -> APIResponse:
        response = self.client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="sage",
            input=text,
            instructions=_instructions,
        )
        return response


def create_tts_chain() -> Runnable:
    return TTS()
