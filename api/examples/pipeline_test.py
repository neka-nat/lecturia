import asyncio
import uuid
from pathlib import Path

from dotenv import load_dotenv

from lecturia.models import Character, MovieConfig
from lecturia.pipeline import create_movie


load_dotenv()

async def main():
    result = await create_movie(
        MovieConfig(
            topic="103万円の壁って何のこと？",
            fps=15,
            detail="小学生でも分かるように、内容は楽しく面白い感じにしてください。最近のニュースをもとに、どのように今後制度が変わっていくかを説明してください。",
            extra_slide_rules=[],
            characters=[
                Character(name="speaker1", role="ニュース記者(男性)", sprite_name="sprite_man_right.png", voice_type="cat"),
                Character(name="speaker2", role="ニュース記者(女性)", sprite_name="sprite_woman_left.png", voice_type="woman"),
            ],
            web_search=True,
        ),
        # work_dir=Path(f"results/{uuid.uuid4()}"),
        work_dir=Path("results/1f1b6f32-3162-41e4-a40d-a9088c136aab"),
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
