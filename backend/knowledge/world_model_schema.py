"""
VELYNX Phase 62 — World Model Scaffold
======================================

Phase 61 gave VELYNX episodic *narrative* memory — the causal story of how a
fact came to exist. Phase 62 evolves the *knowledge* representation itself:
from flat (subject, predicate, object) triples toward an object-oriented
**world model** where entities have a *type*, types inherit from parent types,
and each type declares a schema of typed attributes. The goal is to let VELYNX
reason not just "Blender — created_by — Ton Roosendaal" but "Blender is a
3D Modeling Application, which is Desktop Software, which inherits the
``license_model`` and ``open_source`` attributes from its ancestor types".

This module is the initial scaffold — the type system, attribute schema, and a
registry that validates entities against their declared type. Persistence (a
``world_entities`` SQLite table) and integration with the existing
KnowledgeGraph are deferred to later Phase 62 steps; here we prove the schema
works in-memory against the canonical test case: classifying 3D modeling
software (Blender, Cinema 4D) with an inheritance tree.

Design
------
* :class:`AttributeSchema` — a single typed slot on a type (name, datatype,
  default, required flag, docstring). Datatypes are Python types checked via
  ``isinstance`` so a schema is trivially declarative.
* :class:`EntityType` — a named type with an ordered attribute map and an
  optional single parent (single inheritance is enough for the scaffold and
  keeps attribute resolution a simple MRO walk). Attributes are resolved
  *through* the inheritance chain, with child overrides winning.
* :class:`Entity` — a typed instance. Validates that every required attribute
  (own or inherited) is present and that values match their declared datatype.
  Unknown attributes are rejected so typos surface immediately rather than
  silently becoming free-form graph edges.
* :class:`WorldModelRegistry` — the factory + lookup table. Holds the type
  hierarchy, validates parent references on registration, and can instantiate
  an entity of a registered type from a plain dict (the shape a triple-parsing
  layer will hand it).

Inheritance example (the Phase 62 test case)
--------------------------------------------
    Software                         {license_model, open_source}
      └─ DesktopApplication          {vendor}
           └─ ThreeDModelingApp      {supported_formats}
                ├─ Blender           (instance: open_source=True)
                └─ Cinema 4D         (instance: vendor="Maxon")

Querying ``Blender`` for ``license_model`` resolves up through three ancestors
and returns the inherited default — exactly the behaviour the later retrieval
layer will rely on.

Future Phase 62 work
--------------------
* Persist ``EntityType`` / ``Entity`` rows to a ``world_entities`` SQLite table.
* Bridge to the existing KnowledgeGraph so a triple ``(Blender, is_a, Software)``
  can hydrate into a typed :class:`Entity` on demand.
* Multi-valued + computed attributes, and belief-revision-aware attribute writes
  (so re-teaching a conflicting attribute value flows through the Phase 61
  contradiction path).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Optional, Union

logger = logging.getLogger("velynx.world_model")

# Datatype accepted by an :class:`AttributeSchema`. Any Python type (including
# ``Union`` / ``Optional`` constructs from typing) is permitted; validation uses
# ``isinstance``, with a small allowance for ``Optional[X]`` and ``Union``.
Datatype = Any


@dataclass
class AttributeSchema:
    """A single typed slot declared on an :class:`EntityType`.

    Attributes
    ----------
    name
        The attribute key as it appears on an :class:`Entity` (snake_case).
    datatype
        The expected Python type of the value. ``str``, ``int``, ``float``,
        ``bool``, or any user-defined type. ``Optional[X]`` / ``Union`` forms
        are accepted; the validator unwraps ``None``-permitting unions.
    default
        Value used when an entity omits the attribute and ``required`` is
        False. May be ``None`` (the common case).
    required
        If True, an entity of this type MUST supply a non-None value or
        instantiation raises :class:`SchemaError`.
    description
        Human-readable docstring, surfaced later by the introspection / voice
        layer when VELYNX explains *why* it believes an attribute holds.
    """

    name: str
    datatype: Datatype
    default: Any = None
    required: bool = False
    description: str = ""

    def validate(self, value: Any) -> None:
        """Raise :class:`SchemaError` if *value* is not acceptable for this slot.

        ``None`` is allowed only when the schema is not required (so an
        unspecified optional slot validates against its default).
        """
        if value is None:
            if self.required:
                raise SchemaError(
                    f"attribute {self.name!r} is required and cannot be None"
                )
            return
        if not _instance_check(value, self.datatype):
            raise SchemaError(
                f"attribute {self.name!r} expected {self._type_name()}, "
                f"got {type(value).__name__} ({value!r})"
            )

    def _type_name(self) -> str:
        return getattr(self.datatype, "__name__", str(self.datatype))


def _instance_check(value: Any, datatype: Datatype) -> bool:
    """``isinstance`` that tolerates ``Optional[X]`` / ``Union[A, B]`` forms.

    ``typing.Union`` / ``Optional`` carry their candidate types in
    ``__args__``; we accept the value if it matches any candidate. Anything
    else falls through to a plain ``isinstance``.
    """
    args = getattr(datatype, "__args__", None)
    origin = getattr(datatype, "__origin__", None)
    if origin is Union or args is not None:
        candidates = args or ()
        # Optional[X] -> (X, NoneType); any non-None value must match X.
        return any(_instance_check(value, c) for c in candidates if c is not type(None))
    try:
        return isinstance(value, datatype)
    except TypeError:
        # Non-class datatype (e.g. a ParameterizedGeneric) — be permissive.
        return True


class SchemaError(ValueError):
    """Raised when an entity violates its type's attribute schema."""


@dataclass
class EntityType:
    """A named type in the world model, with an inheritance chain.

    Single inheritance (one optional ``parent``) keeps attribute resolution a
    linear walk and is sufficient for the Phase 62 scaffold. Attributes
    declared on the type itself are *overrides* or *additions* relative to the
    inherited set; the full resolved schema is computed by walking parents to
    the root.
    """

    name: str
    parent: Optional["EntityType"] = None
    attributes: dict[str, AttributeSchema] = field(default_factory=dict)
    description: str = ""

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise SchemaError("EntityType.name must be a non-empty string")
        # Detect inheritance cycles defensively — a self- or ancestor-loop would
        # make resolved_attributes() recurse forever otherwise.
        seen: set[str] = set()
        node: Optional[EntityType] = self
        while node is not None:
            if node.name in seen:
                raise SchemaError(f"inheritance cycle detected at type {node.name!r}")
            seen.add(node.name)
            node = node.parent

    def resolved_attributes(self) -> dict[str, AttributeSchema]:
        """Full attribute schema, walking the inheritance chain root-first.

        Child attributes override parents of the same name (last-write-wins as
        we walk from root to self), so a subtype can narrow a datatype, flip
        ``required``, or supply a different default.
        """
        chain: list["EntityType"] = []
        node: Optional[EntityType] = self
        while node is not None:
            chain.append(node)
            node = node.parent
        chain.reverse()  # root-first so children override
        merged: dict[str, AttributeSchema] = {}
        for t in chain:
            merged.update(t.attributes)
        return merged

    def is_a(self, ancestor_name: str) -> bool:
        """True if this type (or any ancestor) is named *ancestor_name*."""
        node: Optional[EntityType] = self
        while node is not None:
            if node.name == ancestor_name:
                return True
            node = node.parent
        return False

    def ancestors(self) -> list[str]:
        """Names of this type's ancestors, immediate-parent-first (excluding self)."""
        out: list[str] = []
        node: Optional[EntityType] = self.parent
        while node is not None:
            out.append(node.name)
            node = node.parent
        return out


@dataclass
class Entity:
    """A typed instance in the world model.

    Constructed via :meth:`WorldModelRegistry.instantiate` (which validates the
    type exists and the values match its schema). Direct construction is
    allowed but skips parent-link validation — prefer the registry.
    """

    name: str
    type: EntityType
    attributes: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise SchemaError("Entity.name must be a non-empty string")
        # Fill defaults for declared attributes the caller omitted, then
        # validate every supplied + defaulted value against the resolved schema.
        schema = self.type.resolved_attributes()
        for attr_name, attr_schema in schema.items():
            self.attributes.setdefault(attr_name, attr_schema.default)
        # Reject attributes the schema does not know about — typos must not
        # silently become free-form edges (that is the KnowledgeGraph's job).
        unknown = set(self.attributes) - set(schema)
        if unknown:
            raise SchemaError(
                f"entity {self.name!r} of type {self.type.name!r} has unknown "
                f"attribute(s): {sorted(unknown)}"
            )
        for attr_name, value in self.attributes.items():
            schema[attr_name].validate(value)

    def get(self, attr_name: str, default: Any = None) -> Any:
        """Read an attribute, falling back to *default* if it is absent/None.

        Resolves inherited attributes transparently because
        ``__post_init__`` already filled inherited defaults.
        """
        value = self.attributes.get(attr_name, default)
        return value if value is not None else default

    def set(self, attr_name: str, value: Any) -> None:
        """Write an attribute, re-validating against the schema.

        This is the single mutation point; a later Phase 62 step will route
        re-teaches (belief revision) through here so contradictions are flagged.
        """
        schema = self.type.resolved_attributes()
        if attr_name not in schema:
            raise SchemaError(
                f"attribute {attr_name!r} not declared on type {self.type.name!r}"
            )
        schema[attr_name].validate(value)
        self.attributes[attr_name] = value

    def is_a(self, type_name: str) -> bool:
        """Delegate to the type's inheritance check."""
        return self.type.is_a(type_name)

    def to_dict(self) -> dict:
        """Serializable view (the shape a persistence layer will store)."""
        return {
            "name": self.name,
            "type": self.type.name,
            "ancestor_types": self.type.ancestors(),
            "attributes": dict(self.attributes),
        }


class WorldModelRegistry:
    """Factory + lookup table for the world model's type hierarchy.

    Holds the :class:`EntityType` objects, validates parent links at
    registration time, and instantiates :class:`Entity` objects from a plain
    dict — the shape a triple-parsing bridge will hand it once Phase 62 wires
    into the existing KnowledgeGraph.
    """

    def __init__(self) -> None:
        self._types: dict[str, EntityType] = {}
        self._entities: dict[str, Entity] = {}

    # ── types ────────────────────────────────────────────────────────────────
    def register_type(self, entity_type: EntityType) -> EntityType:
        """Register a type. Parent (if any) must already be registered."""
        if entity_type.name in self._types:
            raise SchemaError(f"type {entity_type.name!r} already registered")
        if entity_type.parent is not None and entity_type.parent.name not in self._types:
            raise SchemaError(
                f"parent type {entity_type.parent.name!r} of "
                f"{entity_type.name!r} is not registered"
            )
        self._types[entity_type.name] = entity_type
        logger.info("WorldModel: registered type %s", entity_type.name)
        return entity_type

    def get_type(self, name: str) -> Optional[EntityType]:
        return self._types.get(name)

    def types(self) -> list[str]:
        return sorted(self._types)

    # ── entities ─────────────────────────────────────────────────────────────
    def instantiate(self, name: str, type_name: str,
                    attributes: Optional[dict] = None) -> Entity:
        """Create and register an :class:`Entity` of a registered type.

        Validates the type exists and the attribute dict conforms to the type's
        resolved (inherited) schema. Returns the new entity and indexes it by
        name (unique within the registry).
        """
        entity_type = self._types.get(type_name)
        if entity_type is None:
            raise SchemaError(f"unknown entity type {type_name!r}")
        if name in self._entities:
            raise SchemaError(f"entity {name!r} already exists")
        entity = Entity(name=name, type=entity_type, attributes=dict(attributes or {}))
        self._entities[name] = entity
        logger.info("WorldModel: instantiated %s :: %s", name, type_name)
        return entity

    def get_entity(self, name: str) -> Optional[Entity]:
        return self._entities.get(name)

    def entities(self) -> list[str]:
        return sorted(self._entities)

    # ── introspection ────────────────────────────────────────────────────────
    def describe(self, name: str) -> Optional[dict]:
        """Return a human-readable description dict for an entity or type.

        Used by the future voice/introspection layer when VELYNX explains what
        it knows about a thing. Returns None if *name* matches neither.
        """
        entity = self._entities.get(name)
        if entity is not None:
            d = entity.to_dict()
            d["kind"] = "entity"
            return d
        et = self._types.get(name)
        if et is not None:
            return {
                "kind": "type",
                "name": et.name,
                "parent": et.parent.name if et.parent else None,
                "attributes": {
                    n: {
                        "datatype": s._type_name(),
                        "required": s.required,
                        "default": s.default,
                        "description": s.description,
                    }
                    for n, s in et.resolved_attributes().items()
                },
            }
        return None


# ══════════════════════════════════════════════════════════════════════════════
# Phase 62 test case — 3D modeling software taxonomy
# ══════════════════════════════════════════════════════════════════════════════
def build_3d_software_world() -> WorldModelRegistry:
    """Build the canonical Phase 62 registry: a 3D-modeling software taxonomy.

    Proves the schema handles single inheritance, inherited attributes,
    required-vs-optional slots, and two concrete instances (Blender, Cinema 4D)
    of the same leaf type that differ in their attribute values.

    Hierarchy::

        Software                 {license_model:str, open_source:bool}
          DesktopApplication     {vendor:str (required)}
            ThreeDModelingApp    {supported_formats:list}

    Returns a populated :class:`WorldModelRegistry`.
    """
    reg = WorldModelRegistry()

    # Root type: broadest category, carries attributes every descendant inherits.
    reg.register_type(EntityType(
        name="Software",
        attributes={
            "license_model": AttributeSchema(
                name="license_model", datatype=str, default="proprietary",
                description="How the software is licensed and distributed.",
            ),
            "open_source": AttributeSchema(
                name="open_source", datatype=bool, default=False,
                description="Whether the source code is publicly available.",
            ),
        },
        description="Any computer program or library.",
    ))

    # Mid-level: narrows Software to applications that run on a user's machine.
    reg.register_type(EntityType(
        name="DesktopApplication",
        parent=reg.get_type("Software"),
        attributes={
            "vendor": AttributeSchema(
                name="vendor", datatype=str, required=True,
                description="The company or organisation that publishes it.",
            ),
        },
        description="Software installed and run on a local workstation.",
    ))

    # Leaf type: the category both test instances belong to.
    reg.register_type(EntityType(
        name="ThreeDModelingApp",
        parent=reg.get_type("DesktopApplication"),
        attributes={
            "supported_formats": AttributeSchema(
                name="supported_formats", datatype=list,
                default=list,
                description="File formats the application can import/export.",
            ),
        },
        description="Application for creating and editing 3D geometry.",
    ))

    # Two concrete instances of the leaf type.
    reg.instantiate(
        "Blender", "ThreeDModelingApp",
        attributes={
            "vendor": "Blender Foundation",
            "open_source": True,
            "license_model": "GPL",
            "supported_formats": ["blend", "fbx", "obj", "glb"],
        },
    )
    reg.instantiate(
        "Cinema 4D", "ThreeDModelingApp",
        attributes={
            "vendor": "Maxon",
            "open_source": False,           # inherited default, overridden
            "license_model": "proprietary",
            "supported_formats": ["c4d", "fbx", "obj", "abc"],
        },
    )
    return reg


# ── self-check ────────────────────────────────────────────────────────────────
def _self_check() -> None:
    """Lightweight in-process verification of the scaffold.

    Run via ``python -m backend.knowledge.world_model_schema``. Asserts the
    behaviors the later retrieval layer will lean on: inheritance resolves
    inherited attributes, type checks pass down the chain, and validation
    rejects bad values and unknown attributes.
    """
    reg = build_3d_software_world()

    blender = reg.get_entity("Blender")
    assert blender is not None
    # Inherited attribute resolved through 3 ancestors.
    assert blender.get("license_model") == "GPL"
    assert blender.get("open_source") is True
    # Required attribute (declared on DesktopApplication) is present.
    assert blender.get("vendor") == "Blender Foundation"
    # Type predicate walks the chain.
    assert blender.is_a("Software")
    assert blender.is_a("DesktopApplication")
    assert blender.is_a("ThreeDModelingApp")
    assert not blender.is_a("Nonexistent")

    cinema = reg.get_entity("Cinema 4D")
    assert cinema.get("vendor") == "Maxon"
    assert cinema.get("open_source") is False

    # Validation: wrong datatype is rejected.
    try:
        blender.set("open_source", "yes")  # str, not bool
        raise AssertionError("expected SchemaError for bad datatype")
    except SchemaError:
        pass

    # Validation: unknown attribute is rejected (no silent free-form edges).
    try:
        reg.instantiate("Rogue", "ThreeDModelingApp",
                        attributes={"colour": "red"})
        raise AssertionError("expected SchemaError for unknown attribute")
    except SchemaError:
        pass

    # Validation: missing required attribute is rejected.
    try:
        reg.instantiate("NoVendor", "ThreeDModelingApp", attributes={})
        raise AssertionError("expected SchemaError for missing required attr")
    except SchemaError:
        pass

    print("world_model_schema: self-check OK — taxonomy built, inheritance + "
          "validation behave as designed.")


if __name__ == "__main__":
    _self_check()
