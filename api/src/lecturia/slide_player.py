import asyncio
from pathlib import Path

from playwright.async_api import async_playwright
from pydantic import BaseModel
from tqdm import tqdm

from .models import Event, EventList


class PlayConfig(BaseModel):
    fps: int = 30
    events: EventList
    width: int = 1280
    height: int = 720


async def play_slide(html_content: str, output_dir: Path, config: PlayConfig) -> list[Path]:
    fps = config.fps
    event_durations_sec: list[tuple[str, float, str]] = []
    for prev_event, next_event in zip(
        [Event(type="start", time_sec=0)] + config.events.events[:-1],
        config.events.events,
    ):
        event_durations_sec.append((next_event.type, next_event.time_sec - prev_event.time_sec, next_event.name))

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': config.width, 'height': config.height})
        page = await context.new_page()
        player_html_path = Path(__file__).parent.resolve() / "html" / "player.html"
        await page.goto(player_html_path.as_uri())
        await page.evaluate("""
          async (html) => {
            const blobUrl = URL.createObjectURL(new Blob([html], {type:'text/html'}));
            const iframe  = document.getElementById('slide');
            await new Promise(res => { iframe.onload = () => res(); iframe.src = blobUrl; });
          }
        """, html_content)

        frames: list[Path] = []
        total_frames = int(sum(event_duration for _, event_duration, _ in event_durations_sec) * fps)
        with tqdm(total=total_frames, desc="Generating frames") as pbar:
            for event_index, (event_type, event_duration, event_name) in enumerate(event_durations_sec):
                num_frames = int(event_duration * fps)
                for frame_index in range(num_frames):
                    frame_path = output_dir / f"{event_index:03d}_{frame_index:05d}.png"
                    await page.screenshot(path=frame_path)
                    frames.append(frame_path)
                    pbar.update(1)

                if event_index < len(event_durations_sec) - 1:
                    await page.evaluate("ev => window.playSignal(ev)", {"type": event_type, "name": event_name})
                    await asyncio.sleep(0.1)

        await context.close()
        await browser.close()
        return frames
