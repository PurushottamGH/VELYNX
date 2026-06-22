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
from typing import Iterable, List, Optional

from backend.knowledge.world_model_schema import Entity, WorldModelRegistry

# ── Process-global registry + rendered-profile cache ──────────────────────────
# The registry is installed once at startup (see ``install_default_registry``)
# and swapped atomically. ``_RENDER_CACHE`` maps a casefolded entity name to its
# already-rendered profile block so the live loop never re-walks the schema.
_LOCK = threading.Lock()
_REGISTRY: Optional[WorldModelRegistry] = None
_NAME_INDEX: dict[str, str] = {}          # casefolded name -> canonical entity name
_RENDER_CACHE: dict[str, str] = {}        # casefolded name -> rendered profile


def set_registry(registry: Optional[WorldModelRegistry]) -> None:
    """Install (or replace) the process-wide world model registry.

    Rebuilds the casefolded name index and clears the render cache so the next
    lookup re-renders against the new registry. Passing ``None`` disables
    injection (the pipeline reverts to pre-Phase-62 behaviour).
    """
    global _REGISTRY, _NAME_INDEX, _RENDER_CACHE
    with _LOCK:
        _REGISTRY = registry
        _NAME_INDEX = {}
        _RENDER_CACHE = {}
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

    Includes the type and its ancestor chain, then every resolved attribute
    (own + inherited, defaults filled) in schema-declared order. Booleans are
    lowercased and lists are comma-joined so the LLM reads clean values.
    """
    ancestors = entity.type.ancestors()
    if ancestors:
        type_line = (
            f"{entity.name} — type {entity.type.name} "
            f"(a kind of {', '.join(ancestors)})."
        )
    else:
        type_line = f"{entity.name} — type {entity.type.name}."

    lines: List[str] = [f"[World Model] {type_line}"]
    # resolved_attributes() walks the inheritance chain; iterate in its declared
    # order so inherited roots (license_model, ...) precede leaf slots.
    for attr_name in entity.type.resolved_attributes():
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


__all__ = [
    "set_registry",
    "get_registry",
    "install_default_registry",
    "profile_for_concept",
    "schema_context_for_concepts",
]
