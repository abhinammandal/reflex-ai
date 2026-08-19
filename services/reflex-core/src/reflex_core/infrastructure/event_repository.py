"""Database operations for activity events."""

from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from reflex_core.domain.events import ActivityEvent
from reflex_core.infrastructure.tables import ActivityEventRecord


class ActivityEventRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, event: ActivityEvent) -> bool:
        if self.get(event.event_id) is not None:
            return False

        record = ActivityEventRecord.from_domain(event)

        try:
            self._session.add(record)
            self._session.commit()
        except IntegrityError:
            self._session.rollback()

            if self.get(event.event_id) is not None:
                return False

            raise

        return True

    def get(self, event_id: UUID) -> ActivityEvent | None:
        record = self._session.get(ActivityEventRecord, str(event_id))

        if record is None:
            return None

        return record.to_domain()
