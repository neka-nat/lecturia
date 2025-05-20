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
            topic="地動説と天動説について",
            fps=15,
            detail="小学生でも分かるように、内容は元気で明るい感じにしてください。歴史的背景やどのように地動説が広まっていったかを説明してください。",
            extra_slide_rules=["reveal.jsを使用してスライドを作成してください。"],
            sprite_name="sprite_ancient_scholar.png",
            voice_type="senior_male",
        ),
        # work_dir=Path(f"results/{uuid.uuid4()}"),
        work_dir=Path("results/fe12bd6f-6beb-440c-9443-3f872e174f56"),
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
