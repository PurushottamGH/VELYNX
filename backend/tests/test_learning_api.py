import sys
from pathlib import Path
import importlib
import asyncio

sys.path.append(str(Path(__file__).resolve().parents[1]))

import httpx

from backend.app.main import app
from backend.learning import permanence


def test_feedback_updates_permanence(tmp_path) -> None:
    fact = "Is example.com a test site?"
    test_file = tmp_path / "permanence.json"

    # Route permanence writes to a temp file for deterministic isolation.
    permanence._DEFAULT_PERMANENCE = permanence.PermanenceLayer(path=test_file)

    # Ensure initial baseline
    layer = permanence.PermanenceLayer(path=test_file)
    assert layer.confidence(fact) == 0.5

    payload = {
        "query": fact,
        "rating": 1,
        "meta": {
            "answer": "Is example.com a test site?",
            "confidence": "PROBABLE",
            "source_count": 1,
            "gap_count": 0,
            "contradiction_count": 0,
            "source_domains": ["wikipedia"],
            "sources": ["wikipedia"],
        },
    }
    async def _post_feedback() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.post("/feedback", json=payload)

    resp = asyncio.run(_post_feedback())
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "ok"
    assert "learning" in data
    assert data["learning"]["learning_context"]["answer"] == "Is example.com a test site?"
    assert data["learning"]["learning_context"]["source_count"] == 1

    # Reload module to simulate restart and verify persistence
    importlib.reload(permanence)
    new_layer = permanence.PermanenceLayer(path=test_file)
    assert new_layer.confidence(fact) > 0.5
