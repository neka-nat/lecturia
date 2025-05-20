import base64
import io
import re
import uuid

from bs4 import BeautifulSoup
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.runnables import Runnable
from langchain.schema import SystemMessage, AIMessage
from pydantic import BaseModel, Field, ConfigDict
from PIL import Image


class HtmlSlide(BaseModel):
    html: str = Field(description="スライドのhtml形式の文字列")
    image_map: dict[str, Image.Image] | None = Field(default=None, description="スライド内の画像のマップ")

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def from_html(cls, html: str) -> "HtmlSlide":
        soup = BeautifulSoup(html, "html.parser")
        image_map = {}
        for img_tag in soup.find_all("img"):
            src = img_tag.get("src")
            if src is None:
                continue
            src_id = uuid.uuid4().hex
            image_map[src_id] = Image.open(io.BytesIO(base64.b64decode(src.split(",")[1])))
            img_tag["src"] = src_id
        return cls(html=soup.prettify(), image_map=image_map)

    def export_embed_images(self) -> str:
        if self.image_map is None:
            return self.html
        soup = BeautifulSoup(self.html, "html.parser")
        for img_tag in soup.find_all("img"):
            src = img_tag.get("src")
            if src is None:
                continue
            buf = io.BytesIO()
            self.image_map[src].save(buf, format="PNG")
            img_tag["src"] = f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"
        return soup.prettify()


_prompt_template = """
## スライドの作成ルール
- スライドは1ファイルのhtml形式で作成してください。
- 各スライドのどこかにページ番号を入れてください。
- 以下のようにスライド内で発生するイベントトリガに対してpostMessageで外部から操作できるようにしてください。

| イベントトリガ | 操作 |
| -------------- | ---- |
| slide-next     | 次のスライドへ |
| slide-prev     | 前のスライドへ |
| slide-step     | アニメーションなどのステップを進める |

scriptとしては以下のようなものを挿入してください。
```html
<script>
  window.addEventListener('message', (ev) => {{
    switch (ev.data) {{
      case 'slide-next': nextSlide(); break;
      case 'slide-prev': prevSlide(); break;
      case 'slide-step': slideNextStep(); break;
    }}
  }});
</script>
```

- それぞれのイベントトリガは互いに干渉しない独立したトリガになるようにしてください。
- 作成されたスライドは`iframe`で別のhtmlファイルに埋め込まれることを想定しています。スケールを変更しても文字などが見切れないようにしてください。

埋め込み用のhtmlファイルの例
```html
<head>
  ...
  <style>
    ...
    #slide{{width:90%;height:90%;border:1px solid gray}}
  </style>
</head>
<body>
  ...
  <iframe id="slide"></iframe>
  ...
</body>
```

- 視覚的に見やすいデザインのスライドを作成してください。図やアニメーションを使ったり、文字同士が不必要に重ならないようにレイアウトしてください。
  - 図は簡単な図解や図式のようなものはInline SVGで記述してください。
  - 複雑な写真や絵画のようなものは`<img>`タグを挿入し、`src`に"generated-image"と記述し、画像の説明を`alt`に入れてください。
  - 実在する人物や商品、地域などの写真を挿入したい場合は、`<img>`タグを挿入し、`src`に"searched-image"と記述し、画像の検索クエリ(複数の場合はカンマ区切り)を`alt`に入れてください。
  - 数学的なアニメーションはスライド内に`<canvas>`や`<svg>`を挿入し、MathBoxなどを使用して作成してください。
{extra_rules}

## スライドの内容
タイトル: {topic}
{detail}

## ここから本番
出力は```html```で囲んでください。
出力:
"""

def create_slide_maker_chain(use_web_search: bool = True, num_max_web_search: int = 2) -> Runnable:
    prompt_msgs = [
        SystemMessage(
            content="あなたは講義スライドを作成するプロフェッショナルです。タイトルに基づいた講義スライドをhtml形式で作成してください。"
        ),
        HumanMessagePromptTemplate.from_template(_prompt_template),
    ]
    prompt = ChatPromptTemplate(messages=prompt_msgs)
    llm = ChatAnthropic(
        model="claude-3-7-sonnet-20250219",
        max_tokens=64000,
        thinking={"type": "enabled", "budget_tokens": 4096},
    )

    def parse(ai_message: AIMessage) -> HtmlSlide:
        """Parse the AI message."""
        # indexの0番目は"thinking"で、1番目が"text"
        return HtmlSlide(html=re.search(r"```html\n(.*)\n```", ai_message.content[-1]["text"], re.DOTALL).group(1))


    if use_web_search and num_max_web_search > 0:
        tool = {"type": "web_search_20250305", "name": "web_search", "max_uses": num_max_web_search}
        llm_with_tools = llm.bind_tools([tool])
        chain = prompt | llm_with_tools | parse
    else:
        chain = prompt | llm | parse
    return chain
