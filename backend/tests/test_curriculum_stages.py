"""Tests for Stages 3–7 lesson loading, cognitive_layer, and prerequisites."""
import json
from pathlib import Path

_JSON = Path(__file__).resolve().parents[2] / "data" / "curriculum.json"
_load = lambda: json.loads(_JSON.read_text(encoding="utf-8"))
LAYERS = {3: "grammar", 4: "logic", 5: "abstract", 6: "emotion", 7: "metacognition"}


def test_stages_3_through_7_have_lessons():
    raw = _load()
    for n, layer in LAYERS.items():
        assert any(l.get("cognitive_layer") == layer for l in raw["lessons"]), \
            f"Stage {n} ({layer}) has no lessons"


def test_each_stage_3_to_5_has_minimum_10_lessons():
    raw = _load()
    for n, layer in LAYERS.items():
        if n > 5:
            continue
        count = sum(1 for l in raw["lessons"] if l.get("cognitive_layer") == layer)
        assert count >= 10, f"Stage {n} ({layer}) has {count} lessons, need >= 10"


def test_all_lessons_have_cognitive_layer():
    raw = _load()
    for l in raw["lessons"]:
        assert l.get("cognitive_layer") and isinstance(l["cognitive_layer"], str), \
            f"Lesson '{l.get('id')}' missing cognitive_layer"


def test_cognitive_layers_cover_stages_3_to_7():
    raw = _load()
    found = {l.get("cognitive_layer") for l in raw["lessons"]}
    for expected in LAYERS.values():
        assert expected in found, f"cognitive_layer '{expected}' not found"


def test_prerequisites_reference_existing_lessons():
    raw = _load()
    all_ids = {l["id"] for l in raw["lessons"]}
    for l in raw["lessons"]:
        for p in l.get("prerequisites", []):
            assert p in all_ids, f"'{l['id']}' references unknown prereq '{p}'"


def test_no_self_prerequisites():
    raw = _load()
    for l in raw["lessons"]:
        assert l["id"] not in l.get("prerequisites", []), \
            f"'{l['id']}' lists itself as prerequisite"
