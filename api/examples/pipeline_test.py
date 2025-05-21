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
            topic="NATO(北大西洋条約機構)って何？",
            fps=15,
            detail="小学生でも分かるように、内容は元気で明るい感じにしてください。最近のウクライナとの関係性についてもも触れてください。",
            extra_slide_rules=[],
            sprite_name="sprite_cat.png",
            voice_type="cat",
            web_search=True,
        ),
        work_dir=Path(f"results/{uuid.uuid4()}"),
        # work_dir=Path("results/8b853164-e56c-4670-b2f8-040e97ef270c"),
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
