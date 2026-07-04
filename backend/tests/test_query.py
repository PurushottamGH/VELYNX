import sys
from pathlib import Path
import asyncio

import httpx

sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.app.main import app  # noqa: E402
from backend.pipeline import retrieval_mesh  # noqa: E402


def test_query_endpoint(monkeypatch) -> None:
    async def fake_retrieve_all(_query: str) -> list[dict]:
        return [
            {
                "source": "wikipedia",
                "title": "Widget Manufacturing",
                "snippet": "A widget is manufactured using zinc alloy and precision tooling.",
                "url": "https://example.com/widget",
            }
        ]

    monkeypatch.setattr(retrieval_mesh, "retrieve_all", fake_retrieve_all)
    from memory.memory_manager import memory_manager as mm_instance
    async def _no_recall(*a, **kw):
        return []
    monkeypatch.setattr(mm_instance, "recall", _no_recall)

    async def _post_query() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.post("/query", json={"text": "How are widgets manufactured?"})

    response = asyncio.run(_post_query())

    assert response.status_code == 200
    data = response.json()
    assert data["answer"]
    assert data["confidence"]
    assert data["sources"]


def test_query_seeded_knowledge_shortcuts_retrieval(monkeypatch) -> None:
    def fail_retrieve_all(_query: str) -> list[dict]:
        raise AssertionError("retrieval should not run for seeded knowledge")

    monkeypatch.setattr(retrieval_mesh, "retrieve_all", fail_retrieve_all)

    async def _post_seeded() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.post("/query", json={"text": "Teach me abcb and 123"})

    response = asyncio.run(_post_seeded())

    assert response.status_code == 200
    data = response.json()
    assert "ABCB is VELYNX's bootstrap loop" in data["answer"]
    assert "123 is VELYNX's starter sequence" in data["answer"]
    assert data["confidence"] == "CERTAIN"
    assert data["sources"] == []
    assert data["debug"]["seeded"] is True
