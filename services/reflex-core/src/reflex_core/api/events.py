"""HTTP endpoint for receiving activity events."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session

from reflex_core.application.event_ingestion import (
    ActivityEventIngestionService,
    IngestionResult,
)
from reflex_core.domain.events import ActivityEvent
from reflex_core.infrastructure.database import get_session
from reflex_core.infrastructure.event_repository import ActivityEventRepository

router = APIRouter(prefix="/api/v1", tags=["events"])

DatabaseSession = Annotated[Session, Depends(get_session)]


@router.post("/events", response_model=IngestionResult)
def ingest_activity_event(
    event: ActivityEvent,
    session: DatabaseSession,
) -> IngestionResult:
    repository = ActivityEventRepository(session)
    service = ActivityEventIngestionService(repository)

    return service.ingest(event)
