"""Tests for expanded curriculum Stages 3–7."""
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

# Resolve the real curriculum JSON (project root / data / curriculum.json)
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_CURRICULUM_JSON = _PROJECT_ROOT / "data" / "curriculum.json"


def _load_raw_curriculum() -> dict:
    return json.loads(_CURRICULUM_JSON.read_text(encoding="utf-8"))


# Patch the curriculum module to use the real JSON file before importing
import backend.learning.curriculum as _cur_mod
_cur_mod.CURRICULUM_PATH = _CURRICULUM_JSON
_JSON_CURRICULUM, _JSON_STAGES = _cur_mod._load_curriculum_from_json(_CURRICULUM_JSON)
if _JSON_CURRICULUM:
    _cur_mod.CURRICULUM = _JSON_CURRICULUM
    _cur_mod.STAGES = _JSON_STAGES
    _cur_mod.LESSONS_BY_ID = {lesson.id: lesson for lesson in _JSON_CURRICULUM}

from backend.learning.curriculum import (  # noqa: E402
    CURRICULUM,
    LESSONS_BY_ID,
    STAGES,
    get_lesson,
    lesson_is_mastered,
    next_lesson,
    prerequisites_met,
    score_answer,
)
from backend.learning.permanence import PermanenceLayer  # noqa: E402


# ── Stage coverage ──────────────────────────────────────────────

def test_stages_3_through_7_exist() -> None:
    raw = _load_raw_curriculum()
    stage_ids = {s["id"] for s in raw["stages"]}
    for i in range(3, 8):
        assert f"stage_{i}_" in " ".join(sid for sid in stage_ids if sid.startswith(f"stage_{i}_")), (
            f"Stage {i} missing from curriculum.json"
        )


def test_each_expanded_stage_has_minimum_10_lessons() -> None:
    """Stages 3-5 (grammar, logic, abstract) each have >= 10 lessons."""
    raw = _load_raw_curriculum()
    stage_layer_map = {
        3: "grammar",
        4: "logic",
        5: "abstract",
    }
    for stage_num, layer in stage_layer_map.items():
        lessons = [l for l in raw["lessons"] if l.get("cognitive_layer") == layer]
        assert len(lessons) >= 10, (
            f"Stage {stage_num} ({layer}) has {len(lessons)} lessons, expected >= 10"
        )


# ── Prerequisite gating ─────────────────────────────────────────

def test_prerequisites_reference_existing_lessons() -> None:
    raw = _load_raw_curriculum()
    all_ids = {l["id"] for l in raw["lessons"]}
    for lesson in raw["lessons"]:
        for prereq in lesson.get("prerequisites", []):
            assert prereq in all_ids, (
                f"Lesson '{lesson['id']}' has unknown prerequisite '{prereq}'"
            )


def test_prerequisites_gating_blocks_unmet_lessons(tmp_path) -> None:
    layer = PermanenceLayer(path=tmp_path / "permanence.json")
    # Find a lesson with prerequisites in the loaded curriculum
    gated = [l for l in CURRICULUM if l.prerequisites]
    assert gated, "No lessons with prerequisites found"
    target = gated[0]
    # With default confidence (0.5) and threshold 0.8, prereqs should not be met
    assert prerequisites_met(target, layer) is False


def test_prerequisites_gating_allows_met_lessons(tmp_path) -> None:
    layer = PermanenceLayer(path=tmp_path / "permanence.json")
    gated = [l for l in CURRICULUM if l.prerequisites]
    assert gated, "No lessons with prerequisites found"
    target = gated[0]
    # Reinforce all prerequisites above their thresholds
    for prereq_id in target.prerequisites:
        prereq = LESSONS_BY_ID[prereq_id]
        layer.reinforce(prereq_id, delta=prereq.mastery_threshold)
    assert prerequisites_met(target, layer) is True


def test_parallel_prerequisites_both_required(tmp_path) -> None:
    """Lessons with 2+ prerequisites require ALL of them mastered."""
    raw = _load_raw_curriculum()
    dual = [l for l in raw["lessons"] if len(l.get("prerequisites", [])) >= 2]
    assert len(dual) >= 5, "Expected at least 5 lessons with parallel prerequisites"
    # Verify each dual-prereq lesson requires both — fresh layer per lesson
    for lesson_data in dual[:3]:
        layer = PermanenceLayer(path=tmp_path / f"perm_{lesson_data['id']}.json")
        lesson = get_lesson(lesson_data["id"])
        assert lesson is not None
        # Master only the first prerequisite
        first_prereq = lesson.prerequisites[0]
        layer.reinforce(first_prereq, delta=1.0)
        assert prerequisites_met(lesson, layer) is False, (
            f"Lesson '{lesson.id}' should require all prereqs, not just first"
        )


# ── Mastery threshold ───────────────────────────────────────────

def test_mastery_threshold_applied_correctly(tmp_path) -> None:
    layer = PermanenceLayer(path=tmp_path / "permanence.json")
    lesson = CURRICULUM[0]  # letters_a_to_b, threshold 0.8
    assert lesson_is_mastered(lesson, layer) is False
    layer.reinforce(lesson.id, delta=lesson.mastery_threshold)
    assert lesson_is_mastered(lesson, layer) is True


def test_mastery_threshold_in_valid_range() -> None:
    raw = _load_raw_curriculum()
    for lesson in raw["lessons"]:
        thr = lesson.get("mastery_threshold", 0.8)
        assert 0.0 <= thr <= 1.0, (
            f"Lesson '{lesson['id']}' has out-of-range mastery_threshold: {thr}"
        )


# ── Cognitive layer field ───────────────────────────────────────

def test_all_lessons_have_cognitive_layer() -> None:
    raw = _load_raw_curriculum()
    for lesson in raw["lessons"]:
        layer = lesson.get("cognitive_layer")
        assert layer and isinstance(layer, str), (
            f"Lesson '{lesson.get('id')}' missing cognitive_layer"
        )


def test_cognitive_layers_cover_stages_3_to_7() -> None:
    raw = _load_raw_curriculum()
    layers = {l.get("cognitive_layer") for l in raw["lessons"]}
    for expected in ("grammar", "logic", "abstract", "emotion", "metacognition"):
        assert expected in layers, f"cognitive_layer '{expected}' not found in curriculum"


# ── Scoring ─────────────────────────────────────────────────────

def test_score_answer_text_lesson() -> None:
    lesson = get_lesson("letters_a_to_b")
    assert lesson is not None
    assert score_answer(lesson, "B") is True
    assert score_answer(lesson, "C") is False


def test_score_answer_number_lesson() -> None:
    lesson = get_lesson("addition_two_plus_three")
    assert lesson is not None
    assert score_answer(lesson, "5") is True
    assert score_answer(lesson, "6") is False


def test_lesson_ids_unique() -> None:
    raw = _load_raw_curriculum()
    ids = [l["id"] for l in raw["lessons"]]
    assert len(ids) == len(set(ids)), "Duplicate lesson IDs found"
