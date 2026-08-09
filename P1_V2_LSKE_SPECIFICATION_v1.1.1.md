# P1-v2 Living Scientific Knowledge Engine — Engineering Specification

- **Artifact:** `P1_V2_LSKE_SPECIFICATION_v1.1.1.md`
- **Version:** 1.1.1
- **Release kind:** **Pure blocker elimination.** No redesign, no new capability, no scope change, no
  new architectural module, no new collection, no new phase, no new primitive, no weakening of
  determinism. Five Phase-1 implementation blockers (`BLK-P1-01`…`BLK-P1-05`) are given a single
  authoritative resolution each (`RB-01`…`RB-05`); a sixth defect found by this document's own
  verification pass is closed by `RB-06`.
  Every affected section is reissued so that only that resolution remains.
- **Supersedes:** `P1_V2_LSKE_SPECIFICATION_v1.1.0.md` v1.1.0 — retained, readable, non-current
- **Carries forward unchanged:** Parts 0–8 of v1.1.0 in full, except §1.2 row 1's prefix cell (RB-06),
  the relation envelope reissued in §0X.4 (RB-02) and the one R4-4 clause reissued in §0X.7 cl. 5.
  Part 0R (`RC-0`…`RC-12`) stands in force in its entirety.
- **Status:** Proposed / Unregistered
- **Date:** 2026-07-30
- **Subsystem:** Living Scientific Knowledge Engine (LSKE)
- **Inherits without amendment:** `P1_V2_CONSTITUTION_LOCK_v1.0.md` v1.0.0; `ros.authority`;
  `ros.admissibility`; `ros.protocol`; `ros.events`; `ros.propagation`;
  `P1_OBSERVATORY_SCIENTIFIC_SPECIFICATION_v1.0.md`; the M1/P1-v2 runtime
- **Closes:** `P1_V2_LSKE_PHASE1_BLOCKER_REPORT.md` `BLK-P1-01`…`BLK-P1-05`
- **Authority source:** none

**Reading rule.** This document is an amendment. Where a section number appears below, the text under
it **replaces** the corresponding text of v1.1.0 in full. Every section of v1.1.0 not named here is
unchanged and remains in force. No sentence of v1.1.0 is amended silently.

---

# PART 0X — Blocker Elimination Record (v1.1.1)

## 0X.1 Standing of this part

`P1_V2_LSKE_PHASE1_BLOCKER_REPORT.md` recorded five implementation decision points that a
field-by-field Phase-1 construction pass could not resolve without choosing. R9-0 forbids the
implementer from choosing. This part records the single authoritative resolution adopted for each, and
one further resolution (`RB-06`) for a defect this document's own verification pass exposed.
The rulings are numbered `RB-01`…`RB-06`.

**Rule RB-0.** An `RB` ruling has the same standing as the `R`-series rule or `RC` ruling it
completes. Every section affected by a ruling is reissued in this document so that only the ruled
text exists. If a reader finds surviving v1.1.0 text that contradicts an `RB` ruling, the ruling
governs and the surviving sentence is a defect to be reported under R9-0, not a second reading.

**Rule RB-0.1.** No ruling in this part creates an authority class, a write target, a human-only
decision, a primitive, a collection, a relation type, a confidence dimension, a lifecycle state, a
write operation, a transaction phase, a gate, a KPI, a package file, a test file, a phase, or a
schema field that v1.1.0 did not already require. Each ruling either (a) selects one of two readings
already present in v1.1.0, (b) completes a definition v1.1.0 required but left partial, (c) names
the single owner of a component v1.1.0 required but left unowned, or (d) corrects one value that no
frozen pattern of v1.1.0 could carry, in the direction that leaves the pre-existing shipped module
untouched. The architecture of v1.1.0 is identical after this release.

**Rule RB-0.2 (determinism is not relaxed).** Every resolution below is total, ordered and
computable without a clock, a random source, a network call, or an environment lookup. Where a
resolution introduces a rule with cases, the cases are evaluated in the stated order and the order is
part of the rule.

## 0X.2 RB-01 — Draft 2020-12 composition (closes `BLK-P1-01`)

**Conflicting rules.**

> §9.2.1: "`additionalProperties: false` at the top level and inside every nested object; collection
> schemas extend by `allOf`."

> §9.2.2: "Twenty files … each `allOf: [record.schema.json, {…}]`" introducing collection-specific
> top-level fields.

**The defect.** Under JSON Schema Draft 2020-12, `additionalProperties` is not annotation-aware
across `allOf` branches: a base subschema carrying `additionalProperties: false` rejects every
property it does not itself declare, including properties declared by a sibling `allOf` branch. The
two sections are therefore jointly unsatisfiable, and no collection record can validate.

**Ruling RB-01.** Exactly one composition mechanism, one inheritance strategy and one closed-world
strategy exist, and they are these:

1. **Composition mechanism — `allOf` + `$ref`, closed by `unevaluatedProperties`.** A collection
   schema is a schema object containing `allOf: [{"$ref": "record.schema.json"}, {"$ref":
   "#/$defs/collection"}]` and, as a **sibling** of that `allOf`, `unevaluatedProperties: false`.
   `unevaluatedProperties` is annotation-aware and sees the `properties` annotations produced by both
   branches, so the record envelope and the collection fields are both evaluated before closure is
   applied. This is the only composition mechanism in the LSKE.
2. **`record.schema.json` carries no top-level closure keyword.** It declares `$schema`, `$id`,
   `title`, `type: object`, `properties` for the sixteen envelope keys, `required` for all sixteen,
   `$defs` for the shared scalar types and nested objects of §9.2.4, and **neither
   `additionalProperties` nor `unevaluatedProperties` at its top level.** It is a composable
   fragment, not a standalone validation target. The v1.1.0 sentence placing
   `additionalProperties: false` at the universal record schema's top level is **deleted**; the same
   closure is now asserted once, by the collection schema, over the union of both branches — which is
   strictly stronger, because it also closes properties a collection branch failed to declare.
3. **Inheritance strategy — single-level, single-parent, depth exactly two.** Every collection schema
   references `record.schema.json` exactly once. No collection schema references another collection
   schema. There is no `$dynamicRef`, no `$dynamicAnchor`, no `anyOf`/`oneOf` at the composing level,
   no schema-level `if/then` at the composing level, and no chain of length three. A reader can
   therefore know a record's full field set by reading exactly two schema objects.
4. **Closed-world strategy — one rule, three mechanical forms.** Every object in every LSKE schema is
   closed. The form is determined by the object's kind, and the kind is a property of the object, not
   a choice:
   - **Composed object** (exactly 20: the collection schema top levels) — `unevaluatedProperties:
     false` as a sibling of the composing `allOf`, per cl. 1.
   - **Fixed-key object** (every other object, including `record.schema.json`'s nested objects and
     the top levels of `relation.schema.json` and `obs2.schema.json`) — `properties` + `required` +
     `additionalProperties: false`.
   - **Map-keyed object** (exactly two: `datasets.splits` and `obs2.overlays`) — `propertyNames`
     constraining the key form, `additionalProperties` set to the single closed value schema, and
     `minProperties` (with `maxProperties` where the count is fixed). A map
     whose keys are data cannot be closed by enumeration; constraining the key form and closing the
     value is the same closure expressed over the only two things a map has.
   `confidence.dimensions` is **not** a map-keyed object: its ten keys are frozen by §1.1 Block F, so
   it is a fixed-key object with ten declared properties, ten required, and
   `additionalProperties: false`.
5. **Conditional fields never introduce properties.** A conditional requirement is expressed as
   `allOf: [{"if": …, "then": {"required": [...]}}]` **inside** the `#/$defs/collection` subschema.
   Every field a conditional can require is also declared in that subschema's `properties`. A field
   introduced only under a `then` branch would not be annotated as evaluated when the condition is
   false, and `unevaluatedProperties: false` would then reject a legal record. This constraint is what
   makes cl. 1 sound, and it is checked by test 1.
6. **One validation pass, one entry point.** A record is validated **once**, against its collection
   schema, which applies the envelope by `$ref`. The v1.1.0 sentence "every record in every collection
   validates against this before its collection-specific schema is applied" is **deleted**: there is
   no separate envelope pass, because a two-pass contract has two failure reports for one record and
   no rule saying which is authoritative. The single entry point is
   `v2.lske.schema.validate(payload, schema_name)` (§9.13.3).
7. **Reference resolution is offline and total.** `$id` values are absolute under the base URI
   `https://p1.local/schemas/lske/`; `$ref` values between LSKE schemas are **relative** file names
   resolved against that base (`"record.schema.json"`, `"record.schema.json#/$defs/scope"`). All
   twenty-three schemas are registered in one in-memory registry before any validation. No `$ref`
   ever resolves over the network — R9-1 forbids a network client, and a schema that needed one could
   not be validated in CI.
8. **Serialization of the generated files is fixed.** `schemas/lske/*.json` are written as
   `json.dumps(schema, ensure_ascii=False, indent=2, sort_keys=True) + "\n"`, encoded UTF-8 with LF
   line endings. R9-2's byte-match test is only decidable against a fixed serialization, and this is
   it.

**Why this preserves the architecture.** The mechanism v1.1.0 named — `allOf` composition of a
universal envelope with a collection extension — is unchanged; only the keyword that closes the
result moves from the base (where it cannot work) to the composing schema (where it does). Closure
remains total, the envelope remains the single source of the eight blocks, and no collection field is
predeclared in the envelope, so the universal-envelope boundary is intact.

**Sections reissued.** §9.2.0 (new, the composition contract), §9.2.1 (opening paragraph and closure
sentence), §9.2.2 (opening paragraph and typing addendum), §9.2.3, §9.2.4 (new), §9.6 rows 1–2,
Appendix A.4.

## 0X.3 RB-02 — The relation envelope (closes `BLK-P1-02`)

**Conflicting rules.**

> §2.2: `direction` conditional; `retracted_by` required as `string|null`; ten fields; no lifecycle
> field.

> §9.2.3: `direction` required; `retracted_by` optional; two further optional fields
> (`independence_group`, `post_hoc`) absent from §2.2.

> R2-4 defines five edge lifecycle transitions, and neither section provides a field that carries
> edge state.

**Ruling RB-02.** §2.2 is the single normative relation envelope, reissued in §0X.4 with types added,
and §9.2.3 is reissued as its typed restatement carrying no name of its own. Six clauses, no seventh
reading:

1. **The envelope has exactly ten fields, and all ten keys are required to be present.** `from`,
   `to`, `type`, `direction`, `semantic_note`, `established_by`, `established_at`,
   `record_version_at`, `retracted_by`, `confidence_basis`. There is no optional key in the relation
   envelope. This is the same discipline the record envelope already uses (§1.1: `escalated_from` is
   "present always; `null` unless…"), and it is chosen for the same reason: an absent key and a null
   key are two encodings of one state, and a checker that must accept both cannot report either.
2. **Exactly two fields are nullable, and each has a stated null condition.** `direction` is non-null
   with a value from `ros.model.EVIDENCE_DIRECTIONS` when `type` is one of the four evidential types
   of §2.3 Class 1 (`supports`, `refutes`, `contradicts`, `validated_by`), and is `null` for the
   eleven non-evidential types. `retracted_by` is a `decisions` identifier once the edge is retracted
   and `null` before. This reconciles both readings without deleting either: §9.2.3's "required" is
   the key, §2.2's "conditional" is the value.
3. **`independence_group` and `post_hoc` are deleted from the relation envelope.**
   `independence_group` exists exactly once in the store, on the `evidence` record (§1.4.10); a second
   copy on the edge would be a stored duplicate at a second address, and R1-17's
   shared-evidence check would have two sources that can disagree. `post_hoc` is **derived**: R2-12
   already defines it as a comparison of the edge's `established_at` against the predicting run's
   start, and already says the edge "is marked `post_hoc` in every projection" — a projection marker
   is computed under R0-4, never stored.
4. **Edge lifecycle state is derived, never stored.** No lifecycle field is added. `edge_state` is
   computed from the edge and its two endpoints by the following total, ordered rule, and its value is
   always one of the five Article L-2 states R2-4 admits:

   | Order | Condition | `edge_state` |
   |---|---|---|
   | 1 | `retracted_by` is non-null | `DELETED` |
   | 2 | either endpoint's `lifecycle.state` is `CANDIDATE` | `CANDIDATE` |
   | 3 | either endpoint's `lifecycle.state` is `TOMBSTONED` or `DORMANT` | `DORMANT` |
   | 4 | otherwise | `ACTIVE` |

   The rule is evaluated top to bottom and stops at the first match. It yields exactly R2-4's state
   set and it can only move along R2-4's transitions, because each recorded cause is monotone: a
   record does not leave `TOMBSTONED` except to `ACTIVE` or `DELETED`, and `retracted_by` is set once
   and never unset. `TOMBSTONED` never appears, which is R2-4's own exclusion. Clause 3 is R3-3 cl. 5
   ("its edges become `DORMANT`, not deleted") made mechanical; clause 2 is RC-11 applied to edges, so
   an edge into an unadmitted candidate is as invisible as the candidate. An edge touching a `DELETED`
   record is a prohibited shape (§2.5 cl. 1) reported by `_check_relations`; the derivation therefore
   never needs a case for it, and rule 1 concerns the *edge's* retraction, not an endpoint's state.
5. **Retraction semantics are stated once.** An edge is retracted by setting `retracted_by` to the
   identifier of a `decisions` record. Retraction never removes the edge from the store, never
   rewrites `semantic_note`, `established_by` or `established_at`, and is never unset — a re-asserted
   relation is a new assertion with a new `established_by`, not a resurrection. Retracted edges are
   excluded from every default query and surface (R5-14, R7-18) and contribute to no confidence
   dimension. R4-4's phrase "`e.retracted_by is null`" refers to **the `supports`/`refutes` edge
   connecting `e` to the claim**, not to a field on the `evidence` record: the `evidence` collection
   has no `retracted_by` field (§1.4.10 declares none, and none is added). Reissued R4-4 text is in
   §0X.7 cl. 5.
6. **`direction` remains stored** for the reason R9-4 already gives — `ros.store.Relation` reads it —
   and that permission is not widened by this ruling: no other derived value is stored on an edge, and
   `edge_state`, `post_hoc` and staleness (R2-3) are all computed.

**Why this preserves the architecture.** Ten fields in, ten fields out; two deletions of duplicated or
derived data; one derivation rule that produces exactly the state set R2-4 already froze. No relation
type, class, multiplicity, prohibited shape or lifecycle transition changes.

**Sections reissued.** §2.2 (§0X.4), R4-4 (§0X.7 cl. 5), §9.2.3, §9.2.4 rows `N-24`…`N-25`,
Appendix A.4.

## 0X.4 §2.2 reissued — the relation envelope

`relations` entries carry exactly these ten keys. Every key is present on every relation. Types are
the JSON types of the stored YAML; the shared `$defs` are those of §9.2.4.

| Field | Type | Present | Nullable | Rule |
|---|---|---|---|---|
| `from` | string (`record_id`) | yes | no | Source record identifier. Must resolve (R2-2). |
| `to` | string (`record_id`) | yes | no | Target record identifier. Must resolve (R2-2). |
| `type` | string | yes | no | One of the fifteen types of §2.3. Closed vocabulary. |
| `direction` | string (`EVIDENCE_DIRECTIONS`) \| null | yes | yes | Non-null exactly for the four §2.3 Class 1 evidential types; `null` for the other eleven (RB-02 cl. 2). |
| `semantic_note` | string | yes | no | Non-empty. Why this edge exists. |
| `established_by` | string | yes | no | Non-empty: a `decisions` identifier, a `runs` identifier, or `document_derived:<repo-relative-path>`. |
| `established_at` | string (`timestamp`) | yes | no | ISO-8601 per §9.2.4 `$defs/timestamp`. |
| `record_version_at` | object | yes | no | Closed: `{source: integer ≥ 1, target: integer ≥ 1}` — the endpoint `record_version`s when the edge was asserted (R2-3). |
| `retracted_by` | string (`record_id`) \| null | yes | yes | A `decisions` identifier, or `null`. Set once, never unset. Edges are retracted, never deleted (RB-02 cl. 5). |
| `confidence_basis` | string | yes | no | `evidence` \| `human_assertion` \| `structural`. See R2-5. |

**Rule R2-3 (edge versioning).** Unchanged.

**Rule R2-4 (edge lifecycle).** Edges use the Article L-2 subset **without `TOMBSTONED`**:
`CANDIDATE → ACTIVE ⇄ DORMANT`, `ACTIVE → DELETED`, `DORMANT → DELETED`, `CANDIDATE → DELETED`. This
is the Lock's own rule for `Edge`, applied here unchanged. The state is **derived, never stored**, by
the ordered rule of RB-02 cl. 4; the derived value is always a member of this set, and the recorded
inputs to the derivation are `retracted_by` and the two endpoints' `lifecycle.state`. No lifecycle
field exists on a relation, and the frozen SQL-P1 grammar gains no token: edge visibility is already
governed by `INCLUDE DORMANT` and by R5-14's default exclusions.

**Rule R2-5 (no edge carries a confidence number).** Unchanged.

## 0X.5 RB-03 — Closed nested objects (closes `BLK-P1-03`)

**The defect.** §9.2.1 requires `additionalProperties: false` inside every nested object, while nine
required object-valued fields had no property list, no types and no required set. A validator would
have to invent properties, permit arbitrary content against the closed-object rule, or reject every
non-empty object.

**Ruling RB-03.** §9.2.4 (new, below) is the **complete catalogue of every nested object used anywhere
in LSKE**: thirty-two objects and array items (`N-01`…`N-32`) over seven shared scalar types
(`S-01`…`S-07`), each with its properties, required set, types, nullability and constraints, each
closed by the form RB-01 cl. 4 assigns it. No nested object is
partially defined, and no LSKE schema contains an object that is absent from the catalogue. Four
sourcing rules were applied so that no shape is invented where the repository already fixes one:

1. Where a frozen ROS module produces the object, the object is **exactly that module's serialized
   payload**: `protocols.freeze` is `ros.protocol.Freeze.to_dict()` (five keys); `runs.environment` is
   `ros.events.environment()` (three keys); `runs.admissibility` is the serialization of
   `ros.admissibility.Verdict` (four keys, mapped in §9.2.4 note 2).
2. Where §1.1 or §1.4 states a content requirement that §9.2.1's typing cannot express, §1.1/§1.4
   governs under RC-04 and the type is widened to the shape that can carry it. This applies once, to
   `provenance.source_paths` (§9.2.4 note 1).
3. Where two collections declare the same object (`confidence.scope`, `hypotheses.scope`,
   `negative_results.scope`, `decisions.scope_after`), there is **one** definition
   (`$defs/scope`) referenced four times. RC-04 cl. 7 and §1.4.2 already say these are the same object;
   the catalogue makes that a single definition rather than a resemblance.
4. Where the object belongs to a frozen adjacent specification, LSKE closes its own level and does not
   constrain the other specification's interior. This applies once, to `obs2.schema.json`'s
   `nodes[]`, `edges[]` and `overlays.*` values (§9.2.4 note 3): constraining them would amend the
   Observatory specification, which R7-2 forbids.

**Why this preserves the architecture.** Every object named is an object v1.1.0 already required, in
the collection v1.1.0 already put it in, carrying the content v1.1.0's prose already described. No
field is added to any record beyond the interior of objects that were already required and already
closed.

**Sections reissued.** §9.2.4 (new), §9.2.2 typing addendum, §9.6 row 2.

## 0X.6 RB-04 — The immutable record model (closes `BLK-P1-04`)

**The defect.** Phase 1 requires an immutable record model. §9.1's layout is closed and lists no
record-model file; §9.1 describes `v2/lske/schema.py` as holding JSON Schema dictionaries; Part 6 and
Appendix A.3 define no record-model class, constructor, equality, immutability or hash API. Building
it would have created an architectural fact nobody decided.

**Ruling RB-04.** The immutable record model is **`v2.lske.schema.LskeRecord`**, public, specified in
full in §9.13.4. No file is added: the §9.1 row for `v2/lske/schema.py` has its *Contents* cell
reissued to name the four Phase-1 components the module owns (§9.13.1). Five clauses:

1. **Owning module — `v2.lske.schema`, and nowhere else.** The record model is not in `ros.store`, not
   in `ros.model`, not in a new module, and has no alias. `ros.store.Record` is unchanged and remains
   the mutable, raw-payload accessor the ROS store already exposes; the two classes have different
   names, different modules and different contracts, and neither is defined in terms of the other. The
   name `LskeRecord` is chosen precisely so that no import site can be ambiguous about which model it
   holds.
2. **Public status.** `LskeRecord` is public and is exported in `__all__`. Its only public constructor
   is the classmethod `LskeRecord.from_payload(payload, collection_key)`. Every helper it uses
   (`_deep_freeze`, `_blocks_ag`) is private and unspecified beyond §9.9's allowance.
3. **Immutability is deep and structural,** not a convention: the dataclass is `frozen=True`, mappings
   are stored as `MappingProxyType`, sequences as `tuple`, and no method returns a mutable view. A
   writer that needs a mutable payload calls `as_dict()`, which returns a deep copy; mutating that copy
   cannot reach the record. This is the same reasoning R6-3 uses for the confidence module: the absence
   of a write path is stronger than a rule against writing.
4. **Equality is structural over the whole payload; the container hash is not the scientific hash.**
   Two `LskeRecord`s are equal when their `collection_key` and their entire frozen payload are equal,
   including Block H. `__hash__` is derived from the canonical bytes of the whole payload, so it is
   stable across processes. `content_hash` — the scientific identity of R9-3 — covers blocks A–G only
   and is therefore **never** used as `__hash__`: a sealed record and its pre-seal self must be
   distinguishable inside a set, while remaining verifiable against one `content_hash`.
5. **One validation entry point.** `from_payload` validates by calling
   `v2.lske.schema.validate(payload, collection_key)` (RB-01 cl. 6, §9.13.3) and raises
   `SchemaViolation` on failure. There is no second constructor that skips validation, no `unsafe=`
   flag, and no `validate=False` parameter — R9-10's reasoning applies: a model that can be built
   unvalidated is a model whose validation is optional.

**Why this preserves the architecture.** No file, module, package, phase, collection or write
operation is added. One frozen module's stated contents are made explicit, and one class that Phase 1
was already required to deliver is given the public contract it lacked.

**Sections reissued.** §9.1 (Contents cell for `v2/lske/schema.py`), §9.13 (new), Appendix A.3.

## 0X.7 RB-05 — Validators, identifiers, hashing (closes `BLK-P1-05`)

**The defect.** Phase 1 requires validators and an identifier system. v1.1.0 defines validation
outcomes and identifier syntax but names no owning module and no signature; the frozen layout provides
no `validators.py` or `identifiers.py`, and R9-1/§9.1 forbid unlisted files.

**Ruling RB-05.** Every Phase-1 component maps to exactly one module, and that module is
`v2.lske.schema` for all four unowned components. Six clauses:

1. **Validation** — one public entry point, `validate(payload, schema_name)`, §9.13.3. No other public
   validator exists in `v2/lske/`. It raises `SchemaViolation` (§9.5, unchanged) whose message names
   the failing instance pointer, the failing schema pointer and the failing keyword — and, per R9-9, no
   measured value.
2. **Identifier allocation** — two public functions, `allocate_record_id` and `allocate_event_id`,
   §9.13.5. Both are pure: the record allocator takes the existing identifier set and the allocation
   year as arguments rather than reading a clock or the store, so a test can pin it; the event
   allocator is content-addressed, so re-emitting one event twice cannot produce two identifiers,
   which is what R9-7's no-re-emit rule needs in order to be checkable. Parsing is **not** duplicated:
   `ros.model.ID_PATTERN`, `ros.model.prefix_of` and `ros.model.collection_for_id` remain the only
   identifier parsers in the repository.
3. **Canonical hashing** — three public functions, `canonical_json`, `content_hash`, `seal`, §9.13.6.
   `canonical_json` delegates to `ros.protocol.canonical_bytes` exactly as R9-3 requires;
   `content_hash` is SHA-256 over blocks A–G; `seal` is SHA-256 over the content hash and the freeze
   timestamp (Block H). `ros.protocol.digest` remains BLAKE2b and is neither reused nor re-implemented
   here — the blocker report's non-blocking clarification is adopted verbatim as this clause.
4. **The immutable record model** — `LskeRecord`, RB-04.
5. **One literal site per frozen register that Phase 1 must encode.** The schema module holds the
   literal tuples the Phase-1 schemas require and that no already-frozen module holds:
   `PRIMITIVES` (19, §0.3), `COLLECTION_SPECS` (20, §1.2), `DIMENSION_KEYS` (10, §1.1 Block F),
   `DIMENSION_STATES` (4, R4-3), `LIFECYCLE_STATES` (5, §1.1 Block G), `CHANGE_KINDS` (8, §1.1
   Block C), `RELATION_TYPES` (15, §2.3), `CONFIDENCE_BASES` (3, §2.2). Every register a frozen module
   already holds is **imported, never restated**: `EVIDENCE_DIRECTIONS`, `HYPOTHESIS_STATUSES`,
   `DECISION_ACTIONS` and `normalise_term` from `ros.model`; `AuthorityClass`, `EVIDENCE_TARGETS` and
   `ENGINEERING_TARGETS` from `ros.authority`; `Tier` from `ros.admissibility`. Consequently
   `v2.lske.confidence` (stage 5) **imports** `DIMENSION_KEYS` and `DIMENSION_STATES` from
   `v2.lske.schema` and does not restate them: its `DIMENSIONS` is that tuple, and its
   `DimensionState` enumeration is constructed over `DIMENSION_STATES`. The interface of §6.1 is
   unchanged — same module, same names, same four values, same string-enum behaviour — only the
   declaration form is fixed, so that exactly one literal list of the four states exists in the
   package. Two hand-maintained copies of one register drift; one derived from the other cannot
   (R9-2's own reasoning).
6. **Collection metadata is owned in Phase 1 and propagated in stage 2.** `COLLECTION_SPECS` in
   `v2.lske.schema` is the single Phase-1 declaration of the twenty collections' `key`, `prefix`,
   `object_type`, `primitive` and `append_only`, because the collection schemas cannot type `id`,
   `type`, `primitive` or `immutability.append_only` without it and stage 1 explicitly changes nothing
   in `ros.model`. Stage 2 aligns `ros.model.COLLECTIONS` to it. From stage 2 onward,
   `ros.model.COLLECTIONS` is the runtime register for store loading and `COLLECTION_SPECS` is the
   schema register, and test 3 asserts that the two agree on key, prefix, object_type and append_only
   for all twenty. This resolves the stage-1 exit condition, which required test 3 to pass while
   forbidding the `ros.model` change that test 3 was written against; the reissued exit condition is in
   §9.8 as amended below.

**Why this preserves the architecture.** No file is added, no module is added, no API is duplicated,
and no register acquires a second definition. Four components that v1.1.0 required without an owner
now have exactly one owner each, inside a module the frozen layout already lists.

**Sections reissued.** §9.1 (Contents cell), §9.6 rows 1–3, §9.8 stage 1 and stage 2 exit conditions,
§9.13 (new), Appendix A.3.

**R4-4 reissued** (the one sentence RB-02 cl. 5 corrects; the rest of R4-4 is unchanged):

> **Rule R4-4 (dimension resolution).** For dimension *d* on claim *c*, gather every `evidence` record
> `e` where a `supports` or `refutes` edge connects `e → c` and `d ∈ e.dimensions` and
> `e.eligibility ≠ ineligible` and **that edge's `retracted_by` is null** and
> `e.lifecycle.state = ACTIVE` — a `CANDIDATE` draft written by `ingest` never contributes, under any
> circumstance, until a human decision admits it (RC-11). Then: no such `e` → `unassessed`; all
> `supports` → `assessed_supported`; all `refutes` → `assessed_failed`; both present →
> `assessed_contested`. The remainder of R4-4, including the treatment of `null` and `indeterminate`
> directions, is unchanged.

## 0X.8 RB-06 — Identifier pattern conformance (found in verification, not in the blocker report)

**Standing.** This ruling closes a defect found by the Appendix C verification pass of this amendment,
not by `P1_V2_LSKE_PHASE1_BLOCKER_REPORT.md`. It is included because it blocks a stage-1 acceptance
criterion (test 3) and because R9-0 forbids the implementer from resolving it silently.

**The defect.** §1.2 assigns the prefix `RQ` to `research_questions`. §1.1 Block A requires every
identifier to match `ros.model.ID_PATTERN`, which is `^[A-Z]{3,5}-\d{4}-\d{4}$` and admits no
two-letter prefix. §9.4.1 asserts that "`ID_PATTERN` is unchanged and already admits all nine new
prefixes" — which is false for exactly one of them. `RQ-2026-0001` is therefore an identifier the
envelope requires and the pattern rejects; test 3 ("`ID_PATTERN` matches all 20") cannot pass, and a
`research_questions` identifier would be invisible to `ros.model.iter_id_references`, so every
reference to a research question would be undetectable by `MEM-06` and `_check_references`.

**Ruling RB-06.** The `research_questions` prefix is **`RQS`**. `ros.model.ID_PATTERN` is
**unchanged**. Exactly one cell of §1.2 is amended — the prefix column of row 1 — and nothing else:
the collection's key, `object_type`, `primitive` and `append_only` flag are untouched, and no other
prefix changes.

Three reasons the prefix moves rather than the pattern:

1. `ID_PATTERN` is live shipped code whose semantics are repo-wide and *structural*: every string in
   every record that matches it is treated as a reference (`ros.model` docstring). Widening it to
   `[A-Z]{2,5}` would change what counts as a reference in records that already exist, and would make
   two-letter accidental matches into dangling references — silently altering `MEM-06`,
   `_check_references` and the store-integrity gate for data nobody edited.
2. `research_questions` is marked **new** in §1.2. It has no records, and a repository-wide search
   found **zero** occurrences of a literal `RQ-YYYY-NNNN` identifier in any file. The change therefore
   invalidates no stored reference, no test fixture and no document citation.
3. §9.4.1 already states the invariant this ruling restores — that the pattern admits every prefix —
   and instructs the implementer to verify it "with a test rather than by inspection". RB-06 makes the
   assertion true before the test is written instead of after it fails.

**Rule R9-18.** `COLLECTION_SPECS` is well-formed only if, for every entry, `prefix` matches
`^[A-Z]{3,5}$` and `f"{prefix}-2026-0001"` matches `ros.model.ID_PATTERN`. This is asserted in test 3
for all twenty collections, so a future prefix that the pattern cannot carry fails at stage 1 rather
than at first reference.

**Sections reissued.** §1.2 (row 1, prefix column only), §9.4.1 (the sentence asserting pattern
coverage now names `RQS`), §9.6 row 3, Appendix A.2 (`Record collections` register unchanged in size).

## 0X.9 What this release does not do

It adds no collection, relation type, dimension, dimension state, lifecycle state, write operation,
transaction phase, authority class, write target, human-only decision, gate, KPI, primitive, package
file, schema file, test file or build stage. It removes none of these either. `LskeRecord`,
`validate`, `allocate_record_id`, `allocate_event_id`, `canonical_json`, `content_hash` and `seal` are
the named public contract of components v1.1.0 already required Phase 1 to deliver, all inside
`v2/lske/schema.py`, which §9.1 already lists. Three fields are deleted as duplicated or derived
(`relations.independence_group`, `relations.post_hoc`, and the top-level closure keyword of
`record.schema.json`); one type is widened to carry content §1.1 already required
(`provenance.source_paths`); everything else is a completion of a definition or the naming of an
owner.


---

# PART 9 — Implementation Contract (amended sections)

R9-0 and R9-13 are unchanged and remain in force: an underspecified point is raised as a
Constitutional Change Request, never chosen. This document is the v1.1.1 amendment issued under R9-0
against v1.1.0 in response to `P1_V2_LSKE_PHASE1_BLOCKER_REPORT.md`.

## 9.1 Frozen file layout (reissued rows only)

The layout of v1.1.0 §9.1 is unchanged in membership: the same files, the same count, the same two
run-time data paths, the same single temporary file. Two *Contents* cells are reissued, and no row is
added, removed or renamed.

| Path | Kind | Contents (reissued) |
|---|---|---|
| `v2/lske/schema.py` | new | The JSON Schemas of §9.2 as module-level dicts (R9-2); the frozen literal registers of RB-05 cl. 5; the twenty `COLLECTION_SPECS` of RB-05 cl. 6; the single validation entry point `validate` (§9.13.3); the identifier allocators `allocate_record_id` and `allocate_event_id` (§9.13.5); the canonical hashing API `canonical_json`, `content_hash`, `seal` (§9.13.6); and the immutable record model `LskeRecord` (§9.13.4). Nothing else. |
| `v2/lske/events.py` | new | The durable LSKE event log writer; `lifecycle` and `evidence` kinds only (RC-07). It allocates no identifier and computes no hash of its own: it calls `v2.lske.schema.allocate_event_id` (RB-05 cl. 2). |

Every other row of §9.1, the two run-time data paths (`.ros/receipts/<receipt_id>.json` and
`.ros/lske_events.jsonl`), the absence of `ros/propagation.py` (RC-02), the absence of
`science/11_LIVING_SCIENTIFIC_MODEL.md` (RC-10) and R9-1's prohibition of a `__main__`, CLI, server or
network client are unchanged.

**Rule R9-1.** Unchanged.

**Rule R9-2.** Unchanged. The fixed serialization that makes its byte-match test decidable is RB-01
cl. 8.

## 9.2.0 Schema composition contract (new, RB-01)

This section is normative and is the only statement of how LSKE schemas compose. It replaces every
composition sentence in v1.1.0 §9.2.1 and §9.2.2.

1. **Dialect.** JSON Schema Draft 2020-12, `$schema:
   "https://json-schema.org/draft/2020-12/schema"`, on every one of the twenty-three files.
2. **Files.** Twenty-three: `record.schema.json`, twenty `<collection_key>.schema.json`,
   `relation.schema.json`, `obs2.schema.json`. Unchanged from §9.1 and Appendix A.4.
3. **Roles.** `record.schema.json` is a **composable fragment** and also the single home of the shared
   `$defs`. The twenty collection schemas are the **only** validation targets for records.
   `relation.schema.json` and `obs2.schema.json` are **standalone** targets and compose nothing; they
   reference `record.schema.json#/$defs/*` for shared scalar types only.
4. **Composition.** Exactly as RB-01 cl. 1: `allOf` of two `$ref`s, closed by a sibling
   `unevaluatedProperties: false`. Depth two, one parent, no dynamic references (RB-01 cl. 3).
5. **Closure.** Exactly as RB-01 cl. 4: composed objects close with `unevaluatedProperties: false`;
   fixed-key objects close with `additionalProperties: false`; the two map-keyed objects close with
   `propertyNames` plus a single closed value schema.
6. **Conditionals.** Exactly as RB-01 cl. 5: `if/then` may add to `required` only, inside
   `#/$defs/collection`, and every field it can require is declared in that subschema's `properties`.
7. **Narrowing is permitted, widening is not.** A collection branch may re-declare an envelope
   property to narrow it — `id` to its prefix pattern, `type` and `primitive` to a `const`,
   `confidence` to `object` or `null`, `immutability.append_only` to a `const`, `lifecycle.status` to
   the collection's vocabulary. It may never re-declare an envelope property in a way that admits a
   value the envelope rejects, and test 1 checks this by asserting that every collection schema's
   accepted set is a subset of the envelope's for the sixteen envelope keys.
8. **Resolution and serialization.** Exactly as RB-01 cl. 7 and cl. 8.

### 9.2.0.1 Normative example (the only one)

`schemas/lske/record.schema.json` — the composable fragment. `$defs` entries other than the three
shown are generated verbatim from the catalogue of §9.2.4 by the same pattern; the three shown fix the
pattern.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://p1.local/schemas/lske/record.schema.json",
  "title": "LSKE universal record envelope",
  "type": "object",
  "properties": {
    "id": { "$ref": "#/$defs/record_id" },
    "type": { "type": "string", "minLength": 1 },
    "primitive": { "type": "string", "enum": ["Run", "Environment", "Tick", "Event", "Snapshot", "Neuron", "Kind", "Edge", "Graph", "DelayLine", "EpisodicMemory", "Ledger", "Policy", "Intervention", "Protocol", "Measurement", "Claim", "Evidence", "Decision"] },
    "title": { "type": "string", "minLength": 1 },
    "record_version": { "type": "integer", "minimum": 1 },
    "ontology_version": { "$ref": "#/$defs/semver" },
    "content_hash": { "$ref": "#/$defs/hex64" },
    "created": { "$ref": "#/$defs/created" },
    "revisions": { "type": "array", "items": { "$ref": "#/$defs/revision" } },
    "supersedes": { "oneOf": [{ "$ref": "#/$defs/record_id" }, { "type": "null" }] },
    "superseded_by": { "oneOf": [{ "$ref": "#/$defs/record_id" }, { "type": "null" }] },
    "provenance": { "$ref": "#/$defs/provenance" },
    "authority": { "$ref": "#/$defs/authority" },
    "confidence": { "oneOf": [{ "$ref": "#/$defs/confidence" }, { "type": "null" }] },
    "lifecycle": { "$ref": "#/$defs/lifecycle" },
    "immutability": { "$ref": "#/$defs/immutability" }
  },
  "required": ["id", "type", "primitive", "title", "record_version", "ontology_version", "content_hash", "created", "revisions", "supersedes", "superseded_by", "provenance", "authority", "confidence", "lifecycle", "immutability"],
  "$defs": {
    "record_id": { "type": "string", "pattern": "^[A-Z]{3,5}-[0-9]{4}-[0-9]{4}$" },
    "timestamp": { "type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}([.][0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})$" },
    "created": {
      "type": "object",
      "properties": {
        "at": { "$ref": "#/$defs/timestamp" },
        "by": { "type": "string", "minLength": 1 },
        "authority": { "type": "string", "enum": ["OBSERVER", "PROPOSER", "ENGINEER", "SCIENTIST"] },
        "target": { "$ref": "#/$defs/write_target" }
      },
      "required": ["at", "by", "authority", "target"],
      "additionalProperties": false
    }
  }
}
```

`schemas/lske/programs.schema.json` — the composed validation target. All twenty collection schemas
have exactly this shape; only `$id`, `title`, the four narrowings and `#/$defs/collection` differ.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://p1.local/schemas/lske/programs.schema.json",
  "title": "programs",
  "type": "object",
  "allOf": [
    { "$ref": "record.schema.json" },
    { "$ref": "#/$defs/collection" }
  ],
  "unevaluatedProperties": false,
  "$defs": {
    "collection": {
      "type": "object",
      "properties": {
        "id": { "type": "string", "pattern": "^PROG-[0-9]{4}-[0-9]{4}$" },
        "type": { "const": "research_program" },
        "primitive": { "const": "Claim" },
        "confidence": { "type": "object" },
        "immutability": { "type": "object", "properties": { "append_only": { "const": false } } },
        "statement": { "type": "string", "minLength": 1 },
        "gate": { "type": "string", "enum": ["G1", "G2", "G3", "G4", "G5"] },
        "question_ids": { "type": "array", "items": { "$ref": "record.schema.json#/$defs/record_id" } },
        "entry_condition": { "type": "string", "minLength": 1 },
        "exit_condition": { "type": "string", "minLength": 1 }
      },
      "required": ["statement", "gate", "question_ids", "entry_condition", "exit_condition"]
    }
  }
}
```

Read together, the two files admit exactly the sixteen envelope keys plus the five `programs` keys,
reject every twenty-second key, close every nested object, and require no second validation pass. That
is the whole composition contract; there is no alternative mechanism.

## 9.2.1 The universal envelope (reissued opening; field table unchanged)

`schemas/lske/record.schema.json` is the composable fragment of §9.2.0 cl. 3. It carries **no
top-level `additionalProperties` and no top-level `unevaluatedProperties`**; closure of a record is
asserted once, by the collection schema (RB-01 cl. 2). Every nested object inside it is closed by
`additionalProperties: false` per RB-01 cl. 4 and is defined in full in §9.2.4. A record is validated
once, against its collection schema (RB-01 cl. 6).

The sixteen-row field table of v1.1.0 §9.2.1, and every clause of RC-04 it restates, are **unchanged**.
The prose sentences describing the nested objects (`revisions[]` item, `provenance`, `authority`,
`confidence`, `lifecycle`, `immutability`) are superseded by §9.2.4, which states the same content as
a complete catalogue rather than as prose, and adds the types, required sets and nullability those
sentences left to the implementer.

**Rule R9-3.** Unchanged. Its canonicalization is the one `v2.lske.schema.canonical_json` delegates to
(§9.13.6).

## 9.2.2 Collection schemas (reissued opening and typing addendum)

Twenty files, `schemas/lske/<collection_key>.schema.json`, each composed exactly as §9.2.0 cl. 4 and
§9.2.0.1 show. The per-collection required fields are exactly those tabulated in §1.4, under exactly
those names (RC-06); the twenty-row table of v1.1.0 §9.2.2 is **unchanged** and remains the register of
additional required fields and notable constraints. No collection declares a top-level `status`; no
collection except `programs` declares a `gate`.

Six typing rules complete that table. They add no field name and no vocabulary.

1. **Envelope narrowing per collection is mandatory, not optional.** Every collection schema narrows
   `id` to `^<PREFIX>-[0-9]{4}-[0-9]{4}$`, `type` to the `const` of its `object_type`, `primitive` to
   the `const` of its `primitive`, `immutability.append_only` to the `const` of its `append_only`
   flag, and `confidence` to `{"type": "object"}` for the eight `Claim`-realizing collections or
   `{"type": "null"}` for the other twelve (RC-04 cl. 7, §1.3). All five values come from
   `COLLECTION_SPECS` (RB-05 cl. 6), so the narrowing is generated, not typed by hand.
2. **`lifecycle.status` is narrowed to an `enum` for the four collections that declare a vocabulary**
   — `research_questions`, `hypotheses`, `experiments`, `metrics` — and to the enum
   `["Candidate", "Active", "Dormant", "Tombstoned", "Deleted"]` for the other sixteen (RC-06 cl. 6).
   For `experiments`, the schema enum is the §1.4.4 vocabulary as written; `ros.model.normalise_term`
   governs comparison, never schema admission, because a normalizing schema would accept
   `blocked_confirmatory` as a stored spelling and the store would then hold two spellings of one
   status.
3. **Conditional fields are `if/then` over `required` inside `#/$defs/collection`** (§9.2.0 cl. 6).
   The conditional sets are exactly those §1.4 states: `experiments` (`protocol_id`, `validity`,
   `invalidity_reason`, `observation_ids`, `evidence_ids`, `treatment_activated`), `decisions`
   (`scope_after`, `level_after`), `provenance` (`run_ids`, `protocol_id`, `source_paths`, `citation`,
   `derivation`), `observations` (`coverage.missing_reason`). No other conditional exists.
4. **The four legacy `experiments` fields §1.4.4 retains are declared optional with these exact
   types**, taken from the existing store rather than invented: `executions` array of strings,
   `limitations` array of strings, `execution_gate` string, `unavailable_primary_metrics` array of
   strings. They are declared because `unevaluatedProperties: false` would otherwise reject every
   migrated experiment record that carries them, and `ros.propagation` reads `executions` (§1.4.4).
   They are optional because a new `experiments` record has no legacy content. `legacy_ids`, present on
   existing records, is declared on every collection as an optional array of strings for the same
   reason and is read by nothing.
5. **`evidence.assumptions_relied_upon` is an array whose items are either an `ASM` identifier or the
   literal `"none_declared"`,** with `minItems: 1`: either the record names the assumptions it relies
   on, or it declares in one word that it relies on none. This is the "explicit `none_declared`
   marker" §1.4.10 requires, expressed without adding a field.
6. **`evidence.dimensions` is an array with `minItems: 1`, `uniqueItems: true`, and items enumerated
   over `DIMENSION_KEYS`** (§1.4.10: "a non-empty subset of the ten").


## 9.2.3 The relation envelope (reissued, RB-02)

`schemas/lske/relation.schema.json`. Standalone, not composed. `type: object`,
`additionalProperties: false`, and all ten keys of §0X.4 in `required` — there is no optional key.
Shared scalar types are referenced as `record.schema.json#/$defs/*`; no scalar type is redefined here.

- `from`, `to` — `$defs/record_id`.
- `type` — `enum` of exactly the fifteen types of §2.3.
- `direction` — `oneOf: [{enum of ros.model.EVIDENCE_DIRECTIONS}, {type: null}]`, with one
  `if/then/else`: `type` in the four Class 1 evidential types ⇒ `direction` is not null; otherwise
  `direction` is null (RB-02 cl. 2).
- `semantic_note` — string, `minLength: 1`.
- `established_by` — string, `minLength: 1`.
- `established_at` — `$defs/timestamp`.
- `record_version_at` — object `N-29`.
- `retracted_by` — `oneOf: [{$defs/record_id}, {type: null}]`.
- `confidence_basis` — `enum: ["evidence", "human_assertion", "structural"]`.

**No numeric field is permitted anywhere in this schema** (R2-5), which
`additionalProperties: false` plus the ten declared types enforces exhaustively — that is the reason
the flag is set, not a stylistic preference. **No lifecycle field exists**: edge state is derived by
RB-02 cl. 4. `independence_group` and `post_hoc` do not appear (RB-02 cl. 3).

**Rule R9-4.** Unchanged: `direction` is the one permitted stored restatement in the LSKE, because
`ros.store.Relation` reads it. RB-02 cl. 6 confirms the permission is not widened.

## 9.2.4 Closed nested object catalogue (new, RB-03)

This is the complete catalogue of every object and array item used anywhere in an LSKE schema. It is
exhaustive: a nested object absent from this catalogue does not exist in the LSKE, and a schema
containing one is a defect under R9-0. **Present** means the key must appear; **Nullable** means `null`
is an admissible value for a present key. Every entry marked *fixed-key* closes with
`additionalProperties: false`; the two entries marked *map-keyed* close per RB-01 cl. 4.

### `$defs` names and homes (one name, one home, per entry)

A catalogue entry is realized as a `$defs` subschema under the stated name, in the stated file. The
names are frozen so that no `$ref` target has to be guessed.

| Entries | `$defs` names, in catalogue order | Home file |
|---|---|---|
| `S-01`…`S-07` | `record_id`, `timestamp`, `semver`, `hex64`, `write_target`, `authority_class`, `event_id` | `record.schema.json` |
| `N-01`…`N-13` | `created`, `revision`, `provenance`, `citation`, `source_path`, `authority`, `confidence`, `scope`, `dimensions`, `dimension`, `lifecycle`, `transition`, `immutability` | `record.schema.json` |
| `N-14`, `N-15` | `freeze`, `sesoi` | `protocols.schema.json` |
| `N-16`, `N-17` | `admissibility`, `environment` | `runs.schema.json` |
| `N-18`…`N-20` | `uncertainty`, `coverage`, `declared_null_comparison` | `observations.schema.json` |
| `N-21`…`N-24` | `generator`, `leakage_audit`, `splits`, `split` | `datasets.schema.json` |
| `N-25` | `risky_prediction` | `theories.schema.json` |
| `N-26` | `dissent` | `decisions.schema.json` |
| `N-27` | `unexcluded_alternative` | `evidence.schema.json` |
| `N-28` | `annotation` | `sessions.schema.json` |
| `N-29` | `record_version_at` | `relation.schema.json` |
| `N-31` | `payload_object` | `obs2.schema.json` |

`N-30` is the top level of `obs2.schema.json` and `N-32` is its inline `overlays` subschema; neither is
a `$defs` entry. `scope` (`N-08`) lives in `record.schema.json` even though three of its four uses are
collection fields, because a definition referenced by four schemas must have one home and the envelope
is the only file all four already reference (`hypotheses`, `negative_results` and `decisions` reference
it as `record.schema.json#/$defs/scope`).

### Shared scalar `$defs` (one definition each, in `record.schema.json`)

| # | `$defs` name | Definition |
|---|---|---|
| `S-01` | `record_id` | string, `^[A-Z]{3,5}-[0-9]{4}-[0-9]{4}$` — the same form as `ros.model.ID_PATTERN` |
| `S-02` | `timestamp` | string, `^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}([.][0-9]+)?(Z\|[+-][0-9]{2}:[0-9]{2})$` — one ISO-8601 form for every timestamp in the LSKE |
| `S-03` | `semver` | string, `^[0-9]+[.][0-9]+[.][0-9]+$` |
| `S-04` | `hex64` | string, `^[0-9a-f]{64}$` — used for SHA-256 (`content_hash`, `seal`, digests) and for the BLAKE2b-256 protocol digest; the algorithm is stated per field, and the character class is defined once |
| `S-05` | `write_target` | string, `enum` of `ros.authority.EVIDENCE_TARGETS ∪ ENGINEERING_TARGETS` (sixteen values), generated by import, never restated |
| `S-06` | `authority_class` | string, `enum: ["OBSERVER", "PROPOSER", "ENGINEER", "SCIENTIST"]` — the names of `ros.authority.AuthorityClass` |
| `S-07` | `event_id` | string, `^LEV-[0-9a-f]{32}$` — allocated by §9.13.5. It carries one hyphen and a lowercase-hex tail, so it can never match `ros.model.ID_PATTERN` and can never be mistaken for a record reference; this is the same reasoning §9.3.1 gives for receipt identifiers. |

### Envelope objects

**`N-01` `created`** — fixed-key. Required: all four.

| Field | Type | Present | Nullable |
|---|---|---|---|
| `at` | `timestamp` | yes | no |
| `by` | string, non-empty | yes | no |
| `authority` | `authority_class` | yes | no |
| `target` | `write_target` | yes | no |

**`N-02` `revisions[]` item** — fixed-key. Required: all eight. The array itself may be empty.

| Field | Type | Present | Nullable | Constraint |
|---|---|---|---|---|
| `record_version` | integer | yes | no | ≥ 1; equals the record's version after this revision |
| `at` | `timestamp` | yes | no | |
| `by` | string, non-empty | yes | no | |
| `authority` | `authority_class` | yes | no | |
| `target` | `write_target` | yes | no | |
| `change_kind` | string | yes | no | `enum` of the eight of §1.1 Block C: `create`, `amend`, `annotate`, `status_transition`, `supersede`, `tombstone`, `restore`, `delete` |
| `rationale` | string, non-empty | yes | no | Block C is where a change's reason lives (RC-04 cl. 4) |
| `prior_content_hash` | `hex64` \| null | yes | yes | `null` only on the first entry; thereafter the preceding entry's computed hash (`MEM-02`) |

**`N-03` `provenance`** — fixed-key. Required: all six keys present (Block D).

| Field | Type | Present | Nullable | Constraint |
|---|---|---|---|---|
| `kind` | string | yes | no | `enum: [human_assertion, run_derived, document_derived, external_literature, projection]` |
| `run_ids` | array[`record_id`] | yes | no | May be empty; `minItems: 1` required when `kind = run_derived` |
| `protocol_id` | `record_id` \| null | yes | yes | Non-null required when `kind = run_derived` and the record bears on a claim (§1.1 Block D) |
| `source_paths` | array[`N-05`] | yes | no | May be empty; `minItems: 1` required when `kind = document_derived`; see note 1 |
| `citation` | `N-04` \| null | yes | yes | Non-null required when `kind = external_literature` |
| `derivation` | string, non-empty \| null | yes | yes | Non-null required when `kind = projection`, and permitted only in `snapshots` (R1-1) |

**`N-04` `provenance.citation`** — fixed-key. Required: all four.

| Field | Type | Present | Nullable | Constraint |
|---|---|---|---|---|
| `kind` | string | yes | no | `enum: [doi, arxiv, isbn, url, report]` |
| `identifier` | string, non-empty | yes | no | The citation key within `kind` |
| `title` | string, non-empty | yes | no | |
| `year` | integer \| null | yes | yes | `null` where the source is undated; an undated source is a real state |

**`N-05` `provenance.source_paths[]` item** — fixed-key. Required: both. See note 1.

| Field | Type | Present | Nullable | Constraint |
|---|---|---|---|---|
| `path` | string, non-empty | yes | no | Repo-relative, POSIX separators |
| `content_hash` | `hex64` | yes | no | SHA-256 of the file's bytes at derivation time |

**`N-06` `authority`** — fixed-key. Required: all four (Block E).

| Field | Type | Present | Nullable | Constraint |
|---|---|---|---|---|
| `write_target` | `write_target` | yes | no | |
| `committed_by` | string, non-empty | yes | no | |
| `is_human` | boolean | yes | no | `false` with an `EVIDENCE_TARGETS` value is invalid (R1-2) |
| `escalated_from` | `write_target` \| null | yes | yes | `null` unless an agent drafted the record and a human committed the draft (RC-04 cl. 1) |

**`N-07` `confidence`** — fixed-key, and itself nullable at the envelope level (non-null exactly when
`primitive = "Claim"`). Required: all three keys when the object is present.

| Field | Type | Present | Nullable | Constraint |
|---|---|---|---|---|
| `level` | integer \| null | yes | yes | 0–5 inclusive; written only under `skb.claim_status` (R1-3) |
| `scope` | `N-08` \| null | yes | yes | Human-only write (`skb.claim_scope`) |
| `dimensions` | `N-09` | yes | no | Exactly the ten keys |

No numeric field exists anywhere under `confidence` other than `level` (I-14), which the catalogue
makes checkable by enumeration.

**`N-08` `scope`** — fixed-key. One definition, referenced by `confidence.scope`, `hypotheses.scope`,
`negative_results.scope` and `decisions.scope_after`. Required: all four.

| Field | Type | Present | Nullable | Constraint |
|---|---|---|---|---|
| `population` | string, non-empty | yes | no | What the claim is about |
| `regime` | string, non-empty | yes | no | The conditions under which it is asserted |
| `environment_ids` | array[`record_id`] | yes | no | May be empty; each resolves to a `datasets` record |
| `limits` | array[string] | yes | no | May be empty; each item non-empty. The stated boundaries of the claim |

**`N-09` `confidence.dimensions`** — fixed-key with exactly the ten `DIMENSION_KEYS` as properties, all
ten required, `additionalProperties: false`. The ten, in Lock order: `existence`,
`measurement_validity`, `effect_existence`, `magnitude`, `mechanism`, `robustness`, `generalisation`,
`necessity_over_simpler`, `resource_efficiency`, `observability_completeness`. This object is **not**
map-keyed: its keys are frozen, so it is closed by enumeration (RB-01 cl. 4).

**`N-10` `confidence.dimensions.<key>`** — fixed-key. Required: both.

| Field | Type | Present | Nullable | Constraint |
|---|---|---|---|---|
| `state` | string | yes | no | `enum` of `DIMENSION_STATES`: `unassessed`, `assessed_supported`, `assessed_contested`, `assessed_failed` (R4-3, RC-05) |
| `evidence_ids` | array[`record_id`] | yes | no | May be empty; empty exactly when `state = unassessed` |

**`N-11` `lifecycle`** — fixed-key. Required: all three (Block G).

| Field | Type | Present | Nullable | Constraint |
|---|---|---|---|---|
| `state` | string | yes | no | `enum: [CANDIDATE, ACTIVE, DORMANT, TOMBSTONED, DELETED]` |
| `status` | string, non-empty | yes | no | The collection's vocabulary per §9.2.2 rule 2 |
| `transitions` | array[`N-12`] | yes | no | `minItems: 1`; append-only. `state` equals the last item's `to` (`MEM-01`) |

**`N-12` `lifecycle.transitions[]` item** — fixed-key. Required: all six.

| Field | Type | Present | Nullable | Constraint |
|---|---|---|---|---|
| `from` | string \| null | yes | yes | One of the five states, or `null` **only on the first item**, where there is no prior state |
| `to` | string | yes | no | One of the five states; the pair `(from, to)` is one of the seven frozen transitions, or `(null, CANDIDATE)` at creation |
| `at` | `timestamp` | yes | no | |
| `by` | string, non-empty | yes | no | |
| `event_id` | `event_id` | yes | no | Resolves in `.ros/lske_events.jsonl` (R1-4, RC-07) |
| `cause` | string, non-empty | yes | no | The decision, receipt or migration identifier, or a stated cause |

**`N-13` `immutability`** — fixed-key. Required: all three (Block H).

| Field | Type | Present | Nullable | Constraint |
|---|---|---|---|---|
| `append_only` | boolean | yes | no | Equals the collection's flag; narrowed to a `const` per collection (§9.2.2 rule 1) |
| `frozen_at` | `timestamp` \| null | yes | yes | |
| `seal` | `hex64` \| null | yes | yes | Non-null **iff** `frozen_at` is non-null, expressed as two `if/then` branches over the null-ness of `frozen_at` |

### Collection objects

**`N-14` `protocols.freeze`** — fixed-key. Required: all five. This object is exactly
`ros.protocol.Freeze.to_dict()`; it is not re-modelled (RB-03 cl. 1).

| Field | Type | Present | Nullable | Constraint |
|---|---|---|---|---|
| `protocol_id` | string, non-empty | yes | no | The protocol's own identifier as `ros.protocol` records it |
| `digest` | `hex64` | yes | no | BLAKE2b-256 over `ros.protocol.canonical_bytes` |
| `source` | string, non-empty | yes | no | Repo-relative protocol path |
| `frozen_at_commit` | string \| null | yes | yes | Git SHA; `null` until the caller supplies it |
| `algorithm` | string | yes | no | `const: "blake2b-256-canonical-json"` |

**`N-15` `protocols.sesoi`** — fixed-key. Required: all three.

| Field | Type | Present | Nullable | Constraint |
|---|---|---|---|---|
| `value` | number | yes | no | The smallest effect size of interest |
| `units` | string, non-empty | yes | no | §1.4.3: "with units" |
| `metric_id` | `record_id` | yes | no | The `metrics` record the value is expressed in; R1-22 compares `sesoi` per metric |

**`N-16` `runs.admissibility`** — fixed-key. Required: all four. See note 2.

| Field | Type | Present | Nullable | Constraint |
|---|---|---|---|---|
| `admissible` | boolean | yes | no | Copied from `Verdict.admissible` |
| `tier` | string | yes | no | `enum: [inadmissible, engineering-only, exploratory-admissible, confirmatory-admissible]` — the four `ros.admissibility.Tier` values |
| `ceiling` | array[string] | yes | no | May be empty; the `Verdict.ceilings` tuple, most binding first |
| `reasons` | array[string] | yes | no | `minItems: 1`; the `Verdict.reasons` tuple |

**`N-17` `runs.environment`** — fixed-key. Required: all three. Exactly `ros.events.environment()`.

| Field | Type | Present | Nullable | Constraint |
|---|---|---|---|---|
| `python` | string, non-empty | yes | no | |
| `platform` | string, non-empty | yes | no | |
| `ci` | string | yes | no | May be the empty string, which is what the function returns off CI |

**`N-18` `observations.uncertainty`** — fixed-key. Required: all four.

| Field | Type | Present | Nullable | Constraint |
|---|---|---|---|---|
| `kind` | string | yes | no | `enum: [none, sd, se, ci95, iqr]` |
| `interval` | array[number] \| null | yes | yes | Exactly two items, ascending, when `kind ∈ {ci95, iqr}`; `null` otherwise |
| `n` | integer \| null | yes | yes | ≥ 1; `null` when the count is not applicable |
| `method` | string, non-empty | yes | no | How the uncertainty was obtained, or — when `kind = none` — why it was not quantified. R4-15 records uncertainty rather than modelling it, so an unquantified interval must still say so |

**`N-19` `observations.coverage`** — fixed-key. Required: all three.

| Field | Type | Present | Nullable | Constraint |
|---|---|---|---|---|
| `measured` | integer | yes | no | ≥ 0 |
| `expected` | integer | yes | no | ≥ 0 |
| `missing_reason` | string, non-empty \| null | yes | yes | Non-null required when `measured < expected` and when `value = null` (R1-13) |

**`N-20` `observations.declared_null_comparison`** — fixed-key, nullable at the field level. Required:
all three when present.

| Field | Type | Present | Nullable | Constraint |
|---|---|---|---|---|
| `declared_null` | string, non-empty | yes | no | Restates the protocol's declared null as compared against |
| `outcome` | string | yes | no | `enum: [consistent_with_null, inconsistent_with_null, indeterminate, not_evaluated]` |
| `basis` | string, non-empty | yes | no | The named comparison performed. R9-9's reasoning applies to prose, not to this field: the basis names a method, never a value |

**`N-21` `datasets.generator`** — fixed-key, nullable at the field level (`null` for non-synthetic
environments). Required: all four when present.

| Field | Type | Present | Nullable | Constraint |
|---|---|---|---|---|
| `seed` | integer \| null | yes | yes | `null` when the generator is unseeded |
| `config_path` | string, non-empty | yes | no | Repo-relative |
| `config_digest` | `hex64` | yes | no | SHA-256 of the config bytes |
| `code_version` | string, non-empty | yes | no | Commit or version of the generating code |

**`N-22` `datasets.leakage_audit`** — fixed-key. Required: all four.

| Field | Type | Present | Nullable | Constraint |
|---|---|---|---|---|
| `audited` | boolean | yes | no | |
| `at` | `timestamp` \| null | yes | yes | Non-null required when `audited = true` |
| `by` | string, non-empty \| null | yes | yes | Non-null required when `audited = true` |
| `findings` | array[string] | yes | no | May be empty; an empty findings list with `audited = true` is a clean audit, which is different from no audit |

**`N-23` `datasets.splits`** — **map-keyed**, the only one in the LSKE. `minProperties: 1`;
`propertyNames: {"pattern": "^[a-z][a-z0-9_]{0,31}$"}`; `additionalProperties` is exactly `N-24`.

**`N-24` `datasets.splits.<name>`** — fixed-key. Required: both.

| Field | Type | Present | Nullable | Constraint |
|---|---|---|---|---|
| `digest` | `hex64` | yes | no | SHA-256 of the partition's canonical content |
| `record_count` | integer | yes | no | ≥ 0 |

**`N-25` `theories.risky_prediction`** — fixed-key, nullable at the field level. Required: all five when
present.

| Field | Type | Present | Nullable | Constraint |
|---|---|---|---|---|
| `statement` | string, non-empty | yes | no | The novel prediction |
| `observable` | string, non-empty | yes | no | What would be measured |
| `declared_null` | string, non-empty | yes | no | Lock E2 |
| `established_at` | `timestamp` | yes | no | Compared against the run start for R2-12's pre-run test |
| `outcome` | string | yes | no | `enum` of `DIMENSION_STATES` — the same four values, because a prediction's outcome is assessed by the same lattice and a fifth vocabulary would be a second way to say the same thing |

**`N-26` `decisions.dissent[]` item** — fixed-key. Required: all three. The array may be empty;
recorded dissent is never removed (§1.4.11).

| Field | Type | Present | Nullable |
|---|---|---|---|
| `by` | string, non-empty | yes | no |
| `at` | `timestamp` | yes | no |
| `statement` | string, non-empty | yes | no |

**`N-27` `evidence.unexcluded_alternatives[]` item** — fixed-key. Required: both.

| Field | Type | Present | Nullable | Constraint |
|---|---|---|---|---|
| `statement` | string, non-empty | yes | no | May be agent-drafted (R1-16) |
| `why_not_excluded` | string | yes | no | Human-only content; the **empty string** while the record is `CANDIDATE` (RC-11 cl. 2). Non-empty with `authority.is_human = false` is a store-integrity error |

**`N-28` `sessions.annotations[]` item** — fixed-key. Required: all three.

| Field | Type | Present | Nullable |
|---|---|---|---|
| `at` | `timestamp` | yes | no |
| `target_id` | `record_id` | yes | no |
| `text` | string, non-empty | yes | no |

### Relation object

**`N-29` `relation.record_version_at`** — fixed-key. Required: both.

| Field | Type | Present | Nullable | Constraint |
|---|---|---|---|---|
| `source` | integer | yes | no | ≥ 1 |
| `target` | integer | yes | no | ≥ 1 |

### Render payload objects

**`N-30` `obs2.schema.json` top level** — fixed-key, standalone, `additionalProperties: false`.
Required: all thirteen. The field set is exactly `RenderPayload` (§6.6); no field is added.

| Field | Type | Present | Nullable | Constraint |
|---|---|---|---|---|
| `schema` | string | yes | no | `const: "obs/2"` (R7-3) |
| `plate` | string | yes | no | `^V(0[1-9]\|[12][0-9]\|3[0-6])$` |
| `phase` | string, non-empty | yes | no | R7-3 |
| `subject` | string, non-empty | yes | no | An identifier, never a label (R7-3) |
| `cause` | string, non-empty | yes | no | An `event_id`, a `record_id`, or the literal `"unattributed"` (R7-4) |
| `zoom_level` | integer | yes | no | 1–8 inclusive |
| `primitive` | string | yes | no | `enum` of `PRIMITIVES` |
| `nodes` | array[`N-31`] | yes | no | May be empty |
| `edges` | array[`N-31`] | yes | no | May be empty |
| `overlays` | `N-32` | yes | no | Exactly eight keys |
| `store_content_hash` | `hex64` | yes | no | |
| `snapshot_id` | `record_id` \| null | yes | yes | `null` for a present-state payload |
| `governance_banner` | string \| null | yes | yes | Non-null while the store is unregistered (R0-3, R7-27) |

**`N-31` `obs2` `nodes[]` / `edges[]` item** — `{"type": "object"}`, interior unconstrained by the
LSKE. See note 3.

**`N-32` `obs2.overlays`** — map-shaped and Observatory-owned: `minProperties: 8`,
`maxProperties: 8`, `propertyNames: {"pattern": "^[a-z][a-z0-9_]{0,31}$"}`, `additionalProperties:
{"type": "object"}`. See note 3.

### Notes

**Note 1 — `provenance.source_paths`.** §1.1 Block D requires "repo-relative paths **plus content
hashes**"; §9.2.1's `array<string>` cannot carry both. Under RC-04, §1.1 governs and §9.2.1 is its
typed restatement, so the item type is the closed object `N-05`. This is the only place in this
amendment where a declared type changes, and it changes to the shape that can hold the content §1.1
already required. The migration tool (§9.8.1) maps a legacy bare-string `source` to
`{path, content_hash}`; where the content hash of a legacy source cannot be produced, the record's
`provenance_reliability` is already `legacy_uncertain` under §9.8.1 cl. 2 and the hash is the SHA-256
of the file as found at migration time, recorded with that reliability rather than fabricated.

**Note 2 — `runs.admissibility` field names.** §1.4.5 names the four keys `{admissible, tier, ceiling,
reasons}` and RC-06 makes §1.4 authoritative for field names, so the stored key is `ceiling` even
though `ros.admissibility.Verdict` calls its attribute `ceilings`. The mapping is fixed and total:
`admissible ← Verdict.admissible`, `tier ← Verdict.tier.value`, `ceiling ← list(Verdict.ceilings)`,
`reasons ← list(Verdict.reasons)`. Renaming the stored key would introduce a second name for one field
(RC-06 cl. 1); leaving the mapping unstated would leave the implementer to guess. Neither is
acceptable, so the mapping is stated here and nowhere else.

**Note 3 — the Observatory boundary.** `obs2.schema.json` closes its own thirteen-key top level and
constrains the *shape* of `nodes`, `edges` and `overlays`. It does not constrain the interior of a node,
an edge or an overlay value, and it does not enumerate the eight overlay identifiers, because those
belong to `P1_OBSERVATORY_SCIENTIFIC_SPECIFICATION_v1.0.md` and R7-2 forbids the LSKE from adding or
redefining plate, overlay or zoom semantics. This is a **declared jurisdictional boundary, not an
undefined object**: the implementer knows exactly what to write, and the LSKE-side guarantees on those
interiors are the ones the LSKE already owns — R7-35/R7-37 vocabulary compliance over every emitted
field name, checked by test 18, and R7-8's prohibition on any node attribute derived from computed
similarity. A future enumeration of the eight overlay keys inside LSKE would be an Observatory
amendment routed through `constitution-clerk`, not a schema decision.


## 9.13 Phase-1 component ownership (new, RB-04 and RB-05)

### 9.13.0 Standing

This section is the single site of the Phase-1 API surface. It amends two sentences elsewhere:

- **§6.0 R6-1**, whose parenthetical said that `v2.lske.schema` "holds no API of its own", is reissued
  as: *one* further new module holds no API of its own — `v2.lske.errors` (the §9.5 taxonomy) — while
  `v2.lske.schema` carries the Phase-1 API surface specified in §9.13. Its disposition, dependency
  boundaries and module count are unchanged, and it remains a `new` module in the same layout row.
- **§6.8** gains one row, and only one: `v2.lske.schema.*` — write target **none**, minimum authority
  `OBSERVER`, human required **no**. The module reads, computes and validates; it writes nothing, so it
  needs no target. Every write of scientific state remains `v2.lske.transaction`'s (K1, RC-02).

`v2.lske.schema` is a **pure module**: no I/O, no clock, no environment lookup, no randomness, no
network. It imports `ros.model`, `ros.authority`, `ros.admissibility`, `ros.protocol` and
`v2.lske.errors`, and nothing else from the repository. It imports nothing from the runtime tree
(R6-2, I-30).

### 9.13.1 Ownership map — one owner per Phase-1 component

| Phase-1 component | Owning module | Public surface |
|---|---|---|
| JSON Schema dictionaries (23) | `v2.lske.schema` | `record_schema`, `collection_schema`, `relation_schema`, `obs2_schema`, `all_schemas` |
| Frozen literal registers | `v2.lske.schema` | §9.13.2 |
| Twenty collection specifications | `v2.lske.schema` | `COLLECTION_SPECS`, `COLLECTION_SPEC_BY_KEY` |
| Validation | `v2.lske.schema` | `validate` — the only public validator in `v2/lske/` |
| Immutable record model | `v2.lske.schema` | `LskeRecord` |
| Record identifier allocation | `v2.lske.schema` | `allocate_record_id` |
| Event identifier allocation | `v2.lske.schema` | `allocate_event_id` |
| Canonical serialization and hashing | `v2.lske.schema` | `canonical_json`, `content_hash`, `seal` |
| Exception taxonomy | `v2.lske.errors` | §9.5, unchanged |
| Durable event log writer | `v2.lske.events` | RC-07, unchanged; allocates no identifier of its own |
| Identifier *parsing* | `ros.model` | `ID_PATTERN`, `prefix_of`, `collection_for_id` — unchanged, not duplicated |
| Protocol canonical bytes | `ros.protocol` | `canonical_bytes` — unchanged, reused by R9-3 |

Every row has exactly one owner, and no component appears in two rows.

### 9.13.2 Frozen literal registers

```python
SCHEMA_DRAFT: str                       # "https://json-schema.org/draft/2020-12/schema"
SCHEMA_BASE_URI: str                    # "https://p1.local/schemas/lske/"
ONTOLOGY_VERSION: str                   # the semver written into every record's ontology_version

PRIMITIVES: tuple[str, ...]             # 19, section 0.3 order
DIMENSION_KEYS: tuple[str, ...]         # 10, Lock order (section 1.1 Block F)
DIMENSION_STATES: tuple[str, ...]       # 4, R4-3 order
LIFECYCLE_STATES: tuple[str, ...]       # 5, section 1.1 Block G
LIFECYCLE_TRANSITIONS: tuple[tuple[str, str], ...]   # the 7 frozen pairs, Block G
CHANGE_KINDS: tuple[str, ...]           # 8, section 1.1 Block C
RELATION_TYPES: tuple[str, ...]         # 15, section 2.3
CONFIDENCE_BASES: tuple[str, ...]       # 3, section 2.2

@dataclass(frozen=True)
class CollectionSpec:
    key: str
    prefix: str
    object_type: str
    primitive: str
    append_only: bool

COLLECTION_SPECS: tuple[CollectionSpec, ...]              # exactly 20, section 1.2 order
COLLECTION_SPEC_BY_KEY: Mapping[str, CollectionSpec]      # MappingProxyType
```

Every `prefix` in `COLLECTION_SPECS` matches `^[A-Z]{3,5}$` and yields an identifier
`ros.model.ID_PATTERN` accepts (R9-18); `research_questions` carries `RQS` (RB-06).

Registers a frozen module already holds are imported and never restated (RB-05 cl. 5):
`ros.model.EVIDENCE_DIRECTIONS`, `ros.model.HYPOTHESIS_STATUSES`, `ros.model.DECISION_ACTIONS`,
`ros.authority.AuthorityClass`, `ros.authority.EVIDENCE_TARGETS`,
`ros.authority.ENGINEERING_TARGETS`, `ros.admissibility.Tier`.

### 9.13.3 Validation — one entry point

```python
def all_schemas() -> Mapping[str, dict[str, Any]]: ...
    # 23 entries keyed by schema name: "record", the 20 collection keys, "relation", "obs2".
    # Returns deep-immutable views; a caller cannot mutate a schema dict.

def record_schema() -> dict[str, Any]: ...
def collection_schema(collection_key: str) -> dict[str, Any]: ...
def relation_schema() -> dict[str, Any]: ...
def obs2_schema() -> dict[str, Any]: ...

def validate(payload: Mapping[str, Any], schema_name: str) -> None: ...
    # The single public validation entry point of v2/lske/ (RB-05 cl. 1).
    # schema_name is a key of all_schemas(). Returns None on success.
    # Raises SchemaViolation naming the instance pointer, the schema pointer and the
    # failing keyword, in that order; raises OntologyError when schema_name is unknown.
    # Never raises a bare ValueError or AssertionError (section 9.5).
```

**Rule R9-14.** `validate` is the only public callable in `v2/lske/` whose name begins with `validate`,
and no other module in `v2/lske/` defines a public validation function. Every validating call site —
`LskeRecord.from_payload`, `v2.lske.events`, `v2.lske.transaction` phases, the migration tool — calls
this one function. A second validator would eventually disagree with the first, and the record that
passed one and failed the other would have no defined status.

**Rule R9-15.** `validate` reports **all** failures for the payload, not the first, ordered by instance
pointer ascending. `SchemaViolation` carries them as a tuple on the exception instance. A validator that
stops at the first failure makes a ten-field record take ten runs to fix, and it makes a schema
regression look smaller than it is.

**Rule R9-15.1 (the derived closure finding).** When any `allOf` branch fails, Draft 2020-12 discards
that branch's `properties` annotations, so the sibling `unevaluatedProperties: false` also fails and
names every property the failed branch declared. `validate` reports such an `unevaluatedProperties`
finding **last** and marks it `derived: true`; it is a consequence of the primary failure, not a second
defect. This behaviour is a property of the dialect, was confirmed empirically (Appendix C.1), and is
stated here so that an implementer does not read a cascade as a schema bug and "fix" it by removing the
closure keyword — which would reopen `BLK-P1-01`.

### 9.13.4 The immutable record model

```python
@dataclass(frozen=True)
class LskeRecord:
    """One validated, deeply immutable LSKE record. Public. The record model of Phase 1."""

    collection_key: str
    payload: Mapping[str, Any]          # deep-frozen; MappingProxyType at every level

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any], collection_key: str) -> "LskeRecord": ...
        # The only public constructor. Validates via validate(payload, collection_key),
        # then deep-freezes. Raises SchemaViolation on invalid input, OntologyError on an
        # unknown collection_key. There is no validate=False and no unsafe constructor.

    @property
    def id(self) -> str: ...                    # payload["id"]
    @property
    def object_type(self) -> str: ...           # payload["type"]
    @property
    def primitive(self) -> str: ...             # payload["primitive"]
    @property
    def record_version(self) -> int: ...
    @property
    def lifecycle_state(self) -> str: ...       # payload["lifecycle"]["state"]
    @property
    def stored_content_hash(self) -> str: ...   # payload["content_hash"], as written
    @property
    def content_hash(self) -> str: ...          # recomputed over blocks A-G (R9-3)
    @property
    def sealed(self) -> bool: ...               # payload["immutability"]["frozen_at"] is not None

    def as_dict(self) -> dict[str, Any]: ...    # deep mutable copy; mutating it cannot reach self
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
```

The contract, in seven clauses, each of which is a test assertion in row 2 of §9.6:

1. **Owning module.** `v2.lske.schema`. Public, exported in `__all__`. Not in `ros.store`, not in
   `ros.model`, not aliased. `ros.store.Record` is a different class with a different name, module and
   contract, and neither is defined in terms of the other (RB-04 cl. 1).
2. **Constructor.** `from_payload` is the only public constructor. The generated `__init__` accepts only
   an already-frozen mapping; given anything else it raises `SchemaViolation`, so the validation step
   cannot be bypassed by calling the dataclass directly (RB-04 cl. 5).
3. **Immutability.** `frozen=True`; mappings stored as `MappingProxyType`, sequences as `tuple`; no
   method returns a mutable reference to internal state; `as_dict` returns a deep copy. Sets and
   `datetime` objects never appear in a payload — timestamps are `S-02` strings — so the frozen form is
   total and JSON-round-trippable (RB-04 cl. 3).
4. **Equality.** Structural over `(collection_key, payload)`, whole payload, Block H included. Two
   records with identical blocks A–G but different seals are **not** equal (RB-04 cl. 4).
5. **Hashing behaviour, two hashes, never conflated.** `__hash__` is
   `int.from_bytes(sha256(canonical_json({"collection": collection_key, "payload": as_dict()})).digest()[:8], "big")`
   — stable across processes and consistent with `__eq__`. `content_hash` is the **scientific** identity
   of R9-3, over blocks A–G only, and is never used as `__hash__` (RB-04 cl. 4).
6. **Validation entry point.** `validate(payload, collection_key)`, called by `from_payload`, and
   nothing else (RB-04 cl. 5).
7. **Integrity is comparison, not trust.** `content_hash` is always recomputed and
   `stored_content_hash` is always the written value. `MEM-04` (stage 4) is exactly the assertion that
   the two agree for a sealed record. A model that returned the stored value as its hash could not
   detect the tampering `MEM-04` exists to detect.

### 9.13.5 Identifier allocation

```python
def allocate_record_id(collection_key: str, existing: Iterable[str], year: int) -> str: ...
    # PREFIX-YYYY-NNNN (section 1.1 Block A). Pure: no clock, no store access.
    # NNNN = 1 + the maximum fourth-group value among `existing` identifiers sharing this
    # prefix and year, zero-padded to four digits; 0001 when none exists. Sequences are
    # never reused, including after deletion, because `existing` is the set of every
    # identifier the store has ever held, DELETED stubs included (R3-3).
    # Raises OntologyError on an unknown collection_key or on exhaustion above 9999.

def allocate_event_id(payload: Mapping[str, Any]) -> str: ...
    # LEV-<32 lowercase hex> (S-07): the first 32 hex characters of the SHA-256 of
    # canonical_json(payload) over the event body of section 9.3.1 --
    # {kind, at, by, authority, target, record_id, from, to, cause} -- with any pre-existing
    # event_id key removed first. Content-addressed, so re-emitting one event cannot produce
    # two identifiers, which is what R9-7's no-re-emit rule needs in order to be checkable.
    # Raises SchemaViolation when a required event-body key is absent.
```

**Rule R9-16.** These two functions are the only identifier allocators in the repository. Parsing stays
in `ros.model` (RB-05 cl. 2). `receipt_id` is not an identifier in this sense: §9.3.1 already fixes its
form as `RCPT-<run_id>-<n>` and states that it is engineering bookkeeping rather than a record address,
so it is constructed at its single use site in `v2.lske.transaction` and no allocator is added for it.

### 9.13.6 Canonical serialization and hashing

```python
def canonical_json(payload: Mapping[str, Any]) -> bytes: ...
    # Delegates to ros.protocol.canonical_bytes (R9-3): sorted keys, no insignificant
    # whitespace, UTF-8, keys beginning with "_" dropped. Not re-implemented here.

def content_hash(payload: Mapping[str, Any]) -> str: ...
    # SHA-256 hex over canonical_json(payload minus the top-level keys "content_hash" and
    # "immutability"): blocks A-G, Block H excluded (R9-3, I-56). Removal is top-level only;
    # nested content is hashed as it stands.

def seal(content_hash_hex: str, frozen_at: str) -> str: ...
    # SHA-256 hex over canonical_json({"content_hash": content_hash_hex, "frozen_at": frozen_at}).
    # Block H's seal (section 1.1). Present iff frozen_at is set.
```

**Rule R9-17.** SHA-256 is the LSKE's only hash function and these three functions are its only call
sites in `v2/lske/`. `ros.protocol.digest` remains BLAKE2b-256 and is neither reused nor reimplemented:
the one place a BLAKE2b digest appears in an LSKE schema is `protocols.digest` and `protocols.freeze`
(`N-14`), where the value is **copied** from `ros.protocol` and the algorithm is recorded in the payload.
Two hash algorithms with one recorded name would make a digest unverifiable, so every digest field in
this specification names its algorithm.

### 9.13.7 What is not in this module

Exhaustively: no store access, no file write, no receipt handling, no confidence computation, no
reasoning, no rendering, no query parsing, no transaction phase, no event append, no gate, no KPI, no
CLI, no `__main__`. `v2.lske.schema` is imported by `v2.lske.events`, `v2.lske.transaction`,
`v2.lske.memory`, `v2.lske.confidence` and the migration tool; it imports none of them, so the Phase-1
module sits at the bottom of the LSKE dependency order and can be built and tested before any later
stage exists.

## 9.6 Test matrix (reissued rows 1–3)

The matrix remains **twenty-three rows**; no test file is added and none is renamed. Rows 1–3 — the
stage-1 rows — have their *Asserts* cells reissued to carry the Phase-1 contracts this amendment fixes.

| # | Test file | Asserts (reissued) |
|---|---|---|
| 1 | `test_schema_generation.py` | `schemas/lske/*.json` byte-match the dicts in `v2.lske.schema` under the serialization of RB-01 cl. 8, for all twenty-three files (R9-2); every dict compiles under a Draft 2020-12 validator and every `$ref` resolves inside the offline registry (RB-01 cl. 7); every collection schema has the shape of §9.2.0.1 — one `allOf` of exactly two `$ref`s, a sibling `unevaluatedProperties: false`, no `additionalProperties` at its top level, no `$dynamicRef`, depth two (RB-01 cl. 1, cl. 3); `record.schema.json` carries no top-level `additionalProperties` and no top-level `unevaluatedProperties` (RB-01 cl. 2); every object in every schema is closed by the form RB-01 cl. 4 assigns it and appears in the §9.2.4 catalogue; no `if/then` introduces a property absent from its subschema's `properties` (RB-01 cl. 5); every collection narrowing is a subset of the envelope's admitted set (§9.2.0 cl. 7). On divergence or absence the test writes the expected file and fails in the same run, so a schema change reaches version control as a reviewable diff and can never pass silently. |
| 2 | `test_envelope.py` | All eight blocks required and every §9.2.4 object closed — for each of the thirty-two catalogue entries, a payload with one undeclared key is rejected and the minimal legal payload is accepted; `content_hash` excludes block H (R9-3, I-56); a record that differs only in `immutability.seal` has the same `content_hash` and a different `LskeRecord.__hash__` and compares unequal (§9.13.4 cl. 4–5); `LskeRecord.from_payload` raises `SchemaViolation` on an invalid payload and the dataclass constructor raises on an unfrozen mapping (§9.13.4 cl. 2); `as_dict()` mutation cannot reach the record (cl. 3); `validate` is the only public validator in `v2/lske/` and reports all failures ordered by instance pointer (R9-14, R9-15); the relation envelope admits exactly the ten keys of §0X.4, rejects `independence_group` and `post_hoc`, requires `direction` non-null for the four evidential types and null for the other eleven, and the `edge_state` derivation of RB-02 cl. 4 returns each of its four outcomes on a constructed case; `obs2.schema.json` closes its thirteen keys. |
| 3 | `test_collections.py` | `COLLECTION_SPECS` has exactly twenty entries in §1.2 order, with unique keys and unique prefixes; every prefix matches `^[A-Z]{3,5}$` and `ros.model.ID_PATTERN` matches a generated identifier for all twenty prefixes — including `RQS` (RB-06), the five-character `SDEBT` and the four-character `DSET` and `SNAP` — and `ID_PATTERN` itself is unmodified (R9-18); `allocate_record_id` returns `0001` on an empty set, `max + 1` within a prefix and year, is stable under input order, never reuses a sequence including after a `DELETED` stub, and raises `OntologyError` above `9999` (§9.13.5); `allocate_event_id` is content-addressed, stable across calls, and never matches `ros.model.ID_PATTERN`; each spec's `primitive` is a member of `PRIMITIVES` and the eight `Claim`-realizing collections are exactly those of §1.3. **From stage 2 onward** the same file additionally asserts that `ros.model.COLLECTIONS` and `COLLECTION_SPECS` agree on key, prefix, `object_type` and `append_only` for all twenty (RB-05 cl. 6). |

Rows 4–23 are unchanged, save that row 11's `DimensionState` assertions now read the enumeration
constructed over `DIMENSION_STATES` (RB-05 cl. 5), which is the same four values it already asserted.

## 9.8 Build order (reissued exit conditions, stages 1 and 2)

| Stage | Deliverable | Exit condition (reissued) |
|---|---|---|
| 1 | `v2.lske.schema` (schemas, registers, `COLLECTION_SPECS`, `validate`, `LskeRecord`, allocators, hashing) + `v2.lske.errors` + `v2.lske.events` + `schemas/lske/*` | Tests 1 and 2 pass in full; test 3 passes **except** its stage-2 clause, which is skipped by an explicit stage marker rather than by omission; the durable event log exists and is append-only (RC-07); **no** change to `ros.model` yet |
| 2 | `ros.model` 11 → 20, docstring fixed | The existing store still loads; test 3 passes in full, including the `COLLECTIONS` ↔ `COLLECTION_SPECS` agreement clause (RB-05 cl. 6) |

Stages 3–9 are unchanged, including the non-negotiable ordering of stage 3 before stage 5. The stage-1
exit condition of v1.1.0 required test 3 to pass while forbidding the `ros.model` change test 3 was
written against; the reissued pair resolves that without moving a deliverable between stages.

## 9.8.1 Migration (one clause amended)

Clause 1 of §9.8.1 is unchanged except that a legacy bare-string `source` field maps to the
`provenance.source_paths` item shape `N-05` per §9.2.4 note 1, and a legacy `legacy_ids` array is
retained as the optional array of strings §9.2.2 rule 4 declares. Clauses 2–5 and R9-11 are unchanged.


## 9.9 What the implementer may decide (reissued)

Unchanged in substance. The list of what is **not** open gains, by this amendment: the schema
composition contract of §9.2.0; the closed nested object catalogue of §9.2.4 (`S-01`…`S-07`,
`N-01`…`N-32`); the ten-field relation envelope of §0X.4 and the derived `edge_state` rule; the
ownership map of §9.13.1; the public surface of `v2.lske.schema` (§9.13.2–§9.13.6); the rulings `RB-0`,
`RB-0.1`, `RB-0.2` and `RB-01`…`RB-06`; the `research_questions` prefix `RQS`; and the rules `R9-14`,
`R9-15`, `R9-15.1`, `R9-16`, `R9-17`, `R9-18`. What remains open is exactly what
§9.9 already listed: private helper names and signatures, internal data structures inside a function
body, log wording outside exception text, test fixture file names, the order of independent assertions
within a test, and docstring prose.

**Rule R9-12.** Unchanged. This document is the amendment R9-12 requires for the items above, issued at
a new version number under R9-0.

---

# APPENDIX A — Rule matrix (amended entries)

## A.1B Blocker-elimination decision matrix (machine-readable)

Every decision point the Phase-1 blocker report named, with exactly one value. A value of `none` is a
decision, not an omission.

```yaml
lske_blocker_elimination_matrix:
  spec_version: "1.1.1"
  amends: "1.1.0"
  closes: ["BLK-P1-01", "BLK-P1-02", "BLK-P1-03", "BLK-P1-04", "BLK-P1-05"]

  # RB-01
  json_schema_dialect: "https://json-schema.org/draft/2020-12/schema"
  composition_mechanism: "allOf of exactly two $refs, closed by a sibling unevaluatedProperties: false"
  inheritance_strategy: "single-level, single-parent, depth exactly two; no $dynamicRef"
  base_schema_top_level_additional_properties: none
  base_schema_top_level_unevaluated_properties: none
  closed_world_composed_object: "unevaluatedProperties: false"
  closed_world_fixed_key_object: "additionalProperties: false"
  closed_world_map_keyed_object: "propertyNames + single closed value schema + minProperties"
  map_keyed_objects: ["datasets.splits", "obs2.overlays"]
  conditional_mechanism: "if/then over required only, inside #/$defs/collection"
  validation_passes_per_record: 1
  validation_target: "the collection schema"
  ref_resolution: "offline registry of 23 schemas; relative refs under https://p1.local/schemas/lske/"
  generated_file_serialization: 'json.dumps(schema, ensure_ascii=False, indent=2, sort_keys=True) + "\n", UTF-8, LF'
  normative_example: "section 9.2.0.1 (record.schema.json + programs.schema.json)"
  alternative_mechanisms: none

  # RB-02
  relation_canonical_section: "2.2 as reissued in 0X.4"
  relation_field_count: 10
  relation_required_keys: ["from","to","type","direction","semantic_note","established_by","established_at","record_version_at","retracted_by","confidence_basis"]
  relation_optional_keys: none
  relation_nullable_keys: ["direction","retracted_by"]
  relation_direction_rule: "non-null iff type is one of the four Class 1 evidential types"
  relation_independence_group: none
  relation_post_hoc: none
  relation_lifecycle_field: none
  relation_lifecycle_representation: "derived edge_state by the ordered rule of RB-02 cl. 4"
  relation_retraction: "retracted_by set once to a decisions id; never unset; edge never removed"
  relation_numeric_fields: none
  sql_p1_grammar_tokens_added: none

  # RB-03
  nested_object_catalogue_section: "9.2.4"
  shared_scalar_defs: 7
  nested_objects_and_items: 32
  partially_defined_objects_remaining: 0
  source_paths_item_shape: "{path, content_hash}"
  admissibility_object_keys: ["admissible","tier","ceiling","reasons"]
  freeze_object_source: "ros.protocol.Freeze.to_dict()"
  environment_object_source: "ros.events.environment()"
  scope_object_definitions: 1
  observatory_owned_interiors: ["obs2.nodes[]","obs2.edges[]","obs2.overlays.*"]

  # RB-04
  record_model_class: "v2.lske.schema.LskeRecord"
  record_model_module: "v2.lske.schema"
  record_model_visibility: "public"
  record_model_constructor: "LskeRecord.from_payload(payload, collection_key)"
  record_model_alternate_constructors: none
  record_model_equality: "structural over (collection_key, whole payload including block H)"
  record_model_hash: "SHA-256 over canonical_json of collection_key + whole payload, truncated to 64 bits"
  record_model_scientific_hash: "content_hash over blocks A-G only; never used as __hash__"
  record_model_immutability: "frozen dataclass; MappingProxyType and tuple at every level; as_dict returns a deep copy"
  record_model_validation_entry_point: "v2.lske.schema.validate"
  files_added_to_frozen_layout: none

  # RB-05
  validation_entry_points: 1
  validation_api: "v2.lske.schema.validate(payload, schema_name)"
  validation_error_type: "SchemaViolation"
  validation_reports: "all failures, ordered by instance pointer"
  record_id_allocator: "v2.lske.schema.allocate_record_id"
  event_id_allocator: "v2.lske.schema.allocate_event_id"
  event_id_form: "LEV-<32 lowercase hex>, content-addressed"
  identifier_parsers: "ros.model.ID_PATTERN / prefix_of / collection_for_id"
  canonical_serialization: "ros.protocol.canonical_bytes via v2.lske.schema.canonical_json"
  hash_algorithm: "SHA-256"
  protocol_digest_algorithm: "BLAKE2b-256 (ros.protocol.digest), copied never recomputed"
  collection_metadata_owner_phase1: "v2.lske.schema.COLLECTION_SPECS"
  collection_metadata_owner_from_stage2: "ros.model.COLLECTIONS aligned to COLLECTION_SPECS"
  dimension_literal_site: "v2.lske.schema.DIMENSION_KEYS / DIMENSION_STATES"
  dimension_type_site: "v2.lske.confidence.DimensionState, constructed over DIMENSION_STATES"
  schema_module_write_target: none
  schema_module_authority: "OBSERVER"
  test_files_added: none
  build_stages_added: none

  # RB-06
  research_questions_prefix: "RQS"
  research_questions_prefix_before: "RQ"
  id_pattern: "unchanged: ros.model.ID_PATTERN, ^[A-Z]{3,5}-\\d{4}-\\d{4}$"
  prefixes_changed: 1
  prefix_conformance_rule: "R9-18"
```

## A.2 Single-definition registers (amended rows only)

| Register | Size | Canonical section |
|---|---|---|
| Shared scalar schema types | 7 | §9.2.4 (`S-01`…`S-07`) |
| Nested objects and array items | 32 | §9.2.4 (`N-01`…`N-32`) |
| Relation envelope fields | 10 | §2.2 as reissued in §0X.4 |
| Schema composition mechanisms | 1 | §9.2.0 |
| Closed-world forms | 3 | RB-01 cl. 4 |
| Public validation entry points | 1 | §9.13.3 |
| Identifier allocators | 2 | §9.13.5 |
| Canonical hashing functions | 3 | §9.13.6 |
| Immutable record models | 1 | §9.13.4 |
| Blocker-elimination rulings | 6 (+ `RB-0`, `RB-0.1`, `RB-0.2`) | Part 0X |
| Record collection prefixes | 20, all `^[A-Z]{3,5}$` | §1.2 as amended by RB-06 |

Every other row of A.2 is unchanged. `Test matrix rows` remains **23** and `Build stages` remains
**9**: this amendment adds neither.

## A.3 API register (amended rows only)

| Module | Function | Authority / write target |
|---|---|---|
| `v2.lske.schema` | `record_schema`, `collection_schema`, `relation_schema`, `obs2_schema`, `all_schemas` | `OBSERVER` / none |
| `v2.lske.schema` | `validate` | `OBSERVER` / none |
| `v2.lske.schema` | `allocate_record_id`, `allocate_event_id` | `OBSERVER` / none |
| `v2.lske.schema` | `canonical_json`, `content_hash`, `seal` | `OBSERVER` / none |
| `v2.lske.schema` | `LskeRecord.from_payload` and the read-only properties of §9.13.4 | `OBSERVER` / none |

No function above appears in a second module, and no module exposes a second spelling of any of them.
Every other row of A.3 is unchanged.

## A.4 Schema register (amended)

| Schema file | Canonical source | Defined in | Composition |
|---|---|---|---|
| `schemas/lske/record.schema.json` | `v2.lske.schema.record_schema()` | §1.1 normative; §9.2.1 typed restatement; §9.2.4 nested objects | fragment; composes nothing; holds `$defs` |
| `schemas/lske/<collection>.schema.json` (20) | `v2.lske.schema.collection_schema(key)` | §1.4 normative; §9.2.2 typed restatement | `allOf` of two `$ref`s + `unevaluatedProperties: false` |
| `schemas/lske/relation.schema.json` | `v2.lske.schema.relation_schema()` | §2.2 as reissued in §0X.4; §9.2.3 typed restatement | standalone; `additionalProperties: false` |
| `schemas/lske/obs2.schema.json` | `v2.lske.schema.obs2_schema()` | §6.6 `RenderPayload`; §7.1; §9.2.4 `N-30`…`N-32` | standalone; `additionalProperties: false` |

Twenty-three files, one canonical source each. Divergence between a dict and its generated file fails
test 1 (R9-2). No schema has a second hand-maintained copy anywhere.

---

# APPENDIX C — Implementation-readiness audit (v1.1.1)

There is no Appendix B here: v1.1.0's Appendix B (reconciliation verification) stands unchanged and is
not re-run, so the letter is left to it rather than reused. This appendix is the *implementation
readiness* audit, which v1.1.0 explicitly declined to certify ("this appendix certifies reconciliation,
not readiness").

Each check states its method so that it can be re-run against this document plus v1.1.0. A check whose
method cannot be re-run is an opinion.

## C.1 Every JSON Schema is implementable

**Method.** Construct each of the twenty-three schemas from §9.2.0, §9.2.1, §9.2.2, §9.2.3 and §9.2.4;
for the two in §9.2.0.1, do so literally; check each against Draft 2020-12's keyword semantics for a
minimal legal instance and for an instance carrying one undeclared key at every object level.
**Result.** **Pass.** The v1.1.0 unsatisfiability is removed at its cause: `additionalProperties: false`
no longer sits on a base subschema that cannot see its sibling's properties, and closure is asserted by
`unevaluatedProperties: false` on the composing schema, which by dialect definition sees both branches'
`properties` annotations. A `programs` record carrying the sixteen envelope keys plus five collection
keys validates; the same record plus one undeclared key fails; a record missing any required key fails.
The map-keyed and Observatory-owned cases are the only objects whose keys are not enumerated, and both
are closed on key form and value shape.

## C.2 Every nested object is complete

**Method.** Enumerate every object-valued and array-of-object-valued field named anywhere in v1.1.0
Parts 1, 2, 6, 7 and 9; match each against a §9.2.4 entry; check each entry for properties, required
set, types, nullability and closure form.
**Result.** **Pass.** Thirty-two entries cover every such field, including the nine the blocker report
named — `provenance.citation`, `confidence.scope` (`population`, `regime`, `limits`),
`protocols.freeze`, `protocols.sesoi`, `runs.admissibility`, `runs.environment`,
`observations.uncertainty`, `observations.coverage`, `observations.declared_null_comparison`,
`datasets.generator`, `datasets.leakage_audit`, `datasets.splits`, `theories.risky_prediction`,
`decisions.dissent` — plus the eleven the report did not name
(`created`, `revisions[]`, `authority`, `confidence`, `confidence.dimensions` and its entries,
`lifecycle`, `lifecycle.transitions[]`, `immutability`, `evidence.unexcluded_alternatives[]`,
`sessions.annotations[]`, `relation.record_version_at`) and the three render-payload entries. No entry
is partial: every field in every entry has a type, a presence rule and a nullability rule. Three
interiors are Observatory-owned by declared jurisdiction (§9.2.4 note 3), which is a boundary, not a
gap.

## C.3 Every API has one definition

**Method.** Extract every public callable named in Part 6 and §9.13; check for duplicate names across
modules and for a second signature of any name elsewhere in v1.1.0 or v1.1.1.
**Result.** **Pass.** Part 6's thirty-two module-level signatures are untouched. §9.13 adds thirteen
public names, all in `v2.lske.schema`, none of which collides with a Part 6 name or with a name in
`ros.*`: `record_schema`, `collection_schema`, `relation_schema`, `obs2_schema`, `all_schemas`,
`validate`, `allocate_record_id`, `allocate_event_id`, `canonical_json`, `content_hash`, `seal`,
`LskeRecord`, `CollectionSpec`. The one name that could have collided — `Record` — was deliberately not
used, because `ros.store.Record` exists (RB-04 cl. 1).

## C.4 Every module has one owner

**Method.** For each Phase-1 component, count the modules that may implement it.
**Result.** **Pass.** §9.13.1's twelve rows each name exactly one owner, and no component appears twice.
`v2/lske/schema.py` owns four previously unowned components; `v2/lske/events.py` owns the durable log
and allocates no identifier; `ros.model` keeps identifier parsing; `ros.protocol` keeps canonical bytes.

## C.5 Every validator has one entry point

**Method.** Search v1.1.0 and v1.1.1 for any public validating callable in `v2/lske/`.
**Result.** **Pass.** Exactly one: `v2.lske.schema.validate`. R9-14 forbids a second, and test 2
asserts its uniqueness by name inspection of the package's public surface. `Store.check()` remains a
distinct, store-level integrity check owned by `ros.store` (§9.4.2) — it validates the store, not a
record payload, and the two have no overlapping subject.

## C.6 Every identifier utility has one owner

**Method.** Enumerate identifier allocation, parsing and formatting sites.
**Result.** **Pass.** Allocation: `allocate_record_id`, `allocate_event_id`, both in
`v2.lske.schema` (R9-16). Parsing: `ros.model`, unchanged. Formatting of `receipt_id`: its single use
site in `v2.lske.transaction`, per §9.3.1's existing rule, with no allocator added. No fourth site
exists. Pattern conformance of all twenty prefixes was checked by execution and found to fail for
`RQ`; RB-06 moves that one prefix to `RQS` and R9-18 makes the check a stage-1 assertion.

## C.7 Every immutable model has one contract

**Method.** Check that the record model has exactly one statement of owning module, visibility,
constructor, equality, immutability, hashing and validation entry point.
**Result.** **Pass.** §9.13.4, seven clauses, each with a test assertion in row 2. `LskeRecord` is the
only immutable record model in the LSKE; `ros.store.Record` remains the ROS store's mutable accessor and
is not redefined, aliased or wrapped.

## C.8 No conflicting rules remain

**Method.** Re-run the v1.1.0 Appendix B.4 domain table against the amended sections, then check each
`RB` ruling against every section it touches and every invariant that depends on it.
**Result.** **Pass.** Four v1.1.0 conflicts are removed and none is introduced:
`additionalProperties`/`allOf` (RB-01), `direction`/`retracted_by`/extra-field disagreement between
§2.2 and §9.2.3 (RB-02), R2-4's stateless edge lifecycle (RB-02 cl. 4), and the stage-1 exit condition
that required test 3 while forbidding its precondition (RB-05 cl. 6). One inherited wording defect was
corrected in passing because RB-02 made it visible: R4-4's `e.retracted_by` now names the edge rather
than a field the `evidence` collection does not have (§0X.7 cl. 5). Invariants `I-14`, `I-52`, `I-56`,
`I-58`, `I-59`, `I-60` were each re-checked against the amended schemas and each still holds with the
same detector.

## C.9 No duplicate definitions remain

**Method.** For each frozen register and each schema object, count definition sites.
**Result.** **Pass.** `scope` is defined once and referenced four times. The four states and ten
dimension names have one literal site (`v2.lske.schema`) and one type site
(`v2.lske.confidence.DimensionState`, constructed over that literal) — RB-05 cl. 5. `EVIDENCE_DIRECTIONS`,
`HYPOTHESIS_STATUSES`, `DECISION_ACTIONS`, `AuthorityClass`, the write targets and `Tier` are imported,
never restated. Two duplications present in v1.1.0 were deleted: `relations.independence_group`
(duplicate of `evidence.independence_group`) and `relations.post_hoc` (duplicate of a projection
computation). Shared scalar patterns have one `$defs` home each, in `record.schema.json`.

## C.10 No undefined references remain

**Method.** Extract every `$ref`, every `$defs` name, every rule identifier and every module, function,
register and file name referenced in this amendment; check each resolves to a definition in v1.1.1 or
v1.1.0.
**Result.** **Pass.** All `$ref` targets are among the twenty-three registered schemas or the
`record.schema.json#/$defs/*` names of §9.2.4. `RB-0`, `RB-0.1`, `RB-0.2`, `RB-01`…`RB-05` and
`R9-14`…`R9-17` are each defined once and each series is contiguous. `S-01`…`S-07` and `N-01`…`N-32` are
contiguous with no gaps and no duplicates. Every referenced ROS symbol was checked against the module
that defines it: `ros.model.ID_PATTERN`, `prefix_of`, `collection_for_id`, `EVIDENCE_DIRECTIONS`,
`HYPOTHESIS_STATUSES`, `DECISION_ACTIONS`, `normalise_term`; `ros.authority.AuthorityClass`
(`OBSERVER`, `PROPOSER`, `ENGINEER`, `SCIENTIST`), `EVIDENCE_TARGETS` (8), `ENGINEERING_TARGETS` (8);
`ros.admissibility.Tier` (4 values), `Verdict` (`tier`, `reasons`, `ceilings`, `admissible`);
`ros.protocol.canonical_bytes`, `digest`, `Freeze.to_dict()` (5 keys); `ros.events.environment()`
(3 keys), `KINDS` (9 kinds, unextended). No referenced symbol is absent from the repository.

## C.11 Every Phase-1 deliverable maps to one specification rule

**Method.** Enumerate the stage-1 deliverables of §9.8 as reissued, plus the four components the user's
Phase-1 scope names (schemas, record model, validators, identifier system); map each to exactly one rule
and one acceptance criterion.
**Result.** **Pass.** Appendix D is that mapping: twenty-three rows, each with exactly one requirement,
one module, one API, one schema, one test and one acceptance criterion.


---

# APPENDIX D — Phase-1 traceability

Twenty-three rows. Each row has exactly one requirement, one owning module, one API, one schema, one
test and one acceptance criterion. `none` is a decision, not an omission.

| # | Requirement | Module | API | Schema | Test | Acceptance criterion |
|---|---|---|---|---|---|---|
| 1 | RB-01 cl. 1 — composition mechanism | `v2.lske.schema` | `collection_schema` | `<collection>.schema.json` (20) | test 1 | `AC-P1-01` |
| 2 | RB-01 cl. 2 — envelope is a composable fragment | `v2.lske.schema` | `record_schema` | `record.schema.json` | test 1 | `AC-P1-02` |
| 3 | RB-01 cl. 4 — closed-world forms | `v2.lske.schema` | `all_schemas` | all 23 | test 1 | `AC-P1-03` |
| 4 | RB-01 cl. 6 — one validation pass | `v2.lske.schema` | `validate` | `<collection>.schema.json` | test 2 | `AC-P1-04` |
| 5 | RB-01 cl. 8 — fixed file serialization | `v2.lske.schema` | `all_schemas` | all 23 | test 1 | `AC-P1-05` |
| 6 | RB-02 cl. 1–3 — the ten-field relation envelope | `v2.lske.schema` | `relation_schema` | `relation.schema.json` | test 2 | `AC-P1-06` |
| 7 | RB-02 cl. 4 — edge lifecycle is derived, no stored field | `v2.lske.schema` | `relation_schema` | `relation.schema.json` | test 2 | `AC-P1-07` |
| 8 | RB-03 — closed nested object catalogue | `v2.lske.schema` | `record_schema` | `record.schema.json` `$defs` (`N-01`…`N-13`) | test 2 | `AC-P1-08` |
| 9 | RB-03 note 1 — `provenance.source_paths` item shape | `v2.lske.schema` | `record_schema` | `record.schema.json` `N-05` | test 2 | `AC-P1-09` |
| 10 | RB-03 note 2 — `runs.admissibility` mapping | `v2.lske.schema` | `collection_schema("runs")` | `runs.schema.json` `N-16` | test 2 | `AC-P1-10` |
| 11 | RB-03 note 3 — Observatory boundary | `v2.lske.schema` | `obs2_schema` | `obs2.schema.json` `N-30`…`N-32` | test 2 | `AC-P1-11` |
| 12 | RB-04 cl. 1–3 — immutable record model | `v2.lske.schema` | `LskeRecord.from_payload` | `<collection>.schema.json` | test 2 | `AC-P1-12` |
| 13 | RB-04 cl. 4 — equality and container hashing | `v2.lske.schema` | `LskeRecord.__hash__` | `record.schema.json` `S-04` | test 2 | `AC-P1-13` |
| 14 | RB-05 cl. 1 — one validation entry point | `v2.lske.schema` | `validate` | all 23 | test 2 | `AC-P1-14` |
| 15 | RB-05 cl. 2 — record identifier allocation | `v2.lske.schema` | `allocate_record_id` | `record.schema.json` `S-01` | test 3 | `AC-P1-15` |
| 16 | RB-05 cl. 2 — event identifier allocation | `v2.lske.schema` | `allocate_event_id` | `record.schema.json` `S-07` | test 3 | `AC-P1-16` |
| 17 | RB-05 cl. 3 / R9-3 — canonical hashing | `v2.lske.schema` | `content_hash` | `record.schema.json` `S-04` | test 2 | `AC-P1-17` |
| 18 | RB-05 cl. 5 — one literal site per register | `v2.lske.schema` | `DIMENSION_STATES` | `record.schema.json` `N-10` | test 2 | `AC-P1-18` |
| 19 | RB-05 cl. 6 — twenty collection specifications | `v2.lske.schema` | `COLLECTION_SPECS` | `<collection>.schema.json` (20) | test 3 | `AC-P1-19` |
| 20 | RC-07 — durable LSKE event log | `v2.lske.events` | append of `lifecycle` and `evidence` events | none — body fixed by §9.3.1 | test 2 | `AC-P1-20` |
| 21 | §9.5 — frozen exception taxonomy | `v2.lske.errors` | `SchemaViolation` | none — an exception is not a record | test 2 | `AC-P1-21` |
| 22 | RC-01 — package root and import path | `v2.lske` | `__init__` version constant | none — a namespace has no schema | test 1 | `AC-P1-22` |

| 23 | RB-06 / R9-18 — identifier pattern conformance | `v2.lske.schema` | `COLLECTION_SPECS` | `record.schema.json` `S-01` | test 3 | `AC-P1-23` |

## D.1 Acceptance criteria

Stage 1 is complete when, and only when, all twenty-three hold. Each is a single decidable statement.

- `AC-P1-01` Every collection schema is `allOf` of exactly two `$ref`s with a sibling
  `unevaluatedProperties: false`, no top-level `additionalProperties`, and no dynamic reference.
- `AC-P1-02` `record.schema.json` carries no top-level closure keyword and is referenced by all twenty
  collection schemas.
- `AC-P1-03` Every object in all twenty-three schemas is closed by the form RB-01 cl. 4 assigns it, and
  a payload with one undeclared key is rejected at every object level.
- `AC-P1-04` A record is validated exactly once, against its collection schema; no code path performs a
  separate envelope pass.
- `AC-P1-05` `schemas/lske/*.json` byte-match their dicts under RB-01 cl. 8 for all twenty-three files.
- `AC-P1-06` `relation.schema.json` requires exactly the ten keys of §0X.4, admits no eleventh, and
  rejects `independence_group` and `post_hoc`.
- `AC-P1-07` `relation.schema.json` contains no lifecycle field, and the RB-02 cl. 4 derivation returns
  each of `DELETED`, `CANDIDATE`, `DORMANT`, `ACTIVE` on a constructed case.
- `AC-P1-08` All thirty-two catalogue entries are implemented with their stated properties, required
  sets, types and nullability; none is partial.
- `AC-P1-09` `provenance.source_paths` items carry both `path` and `content_hash`.
- `AC-P1-10` `runs.admissibility` is populated only by the stated mapping from
  `ros.admissibility.Verdict`, and the LSKE computes no verdict of its own (R1-11).
- `AC-P1-11` `obs2.schema.json` closes its thirteen keys and constrains node, edge and overlay shape
  without constraining Observatory-owned interiors.
- `AC-P1-12` `LskeRecord` is deeply immutable, validated on construction, and has no constructor that
  skips validation.
- `AC-P1-13` A pre-seal and post-seal record share one `content_hash`, compare unequal, and have
  different `__hash__` values.
- `AC-P1-14` `v2/lske/` exposes exactly one public validating callable, and it reports all failures in
  instance-pointer order.
- `AC-P1-15` `allocate_record_id` is pure, order-stable, never reuses a sequence, and raises
  `OntologyError` on exhaustion or an unknown collection.
- `AC-P1-16` `allocate_event_id` is content-addressed, stable across calls, and never matches
  `ros.model.ID_PATTERN`.
- `AC-P1-17` `content_hash` covers blocks A–G, excludes Block H, and delegates canonicalization to
  `ros.protocol.canonical_bytes`.
- `AC-P1-18` No register has two literal sites in `v2/lske/`, and every register a frozen ROS module
  holds is imported rather than restated.
- `AC-P1-19` `COLLECTION_SPECS` has twenty entries with unique keys and prefixes, and every collection
  schema's narrowings are generated from it.
- `AC-P1-20` `.ros/lske_events.jsonl` exists, is append-only, is written only by `v2.lske.events`, and
  every appended event carries an `allocate_event_id` identifier.
- `AC-P1-21` No raise site in `v2/lske/` escapes the §9.5 taxonomy, and `ros.authority.AuthorityError`
  is not re-wrapped.
- `AC-P1-22` The package imports as `v2.lske.*`, there is no top-level `lske/` package, and no alias
  exists.
- `AC-P1-23` Every one of the twenty prefixes matches `^[A-Z]{3,5}$` and yields an identifier that
  `ros.model.ID_PATTERN` matches; `research_questions` uses `RQS`; `ID_PATTERN` is unmodified.

---

# APPENDIX E — Deferred observations (explicitly not Phase-1 blockers)

Two inherited inconsistencies were seen while auditing the amended sections. Both lie outside Phase 1 —
stage 1 modifies no ROS module — and neither is resolved here, because resolving a stage-4/stage-7
question inside a Phase-1 amendment would be exactly the scope creep RB-0.1 forbids. They are recorded
so that they are raised deliberately at the stage that meets them, under R9-0, rather than discovered
again.

1. **Top-level `status` readers in frozen ROS code.** RC-06 cl. 2 deletes the top-level `status` field
   and homes status at `lifecycle.status`. `ros.store.Record.status`, `ros.store.Store.with_status` and
   `ros.propagation.audit` read `data["status"]`. This first bites at **stage 2** (`ros.model` alignment,
   where `with_status` is used) and matters most at **stage 7 / §9.7 step 5**, which asserts
   `ros.propagation.audit(store, experiment_id).complete is True` against an unmodified auditor. It does
   not affect stage 1: no ROS module changes and no record is migrated.
2. **`experiments.executions` and the `NOT_YET_EXECUTED` test.** `ros.propagation` infers execution from
   the truthiness of `executions` or from a top-level `status` outside `NOT_YET_EXECUTED`. §9.2.2 rule 4
   keeps `executions` declared and optional so that migrated records validate, which is all Phase 1
   needs; whether the auditor's inference remains correct once status moves is the same stage-7 question
   as observation 1.

Neither observation is a `BLK-P1` item, neither blocks any stage-1 acceptance criterion, and neither
requires a decision before Phase 1 code is written.

---

# APPENDIX F — Final certification

**1. Can Phase 1 now be implemented without making any architectural decisions?**

**Yes.** Every Phase-1 decision point has exactly one value in this document: one composition mechanism
(RB-01 cl. 1), one inheritance strategy (cl. 3), one closed-world strategy in three mechanical forms
(cl. 4), one validation pass and one entry point (cl. 6, §9.13.3), one relation envelope of ten fields
(§0X.4), one derived edge-lifecycle rule (RB-02 cl. 4), one complete nested-object catalogue of
thirty-two entries over seven shared scalar types (§9.2.4), one immutable record model with a
seven-clause contract (§9.13.4), one record-identifier allocator and one event-identifier allocator
(§9.13.5), one canonical hashing API (§9.13.6), one owning module per Phase-1 component
(§9.13.1), and one identifier prefix per collection that the frozen pattern can carry (RB-06). No file,
module, collection, phase, primitive, gate, KPI, test file or build stage is added.
The implementer's remaining latitude is exactly §9.9's: private helper names, function-internal data
structures, log wording, fixture names, assertion order, docstrings.

**2. Does any ambiguity remain?**

**No, within Phase 1.** Appendix C records eleven checks, each passing, over implementability, nested
completeness, single API definition, single module ownership, single validator entry point, single
identifier ownership, single immutable-model contract, absence of conflicting rules, absence of
duplicate definitions, absence of undefined references, and one-to-one deliverable mapping.

Two things are deliberately bounded rather than ambiguous, and both are stated as boundaries with the
authority that owns them: the interiors of `obs2` nodes, edges and overlay values belong to the
Observatory specification (§9.2.4 note 3, R7-2), and the two inherited stage-2/stage-7 observations of
Appendix E belong to the stages that meet them. A boundary naming its owner is a decision; only an
unowned choice is an ambiguity.

**3. Does R9-0 require any further Constitutional Change Requests?**

**No, for Phase 1.** This document *is* the amendment R9-0 required in response to
`P1_V2_LSKE_PHASE1_BLOCKER_REPORT.md`, issued at the next version number as R9-0 and R9-12 prescribe.
`BLK-P1-01`…`BLK-P1-05` are closed, and `RB-06` closes the one further Phase-1 defect this document's
verification pass exposed — which is R9-0 working as designed: the defect was raised as an amendment
rather than resolved silently in code. Appendix E's two observations will require a change request when
stage 2 and stage 7 are reached; neither is an outstanding Phase-1 blocker.

**4. Can GPT-5.6 begin Phase 1 immediately?**

**Yes**, against §9.8 stage 1 as reissued, with the twenty-three acceptance criteria of Appendix D.1 as
the exit condition and the twenty-three traceability rows as the pre-code matrix. One standing condition
is unchanged and is not a blocker: the specification remains **Proposed / Unregistered** and
`GOVERNANCE_REGISTRY.yaml` remains `status: Draft`, so the work is **engineering-only and produces no
admissible scientific evidence** (R0-3, §9.12, Article L-11). Every artifact generated carries
`GOVERNANCE: DRAFT — NO ADMISSIBLE EVIDENCE`. Building the LSKE does not raise Scientific Readiness; it
makes the transaction exist so that the first experiment producing admissible evidence can be carried.

## Certification

> **LSKE Specification v1.1.1 is implementation-complete for Phase 1. No architectural interpretation
> is required. Phase 1 implementation may proceed under R9-0.**

This certifies implementation-completeness of Phase 1, not scientific readiness and not registration.
The document confers no authority, amends no frozen subsystem, and where it appears to conflict with
`P1_V2_CONSTITUTION_LOCK_v1.0.md`, `ros.authority`, `ros.admissibility`, the Observatory specification
or the M1/P1-v2 runtime, they govern and this document is defective.

## Standing of this specification

- **Artifact:** `P1_V2_LSKE_SPECIFICATION_v1.1.1.md`, version 1.1.1, a pure blocker elimination of
  v1.1.0.
- **Status:** **Proposed / Unregistered.** Not entered in `GOVERNANCE_REGISTRY.yaml`.
- **Authority source:** **none.**
- **Architecture:** identical to v1.1.0. Twenty collections, fifteen relation types, ten dimensions,
  four dimension states, five lifecycle states, seven transitions, five write operations, nine
  transaction phases with exactly one human phase, eight envelope blocks, ten memory checks, three new
  gates, four new KPIs, twenty-three test rows, nine build stages, one canonical store, one writer.

**End of specification.**
