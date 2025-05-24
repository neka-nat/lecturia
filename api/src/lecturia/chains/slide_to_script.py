import re

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.runnables import Runnable
from langchain.schema import SystemMessage, AIMessage
from loguru import logger
from pydantic import BaseModel, Field


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
* それぞれが会話しながら進行していくように台本を作成してください。
"""


def build_output_format_prompt(speaker_names: list[str]) -> str:
    if len(speaker_names) == 1:
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
    elif len(speaker_names) == 2:
        return (
            "{{"
            "  \"scripts\": ["
            "    {{"
            "      \"slide_no\": 1,"
            "      \"script\": ["
            "        {{"
            f"          \"name\": \"{speaker_names[0]}\","
            f"          \"content\": \"<{speaker_names[0]}の会話1>\""
            "        }},"
            "        {{"
            f"          \"name\": \"{speaker_names[1]}\","
            f"          \"content\": \"<{speaker_names[1]}の会話1>\""
            "        }},"
            "        {{"
            f"          \"name\": \"{speaker_names[0]}\","
            f"          \"content\": \"<{speaker_names[0]}の会話2>\""
            "        }},"
            "        {{"
            f"          \"name\": \"{speaker_names[1]}\","
            f"          \"content\": \"<{speaker_names[1]}の会話2>\""
            "        }},"
            "        ..."
            "      ]"
            "    }},"
            "    {{"
            "      \"slide_no\": 2,"
            "      \"script\": ["
            "        {{"
            f"          \"name\": \"{speaker_names[0]}\","
            f"          \"content\": \"<{speaker_names[0]}の会話1>\""
            "        }},"
            "        {{"
            f"          \"name\": \"{speaker_names[1]}\","
            f"          \"content\": \"<{speaker_names[1]}の会話1>\""
            "        }},"
            "        {{"
            f"          \"name\": \"{speaker_names[0]}\","
            f"          \"content\": \"<{speaker_names[0]}の会話2>\""
            "        }},"
            "        {{"
            f"          \"name\": \"{speaker_names[1]}\","
            f"          \"content\": \"<{speaker_names[1]}の会話2>\""
            "        }},"
            "        ..."
            "      ]"
            "    }},"
            "    ...\n"
            "  ]\n"
            "}}\n"
        )
    else:
        raise ValueError(f"Invalid number of speaker names: {len(speaker_names)}")


def create_slide_to_script_chain(speaker_names: list[str], use_web_search: bool = True, num_max_web_search: int = 2) -> Runnable:
    prompt_msgs = [
        SystemMessage(
            content="あなたはプレゼンの台本を作成するプロフェッショナルです。与えられたhtml形式のスライド資料からプレゼンの台本を作成してください。"
        ),
        HumanMessagePromptTemplate.from_template(
            _prompt_template.format(
                multiple_speakers_rules=_multiple_speakers_rules.format(
                    speaker_name0=speaker_names[0], speaker_name1=speaker_names[1]
                ) if len(speaker_names) > 1 else "",
                output_format=build_output_format_prompt(speaker_names),
            )
        ),
    ]
    prompt = ChatPromptTemplate(messages=prompt_msgs)
    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",
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
