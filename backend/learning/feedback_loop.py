from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

_DATA_PATH = Path("data/feedback.jsonl")


def record_feedback(query: str, rating: int, meta: dict | None = None) -> None:
    """Record user feedback on answers (append-only)."""
    _DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "query": query,
        "rating": rating,
        "meta": meta or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with _DATA_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload) + "\n")
