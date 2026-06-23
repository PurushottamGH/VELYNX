"""
VELYNX Phase 62 — World Model Context Injection
===============================================

The :mod:`world_model_schema` scaffold proved the object-oriented type system
in-memory: entities have a type, types inherit, and attributes resolve up the
ancestral tree. This module is the *bridge* that wires that schema into the live
retrieval pipeline.

Responsibility
--------------
When the working-memory / reasoning pipeline extracts the concepts for a query
(see ``reasoning_wiring.extract_query_concepts``), any concept that names a
registered :class:`~backend.knowledge.world_model_schema.Entity` is recognised
and its **fully evaluated profile** — every own *and inherited* attribute, with
defaults filled — is rendered into a compact text block. That block is folded
into the reasoner's free-text ``episodic_context`` channel (the same channel the
LLM synthesiser already consumes), so instead of seeing the bare token
``"Blender"`` the reasoning core receives::

    [World Model] Blender — type ThreeDModelingApp (a kind of
    DesktopApplication, Software).
      • license_model: GPL
      • open_source: true
      • vendor: Blender Foundation
      • supported_formats: blend, fbx, obj, glb

Performance
-----------
Profile resolution walks the inheritance chain on every lookup, so we cache the
*rendered* profile per entity name in a process-global dict. Resolution is
deterministic for a given registry generation, so the cache is invalidated only
when the registry is replaced (``set_registry``) — keeping the hot path a single
dict ``get`` with no schema walk and no allocation. This keeps the live query
loop free of added latency (Functional Requirement 4).

Design notes
------------
* **No hard dependency on a populated registry.** If no registry has been
  installed (or it is empty), every public call degrades to a no-op returning
  empty results — the pipeline behaves exactly as it did pre-Phase-62.
* **Case-insensitive, normaliser-aware matching.** Concepts arrive already
  passed through ``concept_normalizer``; we index entities under both their
  exact name and a casefolded key so "blender" matches the entity "Blender".
* **Pure + thread-light.** A single lock guards registry swaps and the cache;
  the read path takes the lock only briefly to read the cache reference.
"""
from __future__ import annotations

import threading
from typing import Any, Dict, Iterable, List, Optional

from backend.knowledge.world_model_schema import Entity, WorldModelRegistry

# ── Process-global registry + rendered-profile cache ──────────────────────────
# The registry is installed once at startup (see ``install_default_registry``)
# and swapped atomically. ``_RENDER_CACHE`` maps a casefolded entity name to its
# already-rendered profile block so the live loop never re-walks the schema.
_LOCK = threading.Lock()
_REGISTRY: Optional[WorldModelRegistry] = None
_NAME_INDEX: dict[str, str] = {}          # casefolded name -> canonical entity name
_RENDER_CACHE: dict[str, str] = {}        # casefolded name -> rendered profile
_FACTS_CACHE: dict[str, list[dict]] = {}  # casefolded name -> structured triples


def set_registry(registry: Optional[WorldModelRegistry]) -> None:
    """Install (or replace) the process-wide world model registry.

    Rebuilds the casefolded name index and clears the render cache so the next
    lookup re-renders against the new registry. Passing ``None`` disables
    injection (the pipeline reverts to pre-Phase-62 behaviour).
    """
    global _REGISTRY, _NAME_INDEX, _RENDER_CACHE, _FACTS_CACHE
    with _LOCK:
        _REGISTRY = registry
        _NAME_INDEX = {}
        _RENDER_CACHE = {}
        _FACTS_CACHE = {}
        if registry is not None:
            for name in registry.entities():
                _NAME_INDEX[name.casefold()] = name


def get_registry() -> Optional[WorldModelRegistry]:
    """Return the currently installed registry (or ``None`` if disabled)."""
    return _REGISTRY


def install_default_registry() -> WorldModelRegistry:
    """Install the canonical Phase 62 taxonomy (3D-modeling software).

    Convenience for startup wiring and tests. Returns the installed registry.
    """
    from backend.knowledge.world_model_schema import build_3d_software_world

    reg = build_3d_software_world()
    set_registry(reg)
    return reg


# ── Lookup ───────────────────────────────────────────────────────────────────
def _resolve_entity(concept: str) -> Optional[Entity]:
    """Map a concept label to a registered :class:`Entity`, case-insensitively.

    Returns ``None`` when no registry is installed or the concept does not name
    a known entity. Never raises.
    """
    reg = _REGISTRY
    if reg is None or not concept:
        return None
    canonical = _NAME_INDEX.get(concept.strip().casefold())
    if canonical is None:
        return None
    return reg.get_entity(canonical)


def _render_profile(entity: Entity) -> str:
    """Render an entity's fully evaluated profile into a compact text block.

    Includes the type and its ancestor chain, any instance/type facets, then
    every resolved attribute (own + inherited + faceted, defaults filled) in
    schema-declared order. Booleans are lowercased and lists are comma-joined so
    the LLM reads clean values.

    The attribute set is taken from the ENTITY's resolved schema
    (``entity._resolved_schema()``), not ``entity.type.resolved_attributes()``.
    The latter only covers the type's inheritance chain (plus type-level facets)
    and silently drops *instance-level* facets — e.g. a Tesla Model 3 typed as
    Vehicle but carrying an Electronics facet would lose power_source / voltage /
    has_screen / manufacturer. Rendering from the entity schema keeps faceted
    attributes visible (Phase 62 multi-category fix).
    """
    ancestors = entity.type.ancestors()
    if ancestors:
        type_line = (
            f"{entity.name} — type {entity.type.name} "
            f"(a kind of {', '.join(ancestors)})."
        )
    else:
        type_line = f"{entity.name} — type {entity.type.name}."

    # Surface instance facets so the reasoner knows the object spans categories
    # (e.g. "also Electronics"), not just its primary type chain.
    facet_names = [f.name for f in getattr(entity, "facets", []) or []]
    if facet_names:
        type_line += f" Also: {', '.join(facet_names)}."

    lines: List[str] = [f"[World Model] {type_line}"]
    # Render from the ENTITY's resolved schema so instance-level facet slots
    # (power_source, voltage, ...) are included alongside the inheritance chain.
    for attr_name in entity._resolved_schema():
        value = entity.get(attr_name)
        lines.append(f"  \u2022 {attr_name}: {_format_value(value)}")
    return "\n".join(lines)


def _format_value(value: object) -> str:
    """Human/LLM-friendly rendering of an attribute value."""
    if value is None:
        return "unknown"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple, set)):
        return ", ".join(str(v) for v in value) if value else "(none)"
    return str(value)


def profile_for_concept(concept: str) -> Optional[str]:
    """Return the cached, rendered world-model profile for *concept*, or ``None``.

    This is the hot-path entry point. The rendered block is memoised per entity
    so a repeated mention in the live loop costs a single dict lookup — no schema
    walk, no string building. Cache entries are only ever invalidated by
    ``set_registry``.
    """
    if not concept:
        return None
    key = concept.strip().casefold()
    if key not in _NAME_INDEX:
        return None  # cheap reject: not an entity, skip the lock entirely.

    cached = _RENDER_CACHE.get(key)
    if cached is not None:
        return cached

    entity = _resolve_entity(concept)
    if entity is None:
        return None
    rendered = _render_profile(entity)
    with _LOCK:
        # Re-check under the lock: set_registry may have swapped the cache out.
        if key in _NAME_INDEX:
            _RENDER_CACHE[key] = rendered
    return rendered


def schema_context_for_concepts(
    concepts: Iterable[str], limit: int = 8
) -> List[str]:
    """Resolve a concept list to rendered world-model profile blocks.

    Used by the pipeline to enrich a query's context. Preserves concept order,
    de-duplicates entities (so the same entity mentioned twice injects once),
    and caps the number of injected profiles at *limit* to bound prompt size.

    Returns an empty list when no registry is installed or no concept names a
    known entity — making this a safe no-op on every non-entity query.
    """
    out: List[str] = []
    seen: set[str] = set()
    for concept in concepts or []:
        key = (concept or "").strip().casefold()
        if not key or key in seen:
            continue
        block = profile_for_concept(concept)
        if block is None:
            continue
        seen.add(key)
        out.append(block)
        if limit and len(out) >= limit:
            break
    return out


# ── Structured fact channel (Phase 62.1) ─────────────────────────────────────
# The reasoner is a *graph* engine: it can only traverse, adjudicate, and
# resolve concepts that arrive as (subject, predicate, object) triples. The
# rendered profile above is high-signal for the LLM synthesiser, but to the
# reasoner it is opaque free text — it lands in the ``episodic_context`` channel
# where it can only nudge a scalar salience bias and never participate in
# pathfinding. So an inherited fact like ``mobility_type=wheeled`` could be
# *displayed* but never *reasoned over*: "Does a Tesla Model 3 have wheels?"
# died at "no connecting evidence" because Tesla and wheels were never linked by
# an edge.
#
# This builder is the structural fix: it projects an entity's fully-resolved
# schema into first-class triples that flow into the engine's fact pool (see
# ``ReasoningEngine.reason(world_model_facts=...)``). Three kinds of edge are
# emitted:
#
#   * Type chain        (entity, is_a, Vehicle), (Vehicle, is_a, PhysicalObject)
#   * Facet membership  (entity, is_a, Electronics)
#   * Attribute values  (entity, mobility_type, wheeled), (entity, propulsion, electric)
#
# Every edge is high-confidence (0.95) because the ontology is a curated,
# authoritative source — these are not noisy web extractions. Attributes whose
# resolved value is ``None`` (unknown) are skipped: an absent value is not a
# fact and would only add a dead-end node.

# Confidence assigned to ontology-derived facts. High, because the World Model
# registry is curated/authoritative — but capped below 1.0 so direct, taught
# evidence can still supersede it during contradiction resolution.
_WORLD_MODEL_FACT_CONFIDENCE = 0.95


def _facts_for_entity(entity: Entity) -> list[dict]:
    """Project an entity's resolved schema into structured triple dicts.

    Returns dicts shaped ``{subject, predicate, object, confidence, source}`` —
    exactly what :meth:`ReasoningEngine._coerce_fact` consumes — so this module
    stays free of any reasoning-engine import (no coupling, no cycle).
    """
    facts: list[dict] = []
    name = entity.name

    def _emit(subject: str, predicate: str, obj: str) -> None:
        s, o = str(subject).strip(), str(obj).strip()
        if not s or not predicate or not o:
            return
        facts.append({
            "subject": s,
            "predicate": predicate,
            "object": o,
            "confidence": _WORLD_MODEL_FACT_CONFIDENCE,
            "source": "world_model",
        })

    # 1) Type chain: entity -> its type -> each ancestor, as is_a edges.
    #    ancestors() is ordered nearest-first (e.g. ['PhysicalObject']); prefix
    #    the entity's own type so the full chain Tesla -> Vehicle -> PhysicalObject
    #    materialises as consecutive transitive edges.
    type_chain = [entity.type.name, *entity.type.ancestors()]
    prev = name
    for type_name in type_chain:
        _emit(prev, "is_a", type_name)
        prev = type_name

    # 2) Facet membership: the entity ALSO is_a each facet category it carries
    #    (e.g. a Tesla typed Vehicle that is also Electronics).
    for facet in getattr(entity, "facets", []) or []:
        _emit(name, "is_a", facet.name)

    # 3) Resolved attribute values: one edge per attribute that has a concrete
    #    (non-None) value. The predicate IS the attribute name so the reasoner
    #    can answer relation-specific questions; the object is the value.
    for attr_name in entity._resolved_schema():
        value = entity.get(attr_name)
        if value is None:
            continue  # unknown -> not a fact, skip the dead-end node.
        if isinstance(value, bool):
            obj = "true" if value else "false"
        elif isinstance(value, (list, tuple, set)):
            # Emit one edge per list member so each value is an addressable node.
            for member in value:
                _emit(name, attr_name, str(member))
            continue
        else:
            obj = str(value)
        _emit(name, attr_name, obj)

    return facts


def facts_for_concept(concept: str) -> Optional[list[dict]]:
    """Return the cached structured triples for *concept*, or ``None``.

    Hot-path entry point mirroring :func:`profile_for_concept`: a casefolded
    name miss rejects without taking the lock, and the projected fact list is
    memoised per entity (invalidated only by ``set_registry``).
    """
    if not concept:
        return None
    key = concept.strip().casefold()
    if key not in _NAME_INDEX:
        return None  # cheap reject: not an entity.

    cached = _FACTS_CACHE.get(key)
    if cached is not None:
        return cached

    entity = _resolve_entity(concept)
    if entity is None:
        return None
    built = _facts_for_entity(entity)
    with _LOCK:
        if key in _NAME_INDEX:
            _FACTS_CACHE[key] = built
    return built


def world_model_facts_for_concepts(
    concepts: Iterable[str], limit: int = 8
) -> List[dict]:
    """Resolve a concept list to a flat list of structured world-model triples.

    The structured counterpart of :func:`schema_context_for_concepts`: instead
    of rendered text blocks for the synthesiser, it returns first-class triples
    for the reasoning engine's fact pool. De-duplicates entities, preserves
    concept order, and caps the number of *entities* contributing facts at
    *limit*. Returns ``[]`` when no registry is installed or no concept names a
    known entity — a safe no-op on every non-entity query.
    """
    out: List[dict] = []
    seen: set[str] = set()
    n_entities = 0
    for concept in concepts or []:
        key = (concept or "").strip().casefold()
        if not key or key in seen:
            continue
        triples = facts_for_concept(concept)
        if not triples:
            continue
        seen.add(key)
        out.extend(triples)
        n_entities += 1
        if limit and n_entities >= limit:
            break
    return out


__all__ = [
    "set_registry",
    "get_registry",
    "install_default_registry",
    "profile_for_concept",
    "schema_context_for_concepts",
    "facts_for_concept",
    "world_model_facts_for_concepts",
]
