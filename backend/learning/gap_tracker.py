from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

_GAPS_PATH = Path("data/gaps.jsonl")


def record_gap(query: str, reason: str) -> None:
    """Record knowledge gaps (append-only)."""
    _GAPS_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "query": query,
        "reason": reason,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with _GAPS_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload) + "\n")
