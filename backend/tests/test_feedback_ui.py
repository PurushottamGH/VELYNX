"""Tests for /feedback endpoint: correct/wrong/incomplete, correction storage, source trust, permanence weakening."""
import asyncio
import sys
from pathlib import Path

import httpx

sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.app.main import app  # noqa: E402
from backend.learning import feedback_loop, gap_tracker, permanence, source_trust  # noqa: E402
from backend.learning import living_constitution  # noqa: E402
from backend.learning.permanence import PermanenceLayer  # noqa: E402


def _patch_paths(tmp_path) -> None:
    feedback_loop._DATA_PATH = tmp_path / "feedback.jsonl"
    gap_tracker._GAPS_PATH = tmp_path / "gaps.jsonl"
    source_trust._TRUST_PATH = tmp_path / "trust.json"
    living_constitution._RULES_PATH = tmp_path / "living_constitution.json"
    permanence._DEFAULT_PERMANENCE = PermanenceLayer(path=tmp_path / "permanence.json")


def test_feedback_accepts_correct_answer(tmp_path) -> None:
    _patch_paths(tmp_path)

    payload = {
        "query": "What is 2 + 3?",
        "rating": 1,
        "meta": {
            "answer": "2 + 3 = 5.",
            "confidence": "CERTAIN",
            "source_count": 1,
            "gap_count": 0,
            "contradiction_count": 0,
            "source_domains": ["wikipedia"],
            "sources": ["wikipedia"],
        },
    }

    async def _post() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.post("/feedback", json=payload)

    resp = asyncio.run(_post())
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


def test_feedback_accepts_wrong_answer(tmp_path) -> None:
    _patch_paths(tmp_path)

    payload = {
        "query": "What is 2 + 3?",
        "rating": -1,
        "meta": {
            "answer": "2 + 3 = 6.",
            "confidence": "PROBABLE",
            "source_count": 1,
            "gap_count": 1,
            "contradiction_count": 0,
            "source_domains": ["wikipedia"],
            "sources": ["wikipedia"],
        },
    }

    async def _post() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.post("/feedback", json=payload)

    resp = asyncio.run(_post())
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "learning" in data


def test_wrong_feedback_with_correction_stores_permanently(tmp_path) -> None:
    _patch_paths(tmp_path)
    query = "What color is the sky?"

    payload = {
        "query": query,
        "rating": -1,
        "meta": {
            "answer": "The sky is green.",
            "confidence": "PROBABLE",
            "source_count": 1,
            "gap_count": 1,
            "contradiction_count": 1,
            "source_domains": ["wikipedia"],
            "sources": ["wikipedia"],
        },
    }

    async def _post() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.post("/feedback", json=payload)

    resp = asyncio.run(_post())
    assert resp.status_code == 200

    # Verify permanence was weakened (confidence < 0.5)
    conf = permanence._DEFAULT_PERMANENCE.confidence(query)
    assert conf < 0.5, f"Expected confidence < 0.5 after wrong feedback, got {conf}"

    # Verify living constitution rule was recorded
    assert (tmp_path / "living_constitution.json").exists()


def test_source_trust_updates_after_wrong_feedback(tmp_path) -> None:
    _patch_paths(tmp_path)

    payload = {
        "query": "Is the earth flat?",
        "rating": -1,
        "meta": {
            "answer": "Yes, the earth is flat.",
            "confidence": "PROBABLE",
            "source_count": 1,
            "gap_count": 0,
            "contradiction_count": 1,
            "source_domains": ["badsource.com"],
            "sources": ["badsource.com"],
        },
    }

    async def _post() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.post("/feedback", json=payload)

    resp = asyncio.run(_post())
    assert resp.status_code == 200

    # Source trust should be negative after wrong feedback
    scores = source_trust.load_trust_scores()
    assert scores.get("badsource.com", 0) < 0, (
        f"Expected negative trust for badsource.com, got {scores.get('badsource.com')}"
    )


def test_permanence_weakens_on_wrong_answer(tmp_path) -> None:
    _patch_paths(tmp_path)
    fact = "What is the capital of France?"

    # First reinforce it
    permanence._DEFAULT_PERMANENCE.reinforce(fact, delta=0.3)
    before = permanence._DEFAULT_PERMANENCE.confidence(fact)
    assert before > 0.5

    # Now give wrong feedback
    payload = {
        "query": fact,
        "rating": -1,
        "meta": {
            "answer": "The capital is Berlin.",
            "confidence": "PROBABLE",
            "source_count": 1,
            "gap_count": 1,
            "contradiction_count": 0,
            "source_domains": ["wikipedia"],
            "sources": ["wikipedia"],
        },
    }

    async def _post() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.post("/feedback", json=payload)

    resp = asyncio.run(_post())
    assert resp.status_code == 200

    after = permanence._DEFAULT_PERMANENCE.confidence(fact)
    assert after < before, f"Expected confidence to decrease: {before} -> {after}"
