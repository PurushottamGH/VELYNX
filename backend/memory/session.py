from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("uvicorn")

_SESSION_PATH = Path("data/session.json")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SessionMemory:
    """File-backed session memory for terminal teaching runs."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or _SESSION_PATH
        self._state = self._load_state()
        self._db_session_id: str | None = None

    def _load_state(self) -> dict:
        if self.path.exists():
            return json.loads(self.path.read_text(encoding="utf-8"))
        return {"current_lesson": None, "history": []}

    def _persist(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._state, indent=2, sort_keys=True), encoding="utf-8")

    def set_current_lesson(self, lesson_id: str | None) -> None:
        self._state["current_lesson"] = lesson_id
        self._persist()

    def current_lesson(self) -> str | None:
        return self._state.get("current_lesson")

    def record_turn(
        self,
        *,
        lesson_id: str,
        prompt: str,
        answer: str,
        correct: bool,
        next_lesson_id: str | None = None,
    ) -> dict:
        entry = {
            "lesson_id": lesson_id,
            "prompt": prompt,
            "answer": answer,
            "correct": correct,
            "next_lesson_id": next_lesson_id,
            "timestamp": _now(),
        }
        self._state.setdefault("history", []).append(entry)
        self._state["current_lesson"] = next_lesson_id
        self._persist()
        return entry

    def history(self) -> list[dict]:
        return list(self._state.get("history", []))

    async def sync_to_db(self) -> str | None:
        """Sync session state to PostgreSQL. Returns session ID."""
        try:
            from database.engine import async_session
            from database.repositories import SessionRepository

            async with async_session() as db:
                repo = SessionRepository(db)
                if self._db_session_id:
                    # Update existing session metadata
                    session_obj = await repo.get_active()
                    if session_obj:
                        session_obj.metadata_ = {
                            "current_lesson": self._state.get("current_lesson"),
                            "turn_count": len(self._state.get("history", [])),
                        }
                        await db.commit()
                else:
                    # Create new session
                    session_obj = await repo.create(metadata={
                        "current_lesson": self._state.get("current_lesson"),
                        "turn_count": len(self._state.get("history", [])),
                    })
                    self._db_session_id = session_obj.id
                    logger.info("Session synced to DB: %s", self._db_session_id)
            return self._db_session_id
        except Exception as exc:
            logger.debug("Session DB sync skipped: %s", exc)
            return None

    async def end_db_session(self) -> None:
        """End the database session record."""
        if not self._db_session_id:
            return
        try:
            from database.engine import async_session
            from database.repositories import SessionRepository

            async with async_session() as db:
                await SessionRepository(db).end_session(self._db_session_id)
                logger.info("Session ended in DB: %s", self._db_session_id)
        except Exception as exc:
            logger.debug("Session DB end skipped: %s", exc)
        finally:
            self._db_session_id = None
