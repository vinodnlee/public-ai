"""
Tests for API routes: health check and chat init.
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from main import create_app


@pytest.fixture
def client(mock_adapter_and_redis: None) -> TestClient:
    """TestClient with mocked DB and Redis so no real services required."""
    return TestClient(create_app())


@pytest.fixture
def mock_adapter_and_redis() -> None:
    """Mock get_adapter and Redis so health and chat can run without real DB/Redis."""
    async def mock_ping() -> bool:
        return True

    async def mock_connect() -> None:
        pass

    async def mock_disconnect() -> None:
        pass

    mock_adapter = AsyncMock()
    mock_adapter.dialect = "sqlite"
    mock_adapter.ping = mock_ping
    mock_adapter.connect = mock_connect
    mock_adapter.disconnect = mock_disconnect

    mock_redis = AsyncMock()
    mock_redis.ping = AsyncMock(return_value=None)

    with patch("src.db.adapters.factory.get_adapter", return_value=mock_adapter), \
         patch("src.api.routes.health.get_redis", new_callable=AsyncMock, return_value=mock_redis):
        yield


def test_health_returns_ok_structure(client: TestClient, mock_adapter_and_redis) -> None:
    """GET /api/health returns api, database, redis keys."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["api"] == "ok"
    assert "database" in data
    assert data["database"]["type"] == "sqlite"
    assert data["database"]["status"] == "ok"
    assert data["redis"] == "ok"


def test_chat_init_returns_stream_url(client: TestClient) -> None:
    """POST /api/chat with query and session_id returns stream_url."""
    resp = client.post(
        "/api/chat",
        json={"query": "How many users?", "session_id": "test-session-123"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "session_id" in data
    assert data["session_id"] == "test-session-123"
    assert "stream_url" in data
    assert "/api/chat/stream/" in data["stream_url"]


def test_chat_init_rejects_empty_query(client: TestClient) -> None:
    """POST /api/chat with empty query returns 422."""
    resp = client.post(
        "/api/chat",
        json={"query": "", "session_id": "test-session"},
    )
    assert resp.status_code == 422


def test_chat_init_requires_session_id(client: TestClient) -> None:
    """POST /api/chat without session_id returns 422."""
    resp = client.post(
        "/api/chat",
        json={"query": "Hello"},
    )
    assert resp.status_code == 422
