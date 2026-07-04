from __future__ import annotations

from pathlib import Path


CONSTITUTION_DIR = Path(__file__).resolve().parents[1] / "constitution"

from backend.learning.living_constitution import render_rules


def load_constitution(cognitive_layer: str | None = None, include_pending: bool = True) -> str:
    parts: list[str] = []
    for name in [
        "logic.md",
        "science.md",
        "epistemology.md",
        "uncertainty.md",
        "communication.md",
        "curiosity.md",
    ]:
        path = CONSTITUTION_DIR / name
        if path.exists():
            parts.append(path.read_text(encoding="utf-8"))
    learned_rules = render_rules(include_pending=include_pending, cognitive_layer=cognitive_layer)
    if learned_rules:
        parts.append("# Learned rules\n" + learned_rules)
    return "\n\n".join(parts)
