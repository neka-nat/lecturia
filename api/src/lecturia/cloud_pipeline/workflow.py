import tempfile
import shutil
from pathlib import Path

import numpy as np
from fastapi import FastAPI, HTTPException, Body
from langchain_core.tracers.stdout import ConsoleCallbackHandler
from loguru import logger
from pydub import AudioSegment

from ..chains.quiz_generator import create_quiz_generator_chain
from ..chains.slide_maker import HtmlSlide, create_slide_maker_chain
from ..chains.slide_to_script import Script, ScriptList, create_slide_to_script_chain
from ..chains.tts import Talk, create_tts_chain
from ..chains.event_extractor import create_event_extractor_chain
from ..slide_editor import edit_slide
from ..utils.intervals import rewrite_talk_with_intervaltree
from ..utils.media import remove_long_silence, detect_nonsilent_ranges
from ..models import MovieConfig, EventList, Event, QuizSectionList
from ..storage import is_exists_in_public_bucket, download_data_from_public_bucket, upload_data_to_public_bucket
from ..firestore import upsert_status
from ..utils.async_tools import gather_limited

app = FastAPI()


def _modify_events_by_check_silence(ev: EventList, audio_file: Path) -> EventList:
    audio = AudioSegment.from_mp3(audio_file)
    ranges = detect_nonsilent_ranges(audio)
    return rewrite_talk_with_intervaltree(ev, ranges, ["right"])


def _create_slide_phase(lecture_id: str, config: MovieConfig) -> HtmlSlide:
    slide_maker = create_slide_maker_chain(config.web_search)
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
        result_slide = edit_slide(result_slide, use_refiner=False)
        upload_data_to_public_bucket(result_slide.export_embed_images(), f"lectures/{lecture_id}/result_slide.html", "text/html")
    return result_slide


def _create_script_phase(lecture_id: str, config: MovieConfig, result_slide: HtmlSlide) -> ScriptList:
    slide_to_script = create_slide_to_script_chain(config.speakers)
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
    return result_script


async def _create_quiz_phase(lecture_id: str, result_slide: HtmlSlide) -> QuizSectionList:
    quiz_generator = create_quiz_generator_chain()
    if is_exists_in_public_bucket(f"lectures/{lecture_id}/result_quiz.json"):
        logger.info(f"Loading result_quiz.json from {f'lectures/{lecture_id}/result_quiz.json'}")
        data = download_data_from_public_bucket(f"lectures/{lecture_id}/result_quiz.json")
        result_quiz: QuizSectionList = QuizSectionList.model_validate_json(data.decode("utf-8"))
    else:
        result_quiz: QuizSectionList = await quiz_generator.ainvoke(
            {"slides": result_slide.html},
            config={
                "callbacks": [ConsoleCallbackHandler()],
            },
        )
        upload_data_to_public_bucket(result_quiz.model_dump_json(), f"lectures/{lecture_id}/result_quiz.json", "application/json")
    return result_quiz


async def _generate_audio_phase(
    lecture_id: str,
    config: MovieConfig,
    result_script: ScriptList,
    temp_dir: str,
    max_parallel: int = 3,
) -> tuple[list[Path], np.ndarray]:
    tts = create_tts_chain()

    async def _render_one(script: Script) -> Path:
        audio_file = Path(temp_dir) / f"audio_{script.slide_no}.mp3"

        if not is_exists_in_public_bucket(f"lectures/{lecture_id}/{audio_file.name}"):
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
            removed = remove_long_silence(AudioSegment.from_mp3(audio_file))
            removed.export(audio_file, format="mp3")
            upload_data_to_public_bucket(
                audio_file.read_bytes(), f"lectures/{lecture_id}/{audio_file.name}", "audio/mpeg"
            )
        else:
            data = download_data_from_public_bucket(f"lectures/{lecture_id}/{audio_file.name}")
            audio_file.write_bytes(data)
        return audio_file

    audio_files = await gather_limited(
        [_render_one(script) for script in result_script.scripts],
        max_parallel=max_parallel,
    )

    # Calculate audio segments with page transition duration
    audio_segments: list[AudioSegment] = []
    for audio_file in audio_files:
        upload_data_to_public_bucket(audio_file.read_bytes(), f"lectures/{lecture_id}/{audio_file.name}", "audio/mpeg")
        audio_segments.append(
            AudioSegment.from_mp3(audio_file) + AudioSegment.silent(duration=config.page_transition_duration_sec * 1000)
        )
    slide_page_event_sec = np.cumsum([len(audio_segment) / 1000 for audio_segment in audio_segments])
    return audio_files, slide_page_event_sec


async def _create_event_phase(
    lecture_id: str,
    result_slide: HtmlSlide,
    result_script: ScriptList,
    result_quiz: QuizSectionList,
    audio_files: list[Path],
    slide_page_event_sec: np.ndarray,
    speaker_left_right_map: dict[str, str],
    max_parallel: int = 3,
) -> EventList:
    slide_no_to_quiz_section_map = {quiz_section.slide_no: quiz_section for quiz_section in result_quiz.quiz_sections}

    event_extractor = create_event_extractor_chain()
    if is_exists_in_public_bucket(f"lectures/{lecture_id}/events.json"):
        logger.info(f"Loading events.json from {f'lectures/{lecture_id}/events.json'}")
        data = download_data_from_public_bucket(f"lectures/{lecture_id}/events.json")
        events: EventList = EventList.model_validate_json(data.decode("utf-8"))
    else:
        events: EventList = EventList(events=[])

        async def _extract_one(slide_no: int, audio_file: Path) -> list[Event]:
            first_speaker = (
                speaker_left_right_map[result_script.scripts[slide_no].script[0].name]
                if len(speaker_left_right_map) > 1
                else None
            )
            ev = await event_extractor.ainvoke(
                result_slide.html,
                slide_no + 1,
                audio_file,
                first_speaker,
            )
            # スピーカーが一人のときは、発話区間を調整
            if len(speaker_left_right_map) == 1:
                ev = _modify_events_by_check_silence(ev, audio_file)
            prev_sec = slide_page_event_sec[slide_no - 1] if slide_no > 0 else 0
            # 開始時刻をずらしたうえで返す
            adjusted = [
                Event(type=e.type, time_sec=prev_sec + e.time_sec, name=e.name, target=e.target)
                for e in ev.events
            ] + [
                Event(type="slideNext", time_sec=slide_page_event_sec[slide_no])
            ]
            # クイズがあれば追加
            if slide_no in slide_no_to_quiz_section_map:
                adjusted.append(
                    Event(
                        type="quiz",
                        time_sec=slide_page_event_sec[slide_no],
                        name=slide_no_to_quiz_section_map[slide_no].name,
                    )
                )
            return adjusted

        results = await gather_limited(
            [_extract_one(idx, f) for idx, f in enumerate(audio_files)],
            max_parallel=max_parallel,
        )
        for ev_list in results:
            events.events.extend(ev_list)
        logger.info(f"Events: {events}")
        upload_data_to_public_bucket(events.model_dump_json(), f"lectures/{lecture_id}/events.json", "application/json")
    return events


@app.get("/")
async def root():
    return {"message": "Hello, World!"}


@app.get("/health")
async def health():
    return {"message": "OK"}


@app.post("/tasks/create-lecture")
async def create_lecture(lecture_id: str, config: MovieConfig = Body(...)):
    upsert_status(lecture_id, "running", progress_percentage=0, current_phase="初期化中")
    try:
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

        upload_data_to_public_bucket(
            (Path(__file__).parent.parent.resolve() / "html" / f"quiz_{character.voice_type}.mp3").read_bytes(),
            f"lectures/{lecture_id}/quiz.mp3",
            "audio/mpeg",
        )

        # Phase 1: Create slides (25% progress)
        upsert_status(lecture_id, "running", progress_percentage=10, current_phase="スライド生成中")
        result_slide = _create_slide_phase(lecture_id, config)

        # Phase 2: Create script (50% progress)
        upsert_status(lecture_id, "running", progress_percentage=25, current_phase="スクリプト作成中")
        result_script = _create_script_phase(lecture_id, config, result_slide)

        # Phase 3: Create quiz (60% progress)
        upsert_status(lecture_id, "running", progress_percentage=60, current_phase="クイズ作成中")
        result_quiz_task = _create_quiz_phase(lecture_id, result_slide)

        # Phase 4: Generate audio (75% progress)
        upsert_status(lecture_id, "running", progress_percentage=50, current_phase="音声生成中")
        temp_dir = tempfile.mkdtemp()
        audio_files, slide_page_event_sec = await _generate_audio_phase(lecture_id, config, result_script, temp_dir)

        # Phase 5: Create events (90% progress)
        result_quiz = await result_quiz_task
        upsert_status(lecture_id, "running", progress_percentage=75, current_phase="イベント作成中")
        await _create_event_phase(
            lecture_id,
            result_slide,
            result_script,
            result_quiz,
            audio_files,
            slide_page_event_sec,
            speaker_left_right_map,
        )

        # Cleanup and completion (100% progress)
        upsert_status(lecture_id, "running", progress_percentage=95, current_phase="最終処理中")
        shutil.rmtree(temp_dir)
        upsert_status(lecture_id, "completed", progress_percentage=100, current_phase="完了")
    except Exception as e:
        logger.error(f"Error creating lecture {lecture_id}: {str(e)}")
        upsert_status(lecture_id, "failed", error=str(e), current_phase="エラー")
        raise
    return {"lecture_id": lecture_id}
