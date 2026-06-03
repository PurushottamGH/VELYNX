from __future__ import annotations

import re
from typing import Iterable

NEGATION = re.compile(r"\b(no|not|never|cannot|doesn't|isn't|won't|without)\b", re.IGNORECASE)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def _extract_claims(sources: Iterable[dict]) -> list[dict]:
    claims: list[dict] = []
    for item in sources:
        snippet = _normalize(item.get("snippet") or "")
        if not snippet:
            continue
        claims.append(
            {
                "text": snippet,
                "is_negative": bool(NEGATION.search(snippet)),
                "source": item.get("source"),
                "url": item.get("url"),
            }
        )
    return claims


def build_evidence_graph(sources: list[dict]) -> dict:
    """Build a lightweight evidence graph linking claims to sources."""
    claims = _extract_claims(sources)
    nodes: list[dict] = []
    edges: list[dict] = []

    for index, claim in enumerate(claims):
        node_id = f"claim_{index}"
        nodes.append(
            {
                "id": node_id,
                "type": "claim",
                "text": claim.get("text"),
                "is_negative": claim.get("is_negative"),
            }
        )

        source_id = f"source_{index}"
        nodes.append(
            {
                "id": source_id,
                "type": "source",
                "source": claim.get("source"),
                "url": claim.get("url"),
            }
        )
        edges.append({"from": source_id, "to": node_id, "type": "supports"})

    return {"nodes": nodes, "edges": edges}


def find_contradictions(sources: list[dict]) -> dict:
    """Detect contradictions across sources (heuristic claim split)."""
    claims = _extract_claims(sources)
    positives = [c for c in claims if not c["is_negative"]]
    negatives = [c for c in claims if c["is_negative"]]

    conflicts: list[dict] = []
    if positives and negatives:
        conflicts.append(
            {
                "summary": "Mixed affirmative and negative claims detected across sources.",
                "positives": positives[:3],
                "negatives": negatives[:3],
                "severity": "debatable",
            }
        )

    report = {
        "total_claims": len(claims),
        "conflicts": conflicts,
    }
    return report
