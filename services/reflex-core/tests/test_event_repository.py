"""Tests for local activity-event storage."""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, create_engine, select

from reflex_core.domain.events import ActionType, ActivityEvent, EventSource
from reflex_core.infrastructure.event_repository import ActivityEventRepository
from reflex_core.infrastructure.tables import ActivityEventRecord


def create_test_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def create_event() -> ActivityEvent:
    return ActivityEvent(
        session_id=uuid4(),
        occurred_at=datetime(2026, 8, 19, 9, 0, tzinfo=UTC),
        source=EventSource.BROWSER,
        action=ActionType.PAGE_VISITED,
        application="Chrome",
        resource="https://youtube.com/",
        target="video-player",
        value_present=False,
        sensitive=False,
    )


def test_saves_and_loads_activity_event() -> None:
    test_engine = create_test_engine()
    ActivityEventRecord.metadata.create_all(test_engine)
    event = create_event()

    with Session(test_engine) as session:
        repository = ActivityEventRepository(session)

        was_stored = repository.save(event)
        loaded_event = repository.get(event.event_id)

    assert was_stored is True
    assert loaded_event == event


def test_does_not_store_duplicate_event() -> None:
    test_engine = create_test_engine()
    ActivityEventRecord.metadata.create_all(test_engine)
    event = create_event()

    with Session(test_engine) as session:
        repository = ActivityEventRepository(session)

        first_save = repository.save(event)
        second_save = repository.save(event)

        records = session.exec(select(ActivityEventRecord)).all()

    assert first_save is True
    assert second_save is False
    assert len(records) == 1
