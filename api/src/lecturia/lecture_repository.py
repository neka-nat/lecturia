from sqlmodel import Session, select

from .db_models import LectureRecord, StatusType, TaskStatusResponse, utc_now
from .models import MovieConfig


def _clamp_progress(progress_percentage: int | None, fallback: int) -> int:
    if progress_percentage is None:
        return fallback
    return max(0, min(progress_percentage, 100))


def get_lecture(session: Session, lecture_id: str) -> LectureRecord | None:
    return session.get(LectureRecord, lecture_id)


def list_active_lectures(session: Session) -> list[LectureRecord]:
    statement = (
        select(LectureRecord)
        .where(LectureRecord.deleted_at.is_(None))
        .order_by(LectureRecord.created_at.desc())
    )
    return list(session.exec(statement).all())


def upsert_lecture(
    session: Session,
    lecture_id: str,
    status: StatusType,
    *,
    config: MovieConfig | None = None,
    error: str | None = None,
    progress_percentage: int | None = None,
    current_phase: str | None = None,
) -> LectureRecord | None:
    lecture = get_lecture(session, lecture_id)
    now = utc_now()

    if lecture is None:
        if config is None:
            return None
        lecture = LectureRecord(
            id=lecture_id,
            topic=config.topic,
            detail=config.detail,
            config_json=config.model_dump(mode="json"),
            status=status,
            progress_percentage=_clamp_progress(progress_percentage, 0),
            current_phase=current_phase,
            error=error,
            created_at=now,
            updated_at=now,
        )
        if status == "running":
            lecture.started_at = now
        if status == "completed":
            lecture.started_at = now
            lecture.completed_at = now
            lecture.progress_percentage = _clamp_progress(progress_percentage, 100)
        if status == "deleted":
            lecture.deleted_at = now
        session.add(lecture)
        session.commit()
        session.refresh(lecture)
        return lecture

    if config is not None:
        lecture.topic = config.topic
        lecture.detail = config.detail
        lecture.config_json = config.model_dump(mode="json")

    lecture.status = status
    lecture.error = error
    lecture.progress_percentage = _clamp_progress(progress_percentage, lecture.progress_percentage)
    if current_phase is not None:
        lecture.current_phase = current_phase
    lecture.updated_at = now

    if status == "pending":
        lecture.started_at = None
        lecture.completed_at = None
        lecture.deleted_at = None
    elif status == "running":
        lecture.started_at = lecture.started_at or now
        lecture.completed_at = None
        lecture.deleted_at = None
    elif status == "completed":
        lecture.started_at = lecture.started_at or now
        lecture.completed_at = now
        lecture.deleted_at = None
        if progress_percentage is None:
            lecture.progress_percentage = 100
    elif status == "failed":
        lecture.completed_at = None
        lecture.deleted_at = None
    elif status == "deleted":
        lecture.deleted_at = now

    session.add(lecture)
    session.commit()
    session.refresh(lecture)
    return lecture


def mark_lecture_deleted(session: Session, lecture_id: str) -> LectureRecord | None:
    return upsert_lecture(session, lecture_id, "deleted", error=None)


def load_movie_config(lecture: LectureRecord) -> MovieConfig:
    return MovieConfig.model_validate(lecture.config_json)


def to_task_status_response(lecture: LectureRecord) -> TaskStatusResponse:
    return TaskStatusResponse(
        id=lecture.id,
        status=lecture.status,
        progress_percentage=lecture.progress_percentage,
        current_phase=lecture.current_phase,
        error=lecture.error,
        created_at=lecture.created_at,
        updated_at=lecture.updated_at,
    )
