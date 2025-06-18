import os
import re

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.runnables import Runnable
from langchain.schema import SystemMessage, AIMessage

from ..models import QuizSectionList


_prompt_template = """
* スライドのページの間に挟むクイズを考えてください。
* どのページの間に挟むかは、クイズを表示する前のページを記載してください。

## スライド資料
```html
{{slides}}
```

## 出力形式
```json
{output_format}
```

## ここから本番
出力は```json```で囲んでください。
出力:
"""


def build_output_format_prompt() -> str:
    return (
        "{{"
        "  \"quiz_sections\": ["
        "    {{"
        "      \"name\": \"<クイズセクションの名前>\","
        "      \"slide_no\": <クイズセクションのスライド番号>,"
        "      \"quizzes\": ["
        "        {{"
        "          \"question\": \"<クイズの問題>\","
        "          \"choices\": [\"<クイズの選択肢1>\", \"<クイズの選択肢2>\", \"<クイズの選択肢3>\", ...],"
        "          \"answer_index\": <正解の選択肢の番号>"
        "        }},"
        "      ],"
        "    }},"
        "    {{"
        "      \"name\": \"<クイズセクションの名前>\","
        "      \"slide_no\": <次のクイズセクションのスライド番号>,"
        "      \"quizzes\": ["
        "        {{"
        "          \"question\": \"<クイズの問題>\","
        "          \"choices\": [\"<クイズの選択肢1>\", \"<クイズの選択肢2>\", \"<クイズの選択肢3>\", ...],"
        "          \"answer_index\": <正解の選択肢の番号>"
        "        }},"
        "      ],"
        "    }},"
        "    ...,"
        "  ]"
        "}}"
    )
 

def create_quiz_generator_chain() -> Runnable:
    prompt_msgs = [
        SystemMessage(
            content="あなたはクイズを作成するプロフェッショナルです。与えられたhtml形式のスライド資料のページの間に挟むクイズを作成してください。"
        ),
        HumanMessagePromptTemplate.from_template(
            _prompt_template.format(
                output_format=build_output_format_prompt(),
            )
        ),
    ]
    prompt = ChatPromptTemplate(messages=prompt_msgs)
    if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ or "K_SERVICE" in os.environ:
        llm = ChatVertexAI(
            model="gemini-2.5-flash-preview-05-20",
            max_tokens=65536,
        )
    else:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-preview-05-20",
            max_tokens=65536,
        )

    def parse(ai_message: AIMessage) -> QuizSectionList:
        """Parse the AI message."""
        text = ai_message.content
        json_str = re.search(r"```json\n(.*)\n```", text, re.DOTALL).group(1)
        return QuizSectionList.model_validate_json(json_str)

    chain = prompt | llm | parse
    return chain
