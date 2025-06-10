import uuid
import tempfile
import time
import shutil
from pathlib import Path

import numpy as np
from fastapi import FastAPI, HTTPException, Body
from langchain_core.tracers.stdout import ConsoleCallbackHandler
from loguru import logger
from pydub import AudioSegment

from ..chains.slide_maker import HtmlSlide, create_slide_maker_chain
from ..chains.slide_to_script import ScriptList, create_slide_to_script_chain
from ..chains.tts import Talk, create_tts_chain
from ..chains.event_extractor import create_event_extractor_chain
from ..slide_editor import edit_slide
from ..media import remove_long_silence
from ..models import MovieConfig, EventList, Event
from ..storage import is_exists_in_public_bucket, download_data_from_public_bucket, upload_data_to_public_bucket
from ..firestore import upsert_status


app = FastAPI()


@app.post("/tasks/create-lecture")
async def create_lecture(lecture_id: str, config: MovieConfig = Body(...)):

    upsert_status(lecture_id, "running")
    
    try:
        slide_maker = create_slide_maker_chain(config.web_search)
        slide_to_script = create_slide_to_script_chain(config.speakers)
        tts = create_tts_chain()
        event_extractor = create_event_extractor_chain()

        speaker_left_right_map = {
            speaker.name: "right" if i == 0 else "left" for i, speaker in enumerate(config.speakers)
        }

        # upload movie_config.json
        upload_data_to_public_bucket(config.model_dump_json(), f"lectures/{lecture_id}/movie_config.json", "application/json")

        # upload sprites
        for i, character in enumerate(config.characters):
            if i == 0:
                sprite_path = Path(__file__).parent.parent.resolve() / "html" / character.sprite_name
                upload_data_to_public_bucket(sprite_path.read_bytes(), f"lectures/{lecture_id}/sprites/right.png", "image/png")
            else:
                sprite_path = Path(__file__).parent.parent.resolve() / "html" / character.sprite_name
                upload_data_to_public_bucket(sprite_path.read_bytes(), f"lectures/{lecture_id}/sprites/left.png", "image/png")

        if is_exists_in_public_bucket(f"lectures/{lecture_id}/result_slide.html"):
            logger.info(f"Loading result_slide.html from {f'lectures/{lecture_id}/result_slide.html'}")
            data = download_data_from_public_bucket(f"lectures/{lecture_id}/result_slide.html")
            result_slide: HtmlSlide = HtmlSlide.from_html(data.decode("utf-8"))
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
            upload_data_to_public_bucket(result_slide.export_embed_images(), f"lectures/{lecture_id}/result_slide.html", "text/html")

        if is_exists_in_public_bucket(f"lectures/{lecture_id}/result_script.json"):
            logger.info(f"Loading result_script.json from {f'lectures/{lecture_id}/result_script.json'}")
            data = download_data_from_public_bucket(f"lectures/{lecture_id}/result_script.json")
            result_script: ScriptList = ScriptList.model_validate_json(data.decode("utf-8"))
        else:
            result_script: ScriptList = slide_to_script.invoke(
                {"slides": result_slide.html},
                config={
                    "callbacks": [ConsoleCallbackHandler()],
                },
            )
            upload_data_to_public_bucket(result_script.model_dump_json(), f"lectures/{lecture_id}/result_script.json", "application/json")

        temp_dir = tempfile.mkdtemp()
        audio_files: list[Path] = []
        for script in result_script.scripts:
            audio_file = Path(temp_dir) / f"audio_{script.slide_no}.mp3"
            if not is_exists_in_public_bucket(f"lectures/{lecture_id}/audio_{script.slide_no}.mp3"):
                if len(config.characters) == 1:
                    text = script.script[0].content
                    audio = tts.invoke(text, voice_type=config.characters[0].voice_type)
                else:
                    talks = [
                        Talk(
                            speaker_name=speaker.name,
                            text=speaker.content,
                            voice_type=config.get_voice_type(speaker.name),
                        )
                        for speaker in script.script
                    ]
                    audio = tts.multi_speaker_invoke(talks)
                audio.save_mp3(str(audio_file))
                removed_silence_audio = remove_long_silence(AudioSegment.from_mp3(audio_file))
                removed_silence_audio.export(audio_file, format="mp3")
            else:
                logger.info(f"Loading audio from {audio_file}")
            audio_files.append(audio_file)
        # Calculate audio segments with page transition duration
        audio_segments: list[AudioSegment] = []
        for audio_file in audio_files:
            upload_data_to_public_bucket(audio_file.read_bytes(), f"lectures/{lecture_id}/{audio_file.name}", "audio/mpeg")
            audio_segments.append(
                AudioSegment.from_mp3(audio_file) + AudioSegment.silent(duration=config.page_transition_duration_sec * 1000)
            )
        slide_page_event_sec = np.cumsum([len(audio_segment) / 1000 for audio_segment in audio_segments])

        if is_exists_in_public_bucket(f"lectures/{lecture_id}/events.json"):
            logger.info(f"Loading events.json from {f'lectures/{lecture_id}/events.json'}")
            data = download_data_from_public_bucket(f"lectures/{lecture_id}/events.json")
            events: EventList = EventList.model_validate_json(data.decode("utf-8"))
        else:
            events: EventList = EventList(events=[])
            for slide_no, audio_file in enumerate(audio_files):
                first_speaker = (
                    speaker_left_right_map[result_script.scripts[slide_no].script[0].name]
                    if len(speaker_left_right_map) > 1
                    else None
                )
                events_anim: EventList = event_extractor.invoke(result_slide.html, slide_no + 1, audio_file, first_speaker)
                prev_sec = slide_page_event_sec[slide_no - 1] if slide_no > 0 else 0
                events.events.extend(
                    [
                        Event(type=event.type, time_sec=prev_sec + event.time_sec, name=event.name, target=event.target)
                        for event in events_anim.events
                    ]
                )
                events.events.append(Event(type="slideNext", time_sec=slide_page_event_sec[slide_no]))
            logger.info(f"Events: {events}")
            upload_data_to_public_bucket(events.model_dump_json(), f"lectures/{lecture_id}/events.json", "application/json")

        shutil.rmtree(temp_dir)
        upsert_status(lecture_id, "completed")
    except Exception as e:
        logger.error(f"Error creating lecture {lecture_id}: {str(e)}")
        upsert_status(lecture_id, "failed", str(e))
        raise
    return {"lecture_id": lecture_id}
