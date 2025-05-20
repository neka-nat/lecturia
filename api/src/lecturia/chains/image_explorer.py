import io
import os

import httpx
import requests
from langchain_core.runnables import Runnable
from loguru import logger
from PIL import Image


class ImageExplorer(Runnable):
    def __init__(self):
        self.api_key = os.getenv("BRAVE_API_KEY")
        if not self.api_key:
            raise ValueError("BRAVE_API_KEY is not set")
        self.base_url = "https://api.search.brave.com/res/v1/images/search"
        self.headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key,
        }

    def invoke(self, queries: list[str], country: str = "JP", count: int = 3) -> list[Image.Image]:
        params = {
            "q": ",".join(queries),
            "safesearch": "strict",
            "count": count,
            "search_lang": "jp",
            "country": country,
            "spellcheck": 1,
        }
        with httpx.Client() as client:
            response = client.get(
                self.base_url,
                params=params,
                headers=self.headers,
            )
            response.raise_for_status()
            results = response.json()["results"]

        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
        }
        images = []
        for result in results:
            try:
                images.append(
                    Image.open(io.BytesIO(requests.get(result["properties"]["url"], headers=headers).content)).convert("RGBA")
                )
            except Exception as e:
                logger.error(f"Failed to load image: {e}")
        return images


def create_image_explorer_chain() -> Runnable:
    return ImageExplorer()
