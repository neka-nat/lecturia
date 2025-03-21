from langchain_core.runnables import Runnable
from openai import OpenAI
from openai import APIResponse


class TTS(Runnable):
    def __init__(self):
        self.client = OpenAI()

    def invoke(self, text: str) -> APIResponse:
        response = self.client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=text,
            instructions="講義を行っているように台本の雰囲気に合わせて話してください。",
        )
        return response


def create_tts_chain() -> Runnable:
    return TTS()
