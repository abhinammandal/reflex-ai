from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from reflex_core.domain.events import ActionType, ActivityEvent, EventSource


def test_accepts_valid_activity_event() -> None:
    session_id = uuid4()

    event = ActivityEvent(
        session_id=session_id,
        occurred_at=datetime(2026, 8, 19, 9, 0, tzinfo=UTC),
        source=EventSource.BROWSER,
        action=ActionType.MEDIA_PLAYED,
        application=" Chrome ",
        resource="youtube.com/watch",
        target="Play button",
    )

    assert event.session_id == session_id
    assert event.application == "Chrome"
    assert event.source is EventSource.BROWSER
    assert event.action is ActionType.MEDIA_PLAYED
    assert event.occurred_at.tzinfo is UTC


def test_rejects_event_without_timezone() -> None:
    with pytest.raises(ValidationError, match="timezone information"):
        ActivityEvent(
            session_id=uuid4(),
            # Intentionally omits tzinfo to test rejection.
            occurred_at=datetime(2026, 8, 19, 9, 0),  # noqa: DTZ001
            source=EventSource.BROWSER,
            action=ActionType.PAGE_VISITED,
            application="Chrome",
        )


def test_rejects_unknown_or_raw_fields() -> None:
    with pytest.raises(ValidationError):
        ActivityEvent.model_validate(
            {
                "session_id": uuid4(),
                "occurred_at": datetime(2026, 8, 19, 9, 0, tzinfo=UTC),
                "source": EventSource.BROWSER,
                "action": ActionType.TEXT_SUBMITTED,
                "application": "Chrome",
                "raw_text": "private search content",
            }
        )
