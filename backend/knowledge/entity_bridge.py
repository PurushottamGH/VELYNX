"""
VELYNX Phase 62 — Entity Bridge
================================

A hydration layer that bridges raw semantic triples from the SQLite
:class:`~backend.memory.knowledge_graph.KnowledgeGraph` into structured,
object-oriented :class:`~backend.knowledge.world_model_schema.Entity`
objects via :class:`~backend.knowledge.world_model_schema.WorldModelRegistry`.

The pipeline
------------
#. Query the ``triples`` table for every triple whose subject matches the
   entity name.
#. Identify the ``(subject, is_a, EntityTypeName)`` triple to determine which
   :class:`~backend.knowledge.world_model_schema.EntityType` to instantiate.
#. Map remaining ``(subject, predicate, object)`` triples into the strongly
   typed attribute slots declared on the resolved type, converting string
   representations to the target datatype (e.g. ``"true"`` → ``True``).
#. Gracefully skip predicates that have no corresponding schema slot (logging
   a warning) so the bridge never crashes the main cognitive pipeline over an
   unexpected triple.

Usage::

    from backend.knowledge.world_model_schema import WorldModelRegistry
    from backend.knowledge.entity_bridge import EntityBridge
    from backend.memory.knowledge_graph import KnowledgeGraph

    kg = KnowledgeGraph()
    registry = WorldModelRegistry()
    bridge = EntityBridge(kg, registry)

    blender = await bridge.hydrate("Blender")
    if blender is not None:
        print(blender.get("license_model"))   # "GPL"
        print(blender.get("open_source"))      # True
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Optional, Union

import aiosqlite

from backend.knowledge.world_model_schema import (
    Entity,
    SchemaError,
    WorldModelRegistry,
)
from backend.memory.knowledge_graph import KnowledgeGraph

logger = logging.getLogger("velynx.entity_bridge")

# ── public API ────────────────────────────────────────────────────────────────


class EntityBridge:
    """Hydrate :class:`Entity` objects from raw semantic triples.

    Parameters
    ----------
    kg:
        The async :class:`KnowledgeGraph` whose ``triples`` table will be
        queried. The bridge reads its ``db_path`` to open its own connection
        for triple queries.
    registry:
        The :class:`WorldModelRegistry` that holds the type hierarchy and will
        register freshly hydrated entities.
    """

    def __init__(
        self, kg: KnowledgeGraph, registry: WorldModelRegistry
    ) -> None:
        self._kg = kg
        self._db_path: Path = kg.db_path
        self._registry = registry

    # ── public hydration methods ──────────────────────────────────────────

    async def hydrate(
        self,
        subject: str,
        *,
        type_hint: Optional[str] = None,
    ) -> Optional[Entity]:
        """Hydrate a single entity named *subject* from its graph triples.

        Parameters
        ----------
        subject:
            The entity name as it appears in the ``triples.subject`` column.
        type_hint:
            Optional explicit type name. When provided the bridge skips the
            ``is_a`` triple lookup and uses this type directly. Useful when
            the caller already knows the type from context.

        Returns
        -------
        An :class:`Entity` registered in ``self._registry``, or ``None`` if
        the subject has no ``is_a`` triple and no *type_hint* was given.
        """
        triples = await self._query_triples(subject)
        if not triples:
            logger.debug("entity_bridge: no triples for %r", subject)
            return None

        # 1. Resolve the type name.
        type_name = type_hint or self._find_type_name(triples)
        if type_name is None:
            logger.warning(
                "entity_bridge: %r has no is_a triple and no type_hint; "
                "cannot hydrate",
                subject,
            )
            return None

        # 2. Make sure the type is registered.
        entity_type = self._registry.get_type(type_name)
        if entity_type is None:
            logger.warning(
                "entity_bridge: type %r (for %r) is not registered; "
                "cannot hydrate",
                type_name,
                subject,
            )
            return None

        # 3. Map predicate→attribute, skipping is_a and known skips.
        attributes: dict[str, Any] = {}
        resolved = entity_type.resolved_attributes()

        for triple in triples:
            predicate = triple["relation"]
            if predicate == "is_a":
                continue  # already consumed for type resolution
            value = triple["object"]

            schema = resolved.get(predicate)
            if schema is None:
                logger.warning(
                    "entity_bridge: predicate %r (subject=%r) is not "
                    "declared on type %r — skipping",
                    predicate,
                    subject,
                    type_name,
                )
                continue

            # 4. Convert string value to the schema's datatype.
            try:
                converted = self._convert(value, schema.datatype)
            except (ValueError, TypeError) as exc:
                logger.warning(
                    "entity_bridge: cannot convert value %r for "
                    "attribute %r on %r: %s — skipping",
                    value,
                    predicate,
                    subject,
                    exc,
                )
                continue

            attributes[predicate] = converted

        # 5. Instantiate (fills defaults for missing optional attributes).
        # If the entity already exists (e.g. from a previous hydrate call),
        # return it as-is — the bridge is a one-shot hydrator, not a sync
        # engine.  A future Phase 62 step may add attribute revision.
        existing = self._registry.get_entity(subject)
        if existing is not None:
            logger.debug(
                "entity_bridge: %r already hydrated — returning cached entity",
                subject,
            )
            return existing

        try:
            entity = self._registry.instantiate(subject, type_name, attributes)
        except SchemaError as exc:
            logger.error(
                "entity_bridge: schema validation failed for %r :: %s: %s",
                subject,
                type_name,
                exc,
            )
            return None

        logger.info(
            "entity_bridge: hydrated %r :: %s (%d attributes)",
            subject,
            type_name,
            len(attributes),
        )
        return entity

    async def hydrate_all(self) -> dict[str, Entity]:
        """Hydrate **every** subject in the graph that has an ``is_a`` triple.

        This is a convenience for bulk hydration — for example after loading
        the seed graph or after a batch of external triple ingestion.

        Returns
        -------
        A dict mapping entity name to :class:`Entity` for every successfully
        hydrated subject. Subjects whose type is unregistered or whose
        attributes fail schema validation are skipped (with a warning logged).
        """
        subjects = await self._query_subjects_with_type()
        results: dict[str, Entity] = {}
        for name in subjects:
            entity = await self.hydrate(name)
            if entity is not None:
                results[name] = entity
        logger.info(
            "entity_bridge: hydrate_all finished — %d / %d entities",
            len(results),
            len(subjects),
        )
        return results

    # ── internal helpers ─────────────────────────────────────────────────

    async def _query_triples(self, subject: str) -> list[dict[str, Any]]:
        """Return all triples whose subject matches *subject*.

        Opens a throwaway connection to avoid holding a long-lived cursor.
        """
        async with aiosqlite.connect(str(self._db_path)) as db:
            from backend.memory._sqlite import apply_async_pragmas

            await apply_async_pragmas(db)
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT subject, relation, object, confidence, source "
                "FROM triples WHERE subject = ?",
                (subject,),
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def _query_subjects_with_type(self) -> list[str]:
        """Return distinct subject names that have an ``is_a`` triple."""
        async with aiosqlite.connect(str(self._db_path)) as db:
            from backend.memory._sqlite import apply_async_pragmas

            await apply_async_pragmas(db)
            cursor = await db.execute(
                "SELECT DISTINCT subject FROM triples WHERE relation = 'is_a'"
            )
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

    @staticmethod
    def _find_type_name(triples: list[dict[str, Any]]) -> Optional[str]:
        """Extract the type name from an ``is_a`` triple.

        Returns the *object* of the first ``(anything, is_a, anything)`` triple,
        or ``None`` if none exists.
        """
        for t in triples:
            if t["relation"] == "is_a":
                return t["object"]
        return None

    @staticmethod
    def _convert(value: Any, target_type: type) -> Any:
        """Convert *value* to *target_type* with best-effort coercion.

        Handles the common type mismatches that arise when triples store
        everything as strings (since SQLite has no native bool/date columns).

        Supported conversions
        ---------------------
        * ``str → bool`` — ``"true"/"1"/"yes"`` → ``True`` (case-insensitive)
        * ``str → int``
        * ``str → float``
        * ``str → list`` — JSON array parse; if that fails, single-item list
        * ``str → dict`` — JSON object parse
        * ``None → any`` — passes through as-is (null from the graph)
        * Already-matching types pass through unchanged.

        Raises ``ValueError`` or ``TypeError`` if conversion is impossible.
        """
        if value is None:
            return None

        target_origin = getattr(target_type, "__origin__", None)
        if target_origin is type(Union):  # noqa: E721 — intentional
            # Optional[X] or Union[A, B] — try each candidate.
            candidates = getattr(target_type, "__args__", ())
            for candidate in candidates:
                if candidate is type(None):
                    continue
                try:
                    return EntityBridge._convert(value, candidate)
                except (ValueError, TypeError):
                    continue
            raise TypeError(f"cannot convert {value!r} to Union {target_type}")

        # Direct isinstance match — pass through.
        if isinstance(value, target_type):
            return value

        # Nullable union: Optional[X] covers None already handled above;
        # if the value is not None, unwrap to the inner type.
        args = getattr(target_type, "__args__", ())
        if args:
            # Optional[X] or Union[A, B, ...]
            non_none = [a for a in args if a is not type(None)]
            if len(non_none) == 1:
                target_type = non_none[0]
            else:
                # Multiple non-None candidates — try each.
                for candidate in non_none:
                    try:
                        return EntityBridge._convert(value, candidate)
                    except (ValueError, TypeError):
                        continue
                raise TypeError(
                    f"cannot convert {value!r} to any of {non_none}"
                )

        # ── scalar conversions ────────────────────────────────────────────
        if target_type is bool:
            return _to_bool(value)

        if target_type is int:
            if isinstance(value, float):
                return int(value)
            return int(value)

        if target_type is float:
            return float(value)

        if target_type is str:
            return str(value)

        # ── compound conversions ─────────────────────────────────────────
        if target_type is list or target_origin is list:
            if isinstance(value, (list, tuple)):
                return list(value)
            # Single value → wrap in list.
            if isinstance(value, str):
                # Try JSON parse first — supports "[a, b, c]".
                value_stripped = value.strip()
                if value_stripped.startswith("[") and value_stripped.endswith("]"):
                    parsed = json.loads(value_stripped)
                    if isinstance(parsed, list):
                        return parsed
                # Comma-separated fallback.
                if "," in value:
                    return [item.strip() for item in value.split(",")]
                return [value]
            return [value]

        if target_type is dict or target_origin is dict:
            if isinstance(value, dict):
                return value
            if isinstance(value, str):
                return json.loads(value)
            raise TypeError(f"cannot convert {type(value).__name__} to dict")

        # Fallback — try direct construction (e.g. ``Path(str)``).
        try:
            return target_type(value)
        except (TypeError, ValueError) as exc:
            raise TypeError(
                f"cannot convert {value!r} to {target_type}: {exc}"
            ) from exc


# ── helper: string-to-bool ────────────────────────────────────────────────────


def _to_bool(value: Any) -> bool:
    """Convert a value to ``bool`` with lenient string parsing.

    Accepts ``True``/``False`` directly, and the strings ``"true"``,
    ``"false"``, ``"1"``, ``"0"``, ``"yes"``, ``"no"`` (case-insensitive).
    Raises ``ValueError`` for anything unrecognised.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lower = value.strip().lower()
        if lower in ("true", "1", "yes"):
            return True
        if lower in ("false", "0", "no"):
            return False
        raise ValueError(f"cannot interpret {value!r} as bool")
    return bool(value)


# ══════════════════════════════════════════════════════════════════════════════
# Self-check
# ══════════════════════════════════════════════════════════════════════════════
def _verify_conversions() -> None:
    """Run quick unit checks on the conversion helper."""
    c = EntityBridge._convert

    # bool
    assert c("true", bool) is True
    assert c("false", bool) is False
    assert c("1", bool) is True
    assert c("yes", bool) is True
    assert c(True, bool) is True

    # int / float
    assert c("42", int) == 42
    assert c("3.14", float) == 3.14
    assert c(7, int) == 7

    # str
    assert c(42, str) == "42"

    # list
    assert c("fbx", list) == ["fbx"]
    assert c('["a","b"]', list) == ["a", "b"]
    assert c("a, b, c", list) == ["a", "b", "c"]

    # None passthrough
    assert c(None, str) is None

    print("entity_bridge: conversion self-check OK")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    _verify_conversions()
