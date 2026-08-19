from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EventSource(StrEnum):
    BROWSER = "browser"
    DESKTOP = "desktop"
    SYSTEM = "system"


class ActionType(StrEnum):
    APPLICATION_OPENED = "application_opened"
    APPLICATION_CLOSED = "application_closed"
    PAGE_VISITED = "page_visited"
    ELEMENT_CLICKED = "element_clicked"
    TEXT_SUBMITTED = "text_submitted"
    MEDIA_PLAYED = "media_played"
    MEDIA_PAUSED = "media_paused"
    FILE_OPENED = "file_opened"
    FILE_SAVED = "file_saved"


class ActivityEvent(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    event_id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    occurred_at: datetime
    source: EventSource
    action: ActionType
    application: str = Field(min_length=1, max_length=100)
    resource: str | None = Field(default=None, max_length=500)
    target: str | None = Field(default=None, max_length=200)
    value_present: bool = False
    sensitive: bool = False
    schema_version: int = Field(default=1, ge=1)

    @field_validator("occurred_at")
    @classmethod
    def normalize_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("occurred_at must include timezone information")

        return value.astimezone(UTC)
