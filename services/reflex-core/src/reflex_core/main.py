"""Reflex Core API."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from reflex_core.api.events import router as events_router
from reflex_core.infrastructure.database import initialize_database


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    initialize_database()
    yield


app = FastAPI(
    title="Reflex Core",
    description="Local intelligence and automation engine",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(events_router)


@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="reflex-core",
        version="0.1.0",
    )
