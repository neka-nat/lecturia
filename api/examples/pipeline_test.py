import asyncio
import uuid
from pathlib import Path

from dotenv import load_dotenv

from lecturia.models import MovieConfig
from lecturia.pipeline import create_movie


load_dotenv()

async def main():
    result = await create_movie(
        MovieConfig(
            topic="選択的夫婦別姓制度って何？",
            fps=15,
            detail="小学生でも分かるように、内容は元気で明るい感じにしてください。最近のニュースをもとに、どのような議論がされているかを説明してください。",
            extra_slide_rules=[],
            sprite_name="sprite_woman.png",
            voice_type="woman",
            web_search=True,
        ),
        # work_dir=Path(f"results/{uuid.uuid4()}"),
        work_dir=Path("results/e6dfaf85-9d28-4f31-9474-f93c6ac22fb0"),
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
