"""Tests for the activity-event HTTP endpoint."""

from collections.abc import Iterator
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, create_engine

from reflex_core.api.events import router as events_router
from reflex_core.infrastructure.database import get_session
from reflex_core.infrastructure.tables import ActivityEventRecord

TEST_API_TOKEN = "reflex-test-token"
AUTH_HEADERS = {"X-Reflex-Token": TEST_API_TOKEN}


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setattr(
        "reflex_core.api.security.load_or_create_api_token",
        lambda: TEST_API_TOKEN,
    )

    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    ActivityEventRecord.metadata.create_all(test_engine)

    def override_get_session() -> Iterator[Session]:
        with Session(test_engine) as session:
            yield session

    test_app = FastAPI()
    test_app.include_router(events_router)
    test_app.dependency_overrides[get_session] = override_get_session

    with TestClient(test_app) as test_client:
        yield test_client


def create_payload(*, sensitive: bool = False) -> dict[str, object]:
    return {
        "event_id": str(uuid4()),
        "session_id": str(uuid4()),
        "occurred_at": "2026-08-19T10:00:00Z",
        "source": "browser",
        "action": "page_visited",
        "application": "Chrome",
        "resource": "https://example.com/",
        "target": "page",
        "value_present": False,
        "sensitive": sensitive,
        "schema_version": "1.0",
    }


def test_stores_event_received_through_api(client: TestClient) -> None:
    payload = create_payload()

    response = client.post(
        "/api/v1/events",
        json=payload,
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == {
        "event_id": payload["event_id"],
        "status": "stored",
    }


def test_reports_duplicate_event_through_api(client: TestClient) -> None:
    payload = create_payload()

    client.post(
        "/api/v1/events",
        json=payload,
        headers=AUTH_HEADERS,
    )
    response = client.post(
        "/api/v1/events",
        json=payload,
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "already_stored"


def test_discards_sensitive_event_through_api(client: TestClient) -> None:
    payload = create_payload(sensitive=True)

    response = client.post(
        "/api/v1/events",
        json=payload,
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "discarded_sensitive"


def test_rejects_unknown_raw_data(client: TestClient) -> None:
    payload = create_payload()
    payload["raw_text"] = "private information"

    response = client.post(
        "/api/v1/events",
        json=payload,
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 422


def test_rejects_missing_api_token(client: TestClient) -> None:
    payload = create_payload()

    response = client.post("/api/v1/events", json=payload)

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing Reflex API token."}


def test_rejects_invalid_api_token(client: TestClient) -> None:
    payload = create_payload()

    response = client.post(
        "/api/v1/events",
        json=payload,
        headers={"X-Reflex-Token": "wrong-test-token"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing Reflex API token."}
