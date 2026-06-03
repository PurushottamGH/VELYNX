from __future__ import annotations

import json
from pathlib import Path

_TRUST_PATH = Path("data/source_trust.json")


def load_trust_scores() -> dict:
    if _TRUST_PATH.exists():
        return json.loads(_TRUST_PATH.read_text(encoding="utf-8"))
    return {}


def update_source_trust(source: str, delta: float) -> None:
    """Update source trust score (simple local store)."""
    _TRUST_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = load_trust_scores()

    current = float(data.get(source, 0.0))
    data[source] = round(current + delta, 3)
    _TRUST_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
