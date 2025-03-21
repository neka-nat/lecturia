import asyncio
from pathlib import Path

from playwright.async_api import async_playwright
from pydantic import BaseModel
from tqdm import tqdm


class PlayConfig(BaseModel):
    fps: int = 30
    event_durations_sec: list[tuple[str, float]]
    width: int = 1280
    height: int = 720


async def play_slide(html_content: str, output_dir: Path, config: PlayConfig) -> list[Path]:
    fps = config.fps
    event_durations_sec = config.event_durations_sec

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': config.width, 'height': config.height})
        page = await context.new_page()
        await page.set_content(html_content)

        frames: list[Path] = []
        total_frames = int(sum(event_duration for _, event_duration in event_durations_sec) * fps)
        with tqdm(total=total_frames, desc="Generating frames") as pbar:
            for event_index, (event_type, event_duration) in enumerate(event_durations_sec):
                num_frames = int(event_duration * fps)
                for frame_index in range(num_frames):
                    frame_path = output_dir / f"{event_index:03d}_{frame_index:05d}.png"
                    await page.screenshot(path=frame_path)
                    frames.append(frame_path)
                    pbar.update(1)

                if event_index < len(event_durations_sec) - 1:
                    await page.keyboard.press("ArrowRight" if event_type == "page" else "Enter")
                    await asyncio.sleep(0.1)

        await browser.close()
        return frames
