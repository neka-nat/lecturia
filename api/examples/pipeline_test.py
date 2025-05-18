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
            topic="排他的経済水域とは？",
            fps=15,
            detail="小学生でも分かるように、内容は元気で明るい感じにしてください。",
            extra_slide_rules=["reveal.jsを使用してスライドを作成してください。"],
            sprite_name="sprite_cat.png",
            voice_type="cat",
        ),
        # work_dir=Path(f"results/{uuid.uuid4()}"),
        work_dir=Path("results/73df2821-a145-41dd-a140-7d1cf6489b7c"),
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
