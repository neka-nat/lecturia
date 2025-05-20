import re
from pathlib import Path

from google import genai
from langchain_core.runnables import Runnable

from ..models import EventList


_prompt = """
添付の音声ファイルは以下のスライドの{slide_no}ページ目の説明を行っています。
後で、ここにスライドの説明を行うキャラクターアニメーションも追加されます。
音声ファイルからスライド内のアニメーションおよびキャラクターのアニメーションの実行タイミングを調整し、そのイベントが発生する時間を秒数で出力してください。
スライド内のアニメーションは対象のアニメーション部分の説明が音声の中で開始されるタイミングを設定するようにしてください。
アニメーションが含まれないスライドであれば、空の`events`を出力してください。

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
{{
  "events": [
    {{"type": "pose", "name": "idle", "time_sec": 0.0}},
    {{"type": "slideStep", "time_sec": 10.5}},
    {{"type": "pose", "name": "talk", "time_sec": 15.0}},
    {{"type": "slideStep", "time_sec": 20.5}},
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
        self.model = "gemini-2.5-flash-preview-04-17"

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
