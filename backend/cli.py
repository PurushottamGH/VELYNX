from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parent))

from app.pipeline import answer_question  # noqa: E402
from learning.curriculum import get_lesson, next_lesson, resolve_foundation_seed_answer, score_answer  # noqa: E402
from learning.online_learner import learn_from_feedback  # noqa: E402
from learning.permanence import _DEFAULT_PERMANENCE  # noqa: E402
from memory.session import SessionMemory  # noqa: E402


def teach_lesson(
    *,
    answer: str,
    lesson_id: str | None = None,
    session: SessionMemory | None = None,
    permanence_layer=None,
) -> dict:
    layer = permanence_layer or _DEFAULT_PERMANENCE
    lesson = get_lesson(lesson_id) if lesson_id else next_lesson(layer)
    if lesson is None:
        return {"status": "complete", "lesson": None, "correct": None, "next_lesson": None}

    correct = score_answer(lesson, answer)
    meta = {
        "answer": lesson.expected_answer,
        "confidence": "CERTAIN" if correct else "UNKNOWN",
        "source_count": 0,
        "gap_count": 0 if correct else 1,
        "contradiction_count": 0,
        "source_domains": ["foundations"],
        "sources": [{"source": "terminal"}],
    }
    learning = learn_from_feedback(lesson.id, 1 if correct else -1, meta=meta)
    next_item = next_lesson(layer)

    if session is not None:
        session.record_turn(
            lesson_id=lesson.id,
            prompt=lesson.prompt,
            answer=answer,
            correct=correct,
            next_lesson_id=next_item.id if next_item else None,
        )

    return {
        "status": "ok",
        "lesson": {
            "id": lesson.id,
            "title": lesson.title,
            "prompt": lesson.prompt,
            "expected_answer": lesson.expected_answer,
            "teaching_answer": lesson.teaching_answer,
        },
        "answer": answer,
        "correct": correct,
        "learning": learning,
        "next_lesson": next_item.id if next_item else None,
        "seed_hint": resolve_foundation_seed_answer(lesson.title),
    }


def teach_fact(
    *,
    prompt: str,
    answer: str,
    session: SessionMemory | None = None,
) -> dict:
    meta = {
        "answer": answer,
        "confidence": "CERTAIN",
        "source_count": 0,
        "gap_count": 0,
        "contradiction_count": 0,
        "source_domains": ["terminal"],
        "sources": [{"source": "terminal"}],
    }
    learning = learn_from_feedback(prompt, 1, meta=meta)

    if session is not None:
        session.record_turn(
            lesson_id="freeform",
            prompt=prompt,
            answer=answer,
            correct=True,
            next_lesson_id=None,
        )

    return {
        "status": "ok",
        "lesson": None,
        "prompt": prompt,
        "answer": answer,
        "correct": True,
        "learning": learning,
        "next_lesson": None,
    }


def _cmd_teach(args: argparse.Namespace) -> int:
    session = SessionMemory(path=Path(args.session_path)) if args.session_path else SessionMemory()
    if args.prompt:
        prompt = args.prompt.strip()
        if args.answer is None:
            answer = input("Teach answer: ").strip()
        else:
            answer = args.answer.strip()
            print(f"Teach answer: {answer}")

        result = teach_fact(prompt=prompt, answer=answer, session=session)
        print(f"Taught: {prompt}")
        print(f"Stored answer: {result['answer']}")
        return 0

    lesson = get_lesson(args.lesson) if args.lesson else next_lesson(_DEFAULT_PERMANENCE)
    if lesson is None:
        print("All current foundation lessons are mastered.")
        return 0

    print(f"Lesson: {lesson.title}")
    print(lesson.prompt)
    if args.answer is None:
        answer = input("Answer: ").strip()
    else:
        answer = args.answer.strip()
        print(f"Answer: {answer}")

    result = teach_lesson(answer=answer, lesson_id=lesson.id, session=session)
    print(f"Correct: {result['correct']}")
    print(f"Teaching answer: {lesson.teaching_answer}")
    if result["next_lesson"]:
        print(f"Next lesson: {result['next_lesson']}")
    return 0


def _cmd_review(args: argparse.Namespace) -> int:
    session = SessionMemory(path=Path(args.session_path)) if args.session_path else SessionMemory()
    history = session.history()
    if not history:
        print("No terminal lessons recorded yet.")
        return 0

    for item in history:
        status = "correct" if item.get("correct") else "miss"
        print(f"{item.get('lesson_id')}: {status} -> {item.get('answer')}")
    return 0


def _cmd_chat(args: argparse.Namespace) -> int:
    question = args.question
    if question:
        response = asyncio.run(answer_question(question.strip()))
        print(f"You: {question.strip()}")
        print(f"Velynx: {response.answer}")
        print(f"Confidence: {response.confidence}")
        return 0

    print("VELYNX chat mode. Type 'exit' to quit.")
    while True:
        try:
            question = input("You: ").strip()
        except EOFError:
            print()
            return 0

        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            return 0

        response = asyncio.run(answer_question(question))
        print(f"Velynx: {response.answer}")
        print(f"Confidence: {response.confidence}")
    


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="velynx", description="VELYNX terminal teaching loop")
    subparsers = parser.add_subparsers(dest="command", required=True)

    teach_parser = subparsers.add_parser("teach", help="Teach one foundation lesson")
    teach_parser.add_argument("--prompt", help="Teach a free-form fact prompt")
    teach_parser.add_argument("--lesson", help="Lesson id to teach")
    teach_parser.add_argument("--answer", help="Provide the learner answer directly")
    teach_parser.add_argument("--session-path", help="Session memory file path")
    teach_parser.set_defaults(func=_cmd_teach)

    review_parser = subparsers.add_parser("review", help="Review terminal lesson history")
    review_parser.add_argument("--session-path", help="Session memory file path")
    review_parser.set_defaults(func=_cmd_review)

    chat_parser = subparsers.add_parser("chat", help="Open a live terminal chat with Velynx")
    chat_parser.add_argument("--question", help="Ask one question and exit")
    chat_parser.set_defaults(func=_cmd_chat)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
