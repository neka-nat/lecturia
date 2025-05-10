from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.runnables import Runnable
from langchain.schema import SystemMessage
from pydantic import BaseModel, Field


class HtmlSlide(BaseModel):
    html: str = Field(description="スライドのhtml形式の文字列")


_prompt_template = """
## スライドの作成ルール
1. スライドは1ファイルのhtml形式で作成してください。
2. 各スライドのどこかにページ番号を入れてください。
3. 以下のようにスライド内で発生するイベントトリガに対してpostMessageで外部から操作できるようにしてください。

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

4. 数学的なアニメーションはスライド内に`<canvas>`や`<svg>`を挿入し、MathBoxなどを使用して作成してください。


## スライドの内容
タイトル: {topic}
{detail}
"""

def create_slide_maker_chain() -> Runnable:
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
    chain = prompt | llm.with_structured_output(HtmlSlide)
    return chain
