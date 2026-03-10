import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://lecturia:lecturia@localhost:5432/lecturia")
os.environ.setdefault("GOOGLE_CLOUD_STORAGE_PUBLIC_BUCKET_NAME", "lecturia-public-storage")
os.environ.setdefault("STORAGE_EMULATOR_HOST", "http://localhost:4443")

from lecturia.database import init_db, session_scope
from lecturia.lecture_repository import upsert_lecture
from lecturia.models import MovieConfig
from lecturia.storage import (
    download_data_from_public_bucket,
    is_exists_in_public_bucket,
    ls_public_bucket,
)


init_db()

lecture_ids = ls_public_bucket("lectures")

for lecture_id in lecture_ids:
    has_events = is_exists_in_public_bucket(f"lectures/{lecture_id}/events.json")
    movie_config_json = download_data_from_public_bucket(f"lectures/{lecture_id}/movie_config.json")
    if movie_config_json is None:
        config = MovieConfig(topic="待機中..." if not has_events else "無題")
    else:
        config = MovieConfig.model_validate_json(movie_config_json)

    with session_scope() as session:
        upsert_lecture(
            session,
            lecture_id,
            "completed" if has_events else "pending",
            config=config,
            progress_percentage=100 if has_events else 0,
            current_phase="完了" if has_events else "待機中",
        )
    print(f"lecture_id {lecture_id} is saved")
