"""SQLite table definitions for Reflex."""

from typing import ClassVar, Self

from sqlmodel import Field, SQLModel

from reflex_core.domain.events import ActivityEvent


class ActivityEventRecord(SQLModel, table=True):
    __tablename__: ClassVar[str] = "activity_events"

    event_id: str = Field(primary_key=True)
    session_id: str = Field(index=True)
    occurred_at: str = Field(index=True)
    source: str = Field(index=True)
    action: str = Field(index=True)
    application: str = Field(index=True)
    sensitive: bool = Field(index=True)
    payload_json: str

    @classmethod
    def from_domain(cls, event: ActivityEvent) -> Self:
        return cls(
            event_id=str(event.event_id),
            session_id=str(event.session_id),
            occurred_at=event.occurred_at.isoformat(),
            source=event.source.value,
            action=event.action.value,
            application=event.application,
            sensitive=event.sensitive,
            payload_json=event.model_dump_json(),
        )

    def to_domain(self) -> ActivityEvent:
        return ActivityEvent.model_validate_json(self.payload_json)
