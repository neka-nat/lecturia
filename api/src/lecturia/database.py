import os
import time
from collections.abc import Iterator
from contextlib import contextmanager

from loguru import logger
from sqlalchemy.engine import URL, Engine
from sqlalchemy.exc import OperationalError
from sqlmodel import Session, SQLModel, create_engine


_ENGINE: Engine | None = None


def _build_database_url_from_parts() -> URL:
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASS") or os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")
    unix_socket = os.getenv("INSTANCE_UNIX_SOCKET")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")

    if not db_user or not db_password or not db_name:
        raise RuntimeError(
            "DATABASE_URL is not set and DB_USER/DB_PASS/DB_NAME are incomplete"
        )

    if unix_socket:
        return URL.create(
            "postgresql+psycopg",
            username=db_user,
            password=db_password,
            database=db_name,
            query={"host": unix_socket},
        )

    if db_host:
        return URL.create(
            "postgresql+psycopg",
            username=db_user,
            password=db_password,
            host=db_host,
            port=int(db_port) if db_port else None,
            database=db_name,
        )

    raise RuntimeError(
        "DATABASE_URL is not set and neither INSTANCE_UNIX_SOCKET nor DB_HOST is configured"
    )


def _get_database_url() -> str | URL:
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url
    return _build_database_url_from_parts()


def get_engine() -> Engine:
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = create_engine(_get_database_url(), pool_pre_ping=True)
    return _ENGINE


def init_db(max_wait_seconds: int = 30) -> None:
    deadline = time.monotonic() + max_wait_seconds
    while True:
        try:
            SQLModel.metadata.create_all(get_engine())
            return
        except OperationalError as exc:
            if time.monotonic() >= deadline:
                raise
            logger.warning("Database is not ready yet: {}", exc)
            time.sleep(1)


@contextmanager
def session_scope() -> Iterator[Session]:
    with Session(get_engine()) as session:
        yield session
