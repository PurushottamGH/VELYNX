"""Soul routing — V1 and V2 soul concept lookup with stem matching."""
from __future__ import annotations

import json
import logging
from pathlib import Path

from nltk.stem import PorterStemmer

logger = logging.getLogger("uvicorn")

SOUL_PATH = Path(__file__).resolve().parent.parent / "soul" / "concepts.json"
SOUL_EDGE_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "concepts.json"
_STEMMER = PorterStemmer()

# Pre-compute stems for all soul concept names on module load
_SOUL_CONCEPT_STEMS: dict[str, str] = {}
_SOUL_EDGES: list[dict] = []
try:
    if SOUL_PATH.exists():
        raw = json.loads(SOUL_PATH.read_text())
        for name in raw:
            _SOUL_CONCEPT_STEMS[name] = _STEMMER.stem(name)
    if SOUL_EDGE_PATH.exists():
        edge_data = json.loads(SOUL_EDGE_PATH.read_text())
        _SOUL_EDGES = edge_data.get("edges", [])
except Exception:
    pass


def _stem_match(query_word: str, concept_name: str) -> bool:
    """Return True if the query word stems to the same root as the concept."""
    s_q = _STEMMER.stem(query_word.strip(",.!?;:'\"()[]{}"))
    s_c = _SOUL_CONCEPT_STEMS.get(concept_name, "")
    if not s_q or not s_c:
        return False
    return s_q == s_c or (len(s_q) >= 4 and s_q[:4] == s_c[:4])


def _get_edge_synthesis(matched: list[str]) -> str | None:
    """If >1 concept matched, look for edges connecting them and synthesize."""
    if len(matched) < 2:
        return None
    pairs = set()
    for e in _SOUL_EDGES:
        src = e.get("source", "")
        tgt = e.get("target", "")
        if src in matched and tgt in matched:
            pairs.add((src, tgt, e.get("relationship_type", ""), e.get("context", "")))
    if not pairs:
        # No explicit edges — generate a default bridging synthesis
        parts = []
        for i in range(len(matched) - 1):
            parts.append(
                f"{matched[i].capitalize()} and {matched[i+1]} are deeply connected human "
                f"experiences. {matched[i].capitalize()} shapes how we experience "
                f"{matched[i+1]}, and understanding both together gives a fuller "
                f"picture of the human condition than either alone."
            )
        return "\n\n".join(parts)
    # Build from found edges
    lines = []
    for src, tgt, rtype, ctx in pairs:
        lines.append(f"{src.capitalize()} {rtype} {tgt}: {ctx}")
    return "\n\n".join(lines)


def _build_soul_block(concept: str, data: dict) -> str:
    """Build a formatted soul response from a single concept's data."""
    core = data.get("core", "").strip()
    if not core:
        return ""
    parts = [core]
    not_list = data.get("what_it_is_not", [])
    if not_list:
        parts.append("It is not: " + ", ".join(not_list[:3]))
    situations = data.get("real_situations", [])
    if situations:
        s = situations[0]
        parts.append(f"In reality: {s.get('why', '')}")
    taught_by = data.get("taught_by", "")
    if taught_by:
        parts.append(f"(Taught by {taught_by})")
    return "\n\n".join(p for p in parts if p)


# ── VELYNX V2 soul pipeline ──────────────────────────────────────────────────


def soul_lookup(query: str) -> dict | None:
    """
    V2 soul lookup using scenario engine + soul graph + embedding index.
    Handles direct, relational, and scenario-type queries that the legacy
    _soul_lookup may miss (e.g. "A man forgave someone who never apologized").
    """
    try:
        from cognition.scenario_engine import parse_scenario
        from soul.soul_graph import synthesize, get_edges, get_tensions
    except Exception:
        return None

    result = parse_scenario(query)
    if not result["concepts"]:
        return None

    soul_path = SOUL_PATH
    if not soul_path.exists():
        return None
    soul = json.loads(soul_path.read_text())

    qtype = result["query_type"]

    # Build concept data with edges/tensions
    concept_data = []
    for concept in result["concepts"][:3]:
        entry = soul.get(concept, {})
        concept_data.append({
            "name": concept,
            "entry": entry,
            "edges": get_edges(concept),
            "tensions": get_tensions(concept),
        })

    if qtype == "direct" and len(result["concepts"]) == 1:
        c = concept_data[0]
        entry = c["entry"]
        if isinstance(entry, dict):
            response = entry.get("definition", entry.get("core", str(entry)))
        else:
            response = str(entry)
    elif qtype in ("relational", "scenario"):
        response = result["arc"]
        if not response:
            names = [c["name"] for c in concept_data]
            response = synthesize(names)
            # synthesize() returns a generic stub when no edges exist —
            # fall through to legacy which builds richer formatted blocks
            if response and response.startswith("These concepts are deeply connected"):
                response = ""
    else:
        response = result["arc"] or str(concept_data[0]["entry"])

    if not response:
        return None

    return {
        "answer": response,
        "concepts": result["concepts"],
        "arc": result["arc"],
        "soul_used": True,
        "v2": True,
        "scores": result.get("scores", {}),
    }


def soul_lookup_legacy(query: str) -> dict | None:
    """
    Legacy soul lookup using Porter stemming on query words and concept names.

    This is the original V1 implementation, preserved as a fallback.
    "forgave"  -> stem "forgiv" matches "forgiveness" -> stem "forgiv".
    Returns a dict with:
      - answer:      str  (combined soul definitions + any edge synthesis)
      - concepts:    list[str]  (all matched concept names)
      - soul_used:   True
    Returns None if nothing matches.
    """
    try:
        if not SOUL_PATH.exists():
            return None

        soul = json.loads(SOUL_PATH.read_text())
        query_words = query.lower().split()

        matched_concepts: list[str] = []
        for concept_name, data in soul.items():
            # 1) exact substring (fast path — keeps old behaviour)
            if concept_name in query.lower():
                matched_concepts.append(concept_name)
                continue
            # 2) stem match on any query word
            for qw in query_words:
                if _stem_match(qw, concept_name):
                    matched_concepts.append(concept_name)
                    break

        if not matched_concepts:
            return None

        # Deduplicate while preserving order
        seen: set[str] = set()
        ordered: list[str] = []
        for c in matched_concepts:
            if c not in seen:
                seen.add(c)
                ordered.append(c)

        # Build answer blocks for each matched concept
        blocks: list[str] = []
        for c in ordered:
            block = _build_soul_block(c, soul[c])
            if block:
                blocks.append(block)

        # If >1 concept matched, add edge synthesis
        synth = _get_edge_synthesis(ordered)
        if synth:
            blocks.append("── Relationship ──")
            blocks.append(synth)

        answer = "\n\n".join(blocks)

        return {
            "answer": answer,
            "concepts": ordered,
            "soul_used": True,
        }

    except Exception:
        return None
