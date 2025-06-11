import re
from pathlib import Path
from typing import Literal

from google import genai
from google.genai import types
from langchain_core.runnables import Runnable

from ..models import EventList


_prompt = """
添付の音声ファイルは以下のスライドの{slide_no}ページ目の説明を行っています。
スライドに合わせて、後でここに音声に合わせた発話を行うキャラクターアニメーションも追加されます。
音声ファイルからスライド内のアニメーションおよびキャラクターのアニメーションの実行タイミングを調整し、そのイベントが発生するタイミングを秒数で出力してください。
スライド内のアニメーションは対象のアニメーション部分の説明が音声の中で開始されるタイミングを設定するようにしてください。
スライドおよびキャラクターのアニメーションが不要なスライドであれば、空の`events`を出力してください。
{multiple_speakers_rules}

イベントの種類には以下のものがあります。

```json
{{"type": "slideStep"}}  # スライド内のアニメーションを1ステップ進めるためのイベント
{{"type": "pose", "name": "idle"}}  # キャラクターアニメーションをアイドル状態にするイベント
{{"type": "pose", "name": "talk"}}  # キャラクターアニメーションを話している状態にするイベント
{{"type": "pose", "name": "point"}}  # キャラクターアニメーションが強調を表現している状態にするイベント
```

### スライド
```html
{slides}
```

### 出力形式
```json
{output_format}
```

### ここから本番
出力は```json```で囲んでください。
出力:
"""


_multiple_speakers_rules = """キャラクターは"left"と"right"の2人がいます。
音声の喋り出しは"{first_speaker}"から始まっています。
"""


def output_format_prompt(multiple_speakers: bool) -> str:
    if multiple_speakers:
        return """{{
  "events": [
    {{"type": "pose", "name": "idle", "time_sec": 0.0, "target": "left"}},
    {{"type": "pose", "name": "idle", "time_sec": 0.0, "target": "right"}},
    {{"type": "slideStep", "time_sec": 10.5}},
    {{"type": "pose", "name": "talk", "time_sec": 15.0, "target": "right"}},
    {{"type": "slideStep", "time_sec": 20.5}},
    {{"type": "pose", "name": "talk", "time_sec": 25.0, "target": "left"}},
    ...
  ]
}}"""
    else:
        return """{{
  "events": [
    {{"type": "pose", "name": "idle", "time_sec": 0.0}},
    {{"type": "slideStep", "time_sec": 10.5}},
    {{"type": "pose", "name": "talk", "time_sec": 15.0}},
    {{"type": "slideStep", "time_sec": 20.5}},
    ...
  ]
}}"""


class EventExtractor(Runnable):
    def __init__(self):
        self.client = genai.Client()
        self.model = "gemini-2.5-flash-preview-05-20"

    async def ainvoke(
        self,
        slides_html: str,
        slide_no: int,
        audio_file: Path | str,
        first_speaker: Literal["left", "right"] | None = None,
    ) -> EventList:
        file = self.client.files.upload(file=audio_file)
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=[
                file,
                _prompt.format(
                    slide_no=slide_no,
                    slides=slides_html,
                    output_format=output_format_prompt(first_speaker is not None),
                    multiple_speakers_rules=_multiple_speakers_rules.format(first_speaker=first_speaker) if first_speaker else "",
                ),
            ],
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    include_thoughts=True
                )
            )
        )
        json_str = re.search(r"```json\n(.*)\n```", response.text, re.DOTALL).group(1)
        return EventList.model_validate_json(json_str)


def create_event_extractor_chain() -> Runnable:
    return EventExtractor()
