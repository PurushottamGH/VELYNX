# Ontology

The ontology subsystem lives entirely in the `backend/` application layer.
There is **no ontology in `core/`**. This document describes only
repository-supported behaviour and states the canonical status explicitly.

## 1. Two different "ontologies" - do not conflate them

VELYNX's history contains two distinct things both called an ontology. They
must not be confused:

1. **The hand-authored "Soul Graph" ontology** (Program B) - 32 authored
   concepts with edge labels. PROGRAM_D_CANONICAL.md Section 5 marks this
   `[REJECTED]` as designer artifacts, not evidence. It "must not appear
   in live code" except as an archive/delete target. Do not build, import,
   or reference it as a live mechanism.
2. **The Phase 62 data-driven world-model ontology** - `backend/data/
   world_ontology.json`, a 17-type object-oriented taxonomy (physical
   objects + 3D-software) used by the Program A application for entity
   resolution, schema validation, and TEACH. This is live engineering in
   `backend/`. It is **not** part of the canonical five-primitive science
   in `core/` (see `prediction.md`), and none of {EXP-0, EXP-1, EXP-2, E0}
   require it (canon Section 1, rule 2).

The rest of this document covers (2) only.

## 2. Where it lives

- `backend/data/world_ontology.json` - the data file. 17-type baseline
  (Phase 62). Includes a `predicate_map` block and demo entities.
- `backend/knowledge/ontology_loader.py` - builds a
  `WorldModelRegistry` from the JSON and `absorb`s the 3D-software
  taxonomy into one runtime registry.
- `backend/knowledge/world_model_schema.py` - `Entity`, `EntityType`,
  `AttributeSchema`, `WorldModelRegistry`, `SchemaError`.
- `backend/knowledge/world_model_context.py` - installs/holds the runtime
  registry (`set_registry`); ontology-derived edges carry high confidence.
- `backend/knowledge/schema_gatekeeper.py` - the four-stage validation
  layer that intercepts TEACH triples before the Knowledge Graph.
- `backend/knowledge/fact_extractor.py` - extracts `(subject, predicate,
  object)` triples and persists them; calls the gatekeeper.
- `backend/tests/test_expanded_ontology.py`,
  `backend/tests/test_inheritance_inference.py` - structural-integrity
  tests for the 17-type baseline.

## 3. Responsibilities (repository-supported)

- Move VELYNX from flat `(subject, predicate, object)` triples to an
  object-oriented taxonomy: entities have a type, types inherit from parent
  types, each type declares a schema of typed, constrained attributes.
- Provide a single runtime registry combining the JSON physical ontology
  and the 3D-software taxonomy.
- Validate TEACH triples against the schema before they reach the Knowledge
  Graph, rejecting structurally impossible assertions and teaching the
  user the ontology on rejection.
- Stay data-driven: adding a category is an edit to `world_ontology.json`,
  not a Python change.

## 4. Loader behaviour

`ontology_loader.py`:

- `DEFAULT_ONTOLOGY_PATH` is `VELYNX_ONTOLOGY_PATH` env or
  `backend/data/world_ontology.json` (anchored to BACKEND_ROOT, CWD-safe).
- `load_ontology(path) -> (WorldModelRegistry, dict)`.
- `install_combined_registry()` - runtime registry = physical ontology
  (JSON) + software taxonomy.
- Resolution order: parse JSON -> register types in dependency order
  (topological sort by parent; roots first) -> resolve
  `parent`/`facets`/`disjoint_with` references -> instantiate demo
  entities -> `absorb` the 3D-software taxonomy (non-destructive merge).
- Datatype strings map to Python types via an explicit table, **not**
  `eval`, so the JSON never executes code (data-not-code).
- Failure mode: malformed JSON, dangling parent, or constraint typo raises
  `SchemaError`. The pipeline bootstrap wraps the install in `try/except`
  so a bad ontology degrades to "no world model" rather than crashing
  startup.
- Logger: `velynx.ontology_loader`. A `python -m` self-check is provided.

## 5. Gatekeeper behaviour (the four-stage classifier)

`schema_gatekeeper.py` validates each extracted triple; the first
non-ACCEPT verdict wins:

1. **Entity resolution** - does `subject` name a registered, typed Entity
   (case-insensitive, via the world-model name index)? If not, the subject
   is untyped -> **ACCEPT** (open-world).
2. **Predicate mapping** - map `relation` to a canonical attribute key via
   the JSON `predicate_map` (single source of truth shared with the
   loader). If the predicate is NOT in the map, it is free-form ->
   **ACCEPT** (open-world).
3. **Schema membership** - is the mapped attribute declared on the
   subject's resolved schema (type's parent chain + facets)? If NOT ->
   **REJECT** `UNKNOWN_ATTRIBUTE`. (This is the structural "5000 legs"
   kill: `has legs` maps to `leg_count`, but `leg_count` is not on
   Vehicle/Electronics/PhysicalObject.)
4. **Value validation** - coerce `object` to the attribute's datatype and
   enforce `enum`/`min`/`max`/`pattern` constraints. Failure -> **REJECT**
   `TYPE_MISMATCH` or `CONSTRAINT_VIOLATION`; otherwise **ACCEPT**.

Public API: `validate_triples(triples) -> (accepted, rejections)`.
Deterministic and never raises - a malformed triple is treated as
free-form and accepted. Every `Rejection` carries a reason code, a
human-readable message, and the entity's VALID attributes so the TEACH
response can teach the ontology.

## 6. Invariants

- **Data-driven.** The `predicate_map` and type schema live in
  `world_ontology.json`. Adding a predicate synonym or a category is a JSON
  edit, not a code edit. The loader is generic over the schema shape and
  does not hard-code `Vehicle`/`Electronics`.
- **Open-world safe.** The only rejections are a recognised predicate
  hitting a typed entity it does not belong to, or a bad value for a slot
  that does. Untyped subjects, unknown predicates, and free-form
  descriptions flow to the triples table unchanged.
- **Single source of truth.** The `predicate_map` is loaded lazily ONCE
  from the ontology JSON and shared between the loader and the gatekeeper.
- **Graceful degradation.** A bad or missing ontology degrades to "no
  world model" rather than crashing startup.
- **Data-not-code.** The JSON never executes; datatype mapping is
  explicit.

## 7. Extension points

- Add a category: edit `world_ontology.json` (a new type with `parent`,
  `facets`, attributes, and `predicate_map` synonyms). No Python change.
- Add a predicate synonym: edit the `predicate_map` block in the JSON.
- Swap the ontology for tests: set `VELYNX_ONTOLOGY_PATH`, or call the
  gatekeeper's test hook to force a re-read of the `predicate_map`.
- Do NOT add a hand-authored soul-graph ontology. That construct is
  `[REJECTED]` (Section 1).

## 8. What is not present

- There is no ontology engine in `core/`. The canonical science has no
  ontology primitive.
- The 17-type world ontology is not validated by any experiment in
  {EXP-0, EXP-1, EXP-2, E0}. It supports the Program A product only.
- There is no learning-of-the-ontology mechanism in `core/`. Ontology
  growth in `backend/` (e.g. `concept_birth.py` exports birthed concepts via
  `update_ontology()`) is an application feature, not a canonical
  scientific claim, and must not be sold as "emergence" (canon Section 1).