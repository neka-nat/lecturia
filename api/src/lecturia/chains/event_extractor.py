import re
from pathlib import Path
from typing import Literal

from google import genai
from langchain_core.runnables import Runnable
from pydantic import BaseModel


class Event(BaseModel):
    type: Literal["start", "page", "animation", "end"]
    time_sec: float


class EventList(BaseModel):
    events: list[Event]


_prompt = """
添付の音声ファイルは以下のスライドの{slide_no}ページ目の説明を行っています。
音声ファイルからスライド内でのアニメーションの実行タイミングを抽出し、そのイベントが発生する時間を秒数で出力してください。
音声の流れに合うようにアニメーションの実行タイミングを調整してください。
アニメーションが含まれないスライドであれば、空の`events`を出力してください。

### スライド
```html
{slides}
```

### 出力形式
```json
{{
  "events": [
    {{"type": "animation", "time_sec": 10.5}},
    {{"type": "animation", "time_sec": 20.5}},
    ...
  ]
}}
```

### ここから本番
出力は```json```で囲んでください。
出力:
"""


class EventExtractor(Runnable):
    def __init__(self):
        self.client = genai.Client()
        self.model = "gemini-2.0-flash-001"

    def invoke(self, slides_html: str, slide_no: int, audio_file: Path | str) -> EventList:
        file = self.client.files.upload(file=audio_file)
        response = self.client.models.generate_content(
            model=self.model,
            contents=[
                file,
                _prompt.format(slide_no=slide_no, slides=slides_html),
            ],
        )
        json_str = re.search(r"```json\n(.*)\n```", response.text, re.DOTALL).group(1)
        return EventList.model_validate_json(json_str)


def create_event_extractor_chain() -> Runnable:
    return EventExtractor()
