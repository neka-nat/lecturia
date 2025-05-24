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
            topic="半導体ってなんだろう？",
            fps=15,
            detail="小学生でも分かるように、内容は楽しく面白い感じにしてください。最近のニュースをもとに、半導体の重要性がどのように増してきているかを説明してください。",
            extra_slide_rules=[],
            characters=[Character(name="speaker1", role="講師", sprite_name="sprite_cat.png", voice_type="cat")],
            web_search=True,
        ),
        # work_dir=Path(f"results/{uuid.uuid4()}"),
        work_dir=Path("results/a12814db-2eed-4a19-8316-01dab6ee78da"),
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
