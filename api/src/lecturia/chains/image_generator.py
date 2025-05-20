from io import BytesIO

from google import genai
from google.genai.types import GenerateContentConfig, Modality

from langchain_core.runnables import Runnable
from PIL import Image


class ImageGenerator(Runnable):
    def __init__(self):
        self.client = genai.Client()
        self.model = "gemini-2.0-flash-preview-image-generation"
        self.config = GenerateContentConfig(response_modalities=[Modality.TEXT, Modality.IMAGE])

    def invoke(self, prompt: str) -> list[Image.Image]:
        response = self.client.models.generate_content(
            model=self.model,
            contents=[
                f"「{prompt}」の画像を生成してください。",
            ],
            config=self.config,
        )
        images = []
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                images.append(Image.open(BytesIO(part.inline_data.data)).convert("RGBA"))
        return images


def create_image_generator_chain() -> Runnable:
    return ImageGenerator()
