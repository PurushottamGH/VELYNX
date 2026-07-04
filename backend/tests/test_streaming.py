"""Tests for Phase 11F — Streaming endpoint."""
from __future__ import annotations

import json

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from backend.app.main import app


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


class TestStreamingEndpoint:
    @pytest.mark.asyncio
    async def test_stream_endpoint_exists(self, client: AsyncClient):
        resp = await client.get("/stream/query", params={"text": "hello"}, timeout=10.0)
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_stream_returns_events(self, client: AsyncClient):
        resp = await client.get("/stream/query", params={"text": "what is ai?"}, timeout=30.0)
        assert resp.status_code == 200
        body = resp.text
        assert "event: pipeline_stage" in body
        assert "event: answer" in body

    @pytest.mark.asyncio
    async def test_stream_with_session_id(self, client: AsyncClient):
        resp = await client.get(
            "/stream/query",
            params={"text": "test query", "session_id": "test-session"},
            timeout=30.0,
        )
        assert resp.status_code == 200
        body = resp.text
        assert "event: answer" in body

    @pytest.mark.asyncio
    async def test_stream_monologue_steps(self, client: AsyncClient):
        resp = await client.get(
            "/stream/query",
            params={"text": "how does quantum computing work in practice?", "session_id": "mono-test"},
            timeout=30.0,
        )
        body = resp.text
        assert "event: monologue_step" in body


class TestStreamEventFormat:
    def test_sse_format(self):
        from app.streaming import _sse
        result = _sse("test_event", {"key": "value"})
        assert result.startswith("event: test_event\ndata: ")
        assert result.endswith("\n\n")
        parsed = json.loads(result.split("data: ", 1)[1].strip())
        assert parsed == {"key": "value"}
