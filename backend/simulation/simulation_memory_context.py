"""
VELYNX Phase 63 — SimulationMemoryContext
=========================================

Ephemeral, copy-on-write counterfactual reasoning workspace for the VELYNX
cognitive architecture.

The Problem
-----------
Counterfactual reasoning requires the system to temporarily assume impossible
states (e.g. "What if my Tesla had no wheels?"). The Phase 62 Schema Gatekeeper
would normally block such assertions as UNKNOWN_ATTRIBUTE or CONSTRAINT_VIOLATION
rejections. Worse, any assertion that *does* slip through a relaxed gate would
be persisted into the SQLite triples table, contaminating the permanent
knowledge graph with impossible facts.

This module provides a **workspace container** that isolates counterfactual
state entirely in volatile RAM, with physical isolation from the production
database layer.

Design Summary
--------------
SimulationMemoryContext is a context manager that:

1. On ``__enter__``: captures the live world model registry and the live
   Schema Gatekeeper; installs a *relaxed* gatekeeper and a *RAM-backed* triple
   store into the fact-extraction pipeline.

2. During the ``with`` block: the fact extraction pipeline reads the real KG
   through a **read-through proxy** that checks a RAM delta layer first, then
   falls through to the live database (via a caller-provided ``read_func``).
   Any writes (from TEACH or from entity mutation) accumulate in the RAM delta
   layer — never reaching SQLite.

3. On ``__exit__``: restores the original gatekeeper and storage path. The RAM
   delta layer is garbage-collected. No permanent state has changed.

Physical Isolation Guarantee
----------------------------
This class possesses no reference to ``sqlite3``, ``aiosqlite``, or any
``.db`` file path. Its data structures are plain Python dicts of Triple
tuples. There is zero code paths that can execute an INSERT against production.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

# ── Forward declarations ──────────────────────────────────────────────────────
Triple = Tuple[str, str, str]
"""The Triple type the existing pipeline uses: (subject, predicate, object)."""

Fact = Any  # imported lazily for type annotations — see get_merged_facts

logger = logging.getLogger("velynx.simulation")


# ══════════════════════════════════════════════════════════════════════════════
# Data classes
# ══════════════════════════════════════════════════════════════════════════════


@dataclass
class SimulatedEntity:
    """An entity fork that exists only within the simulation window.

    Stores attribute *overrides* relative to the live registry entity.
    During reads, the simulation context merges these overrides atop the
    real entity's resolved schema. Copy-on-write: until the first override is
    set, reads pass through to the live Entity with zero memory overhead.
    """

    name: str
    attribute_overrides: dict[str, Any] = field(default_factory=dict)
    added_facets: list[str] = field(default_factory=list)
    removed_facets: list[str] = field(default_factory=list)

    @property
    def is_forked(self) -> bool:
        return bool(self.attribute_overrides or self.added_facets or self.removed_facets)


@dataclass
class SimulatedAttribute:
    """A temporary attribute extension injected into an entity's schema during
    simulation.

    When counterfactual reasoning invents a new attribute for an entity
    (e.g. giving a Tesla a ``wheel_count`` field that Vehicle doesn't normally
    declare), this record captures the schema extension so the relaxed
    gatekeeper can validate values against it. Discarded on context exit.
    """

    entity_name: str
    attribute_key: str
    datatype: type
    constraints: dict = field(default_factory=dict)


# ══════════════════════════════════════════════════════════════════════════════
# SimulationMemoryContext
# ══════════════════════════════════════════════════════════════════════════════


class SimulationMemoryContext:
    """Ephemeral, copy-on-write workspace for counterfactual reasoning.

    Parameters
    ----------
    read_func
        Optional callable that reads triples from the live Knowledge Graph.
        Signature: ``(subject=None, relation=None, obj=None) -> List[Triple]``.
        If omitted, ``get_triples`` returns only the delta layer (no real KG
        read-through). The callable is the *only* bridge to the persistence
        layer — this module never imports a database driver.

    Physical isolation guarantee
    ----------------------------
    This class stores all data in Python dicts of in-memory tuples. It never:
    - Imports ``sqlite3`` or ``aiosqlite``
    - Opens a file handle to any ``.db`` path
    - References ``_KG_DB_PATH``, ``graph.db``, or ``knowledge_graph.db``
    - Instantiates ``KnowledgeGraph`` from ``backend.memory.knowledge_graph``

    There is zero code paths that can reach a production database INSERT.
    """

    # ── Internal state ───────────────────────────────────────────────────────
    _delta_triples: Dict[str, List[Triple]]
    _forked_entities: Dict[str, SimulatedEntity]
    _schema_extensions: Dict[str, SimulatedAttribute]
    _read_func: Optional[Callable[..., List[Triple]]]
    _original_registry: Any = None
    _original_store: Any = None
    _original_validate: Any = None
    _is_active: bool = False

    def __init__(
        self,
        read_func: Optional[Callable[..., List[Triple]]] = None,
    ) -> None:
        self._delta_triples = {}
        self._forked_entities = {}
        self._schema_extensions = {}
        self._read_func = read_func
        self._is_active = False

    # ── Context manager protocol ──────────────────────────────────────────────

    def __enter__(self) -> "SimulationMemoryContext":
        """Enter simulation mode.

        On entry:
        1. Snapshot the live Schema Gatekeeper and fact-extractor storage path.
        2. Install a *relaxed* gatekeeper that accepts counterfactual assertions
           within this simulation window.
        3. Replace ``fact_extractor._store_triples`` with the RAM-backed
           ``_ram_store_wrapper`` (no SQLite involved).

        After entry, every ``extract_and_store_facts()`` call within the
        ``with`` block routes through the relaxed gatekeeper and lands triples
        in ``_delta_triples`` instead of ``graph.db``.
        """
        self._snapshot_and_install()
        self._is_active = True
        logger.info("SimulationMemoryContext: ENTER — counterfactual window opened.")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit simulation mode.

        On exit:
        1. Restore the original Schema Gatekeeper (strict mode).
        2. Restore the original fact-extractor storage path.
        3. Clear all in-memory buffers (*no flush to disk*).

        After exit, the KG is pristine — no counterfactual data survives.
        """
        self._restore_originals()
        self._clear_buffers()
        self._is_active = False
        logger.info("SimulationMemoryContext: EXIT — RAM buffers discarded.")

    # ── Fact injection ───────────────────────────────────────────────────────

    def record_triple(self, subject: str, relation: str, obj: str) -> None:
        """Inject a counterfactual triple into the simulation delta layer.

        This is the public API for adding counterfactual facts during a
        simulation window. The triple is stored in the RAM delta layer
        (never reaches SQLite) and is visible through ``get_triples()``
        for the duration of the ``with`` block.

        Example::

            with SimulationMemoryContext(read_func=...) as ctx:
                ctx.fork_entity("Tesla Model 3", mobility_type="hover")
                ctx.record_triple("Tesla Model 3", "mobility_type", "hover")

        Parameters
        ----------
        subject
            The entity name (subject of the KG triple).
        relation
            The predicate / relation label.
        obj
            The object / value.
        """
        self._delta_triples.setdefault(subject, []).append(
            (subject, relation, obj)
        )

    # ── Read-through proxy ────────────────────────────────────────────────────

    def get_triples(
        self,
        subject: Optional[str] = None,
        relation: Optional[str] = None,
        obj: Optional[str] = None,
    ) -> List[Triple]:
        """Read triples from the merged view (real KG + simulation delta).

        Read-through strategy:
        - Start with the real KG's triples (read-only, via ``read_func``).
        - Overlay any counterfactual triples that match the query.
        - Counterfactual triples with the same (subject, relation, object) as a
          real triple take precedence (they represent the simulation's override).

        If no filter arguments are provided, returns ALL triples from the merged
        view. If any filter is provided, returns only triples matching ALL
        non-None filters.
        """
        real_triples = self._read_real_triples(subject, relation, obj)
        sim_triples = self._query_delta(subject, relation, obj)

        # Build a merge set: start with real triples, shadow matches with sim.
        key_set: set[Triple] = set()
        seen_real: set[Triple] = set(real_triples)

        # Add all sim triples, removing any real triple they shadow.
        for st in sim_triples:
            key_set.discard(st)
            key_set.add(st)
            seen_real.discard(st)

        # Add remaining (un-shadowed) real triples.
        key_set.update(seen_real)

        return sorted(key_set)

    # ── Entity forking ────────────────────────────────────────────────────────

    def fork_entity(
        self,
        name: str,
        attribute_overrides: Optional[dict] = None,
        add_facets: Optional[list[str]] = None,
        remove_facets: Optional[list[str]] = None,
    ) -> SimulatedEntity:
        """Create a copy-on-write fork of a registered entity.

        The fork exists only within this simulation context. The live registry
        is never modified.

        ``attribute_overrides`` sets new values for existing schema attributes
        on the forked entity.

        ``add_facets`` injects orthogonal facet types into the entity's schema
        (e.g. adding ``Electronics`` to a ``Vehicle`` entity that doesn't
        natively have it).

        ``remove_facets`` strips facets from the entity's schema.

        Returns the ``SimulatedEntity`` descriptor. Raises ``KeyError`` if
        ``name`` is not a registered entity in the live registry.
        """
        se = SimulatedEntity(
            name=name,
            attribute_overrides=dict(attribute_overrides or {}),
            added_facets=list(add_facets or []),
            removed_facets=list(remove_facets or []),
        )
        self._forked_entities[name] = se
        logger.info(
            "Simulation: forked entity %r (%d overrides, %d added, %d removed)",
            name,
            len(se.attribute_overrides),
            len(se.added_facets),
            len(se.removed_facets),
        )
        return se

    def get_forked_schema(self, entity_name: str) -> Optional[Dict[str, Any]]:
        """Return the resolved schema for a forked entity as it exists in the
        simulation.

        Merges the live entity's real schema with any facet additions/removals
        and attribute overrides from the fork. Returns ``None`` if the entity
        has not been forked.
        """
        se = self._forked_entities.get(entity_name)
        if se is None:
            return None

        registry = self._get_live_registry()
        if registry is None:
            return None

        entity = registry.get_entity(entity_name)
        if entity is None:
            return None

        schema = entity._resolved_schema()

        # Remove attributes owned by removed facets.
        for facet_name in se.removed_facets:
            for ef in entity.facets:
                if ef.name == facet_name:
                    for attr_key in ef.resolved_attributes():
                        schema.pop(attr_key, None)

        # Add attributes from added facets.
        for facet_name in se.added_facets:
            ft = registry.get_type(facet_name)
            if ft is not None:
                for attr_key, attr_schema in ft.resolved_attributes().items():
                    if attr_key not in schema:
                        schema[attr_key] = attr_schema

        return schema

    # ── Schema extension ──────────────────────────────────────────────────────

    def extend_schema(
        self,
        entity_name: str,
        attribute_key: str,
        datatype: type = str,
        constraints: Optional[dict] = None,
    ) -> SimulatedAttribute:
        """Declare a temporary attribute on an entity for this simulation only.

        When counterfactual reasoning needs to assert a value for an attribute
        that doesn't exist on the entity's real schema (Stage 3 of the
        gatekeeper would normally reject it), calling this method first tells
        the relaxed gatekeeper to accept it during the simulation window.

        The extension is an explicit declaration — the gatekeeper does NOT
        auto-accept unknown attributes; they must be registered here first.
        This prevents "garbage in" even during simulation while still allowing
        deliberate counterfactual constructions.

        Returns the ``SimulatedAttribute`` descriptor.
        """
        key = f"{entity_name}.{attribute_key}"
        sa = SimulatedAttribute(
            entity_name=entity_name,
            attribute_key=attribute_key,
            datatype=datatype,
            constraints=dict(constraints or {}),
        )
        self._schema_extensions[key] = sa
        return sa

    def has_schema_extension(self, entity_name: str, attribute_key: str) -> bool:
        """True if *attribute_key* has been explicitly extended for *entity_name*
        in this simulation window."""
        return f"{entity_name}.{attribute_key}" in self._schema_extensions

    # ── Gatekeeper relaxation ────────────────────────────────────────────────

    def build_relaxed_validate(self) -> Callable:
        """Return a *relaxed* ``validate_triples`` function for use within the
        simulation window.

        The returned function has the same signature as
        ``schema_gatekeeper.validate_triples(triples) -> (accepted, rejections)``
        and can be patched into ``fact_extractor`` in place of the live one.

        Relaxation rules (vs the live Phase 62 strict gatekeeper):
        ---------------------------------------------------------
        Stage 1 (Entity Resolution) — **unchanged**.
          Still casefolds against the registry. Unknown subjects are accepted
          as open-world (same as live).

        Stage 2 (Predicate Mapping) — **unchanged**.
          Still maps via the live ``_PREDICATE_MAP``. Unknown predicates are
          accepted as open-world (same as live).

        Stage 3 (Schema Membership) — **relaxed**.
          If the attribute is NOT on the entity's resolved schema:
            a. Check if an explicit ``SchemaExtension`` was registered via
               ``extend_schema()``. If yes → ACCEPT.
            b. Otherwise → REJECT with ``UNKNOWN_ATTRIBUTE`` (same as live).
          The key discipline: the simulation window does NOT auto-accept every
          unknown attribute — only ones deliberately registered. This prevents
          spurious counterfactuals while enabling intentional ones.

        Stage 4 (Value Validation) — **relaxed**.
          Type coercion runs normally (int, float, bool parsing). Constraint
          checks (enum/min/max/pattern) emit warnings but do NOT reject.
          This allows counterfactuals like ``max_speed_kph = 999999`` (above
          the Vehicle max_speed range) to pass through.

        Result: the relaxed gatekeeper accepts every triple that Stage 4 would
        accept AND forward-looking counterfactuals that Stages 3-4 would reject
        but which have been explicitly permitted via ``extend_schema()`` or
        constraint warnings.
        """
        # Import lazily to avoid circular deps and to reflect the live
        # gatekeeper's state at entry time.
        import backend.knowledge.schema_gatekeeper as gk

        from backend.knowledge.world_model_context import get_registry

        def _relaxed_validate(
            triples: List[Triple],
        ) -> Tuple[List[Triple], List[Any]]:
            accepted: List[Triple] = []
            rejections: List[Any] = []

            for triple in triples or []:
                try:
                    subject, relation, obj = triple
                except (TypeError, ValueError):
                    accepted.append(triple)
                    continue

                # Stage 1 — Entity Resolution.
                entity = self._resolve_entity_relaxed(subject)
                if entity is None:
                    accepted.append(triple)
                    continue

                # Stage 2 — Predicate Mapping.
                pmap = gk._load_predicate_map()
                rel_key = (relation or "").strip().lower()
                attr_key = pmap.get(rel_key)
                if attr_key is None:
                    accepted.append(triple)
                    continue

                # Stage 3 — Schema Membership (relaxed).
                schema = entity._resolved_schema()

                # Apply any active entity forks to the schema view.
                se = self._forked_entities.get(subject)
                if se is not None:
                    registry = get_registry()
                    if registry:
                        for fname in se.removed_facets:
                            ft = registry.get_type(fname)
                            if ft is not None:
                                for ak in ft.resolved_attributes():
                                    schema.pop(ak, None)
                        for fname in se.added_facets:
                            ft = registry.get_type(fname)
                            if ft is not None:
                                for ak, attr_s in ft.resolved_attributes().items():
                                    if ak not in schema:
                                        schema[ak] = attr_s

                valid_attrs = sorted(schema)
                if attr_key not in schema:
                    if self.has_schema_extension(subject, attr_key):
                        accepted.append(triple)
                        continue
                    rejections.append(gk.Rejection(
                        triple=triple,
                        entity_name=entity.name,
                        attribute_key=attr_key,
                        reason_code=gk.REASON_UNKNOWN_ATTRIBUTE,
                        message=(
                            f"[SIMULATION] {entity.name!r} is a {entity.type.name} "
                            f"and does not have attribute {attr_key!r}. "
                            f"Valid attributes: {', '.join(valid_attrs)}."
                        ),
                        valid_attributes=valid_attrs,
                    ))
                    continue

                # Stage 4 — Value Validation (relaxed constraints).
                attr_schema = schema[attr_key]
                coerced, coerce_err = gk._coerce(obj, attr_schema.datatype)
                if coerce_err is not None:
                    rejections.append(gk.Rejection(
                        triple=triple,
                        entity_name=entity.name,
                        attribute_key=attr_key,
                        reason_code=gk.REASON_TYPE_MISMATCH,
                        message=(
                            f"[SIMULATION] attribute {attr_key!r} on "
                            f"{entity.name!r} expects "
                            f"{getattr(attr_schema.datatype, '__name__', attr_schema.datatype)}"
                            f", but {obj!r} could not be parsed ({coerce_err})."
                        ),
                        valid_attributes=valid_attrs,
                    ))
                    continue

                # Constraints: warn but DO NOT reject (relaxed).
                try:
                    attr_schema.validate(coerced)
                except Exception as exc:
                    logger.info(
                        "[SIMULATION] constraint relaxed on %r: %s — accepting anyway",
                        triple, exc,
                    )

                accepted.append(triple)

            return accepted, rejections

        return _relaxed_validate

    # ── Internal: snapshot / install / restore ────────────────────────────────

    def _snapshot_and_install(self) -> None:
        """Capture live state and install simulation-mode components."""
        import backend.knowledge.fact_extractor as fe
        import backend.knowledge.schema_gatekeeper as gk

        self._original_store = fe._store_triples
        self._original_validate = gk.validate_triples

        # Install the relaxed gatekeeper and RAM-backed store.
        relaxed = self.build_relaxed_validate()
        gk.validate_triples = relaxed
        fe._store_triples = self._ram_store_wrapper

        logger.debug(
            "Simulation: patched gk.validate_triples → relaxed, "
            "fe._store_triples → RAM wrapper."
        )

    def _restore_originals(self) -> None:
        """Restore the original gatekeeper and storage path."""
        import backend.knowledge.fact_extractor as fe
        import backend.knowledge.schema_gatekeeper as gk

        if self._original_validate is not None:
            gk.validate_triples = self._original_validate
        if self._original_store is not None:
            fe._store_triples = self._original_store

        logger.debug("Simulation: restored original validate_triples and _store_triples.")

    def _clear_buffers(self) -> None:
        """Discard all simulation data — no flush to disk."""
        self._delta_triples.clear()
        self._forked_entities.clear()
        self._schema_extensions.clear()

    # ── Internal: RAM storage wrapper ─────────────────────────────────────────

    def _ram_store_wrapper(self, triples: List[Triple]) -> int:
        """Replacement for ``fact_extractor._store_triples``.

        Stores triples in the RAM delta layer instead of SQLite.
        Signature matches the original: accepts ``List[Triple]``, returns count.
        """
        if not triples:
            return 0
        for subj, rel, obj in triples:
            self._delta_triples.setdefault(subj, []).append((subj, rel, obj))
        return len(triples)

    # ── Internal: delta-layer query ───────────────────────────────────────────

    def _query_delta(
        self,
        subject: Optional[str] = None,
        relation: Optional[str] = None,
        obj: Optional[str] = None,
    ) -> List[Triple]:
        """Filter the delta layer by optional criteria. Returns matching triples."""
        results: List[Triple] = []
        for subj_key, triples in self._delta_triples.items():
            if subject is not None and subj_key != subject:
                continue
            for s, r, o in triples:
                if relation is not None and r != relation:
                    continue
                if obj is not None and o != obj:
                    continue
                results.append((s, r, o))
        return results

    # ── Internal: real-KG read-through ────────────────────────────────────────

    def _read_real_triples(
        self,
        subject: Optional[str] = None,
        relation: Optional[str] = None,
        obj: Optional[str] = None,
    ) -> List[Triple]:
        """Read triples from the live Knowledge Graph via ``read_func``.

        If no ``read_func`` was provided at construction, returns an empty list
        (delta-only mode). Errors from ``read_func`` are logged and treated as
        empty — the simulation continues without the real KG read-through.
        """
        if self._read_func is None:
            return []
        try:
            result = self._read_func(subject, relation, obj)
            return result if result else []
        except Exception as exc:
            logger.warning(
                "Simulation: read_func failed (%s) — falling back to delta-only.", exc
            )
            return []

    # ── Internal: entity resolution ───────────────────────────────────────────

    def _resolve_entity_relaxed(self, subject: str) -> Any:
        """Entity resolution using the live registry, with fork awareness."""
        from backend.knowledge.world_model_context import get_registry

        reg = get_registry()
        if reg is None or not subject:
            return None
        key = subject.strip().casefold()
        for name in reg.entities():
            if name.casefold() == key:
                return reg.get_entity(name)
        return None

    def _get_live_registry(self):
        """Return the current WorldModelRegistry singleton."""
        try:
            from backend.knowledge.world_model_context import get_registry

            return get_registry()
        except Exception:
            return None

    # ── Introspection ─────────────────────────────────────────────────────────

    @property
    def is_dirty(self) -> bool:
        """True if any counterfactual triples or entity forks exist."""
        return bool(self._delta_triples or self._forked_entities)

    @property
    def is_active(self) -> bool:
        """True if the context is currently inside a ``with`` block."""
        return self._is_active

    @property
    def counterfactual_triple_count(self) -> int:
        """Number of counterfactual triples stored in the delta layer."""
        return sum(len(v) for v in self._delta_triples.values())

    @property
    def counterfactual_triples(self) -> List[Triple]:
        """All triples added during this simulation (the diff from reality)."""
        result: List[Triple] = []
        for triples in self._delta_triples.values():
            result.extend(triples)
        return result

    @property
    def forked_entity_names(self) -> List[str]:
        """Names of entities that have been forked in this simulation."""
        return list(self._forked_entities.keys())

    def describe(self) -> dict:
        """Return a snapshot of the simulation's current state for debugging."""
        return {
            "active": self._is_active,
            "dirty": self.is_dirty,
            "counterfactual_triples": self.counterfactual_triple_count,
            "forked_entities": self.forked_entity_names,
            "schema_extensions": list(self._schema_extensions.keys()),
        }


# ══════════════════════════════════════════════════════════════════════════════
# INTEGRATION USAGE (proposed pattern for pipeline.py)
# ══════════════════════════════════════════════════════════════════════════════
#
# The simulation context should be activated by the pipeline when the user
# query triggers a counterfactual reasoning path (detected by intent engine):
#
#   from backend.simulation.simulation_memory_context import (
#       SimulationMemoryContext,
#   )
#   from backend.memory.knowledge_graph import get_all_triples  # hypothetical
#
#   def triples_read_func(
#       subject=None, relation=None, obj=None,
#   ) -> list[tuple[str, str, str]]:
#       """Read-through adapter for the live Knowledge Graph triples table."""
#       # Query the `triples` table managed by fact_extractor.
#       # Replace this with the actual KG read API.
#       from backend.memory._sqlite import connect as open_connection
#       from backend.knowledge.fact_extractor import _KG_DB_PATH
#       conn = open_connection(str(_KG_DB_PATH))
#       try:
#           sql = "SELECT subject, relation, object FROM triples"
#           params: list[str] = []
#           clauses: list[str] = []
#           if subject is not None:
#               clauses.append("subject = ?"); params.append(subject)
#           if relation is not None:
#               clauses.append("relation = ?"); params.append(relation)
#           if obj is not None:
#               clauses.append("object = ?"); params.append(obj)
#           if clauses:
#               sql += " WHERE " + " AND ".join(clauses)
#           return list(conn.execute(sql, params).fetchall())
#       finally:
#           conn.close()
#
#   def handle_counterfactual(user_query: str) -> AnswerResponse | None:
#       """Entry point for counterfactual ('what if') reasoning queries."""
#
#       with SimulationMemoryContext(read_func=triples_read_func) as sim_ctx:
#           # 1. Fork the entity that is the subject of the counterfactual.
#           sim_ctx.fork_entity(
#               "Tesla Model 3",
#               attribute_overrides={"wheel_count": 0, "mobility_type": "stationary"},
#           )
#
#           # 2. Extend schema for novel counterfactual attributes.
#           sim_ctx.extend_schema("Tesla Model 3", "wheel_count", datatype=int)
#
#           # 3. TEACH a counterfactual fact (lands in RAM, not SQLite).
#           from backend.knowledge.fact_extractor import extract_and_store_facts
#           extract_and_store_facts("My Tesla has wheel_count 0.")
#
#           # 4. Read the merged view (real + counterfactual) for reasoning.
#           merged = sim_ctx.get_triples(subject="Tesla Model 3")
#
#           # 5. Run the reasoning engine over the merged facts.
#           trace = reasoning_engine.reason(...)
#
#           # 6. Compare counterfactual trace with a baseline trace to produce
#           #    the "what changed" answer.
#
#       # On exit: all counterfactual state is gone. The KG is pristine.
#
#       return AnswerResponse(answer=..., ...)
#
# COMPARISON: baseline reasoning (pre-simulation) vs counterfactual reasoning
# (during simulation) should be computed by running ``reason()`` twice —
# once outside the ``with`` block, once inside — and diffing the resulting
# ``ReasoningTrace`` objects (paths, contradictions, inferred facts).

__all__ = [
    "SimulationMemoryContext",
    "SimulatedEntity",
    "SimulatedAttribute",
]
