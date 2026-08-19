"""Application logic for ingesting activity events."""

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel

from reflex_core.domain.events import ActivityEvent
from reflex_core.infrastructure.event_repository import ActivityEventRepository


class IngestionStatus(StrEnum):
    STORED = "stored"
    ALREADY_STORED = "already_stored"
    DISCARDED_SENSITIVE = "discarded_sensitive"


class IngestionResult(BaseModel):
    event_id: UUID
    status: IngestionStatus


class ActivityEventIngestionService:
    def __init__(self, repository: ActivityEventRepository) -> None:
        self._repository = repository

    def ingest(self, event: ActivityEvent) -> IngestionResult:
        if event.sensitive:
            return IngestionResult(
                event_id=event.event_id,
                status=IngestionStatus.DISCARDED_SENSITIVE,
            )

        was_stored = self._repository.save(event)

        status = IngestionStatus.STORED if was_stored else IngestionStatus.ALREADY_STORED

        return IngestionResult(
            event_id=event.event_id,
            status=status,
        )
