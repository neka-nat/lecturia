import re

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.runnables import Runnable
from langchain.schema import SystemMessage, AIMessage
from loguru import logger
from pydantic import BaseModel, Field

from ..utils.ai_models import AI_MODELS


class Speaker(BaseModel):
    name: str = Field(default="", description="スライドの台本の発話者の名前")
    content: str = Field(description="発話内容")


class Script(BaseModel):
    slide_no: int = Field(description="スライドのページ番号")
    script: list[Speaker] = Field(description="スライドの台本")


class ScriptList(BaseModel):
    scripts: list[Script] = Field(description="スライドの台本のリスト")


_prompt_template = """
* 台本はスライドのページごとに分けて作成するようにしてください。
* スライドの雰囲気に合わせた話し方になるようにしてください。
* スライドの台本内でダブルクォーテーションを含む文字列はエスケープしてください。
* そのまま機械発話に読ませることを想定して、台本を書いてください。
{multiple_speakers_rules}

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


_multiple_speakers_rules = """
* 台本内で話者は{speaker_name0}と{speaker_name1}の2人います。
* {speaker_name0}の役割は{speaker_role0}です。
* {speaker_name1}の役割は{speaker_role1}です。
* それぞれが会話しながら進行していくように台本を作成してください。
"""


class Speaker(BaseModel):
    name: str = Field(description="スライドの台本の発話者の名前")
    role: str = Field(description="スライドの台本の発話者の役割")


def build_output_format_prompt(speakers: list[Speaker]) -> str:
    if len(speakers) == 1:
        return (
            "{{"
            "  \"scripts\": ["
            "    {{"
            "      \"slide_no\": 1,"
            "      \"script\": [{{"
            "        \"content\": \"<スライド1の台本>\"}}"
            "      ]"
            "    }},"
            "    {{"
            "      \"slide_no\": 2,"
            "      \"script\": [{{"
            "        \"content\": \"<スライド2の台本>\"}}"
            "      ]"
            "    }},"
            "    ..."
            "  ]"
            "}}"
        )
    elif len(speakers) == 2:
        return (
            "{{"
            "  \"scripts\": ["
            "    {{"
            "      \"slide_no\": 1,"
            "      \"script\": ["
            "        {{"
            f"          \"name\": \"{speakers[0].name}\","
            f"          \"content\": \"<{speakers[0].name}の会話1>\""
            "        }},"
            "        {{"
            f"          \"name\": \"{speakers[1].name}\","
            f"          \"content\": \"<{speakers[1].name}の会話1>\""
            "        }},"
            "        {{"
            f"          \"name\": \"{speakers[0].name}\","
            f"          \"content\": \"<{speakers[0].name}の会話2>\""
            "        }},"
            "        {{"
            f"          \"name\": \"{speakers[1].name}\","
            f"          \"content\": \"<{speakers[1].name}の会話2>\""
            "        }},"
            "        ..."
            "      ]"
            "    }},"
            "    {{"
            "      \"slide_no\": 2,"
            "      \"script\": ["
            "        {{"
            f"          \"name\": \"{speakers[0].name}\","
            f"          \"content\": \"<{speakers[0].name}の会話1>\""
            "        }},"
            "        {{"
            f"          \"name\": \"{speakers[1].name}\","
            f"          \"content\": \"<{speakers[1].name}の会話1>\""
            "        }},"
            "        {{"
            f"          \"name\": \"{speakers[0].name}\","
            f"          \"content\": \"<{speakers[0].name}の会話2>\""
            "        }},"
            "        {{"
            f"          \"name\": \"{speakers[1].name}\","
            f"          \"content\": \"<{speakers[1].name}の会話2>\""
            "        }},"
            "        ..."
            "      ]"
            "    }},"
            "    ...\n"
            "  ]\n"
            "}}\n"
        )
    else:
        raise ValueError(f"Invalid number of speaker names: {len(speakers)}")


def create_slide_to_script_chain(speakers: list[Speaker], use_web_search: bool = True, num_max_web_search: int = 2) -> Runnable:
    prompt_msgs = [
        SystemMessage(
            content="あなたはプレゼンの台本を作成するプロフェッショナルです。与えられたhtml形式のスライド資料からプレゼンの台本を作成してください。"
        ),
        HumanMessagePromptTemplate.from_template(
            _prompt_template.format(
                multiple_speakers_rules=_multiple_speakers_rules.format(
                    speaker_name0=speakers[0].name, speaker_name1=speakers[1].name,
                    speaker_role0=speakers[0].role, speaker_role1=speakers[1].role,
                ) if len(speakers) > 1 else "",
                output_format=build_output_format_prompt(speakers),
            )
        ),
    ]
    prompt = ChatPromptTemplate(messages=prompt_msgs)
    llm = ChatAnthropic(
        model=AI_MODELS["claude-default"],
        max_tokens=64000,
        thinking={"type": "enabled", "budget_tokens": 4096},
    )

    def parse(ai_message: AIMessage) -> ScriptList:
        """Parse the AI message."""
        text = "".join([m["text"] for m in ai_message.content if m["type"] == "text"])
        json_str = re.search(r"```json\n(.*)\n```", text, re.DOTALL).group(1)
        return ScriptList.model_validate_json(json_str)

    if use_web_search and num_max_web_search > 0:
        tool = {"type": "web_search_20250305", "name": "web_search", "max_uses": num_max_web_search}
        llm_with_tools = llm.bind_tools([tool])
        chain = prompt | llm_with_tools | parse
    else:
        chain = prompt | llm | parse
    return chain
