"""Tests for the activity-event ingestion decisions."""

from collections.abc import Iterator
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, create_engine

from reflex_core.application.event_ingestion import (
    ActivityEventIngestionService,
    IngestionStatus,
)
from reflex_core.domain.events import ActionType, ActivityEvent, EventSource
from reflex_core.infrastructure.event_repository import ActivityEventRepository
from reflex_core.infrastructure.tables import ActivityEventRecord


@pytest.fixture
def session() -> Iterator[Session]:
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    ActivityEventRecord.metadata.create_all(test_engine)

    with Session(test_engine) as database_session:
        yield database_session


def create_event(*, sensitive: bool = False) -> ActivityEvent:
    return ActivityEvent(
        session_id=uuid4(),
        occurred_at=datetime(2026, 8, 19, 10, 0, tzinfo=UTC),
        source=EventSource.BROWSER,
        action=ActionType.PAGE_VISITED,
        application="Chrome",
        resource="https://example.com/",
        target="page",
        value_present=False,
        sensitive=sensitive,
    )


def test_stores_normal_event(session: Session) -> None:
    repository = ActivityEventRepository(session)
    service = ActivityEventIngestionService(repository)
    event = create_event()

    result = service.ingest(event)

    assert result.status is IngestionStatus.STORED
    assert repository.get(event.event_id) == event


def test_reports_duplicate_event(session: Session) -> None:
    repository = ActivityEventRepository(session)
    service = ActivityEventIngestionService(repository)
    event = create_event()

    service.ingest(event)
    result = service.ingest(event)

    assert result.status is IngestionStatus.ALREADY_STORED


def test_discards_sensitive_event(session: Session) -> None:
    repository = ActivityEventRepository(session)
    service = ActivityEventIngestionService(repository)
    event = create_event(sensitive=True)

    result = service.ingest(event)

    assert result.status is IngestionStatus.DISCARDED_SENSITIVE
    assert repository.get(event.event_id) is None
