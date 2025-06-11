import tempfile
import time
from pathlib import Path

import numpy as np
from langchain.callbacks.tracers import ConsoleCallbackHandler
from loguru import logger
from moviepy.editor import AudioFileClip, ImageSequenceClip
from pydub import AudioSegment

from ..chains.event_extractor import create_event_extractor_chain
from ..chains.slide_maker import HtmlSlide, create_slide_maker_chain
from ..chains.slide_to_script import ScriptList, create_slide_to_script_chain
from ..chains.tts import Talk, create_tts_chain
from ..models import Event, EventList, MovieConfig
from ..media import remove_long_silence
from ..slide_editor import edit_slide
from .slide_player import PlayConfig, play_slide


async def create_movie(config: MovieConfig, work_dir: Path | None = None) -> Path:
    if work_dir is None:
        temp_dir = tempfile.TemporaryDirectory(prefix="lecturia_", delete=False)
        work_dir = Path(temp_dir.name)

    work_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Working directory: {work_dir}")
    with open(work_dir / "movie_config.json", "w") as f:
        f.write(config.model_dump_json())

    slide_maker = create_slide_maker_chain(config.web_search)
    slide_to_script = create_slide_to_script_chain(config.speakers)
    tts = create_tts_chain()
    event_extractor = create_event_extractor_chain()
    speaker_left_right_map = {
        speaker.name: "right" if i == 0 else "left" for i, speaker in enumerate(config.speakers)
    }

    if (work_dir / "result_slide.html").exists():
        logger.info(f"Loading result_slide.html from {work_dir / 'result_slide.html'}")
        with open(work_dir / "result_slide.html", "r") as f:
            result_slide: HtmlSlide = HtmlSlide.from_html(f.read())
    else:
        result_slide: HtmlSlide = slide_maker.invoke(
            {
                "topic": config.topic,
                "detail": config.detail or "",
                "extra_rules": "\n".join([f"- {rule}" for rule in config.extra_slide_rules]),
            },
            config={
                "callbacks": [ConsoleCallbackHandler()],
            },
        )
        # Avoid rate limit
        time.sleep(60)
        result_slide = edit_slide(result_slide)
        with open(work_dir / "result_slide.html", "w") as f:
            f.write(result_slide.export_embed_images())

    if (work_dir / "result_script.json").exists():
        logger.info(f"Loading result_script.json from {work_dir / 'result_script.json'}")
        with open(work_dir / "result_script.json", "r") as f:
            result_script: ScriptList = ScriptList.model_validate_json(f.read())
    else:
        result_script: ScriptList = slide_to_script.invoke(
            {"slides": result_slide.html},
            config={
                "callbacks": [ConsoleCallbackHandler()],
            },
        )
        with open(work_dir / "result_script.json", "w") as f:
            f.write(result_script.model_dump_json())

    audio_files: list[Path] = []
    for script in result_script.scripts:
        audio_file = work_dir / f"audio_{script.slide_no}.mp3"
        if not audio_file.exists():
            if len(config.characters) == 1:
                text = script.script[0].content
                audio = await tts.ainvoke(text, voice_type=config.characters[0].voice_type)
            else:
                talks = [
                    Talk(
                        speaker_name=speaker.name,
                        text=speaker.content,
                        voice_type=config.get_voice_type(speaker.name),
                    )
                    for speaker in script.script
                ]
                audio = await tts.multi_speaker_ainvoke(talks)
            audio.save_mp3(str(audio_file))
            removed_silence_audio = remove_long_silence(AudioSegment.from_mp3(audio_file))
            removed_silence_audio.export(audio_file, format="mp3")
        else:
            logger.info(f"Loading audio from {audio_file}")
        audio_files.append(audio_file)
    # Combine audio files with page transition duration
    audio_segments: list[AudioSegment] = []
    for audio_file in audio_files:
        audio_segments.append(
            AudioSegment.from_mp3(audio_file) + AudioSegment.silent(duration=config.page_transition_duration_sec * 1000)
        )
    slide_page_event_sec = np.cumsum([len(audio_segment) / 1000 for audio_segment in audio_segments])
    combined_audio = sum(audio_segments)
    combined_audio_file = work_dir / "combined_audio.mp3"
    combined_audio.export(combined_audio_file, format="mp3")
    logger.info(f"Generated combined audio file: {combined_audio_file}")


    if (work_dir / "events.json").exists():
        logger.info(f"Loading events.json from {work_dir / 'events.json'}")
        with open(work_dir / "events.json", "r") as f:
            events: EventList = EventList.model_validate_json(f.read())
    else:
        events: EventList = EventList(events=[])
        for slide_no, audio_file in enumerate(audio_files):
            first_speaker = (
                speaker_left_right_map[result_script.scripts[slide_no].script[0].name]
                if len(speaker_left_right_map) > 1
                else None
            )
            events_anim: EventList = await event_extractor.ainvoke(result_slide.html, slide_no + 1, audio_file, first_speaker)
            prev_sec = slide_page_event_sec[slide_no - 1] if slide_no > 0 else 0
            events.events.extend(
                [
                    Event(type=event.type, time_sec=prev_sec + event.time_sec, name=event.name, target=event.target)
                    for event in events_anim.events
                ]
            )
            events.events.append(Event(type="slideNext", time_sec=slide_page_event_sec[slide_no]))
        logger.info(f"Events: {events}")
        with open(work_dir / "events.json", "w") as f:
            f.write(events.model_dump_json())

    play_config = PlayConfig(
        fps=config.fps,
        events=events,
        sprite_names=config.sprite_names,
        layout="topleft" if len(config.characters) == 1 else "center",
    )
    logger.info(f"Play slide config: {play_config}")
    frames = await play_slide(result_slide.export_embed_images(), work_dir / "frames", play_config)

    movie_clip = ImageSequenceClip([str(frame) for frame in frames], fps=play_config.fps)
    audio_clip = AudioFileClip(str(combined_audio_file))
    movie_clip = movie_clip.set_audio(audio_clip)
    movie_path = work_dir / "movie.mp4"
    movie_clip.write_videofile(str(movie_path), codec="libx264", audio_codec="aac")

    return movie_path
