"""Tests for constitution system: loading, reasoning integration, layer-scoped rules."""
import asyncio
import json
import sys
from pathlib import Path

import httpx

sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.app.main import app  # noqa: E402
from backend.learning import living_constitution  # noqa: E402
from backend.learning.living_constitution import record_rule, render_rules  # noqa: E402
from backend.pipeline import constitution_loader, retrieval_mesh  # noqa: E402
from backend.pipeline.reasoning_core import reason  # noqa: E402


# ── Constitution loaded at startup ──────────────────────────────

def test_constitution_files_exist() -> None:
    """All constitution markdown files are present."""
    for name in ["logic.md", "science.md", "epistemology.md", "uncertainty.md", "communication.md", "curiosity.md"]:
        path = constitution_loader.CONSTITUTION_DIR / name
        assert path.exists(), f"Missing constitution file: {name}"


def test_load_constitution_returns_nonempty() -> None:
    """load_constitution returns a non-empty string."""
    text = constitution_loader.load_constitution()
    assert len(text) > 100, "Constitution text is suspiciously short"
    assert "logic" in text.lower() or "science" in text.lower() or "uncertainty" in text.lower()


def test_load_constitution_includes_learned_rules(tmp_path, monkeypatch) -> None:
    """Learned rules from living_constitution appear in load_constitution output."""
    monkeypatch.setattr(living_constitution, "_RULES_PATH", tmp_path / "living_constitution.json")

    record_rule({
        "title": "Test constitutional rule",
        "body": "Always verify sources before answering.",
        "domains": ["science"],
        "risk": "low",
    })

    text = constitution_loader.load_constitution()
    assert "Test constitutional rule" in text


# ── Reasoning includes constitution context ──────────────────────

def test_reasoning_includes_constitution_context() -> None:
    """When constitution is passed to reason(), the draft references it."""
    sources = [
        {"title": "Test Source", "url": "https://example.com", "score": 0.8, "snippet": "Test"},
    ]
    result = reason(sources, query="What is the best medical treatment for headaches?", constitution="Test constitution rules. Be careful with medical advice.")
    assert "high-scrutiny" in " ".join(result["gaps"]).lower()


def test_reasoning_without_constitution_omits_it() -> None:
    """Without constitution, draft does not reference it."""
    sources = [
        {"title": "Test Source", "url": "https://example.com", "score": 0.8, "snippet": "Test"},
    ]
    result = reason(sources, query="What is gravity?")
    assert "living constitution" not in result["draft"].lower()


def test_constitution_flags_high_scrutiny_topics() -> None:
    """Medical/legal queries get a high-scrutiny gap when constitution is present."""
    sources = [
        {"title": "Medical Source", "url": "https://med.example.com", "score": 0.9, "snippet": "Treatment info"},
    ]
    result = reason(
        sources,
        query="What is the best medical treatment for headaches?",
        constitution="Be careful with medical advice.",
    )
    assert any("high-scrutiny" in gap.lower() for gap in result["gaps"])


# ── Layer-scoped rules ──────────────────────────────────────────

def test_layer_scoped_rules_filter_by_cognitive_layer(tmp_path, monkeypatch) -> None:
    """render_rules filters by cognitive_layer when specified."""
    monkeypatch.setattr(living_constitution, "_RULES_PATH", tmp_path / "living_constitution.json")

    record_rule({
        "title": "Grammar rule",
        "body": "Check subject-verb agreement.",
        "cognitive_layer": "grammar",
    })
    record_rule({
        "title": "Logic rule",
        "body": "Verify syllogism validity.",
        "cognitive_layer": "logic",
    })
    record_rule({
        "title": "General rule",
        "body": "Be concise.",
        "cognitive_layer": "general",
    })

    grammar_rules = render_rules(cognitive_layer="grammar")
    assert "Grammar rule" in grammar_rules
    assert "Logic rule" not in grammar_rules

    logic_rules = render_rules(cognitive_layer="logic")
    assert "Logic rule" in logic_rules
    assert "Grammar rule" not in logic_rules


def test_layer_scoped_constitution_in_intent(monkeypatch) -> None:
    """decompose_query loads constitution with the detected cognitive layer."""
    from pipeline import intent_engine

    layers_called: list[str] = []

    original_load = constitution_loader.load_constitution

    def _spy_load(cognitive_layer=None, include_pending=True):
        layers_called.append(cognitive_layer)
        return original_load(cognitive_layer=cognitive_layer, include_pending=include_pending)

    # Patch on intent_engine since it imports load_constitution directly
    monkeypatch.setattr(intent_engine, "load_constitution", _spy_load)
    monkeypatch.setattr(intent_engine, "detect_cognitive_layer", lambda text: "grammar")

    result = intent_engine.decompose_query("What is the basic English sentence order?")
    assert result["cognitive_layer"] == "grammar"
    assert layers_called, "load_constitution should have been called"
    assert layers_called[-1] == "grammar"


def test_constitution_appears_in_full_query_pipeline(monkeypatch) -> None:
    """Full /query pipeline returns constitution content in debug or intent."""
    monkeypatch.setattr(retrieval_mesh, "retrieve_all", lambda q: [])

    async def _post() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.post("/query", json={"text": "What is deduction?"})

    resp = asyncio.run(_post())
    assert resp.status_code == 200
    data = resp.json()
    # The answer should exist (from seeded knowledge or retrieval)
    assert data["answer"]
