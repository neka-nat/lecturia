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
            topic="万博って何？",
            fps=15,
            detail="小学生でも分かるように、内容は楽しく面白い感じにしてください。今年大阪で開催されている大阪万博についても触れてください。",
            extra_slide_rules=[],
            characters=[
                Character(name="speaker1", role="講師1(男性)", sprite_name="sprite_man_right.png", voice_type="man"),
                Character(name="speaker2", role="講師2(女性)", sprite_name="sprite_woman_left.png", voice_type="woman"),
            ],
            # characters=[
            #     Character(name="speaker1", role="学者", sprite_name="sprite_ancient_scholar.png", voice_type="senior_male"),
            # ],
            web_search=True,
        ),
        # work_dir=Path(f"results/{uuid.uuid4()}"),
        work_dir=Path("results/dda01fb0-316e-4c9f-91e6-eeac8f87c08d"),
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
