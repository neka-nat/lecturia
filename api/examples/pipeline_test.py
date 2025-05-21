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
            topic="なんでお米の価格が上がっているの？",
            fps=15,
            detail="小学生でも分かるように、内容は元気で明るい感じにしてください。最近のニュースをもとに、お米の価格が上がっている理由を説明してください。",
            extra_slide_rules=[],
            sprite_name="sprite_cat.png",
            voice_type="cat",
            web_search=True,
        ),
        #work_dir=Path(f"results/{uuid.uuid4()}"),
        work_dir=Path("results/9a943ff4-d92d-4245-9efc-7d1bc50cdb84"),
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
