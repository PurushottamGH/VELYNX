"""
VELYNX Phase 62 — Foundational Ontology Loader
================================================

Phase 62's *world model* moves VELYNX from flat (subject, predicate, object)
triples to an object-oriented taxonomy: entities have a type, types inherit
from parent types, and each type declares a schema of typed, constrained
attributes. ``world_model_schema`` proved that system works in-memory against
a hard-coded 3D-software taxonomy; this module makes the ontology
**data-driven** and **composable**.

Responsibility
--------------
Read ``backend/data/world_ontology.json`` and build a populated
:class:`~backend.knowledge.world_model_schema.WorldModelRegistry` from it, then
:func:`absorb` the existing 3D-software taxonomy (built by
:func:`build_3d_software_world`) so the two coexist in ONE runtime registry.
A consumer (the pipeline bootstrap) then installs the combined registry via
:func:`~backend.knowledge.world_model_context.set_registry`.

Data-driven design
------------------
Adding a category (Phase 63's ``ConnectedDevice``, ``Animal``, ...) is editing
``world_ontology.json`` — no Python change. The loader is generic over the
schema's shape; it does not hard-code ``Vehicle`` or ``Electronics``. The
``predicate_map`` block in the JSON is the single source of truth shared with
the :mod:`schema_gatekeeper`, which maps extracted predicates to attribute keys.

Resolution order
----------------
#. Parse JSON.
#. Register types in dependency order: a type's ``parent`` (if named) must be
   registered first, so we topologically sort by parent links. Root types
   (``parent: null``) go first.
#. Resolve ``parent`` / ``facets`` / ``disjoint_with`` name references to live
   ``EntityType`` objects.
#. Instantiate the demo entities declared in the JSON (e.g. Tesla Model 3).
#. ``absorb`` the 3D-software taxonomy (non-destructive merge).

Failure mode
------------
Any malformed JSON, dangling parent reference, or constraint typo raises a
:class:`SchemaError`. The pipeline bootstrap wraps the install in try/except so
a bad ontology degrades to "no world model" rather than crashing startup — the
established VELYNX convention.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from backend.knowledge.world_model_schema import (
    AttributeSchema,
    EntityType,
    SchemaError,
    WorldModelRegistry,
)

logger = logging.getLogger("velynx.ontology_loader")

# Anchor the ontology file to the BACKEND ROOT (the same absolute-path pattern
# the memory + KG stores use) so the loader finds it regardless of the process
# CWD. ``VELYNX_ONTOLOGY_PATH`` overrides for tests / production overrides.
BACKEND_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ONTOLOGY_PATH = Path(
    __import__("os").environ.get(
        "VELYNX_ONTOLOGY_PATH", str(BACKEND_ROOT / "data" / "world_ontology.json")
    )
)

# Map the JSON ``datatype`` strings to Python types used by AttributeSchema.
# Keep this explicit (not ``eval``) so the JSON never executes arbitrary code —
# the ontology is trusted data, but the loader stays data-not-code.
_DATATYPE_MAP = {
    "str": str,
    "string": str,
    "int": int,
    "integer": int,
    "float": float,
    "number": float,
    "bool": bool,
    "boolean": bool,
    "list": list,
    "dict": dict,
    "any": object,
}


def _resolve_datatype(name: str) -> type:
    """Translate a JSON datatype string to a Python type for ``isinstance`` checks."""
    key = (name or "").strip().lower()
    if key not in _DATATYPE_MAP:
        raise SchemaError(
            f"unknown datatype {name!r}; expected one of {sorted(_DATATYPE_MAP)}"
        )
    return _DATATYPE_MAP[key]


def _build_attribute_schema(name: str, spec: dict) -> AttributeSchema:
    """Construct an :class:`AttributeSchema` from one JSON attribute spec dict."""
    datatype = _resolve_datatype(spec.get("datatype", "str"))
    constraints = spec.get("constraints") or {}
    return AttributeSchema(
        name=name,
        datatype=datatype,
        default=spec.get("default", None),
        required=bool(spec.get("required", False)),
        description=spec.get("description", ""),
        constraints=dict(constraints),
    )


def _ordered_types(types_spec: dict) -> list[tuple[str, dict]]:
    """Return ``(name, spec)`` pairs in parent-before-child order.

    Roots (``parent: null``) come first; a type may only be registered once its
    named parent is ahead of it. Raises :class:`SchemaError` on a dangling
    parent reference or an inheritance cycle.
    """
    remaining = dict(types_spec)
    ordered: list[tuple[str, dict]] = []
    placed: set[str] = set()
    # Iterate to a fixpoint. Each pass places any type whose parent is already
    # placed (or null). If a full pass places nothing but types remain, that is
    # a dangling parent or a cycle.
    while remaining:
        progressed = False
        for name in list(remaining):
            spec = remaining[name]
            parent_name = spec.get("parent")
            if parent_name is None or parent_name in placed:
                ordered.append((name, spec))
                placed.add(name)
                del remaining[name]
                progressed = True
        if not progressed:
            raise SchemaError(
                f"ontology type dependency error: cannot resolve parents for "
                f"{sorted(remaining)} (dangling reference or cycle)"
            )
    return ordered


def load_ontology(path: Path = DEFAULT_ONTOLOGY_PATH) -> tuple[WorldModelRegistry, dict]:
    """Build a populated :class:`WorldModelRegistry` from the ontology JSON.

    Returns a 2-tuple ``(registry, raw_json)``. The raw JSON is exposed so the
    :mod:`schema_gatekeeper` can read the same ``predicate_map`` from the single
    source of truth rather than re-loading or duplicating it.
    """
    path = Path(path)
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    types_spec = data.get("types") or {}
    if not types_spec:
        raise SchemaError(f"ontology {path} defines no types")

    reg = WorldModelRegistry()

    # Pass 1: register every type with its parent chain resolved. Facets and
    # disjoint_with are name references resolved AFTER all types exist, in a
    # second pass, so forward references work (a facet may name a type declared
    # later in the JSON).
    pending_facets: dict[str, list[str]] = {}
    pending_disjoint: dict[str, list[str]] = {}
    for name, spec in _ordered_types(types_spec):
        parent_name = spec.get("parent")
        parent = reg.get_type(parent_name) if parent_name else None
        attributes = {
            attr_name: _build_attribute_schema(attr_name, attr_spec)
            for attr_name, attr_spec in (spec.get("attributes") or {}).items()
        }
        etype = EntityType(
            name=name,
            parent=parent,
            attributes=attributes,
            description=spec.get("description", ""),
        )
        reg.register_type(etype)
        pending_facets[name] = list(spec.get("facets") or [])
        pending_disjoint[name] = list(spec.get("disjoint_with") or [])

    # Pass 2: resolve facet + disjoint name references to live EntityType objects.
    for name, facet_names in pending_facets.items():
        etype = reg.get_type(name)
        for fname in facet_names:
            facet_type = reg.get_type(fname)
            if facet_type is None:
                raise SchemaError(
                    f"type {name!r} references unknown facet type {fname!r}"
                )
            etype.facets.append(facet_type)
    for name, disjoint_names in pending_disjoint.items():
        etype = reg.get_type(name)
        # disjoint_with is just a list of names; no live-object resolution needed,
        # but we validate they point at real types so typos surface here, not at
        # gatekeeper time.
        for dn in disjoint_names:
            if reg.get_type(dn) is None:
                raise SchemaError(
                    f"type {name!r} declares disjoint_with unknown type {dn!r}"
                )
            etype.disjoint_with.append(dn)

    # Demo entities declared in the JSON let the ontology ship ready-to-query
    # canonical instances (Tesla Model 3) without Python wiring. The JSON shapes
    # ``instances`` as a name-keyed mapping (with a ``_comment`` key we skip).
    # Two value forms are accepted so the ontology can stay terse where no
    # attributes/facets are needed:
    #   * structured dict: {"type": "Vehicle", "facets": [...], "attributes": {...}}
    #   * bare string shorthand: "Vehicle"  (== {"type": "Vehicle"}, no facets/attrs)
    instances = data.get("instances") or {}
    for inst_name, inst in instances.items():
        if inst_name == "_comment":
            continue
        if isinstance(inst, str):
            # Bare-string shorthand: the value is just the type name.
            type_name = inst
            attrs: dict = {}
            facets: list = []
        elif isinstance(inst, dict):
            type_name = inst.get("type")
            if not type_name:
                raise SchemaError(
                    f"instance {inst_name!r} is missing required 'type' field"
                )
            attrs = inst.get("attributes") or {}
            facets = inst.get("facets") or []
        else:
            raise SchemaError(
                f"instance {inst_name!r} must be a type-name string or a dict, "
                f"got {type(inst).__name__}"
            )
        reg.instantiate(inst_name, type_name, attributes=attrs, facets=facets)

    logger.info(
        "Ontology loaded from %s: %d type(s), %d instance(s)",
        path, len(reg.types()), len(reg.entities()),
    )
    return reg, data


def load_combined_registry(
    path: Path = DEFAULT_ONTOLOGY_PATH,
) -> WorldModelRegistry:
    """Build the runtime registry: physical ontology (JSON) + software taxonomy.

    The JSON-driven physical taxonomy (PhysicalObject, Vehicle, Electronics,
    Person) is loaded first, then the existing 3D-software taxonomy
    (Software → DesktopApplication → ThreeDModelingApp, with Blender + Cinema 4D)
    is :func:`absorb`-merged into the same registry. The two coexist — Phase 62
    grows rather than replaces. This is the entry point the pipeline bootstrap
    calls at startup (see ``backend/app/pipeline.py``).
    """
    reg, _data = load_ontology(path)
    from backend.knowledge.world_model_schema import build_3d_software_world

    reg.absorb(build_3d_software_world())
    return reg


def install_combined_registry(
    path: Path = DEFAULT_ONTOLOGY_PATH,
) -> WorldModelRegistry:
    """Build the combined registry and install it process-wide.

    Mirrors :func:`~backend.knowledge.world_model_context.install_default_registry`
    in shape so the pipeline bootstrap can swap one call for the other. Returns
    the installed registry.
    """
    from backend.knowledge.world_model_context import set_registry

    reg = load_combined_registry(path)
    set_registry(reg)
    return reg


# ── self-check ────────────────────────────────────────────────────────────────
def _self_check() -> None:
    """In-process verification of the loader (``python -m ...ontology_loader``).

    Asserts the behaviours the rest of Phase 62 leans on: the four physical
    types load, facets resolve Tesla's Electronics attributes, the is-a chain
    walks to PhysicalObject, the 3D-software taxonomy still coexists
    (non-destructive), constraints reject bad values, and ``leg_count`` is
    correctly absent from Vehicle (the gatekeeper's structural rejection basis).
    """
    reg = load_combined_registry()

    # Physical taxonomy present.
    for t in ("PhysicalObject", "Vehicle", "Electronics", "Person"):
        assert reg.get_type(t) is not None, f"missing type {t}"

    # 3D-software taxonomy still present (non-destructive coexistence).
    for t in ("Software", "DesktopApplication", "ThreeDModelingApp"):
        assert reg.get_type(t) is not None, f"missing software type {t}"
    blender = reg.get_entity("Blender")
    assert blender is not None and blender.get("license_model") == "GPL"

    # Build the canonical multi-category instance: Tesla is a Vehicle WITH an
    # Electronics facet (instance-level, not type-level).
    if reg.get_entity("Tesla Model 3") is None:
        reg.instantiate(
            "Tesla Model 3", "Vehicle",
            attributes={
                "mobility_type": "wheeled",
                "propulsion": "electric",
                "passenger_capacity": 5,
                "max_speed_kph": 261.0,
                "power_source": "battery",
                "voltage": 400.0,
                "has_screen": True,
                "manufacturer": "Tesla",
            },
            facets=["Electronics"],
        )
    tesla = reg.get_entity("Tesla Model 3")

    # Vehicle-chain attribute resolves.
    assert tesla.get("mobility_type") == "wheeled"
    assert tesla.get("max_speed_kph") == 261.0
    # Inherited from PhysicalObject.
    assert "mass_kg" in tesla._resolved_schema()
    assert tesla.is_a("PhysicalObject")
    # Electronics-FACET attribute resolves (the multi-category proof).
    assert tesla.get("power_source") == "battery"
    assert tesla.get("voltage") == 400.0
    assert tesla.has_facet("Electronics")
    assert not tesla.is_a("Electronics")  # facet is NOT is_a

    # Constraint enforcement (range violation rejected).
    try:
        tesla.set("max_speed_kph", 999999.0)
        raise AssertionError("expected SchemaError for max_speed_kph range")
    except SchemaError:
        pass
    # Enum enforcement.
    try:
        tesla.set("mobility_type", "teleportation")
        raise AssertionError("expected SchemaError for mobility_type enum")
    except SchemaError:
        pass

    # The structural basis for the "5000 legs" rejection: leg_count is NOT on
    # Vehicle (nor its chain/facets). The gatekeeper relies on this.
    assert "leg_count" not in tesla._resolved_schema()

    print(
        "ontology_loader: self-check OK — "
        f"{len(reg.types())} types, {len(reg.entities())} entities, "
        "physical + software taxonomies coexist, facets + constraints behave."
    )


if __name__ == "__main__":
    _self_check()
