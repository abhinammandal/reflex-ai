"""Database operations for activity events."""

from uuid import UUID

from sqlmodel import Session

from reflex_core.domain.events import ActivityEvent
from reflex_core.infrastructure.tables import ActivityEventRecord


class ActivityEventRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, event: ActivityEvent) -> ActivityEvent:
        existing_event = self.get(event.event_id)

        if existing_event is not None:
            return existing_event

        record = ActivityEventRecord.from_domain(event)
        self._session.add(record)
        self._session.commit()

        return event

    def get(self, event_id: UUID) -> ActivityEvent | None:
        record = self._session.get(ActivityEventRecord, str(event_id))

        if record is None:
            return None

        return record.to_domain()
