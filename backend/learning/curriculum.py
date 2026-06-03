from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re


@dataclass(frozen=True)
class Lesson:
    id: str
    title: str
    prompt: str
    expected_answer: str
    teaching_answer: str
    answer_type: str = "text"
    aliases: tuple[str, ...] = ()
    prerequisites: tuple[str, ...] = ()
    mastery_threshold: float = 0.8
    cognitive_layer: str = "foundation"
    domains: tuple[str, ...] = ()


@dataclass(frozen=True)
class Stage:
    id: str
    name: str
    description: str = ""
    order: int = 0


CURRICULUM_PATH = Path("data/curriculum.json")


def _load_curriculum_from_json(path: Path) -> tuple[tuple[Lesson, ...], tuple[Stage, ...]]:
    if not path.exists():
        return (), ()

    payload = json.loads(path.read_text(encoding="utf-8"))
    lessons_payload = payload.get("lessons") or []
    stages_payload = payload.get("stages") or []

    lessons: list[Lesson] = []
    for raw in lessons_payload:
        lessons.append(
            Lesson(
                id=str(raw.get("id", "")),
                title=str(raw.get("title", "")),
                prompt=str(raw.get("prompt", "")),
                expected_answer=str(raw.get("expected_answer", "")),
                teaching_answer=str(raw.get("teaching_answer", "")),
                answer_type=str(raw.get("answer_type", "text")),
                aliases=tuple(raw.get("aliases") or ()),
                prerequisites=tuple(raw.get("prerequisites") or ()),
                mastery_threshold=float(raw.get("mastery_threshold", 0.8)),
                cognitive_layer=str(raw.get("cognitive_layer", "foundation")),
                domains=tuple(raw.get("domains") or ()),
            )
        )

    stages: list[Stage] = []
    for raw in stages_payload:
        stages.append(
            Stage(
                id=str(raw.get("id", "")),
                name=str(raw.get("name", "")),
                description=str(raw.get("description", "")),
                order=int(raw.get("order", 0)),
            )
        )

    return tuple(lessons), tuple(stages)


_DEFAULT_CURRICULUM: tuple[Lesson, ...] = (
    Lesson(
        id="letters_a_to_b",
        title="Letters: A to B",
        prompt="What letter comes after A?",
        expected_answer="B",
        teaching_answer="B comes after A.",
        aliases=("alphabet", "letters", "letter", "abc"),
        cognitive_layer="symbols",
        domains=("language",),
    ),
    Lesson(
        id="numbers_after_three",
        title="Numbers: after 3",
        prompt="What number comes after 3?",
        expected_answer="4",
        teaching_answer="4 comes after 3.",
        aliases=("numbers", "count", "counting", "number"),
        prerequisites=("letters_a_to_b",),
        cognitive_layer="quantity",
        domains=("math",),
    ),
    Lesson(
        id="counting_one_to_five",
        title="Counting: 1 to 5",
        prompt="Count from 1 to 5.",
        expected_answer="1 2 3 4 5",
        teaching_answer="The counting sequence is 1, 2, 3, 4, 5.",
        answer_type="sequence",
        aliases=("counting", "sequence", "one to five"),
        prerequisites=("numbers_after_three",),
        cognitive_layer="quantity",
        domains=("math",),
    ),
    Lesson(
        id="addition_two_plus_three",
        title="Addition: 2 + 3",
        prompt="What is 2 + 3?",
        expected_answer="5",
        teaching_answer="2 + 3 = 5.",
        answer_type="number",
        aliases=("addition", "add", "plus"),
        prerequisites=("counting_one_to_five",),
        cognitive_layer="quantity",
        domains=("math",),
    ),
    Lesson(
        id="subtraction_five_minus_two",
        title="Subtraction: 5 - 2",
        prompt="What is 5 - 2?",
        expected_answer="3",
        teaching_answer="5 - 2 = 3.",
        answer_type="number",
        aliases=("subtraction", "subtract", "minus"),
        prerequisites=("addition_two_plus_three",),
        cognitive_layer="quantity",
        domains=("math",),
    ),
    Lesson(
        id="multiplication_three_times_four",
        title="Multiplication: 3 x 4",
        prompt="What is 3 x 4?",
        expected_answer="12",
        teaching_answer="3 x 4 = 12.",
        answer_type="number",
        aliases=("multiplication", "multiply", "times"),
        prerequisites=("addition_two_plus_three",),
        cognitive_layer="quantity",
        domains=("math",),
    ),
    Lesson(
        id="division_eight_divided_by_two",
        title="Division: 8 / 2",
        prompt="What is 8 / 2?",
        expected_answer="4",
        teaching_answer="8 / 2 = 4.",
        answer_type="number",
        aliases=("division", "divide", "split"),
        prerequisites=("multiplication_three_times_four",),
        cognitive_layer="quantity",
        domains=("math",),
    ),
)

_DEFAULT_STAGES: tuple[Stage, ...] = (
    Stage(id="stage_0_sensation", name="Sensation", description="Detect contrast, repetition, change, and rhythm.", order=0),
    Stage(id="stage_1_symbols", name="Symbols", description="Bind symbols to meanings (letters, digits).", order=1),
    Stage(id="stage_2_quantity", name="Quantity", description="Counting, comparison, and basic patterns.", order=2),
    Stage(id="stage_3_grammar", name="Grammar", description="Sentence structure and operations as sequences.", order=3),
    Stage(id="stage_4_logic", name="Logic", description="Deduction, induction, abduction, and reasoning.", order=4),
    Stage(id="stage_5_abstract", name="Abstract", description="Algebra, functions, and coding concepts.", order=5),
    Stage(id="stage_6_emotion", name="Emotion", description="Affective tone and empathy patterns.", order=6),
    Stage(id="stage_7_metacognition", name="Metacognition", description="Self-checking, uncertainty, and strategy selection.", order=7),
)

_JSON_CURRICULUM, _JSON_STAGES = _load_curriculum_from_json(CURRICULUM_PATH)

CURRICULUM: tuple[Lesson, ...] = _JSON_CURRICULUM or _DEFAULT_CURRICULUM
STAGES: tuple[Stage, ...] = _JSON_STAGES or _DEFAULT_STAGES

LESSONS_BY_ID = {lesson.id: lesson for lesson in CURRICULUM}


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _normalize(text: str) -> str:
    return " ".join(_tokens(text))


def _contains_alias(text: str, alias: str) -> bool:
    if len(alias) < 3:  # Skip short aliases like "on", "in", "is"
        return False
    pattern = rf"(?<![a-z0-9]){re.escape(alias.lower())}(?![a-z0-9])"
    return re.search(pattern, text) is not None


def match_lessons(text: str) -> list[Lesson]:
    lowered = text.lower()
    matched: list[Lesson] = []
    for lesson in CURRICULUM:
        # Use word boundary for lesson ID too (not raw substring)
        id_pattern = rf"(?<![a-z0-9]){re.escape(lesson.id.lower())}(?![a-z0-9])"
        if re.search(id_pattern, lowered) or any(_contains_alias(lowered, alias) for alias in lesson.aliases):
            matched.append(lesson)
    return matched


def detect_cognitive_layer(text: str) -> str:
    matched = match_lessons(text)
    if not matched:
        return "general"

    counts: dict[str, int] = {}
    for lesson in matched:
        layer = lesson.cognitive_layer or "general"
        counts[layer] = counts.get(layer, 0) + 1
    return max(counts.items(), key=lambda item: item[1])[0]


def get_lesson(lesson_id: str | None) -> Lesson | None:
    if not lesson_id:
        return None
    return LESSONS_BY_ID.get(lesson_id)


def lesson_mastery(lesson_id: str, permanence_layer) -> float:
    return float(permanence_layer.confidence(lesson_id))


def lesson_is_mastered(lesson: Lesson, permanence_layer) -> bool:
    return lesson_mastery(lesson.id, permanence_layer) >= lesson.mastery_threshold


def prerequisites_met(lesson: Lesson, permanence_layer) -> bool:
    return all(lesson_is_mastered(LESSONS_BY_ID[prereq], permanence_layer) for prereq in lesson.prerequisites)


def next_lesson(permanence_layer) -> Lesson | None:
    for lesson in CURRICULUM:
        if prerequisites_met(lesson, permanence_layer) and not lesson_is_mastered(lesson, permanence_layer):
            return lesson
    return None


def score_answer(lesson: Lesson, learner_answer: str) -> bool:
    if lesson.answer_type == "sequence":
        return _tokens(learner_answer) == _tokens(lesson.expected_answer)
    if lesson.answer_type == "number":
        try:
            return float(learner_answer.strip()) == float(lesson.expected_answer)
        except ValueError:
            return _normalize(learner_answer) == _normalize(lesson.expected_answer)
    return _normalize(learner_answer) == _normalize(lesson.expected_answer)


def resolve_foundation_seed_answer(text: str) -> dict | None:
    matched = match_lessons(text)

    if not matched:
        return None

    answer = " ".join(lesson.teaching_answer for lesson in matched)
    layers = sorted({lesson.cognitive_layer for lesson in matched if lesson.cognitive_layer})
    return {
        "answer": answer,
        "confidence": "CERTAIN",
        "citations": [],
        "gaps": [],
        "tone": "teaching",
        "seed_keys": [lesson.id for lesson in matched],
        "lessons": [asdict(lesson) for lesson in matched],
        "cognitive_layers": layers or ["general"],
    }


def resolve_chat_answer(text: str) -> dict | None:
    lowered = text.strip().lower()
    if not lowered:
        return None

    if lowered in {"hi", "hello", "hey", "hello velynx", "hi velynx"}:
        return {
            "answer": "Hello! Ask me a basics question, like a letter, number, or simple math.",
            "confidence": "CERTAIN",
            "citations": [],
            "gaps": [],
            "tone": "human",
            "seed_keys": ["greeting"],
        }

    incomplete = re.search(r"\b(?:what is|calculate|solve)?\s*(\d+)\s*([+\-*/x×])\s*$", lowered)
    if incomplete:
        return {
            "answer": "Please complete the math expression, like 2+3 or 8/2.",
            "confidence": "CERTAIN",
            "citations": [],
            "gaps": [],
            "tone": "teaching",
            "seed_keys": ["incomplete_math"],
        }

    complete = re.search(r"\b(?:what is|calculate|solve)?\s*(\d+)\s*([+\-*/x×])\s*(\d+)\b", lowered)
    if complete:
        left = int(complete.group(1))
        operator = complete.group(2)
        right = int(complete.group(3))

        if operator == "+":
            result = left + right
            symbol = "+"
        elif operator == "-":
            result = left - right
            symbol = "-"
        elif operator in {"x", "×", "*"}:
            result = left * right
            symbol = "x"
        else:
            if right == 0:
                return {
                    "answer": "Division by zero is not allowed.",
                    "confidence": "CERTAIN",
                    "citations": [],
                    "gaps": [],
                    "tone": "teaching",
                    "seed_keys": ["division_by_zero"],
                }
            result = left / right
            symbol = "/"
            if float(result).is_integer():
                result = int(result)

        return {
            "answer": f"{left} {symbol} {right} = {result}.",
            "confidence": "CERTAIN",
            "citations": [],
            "gaps": [],
            "tone": "teaching",
            "seed_keys": ["simple_math"],
        }

    return None
