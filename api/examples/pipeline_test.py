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
            topic="与党と野党ってなんですか？",
            fps=15,
            detail="小学生でも分かるように、内容は元気で明るい感じにしてください。",
            extra_slide_rules=["reveal.jsを使用してスライドを作成してください。"],
        ),
        work_dir=Path(f"results/{uuid.uuid4()}"),
        # work_dir=Path("results/4992ab72-b38a-4edb-b1b2-c02b1a34e9d9"),
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
