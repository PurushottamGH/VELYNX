import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from cli import teach_lesson  # noqa: E402
from cli import teach_fact  # noqa: E402
from backend.app.pipeline import answer_question  # noqa: E402
from backend.learning import feedback_loop, gap_tracker, permanence, source_trust  # noqa: E402
from backend.learning.curriculum import CURRICULUM, get_lesson, next_lesson, score_answer  # noqa: E402
from backend.learning.permanence import PermanenceLayer  # noqa: E402
from backend.memory import vector_store  # noqa: E402
from backend.memory.session import SessionMemory  # noqa: E402


def _patch_learning_paths(tmp_path) -> None:
    feedback_loop._DATA_PATH = tmp_path / "feedback.jsonl"
    gap_tracker._GAPS_PATH = tmp_path / "gaps.jsonl"
    source_trust._TRUST_PATH = tmp_path / "trust.json"

    from learning import living_constitution

    living_constitution._RULES_PATH = tmp_path / "living_constitution.json"
    permanence._DEFAULT_PERMANENCE = PermanenceLayer(path=tmp_path / "permanence.json")
    vector_store._DEFAULT_VECTOR_STORE = vector_store.VectorStore(path=tmp_path / "neural_links.json")


def test_terminal_lesson_updates_memory(tmp_path) -> None:
    _patch_learning_paths(tmp_path)
    session = SessionMemory(path=tmp_path / "session.json")

    result = teach_lesson(
        answer="5",
        lesson_id="addition_two_plus_three",
        session=session,
        permanence_layer=permanence._DEFAULT_PERMANENCE,
    )

    assert result["correct"] is True
    assert result["lesson"]["id"] == "addition_two_plus_three"
    assert permanence._DEFAULT_PERMANENCE.confidence("addition_two_plus_three") > 0.5
    assert session.history()[-1]["correct"] is True
    assert (tmp_path / "feedback.jsonl").exists()

    wrong = teach_lesson(
        answer="4",
        lesson_id="addition_two_plus_three",
        session=session,
        permanence_layer=permanence._DEFAULT_PERMANENCE,
    )

    assert wrong["correct"] is False
    assert permanence._DEFAULT_PERMANENCE.confidence("addition_two_plus_three") < result["learning"]["confidence"]
    assert (tmp_path / "gaps.jsonl").exists()


def test_curriculum_progresses_by_mastery(tmp_path) -> None:
    _patch_learning_paths(tmp_path)
    layer = permanence._DEFAULT_PERMANENCE

    first = next_lesson(layer)
    assert first is not None
    assert first.id == CURRICULUM[0].id

    layer.reinforce(first.id, delta=0.4)
    next_item = next_lesson(layer)
    assert next_item is not None
    assert next_item.id != first.id
    assert next_item.id == "numbers_after_three"


def test_foundation_seed_resolution_matches_curriculum() -> None:
    lesson = get_lesson("multiplication_three_times_four")
    assert lesson is not None
    assert score_answer(lesson, "12") is True


def test_answer_question_handles_foundation_prompt() -> None:
    response = __import__("asyncio").run(answer_question("What number comes after 3?"))
    assert response.answer
    assert response.confidence in {"CERTAIN", "UNKNOWN", "PROBABLE", "DEBATED"}


def test_answer_question_handles_greeting_and_math() -> None:
    import asyncio

    greeting = asyncio.run(answer_question("hi"))
    assert "hello" in greeting.answer.lower()

    math = asyncio.run(answer_question("what is 2+3?"))
    assert "2 + 3 = 5" in math.answer


def test_answer_question_uses_internet_style_lookup(monkeypatch) -> None:
    import asyncio

    async def fake_dictionary_lookup(_word: str) -> dict:
        return {
            "answer": "Example (noun) means a representative form or pattern used to show the nature of something.",
            "confidence": "CERTAIN",
            "citations": ["https://api.dictionaryapi.dev/api/v2/entries/en/example"],
            "gaps": [],
            "tone": "human",
            "sources": [
                {
                    "url": "https://api.dictionaryapi.dev/api/v2/entries/en/example",
                    "title": "Dictionary definition of example",
                    "snippet": "a representative form or pattern",
                    "source": "dictionaryapi",
                    "score": 1.0,
                }
            ],
            "debug": {"topic": "example", "mode": "dictionary"},
        }

    from learning import knowledge_tutor

    monkeypatch.setattr(knowledge_tutor, "_fetch_dictionary_definition", fake_dictionary_lookup)

    response = asyncio.run(answer_question("what does example mean?"))
    assert "example" in response.answer.lower()
    assert response.sources


def test_conversational_sentence_does_not_become_word_lookup(monkeypatch) -> None:
    import asyncio

    from learning import knowledge_tutor

    called = {"dictionary": False}

    async def fake_dictionary_lookup(_word: str) -> dict:
        called["dictionary"] = True
        return {
            "answer": "should not be used",
            "confidence": "CERTAIN",
            "citations": [],
            "gaps": [],
            "tone": "human",
            "sources": [],
            "debug": {},
        }

    monkeypatch.setattr(knowledge_tutor, "_fetch_dictionary_definition", fake_dictionary_lookup)

    response = asyncio.run(answer_question("i think you are good in learning what you think velynx"))
    assert called["dictionary"] is False
    assert "should not be used" not in response.answer.lower()


def test_answer_question_fixes_basic_grammar() -> None:
    import asyncio

    response = asyncio.run(answer_question("how do I fix this grammar: i is happy"))
    assert "I am happy" in response.answer


def test_freeform_teach_stores_memory_and_recalls_it(tmp_path) -> None:
    _patch_learning_paths(tmp_path)
    session = SessionMemory(path=tmp_path / "session.json")

    taught = teach_fact(
        prompt="Velynx likes apples",
        answer="Velynx likes apples.",
        session=session,
    )

    assert taught["correct"] is True
    assert session.history()[-1]["lesson_id"] == "freeform"

    import asyncio

    response = asyncio.run(answer_question("what does velynx like?"))
    assert "logic path broken" in response.answer.lower()

