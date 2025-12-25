import re

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.runnables import Runnable
from langchain.messages import SystemMessage, AIMessage

from .slide_maker import HtmlSlide
from ..utils.ai_models import AI_MODELS


_prompt_template = """
### スライドの修正方法
- スライドの内容は変えずに以下の点を修正してください。
  - デザインやレイアウトが見やすくなっているか
  - 文字や図の見切れ、重なりが発生していないか
  - 全体を通して統一感のあるデザインになっているか
- `<script>`の部分は絶対に変更しないでください。

### 修正前のスライド
{before_slide}

### ここから本番
出力は```html```で囲んでください。
出力:
"""


def create_slide_refiner_chain() -> Runnable:
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(
                content="あなたは講義スライドを作成するプロフェッショナルです。与えられた講義スライドの修正を行ってください。"
            ),
            HumanMessagePromptTemplate.from_template(_prompt_template),
        ]
    )
    llm = ChatAnthropic(
        model=AI_MODELS["claude-default"],
        max_tokens=64000,
    )

    def parse(ai_message: AIMessage) -> HtmlSlide:
        """Parse the AI message."""
        return HtmlSlide(html=re.search(r"```html\n(.*)\n```", ai_message.content, re.DOTALL).group(1))

    return prompt | llm | parse
