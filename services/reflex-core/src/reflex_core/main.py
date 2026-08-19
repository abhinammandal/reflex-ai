from fastapi import FastAPI
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


app = FastAPI(
    title="Reflex Core",
    description="Local intelligence and automation engine for Reflex.",
    version="0.1.0",
)


@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="reflex-core",
        version="0.1.0",
    )
