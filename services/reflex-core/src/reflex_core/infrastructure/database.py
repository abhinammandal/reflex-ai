"""Database configuration for Reflex's local SQLite storage."""

import os
from collections.abc import Iterator
from pathlib import Path

from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine

from reflex_core.infrastructure.tables import ActivityEventRecord


def _get_data_directory() -> Path:
    local_app_data = os.getenv("LOCALAPPDATA")

    if local_app_data:
        return Path(local_app_data) / "Reflex"

    return Path.home() / ".reflex"


DATA_DIRECTORY = _get_data_directory()
DATABASE_PATH = DATA_DIRECTORY / "reflex.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"


def create_database_engine(database_url: str = DATABASE_URL) -> Engine:
    return create_engine(
        database_url,
        connect_args={"check_same_thread": False},
    )


engine = create_database_engine()


def initialize_database() -> None:
    DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
    ActivityEventRecord.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
