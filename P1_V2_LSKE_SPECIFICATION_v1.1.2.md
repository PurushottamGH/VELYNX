# P1-v2 Living Scientific Knowledge Engine — Engineering Specification

**GOVERNANCE: DRAFT — NO ADMISSIBLE EVIDENCE**

- **Artifact:** `P1_V2_LSKE_SPECIFICATION_v1.1.2.md`
- **Version:** 1.1.2
- **Release kind:** **Final Phase-1 normative-defect correction.** No redesign, no new capability, no
  scope change, no new architectural module, no new collection, no new phase, no new primitive, no new
  authority class, no new write target, no new transaction phase, no new gate, no new KPI, no new
  package file, no new test file, no new build stage, no weakening of determinism. Five normative
  defects recorded by `P1_V2_LSKE_V1.1.1_PHASE1_STRICT_CONFORMANCE_REVIEW.md` and classified as
  **Normative Defect** by the Final Implementation Authority Review (`IMP-BLK-03`, `IMP-BLK-04`,
  `IMP-BLK-05`, `IMP-BLK-06`, `IMP-BLK-07B`) are closed by the six rulings `RF-01`…`RF-06` — `IMP-BLK-03`
  requiring two, one for the payload representation and one for the ordering and derived rule — and the
  Phase-1 test matrix and Appendix D mapping are updated to match.
- **Supersedes:** `P1_V2_LSKE_SPECIFICATION_v1.1.1.md` v1.1.1 — retained, readable, non-current
- **Carries forward unchanged:** the whole of v1.1.1, and through it the whole of v1.1.0, except the
  sections this document names. Part 0R (`RC-0`…`RC-12`) and Part 0X (`RB-0`…`RB-06`) stand in force in
  their entirety.
- **Status:** Proposed / Unregistered
- **Date:** 2026-07-30
- **Subsystem:** Living Scientific Knowledge Engine (LSKE)
- **Inherits without amendment:** `P1_V2_CONSTITUTION_LOCK_v1.0.md` v1.0.0; `ros.authority`;
  `ros.admissibility`; `ros.protocol`; `ros.events`; `ros.propagation`;
  `P1_OBSERVATORY_SCIENTIFIC_SPECIFICATION_v1.0.md`; the M1/P1-v2 runtime
- **Closes:** `IMP-BLK-03`, `IMP-BLK-04`, `IMP-BLK-05`, `IMP-BLK-06`, `IMP-BLK-07B`
- **Permanently closed as Implementation Latitude, not amended here:** `IMP-BLK-01`, `IMP-BLK-02`,
  `IMP-BLK-07A`
- **Authority source:** none

**Reading rule.** This document is an amendment. Where a section number appears below, the text under
it **replaces** the corresponding text of v1.1.1 — or, where v1.1.1 did not reissue that section, of
v1.1.0 — in full. Every section not named here is unchanged and remains in force. No sentence of
v1.1.1 or v1.1.0 is amended silently. Where this document and v1.1.1 disagree on a named section, this
document governs; where they do not disagree, both stand.

---

# PART 0Y — Final Amendment Record (v1.1.2)

## 0Y.1 Standing of this part

`P1_V2_LSKE_V1.1.1_PHASE1_STRICT_CONFORMANCE_REVIEW.md` recorded seven remaining implementation
findings (`IMP-BLK-01`…`IMP-BLK-07`, the seventh in two parts). The Final Implementation Authority
Review classified each. This part records the single authoritative resolution adopted for each finding
classified **Normative Defect**, and nothing else. The rulings are numbered `RF-01`…`RF-06`.

**Rule RF-0.** An `RF` ruling has the same standing as the `R`-series rule, `RC` ruling or `RB` ruling
it completes. Every section affected by a ruling is reissued in this document so that only the ruled
text exists. If a reader finds surviving v1.1.1 or v1.1.0 text that contradicts an `RF` ruling, the
ruling governs and the surviving sentence is a defect to be reported under R9-0, not a second reading.

**Rule RF-0.1.** No ruling in this part creates an authority class, a write target, a human-only
decision, a primitive, a collection, a relation type, a confidence dimension, a lifecycle state, a
write operation, a transaction phase, a gate, a KPI, a package file, a schema file, a test file, a
phase, a build stage, or a schema field that v1.1.1 did not already require. Each ruling either
(a) fixes the one public representation of a contract v1.1.1 required but left unrepresented,
(b) selects one of two readings already present in v1.1.1, (c) completes a rule v1.1.1 stated but left
partial, or (d) names the literal value or public signature of a component v1.1.1 required but left
unvalued or unsigned. The architecture of v1.1.1 is identical after this release.

**Rule RF-0.2 (determinism is not relaxed).** Every resolution below is total, ordered and computable
without a clock, a random source, a network call, or an environment lookup. Where a resolution
introduces a rule with cases, the cases are evaluated in the stated order and the order is part of the
rule.

**Rule RF-0.3 (no reopening).** `IMP-BLK-01`, `IMP-BLK-02` and `IMP-BLK-07A` are permanently
classified as Implementation Latitude by the Final Implementation Authority Review. This document
makes no amendment concerning them, and §0Y.2 restates that classification without altering any
normative text.

### Ruling index

| Amendment | Ruling | Closes | Subject | Sections reissued or added |
|---|---|---|---|---|
| A-1 | `RF-01` | `IMP-BLK-03` | The public `SchemaViolation` failure payload | §9.5.1 (new); §9.13.0 (one sentence); §9.1 row `v2/lske/errors.py`; §9.13.1 row `Exception taxonomy` |
| A-2 | `RF-02` | `IMP-BLK-03` | Completion of R9-15 ordering, reported-application granularity, and R9-15.1 derived behaviour | §9.13.3 (reissued) |
| A-3 | `RF-03` | `IMP-BLK-04` | Schema accessor return type, copy semantics, identity | §9.13.3 (reissued) |
| A-4 | `RF-04` | `IMP-BLK-05` | `ONTOLOGY_VERSION` literal, owner, authority, update rule | §9.13.2 (one line) |
| A-5 | `RF-05` | `IMP-BLK-06` | The immutable constructor predicate | §9.13.4 cl. 2 (reissued) |
| A-6 | `RF-06` | `IMP-BLK-07B` | The durable event writer public API | §9.13.8 (new); §9.1 row `v2/lske/events.py`; §9.13.1 row `Durable event log writer` |
| A-7 | — | all of the above | Phase-1 test matrix | §9.6 rows 1–2 (Asserts cells, additively) |
| A-8 | — | all of the above | Phase-1 traceability and acceptance criteria | Appendix C.3 and C.11 count sentences; Appendix D; Appendix D.1 |

This column names the sections each ruling reissues or adds. Four further sections are amended by the
rulings jointly and are therefore listed once rather than per row: §9.9's not-open list and Appendices
A.1B (one key), A.2 and A.3. Four appendix sections are added — A.1C, G, H and J — and one rule is
appended: R9-19 (§9.14). Appendix H row 6 is the complete change inventory.

`A-7` and `A-8` carry no ruling number: they are the mechanical propagation of `RF-01`…`RF-06` into
the test matrix and the traceability mapping, and they add no requirement that `RF-01`…`RF-06` do not
already state.

## 0Y.2 Findings permanently classified as Implementation Latitude

The following findings are **not** normative defects, are **not** amended by this document, and are
**permanently closed**. They are listed so that no future review reopens them as specification gaps.

| Finding | Subject | Classification | Governing authority for the classification |
|---|---|---|---|
| `IMP-BLK-01` | Draft 2020-12 validator dependency / evaluation mechanism | **Implementation Latitude — permanently closed** | Final Implementation Authority Review; R9-19 cl. 3 (§9.14) |
| `IMP-BLK-02` | The callable that computes the derived `edge_state` of RB-02 cl. 4 | **Implementation Latitude — permanently closed** | Final Implementation Authority Review; R9-19 cl. 3 (§9.14) |
| `IMP-BLK-07A` | `AC-P1-10`'s population path for `runs.admissibility` | **Implementation Latitude — permanently closed** | Final Implementation Authority Review; R9-19 cl. 3 (§9.14) |

No sentence of v1.1.1 or v1.1.0 concerning these three findings is amended, deleted, narrowed or
widened by this document, and §9.9's open list gains no item on their account: their classification rests
on the Final Implementation Authority Review and on R9-19, the governance rule this document is ordered to
append. RB-01, RB-02 cl. 4, §9.2.4 note 2, Appendix D rows 1–11 and `AC-P1-01`…
`AC-P1-11` stand exactly as v1.1.1 issued them.


## 0Y.3 RF-01 — The public `SchemaViolation` failure payload (closes `IMP-BLK-03`, amendment A-1)

**The defect.** R9-15 requires `validate` to report **all** failures and says `SchemaViolation`
"carries them as a tuple on the exception instance"; R9-15.1 requires a derived finding to be reported
last and "marked `derived: true`". Both are externally observable acceptance behaviour asserted by
`AC-P1-14`. v1.1.1 names no attribute, no item type, no field names, no ordering rule for two failures
at one instance pointer, and does not say whether the carrier is `args`, a named attribute, tuples of
primitives, mappings or objects. §9.9 does not permit a public exception payload to be invented.

**Ruling RF-01.** The failure payload has exactly one public representation, specified in full in
§9.5.1. Six clauses:

1. **Attribute name — `failures`, and no other.** The payload is reachable as
   `exc.failures` and by no other public name. There is no `errors`, `details`, `violations`,
   `failure_list`, `to_dict()`, `as_json()` or `__iter__` alternative, and no failure information is
   carried in `args` beyond the message.
2. **Data type — `tuple[tuple[str, str, str, bool], ...]`.** The payload is a `tuple`; every item is a
   four-element `tuple` of primitives. It is never `None`, never a `list`, never a `dict`, never a
   generator, and never a tuple of objects. Primitives are chosen because the failure payload must be
   comparable, hashable, `repr`-stable and assertable in a test without importing a second public type —
   and because §9.1 fixes the contents of `v2/lske/errors.py` as the §9.5 taxonomy, which §9.5.1's reissue
   of the §9.13.0 sentence confirms means no function, register or class of its own beyond that taxonomy.
   A new public failure class would contradict both.
3. **Payload representation — `(instance_pointer, schema_pointer, keyword, derived)`,** in that
   positional order, with the types and value spaces of §9.5.1 cl. 3. The item order is positional and
   fixed; there is no keyword access, no named tuple, no field aliasing.
4. **Derived marker — position 4, a `bool`.** `derived` is `True` for exactly the findings R9-15.1 as
   completed by `RF-02` designates, and `False` for every other finding. There is no third state and no
   `None`.
5. **Deterministic ordering — enforced by the exception, not by the raiser.** `SchemaViolation`
   normalizes its payload on construction: it de-duplicates identical items and sorts by the total key
   of §9.5.1 cl. 5. Every `SchemaViolation` instance therefore presents the same order for the same
   failure set regardless of which raise site produced it, and a test may assert the order against the
   exception alone.
6. **One representation only.** No other public error representation may exist anywhere in `v2/lske/`:
   no other exception in the §9.5 taxonomy carries a failure payload, no callable returns a validation
   error object instead of raising, and no callable returns a boolean or a list of messages in place of
   raising `SchemaViolation`.

**Why this preserves the architecture.** The §9.5 taxonomy keeps its seven classes, its bases and its
raise-site rule. `v2.lske.errors` gains no function, no module-level constant and no public class: one
existing class acquires the constructor signature and the one attribute R9-15 already required it to
carry.

**Sections reissued.** §9.5.1 (new), §9.13.0 (the one sentence describing `v2.lske.errors`), §9.1
(Contents cell for `v2/lske/errors.py`), §9.13.1 (the `Exception taxonomy` row), §9.6 row 2,
Appendix A.2, Appendix A.3, Appendix D.

## 0Y.4 RF-02 — Completion of the failure ordering and the derived rule (closes `IMP-BLK-03`, amendment A-2)

**The defect.** R9-15 orders failures "by instance pointer ascending" and supplies no tie-break, so two
failures at one instance pointer have no defined order. R9-15.1 states that a derived
`unevaluatedProperties` finding is reported "last" and marked `derived: true`, but does not define
which findings are derived, how a derived finding is recognised, how two derived findings order among
themselves, or whether a derived finding may be suppressed.

**Ruling RF-02.** R9-15 and R9-15.1 are completed as follows, with no change to either rule's decided
substance — all failures are still reported, derived findings are still reported last, and the closure
keyword is still never removed. Six clauses, reissued as part of §9.13.3:

1. **Derived is a computed property of the failure set, evaluated once.** A failure item is `derived`
   **iff** both hold: its `keyword` is exactly `"unevaluatedProperties"`, **and** the failure set
   contains at least one item whose `keyword` is not `"unevaluatedProperties"` and whose
   `instance_pointer` is at or below the `unevaluatedProperties` item's own `instance_pointer`. "At or
   below" is the decidable string test of §9.5.1 cl. 4. Evaluation is over the complete primary failure
   set, once, before ordering; it is not recursive and it does not consider items already marked
   derived.
2. **Every other keyword is never derived.** For an item whose `keyword` is not
   `"unevaluatedProperties"`, `derived` is `False`. There is exactly one producer of a `True` marker.
3. **A genuine closure failure is not derived.** An `unevaluatedProperties` failure with no primary
   failure at or below its instance pointer — the record that carries a truly undeclared key while both
   `allOf` branches pass — has `derived` `False` and sorts in the primary block. This is the case
   `AC-P1-03` tests, and it must remain distinguishable from a cascade.
4. **Derived findings are reported, never suppressed and never merged.** The tuple contains both the
   primary failure and every derived consequence of it. R9-15's "all failures" is unweakened;
   R9-15.1's "last" is realised by clause 1 of the ordering key.
5. **Ordering is total.** The order is `derived` ascending (`False` before `True`), then
   `instance_pointer`, then `schema_pointer`, then `keyword`, each ascending by Unicode code point.
   Because items are unique after de-duplication, this key admits no tie, so the order is a function of
   the failure set alone.
6. **The reported item set is fixed too.** An order is only deterministic over a determinate set, so
   §9.13.3 also fixes which keyword applications are reported: assertion applications that evaluate to
   false on a wholly failing evaluation path, one item per occurrence, never an applicator. Without this,
   two implementations could agree on the ordering rule and still disagree on what they ordered.

**Why this preserves the architecture.** No dialect behaviour is asserted that RB-01 and Appendix C.1
did not already establish, no closure keyword moves, and no failure is hidden. The rule that a cascade
must not be read as a schema bug is unchanged; it is now checkable.

**Sections reissued.** §9.13.3 (`validate`, R9-15, R9-15.1), §9.6 row 2, Appendix D row 14.


## 0Y.5 RF-03 — Schema accessor mutability (closes `IMP-BLK-04`, amendment A-3)

**Conflicting rules.**

> §9.13.3: `all_schemas() -> Mapping[str, dict[str, Any]]` … "Returns deep-immutable views; a caller
> cannot mutate a schema dict."

> §9.13.3: `record_schema()`, `collection_schema()`, `relation_schema()`, `obs2_schema()` each return
> `dict[str, Any]`.

**The defect.** A deep-immutable view and a `dict[str, Any]` are different objects. The contract does
not say whether an accessor returns a mutable deep copy, the canonical mutable dictionary, a mapping
proxy, or another frozen representation; and it does not say whether `all_schemas()["record"]` and
`record_schema()` are the same object. The choice is externally observable: it decides validator
compatibility, equality and serialization behaviour in test 1, and whether a caller can corrupt
canonical state.

**Ruling RF-03.** One representation, one copy discipline, one identity rule. Six clauses, reissued as
part of §9.13.3:

1. **Canonical ownership.** The twenty-three canonical schema objects are **module-private state of
   `v2.lske.schema`**, constructed once when the module is imported, and are the single source used by
   `all_schemas`, the four accessors, `validate` and the generated `schemas/lske/*.json` files. No
   public name exposes a canonical object, and no canonical object is ever returned to a caller.
2. **Return types are exactly as v1.1.1 declares them, and they do not change.**
   `record_schema() -> dict[str, Any]`, `collection_schema(collection_key) -> dict[str, Any]`,
   `relation_schema() -> dict[str, Any]`, `obs2_schema() -> dict[str, Any]`,
   `all_schemas() -> Mapping[str, dict[str, Any]]`.
3. **Copy semantics — the four accessors return a fresh deep copy on every call.** Every nested mapping
   in the returned value is a fresh `dict`, every nested array a fresh `list`. The returned tree
   contains only JSON types — `dict`, `list`, `str`, `bool`, `int`, `float`, `None` — so a returned
   schema is directly usable by any Draft 2020-12 evaluator and directly acceptable to `json.dumps`.
4. **Mutability — a returned schema is mutable, and mutating it reaches nothing.** A caller may mutate
   the object it received. No mutation of a returned object can reach canonical module state, another
   returned object, another accessor's result, `validate`'s behaviour, or a generated file. The v1.1.1
   sentence "Returns deep-immutable views; a caller cannot mutate a schema dict" is reissued as: *no
   mutation of a returned object can reach canonical module state* — that is its only meaning, and the
   deep-immutability of the returned object itself is **not** asserted.
5. **`all_schemas` — an immutable mapping over fresh deep copies.** `all_schemas()` returns a fresh
   `types.MappingProxyType` over a fresh `dict` of exactly twenty-three entries, whose values are fresh
   deep copies produced exactly as clause 3 produces them. The mapping itself rejects item assignment
   and deletion (`TypeError`); its values are mutable copies under clause 4. Key order is fixed and
   deterministic: `"record"`, then the twenty collection keys in §1.2 order, then `"relation"`, then
   `"obs2"`; iteration, `keys()`, `values()` and `items()` follow that order.
6. **Object identity — nothing is shared and nothing is cached.** For any two accessor calls
   `a` and `b`, whatever their arguments, `a is not b`. `all_schemas() is not all_schemas()`, and
   `all_schemas()[k] is not <accessor for k>()`. Equality always holds where the subject is the same:
   `record_schema() == record_schema()`, and `all_schemas()["record"] == record_schema()`. Canonical
   state is never an accessor's return value, so identity with it is never observable.

**Unknown-key behaviour.** `collection_schema(collection_key)` raises `OntologyError` when
`collection_key` is not one of the twenty keys of `COLLECTION_SPEC_BY_KEY`. This is not a new rule: it
is what §9.5 already requires — every raise site in `v2/lske/` uses the taxonomy, so a bare `KeyError`
may not escape — applied to the one accessor that takes a key, and it is the same exception `validate`
and `allocate_record_id` already raise for the same input class.

**Why this preserves the architecture.** No signature, no return annotation and no name changes. The
module remains pure (§9.13.7): copying is computation, not I/O. Closure, composition and the byte-match
contract of R9-2 are untouched, and the guarantee the v1.1.1 sentence existed to give — a caller cannot
corrupt canonical schema state — is preserved exactly, now with one observable mechanism.

**Sections reissued.** §9.13.3 (accessor block), §9.6 row 1, Appendix A.2, Appendix D.

## 0Y.6 RF-04 — `ONTOLOGY_VERSION` (closes `IMP-BLK-05`, amendment A-4)

**The defect.** §9.13.2 declares `ONTOLOGY_VERSION: str` as "the semver written into every record's
`ontology_version`" and states no value and no source. §9.1 gives `v2/lske/__init__.py` a version
constant. The pre-code package skeleton holds `__version__ = "1.1.0"` **and**
`ONTOLOGY_VERSION = __version__` in `v2/lske/__init__.py`, so the register that must have one literal
site has two candidate sites and four candidate values (`1.1.0`, `1.1.1`, `1.1.2`, or a separately
maintained ontology version). R9-13 requires exactly one value; RB-05 cl. 5 requires exactly one
literal site.

**Ruling RF-04.** Four clauses:

1. **Literal value — `"1.1.2"`.** `ONTOLOGY_VERSION` is the string literal `"1.1.2"`. It is written,
   verbatim, into the `ontology_version` field of every record the LSKE writes.
2. **Single owner — `v2.lske.schema`.** The literal appears exactly once in the **package**: one
   declaration in the frozen register block of §9.13.2, and nowhere else in `v2/lske/` or in
   `schemas/lske/`. It is not read from `pyproject.toml`, not derived from a package version, not computed
   from a file name, not obtained from version control, and not passed in. `v2/lske/__init__.py` **does not
   define, re-export or alias `ONTOLOGY_VERSION`**; the pre-code line `ONTOLOGY_VERSION = __version__` and
   its `__all__` entry are superseded by this ruling and are removed. `v2.lske.schema.ONTOLOGY_VERSION` is
   the only public access path. The value also appears in this specification, which is its authority
   (cl. 3), and in test 2's pinning assertion, which exists precisely to detect a drift between the two;
   neither is a second source, because neither is read by the package.
3. **Version authority — the LSKE specification, and the two quantities are distinct.**
   `ONTOLOGY_VERSION` is the version of the LSKE **specification in force**, and its value is that
   specification's own version number. `v2.lske.__version__` is the **package** version, owned by
   `v2/lske/__init__.py` (§9.1, `AC-P1-22`), is not written into any record, and is a different
   quantity: equality between the two is neither required nor asserted, and no code, test or schema may
   derive one from the other. This preserves `AC-P1-22`'s package/version surface unchanged while
   removing the second ontology-version site.
4. **Update rule.** `ONTOLOGY_VERSION` changes by, and only by, a specification amendment issued under
   R9-0 and R9-12, and its new value is that amendment's version number. It is never changed by an
   implementer, a migration, a runtime value, an environment variable or a release script. Records
   already written retain the value they were written with: the `ontology_version` field is constrained
   by the schema to the semver form only and **not** to a single value, so a record migrated from an
   earlier ontology remains valid — which is what §9.8.1 already requires and what makes the field
   worth storing.

**Why this preserves the architecture.** No field is added to any record, no schema constraint changes,
no register is added, and the §9.13.2 declaration line keeps its name and type. One register acquires
its literal and loses its second site.

**Sections reissued.** §9.13.2 (the `ONTOLOGY_VERSION` line), §9.6 row 2, Appendix A.2, Appendix D.


## 0Y.7 RF-05 — The immutable constructor predicate (closes `IMP-BLK-06`, amendment A-5)

**The defect.** §9.13.4 cl. 2 states that the generated `__init__` "accepts only an already-frozen
mapping" and otherwise raises `SchemaViolation`, and test-matrix row 2 asserts that rejection.
"Already-frozen mapping" is not a decidable input predicate: it could mean a `MappingProxyType` at the
top level only, a recursively frozen tree, any immutable `Mapping`, or only a value produced by the
module's private deep-freeze helper. The signature accepts `Mapping[str, Any]`, so the accepted input
domain is unstated while the rejection is an acceptance criterion.

**Ruling RF-05.** The predicate is total, decidable and structural. Six clauses, reissued as
§9.13.4 cl. 2:

1. **The predicate — `is_frozen_payload(value)`.** `value` satisfies the predicate iff it is an instance
   of `types.MappingProxyType` and every node of its value tree satisfies the recursive rule of
   clause 2. The predicate is evaluated by a private helper whose name and signature remain §9.9
   latitude; its **behaviour** is normative and is this rule.
2. **Recursive rule.** For each node:
   - a **mapping node** satisfies the rule iff it is an instance of `types.MappingProxyType`, every key
     is an instance of `str`, and every value satisfies the rule;
   - a **sequence node** satisfies the rule iff it is an instance of `tuple` and every item satisfies
     the rule;
   - a **leaf node** satisfies the rule iff it is `None` or an instance of `str`, `bool`, `int` or
     `float`.
   No other node satisfies the rule.
3. **Accepted inputs.** Exactly the values satisfying clauses 1–2: a `MappingProxyType` whose entire
   tree is composed only of `MappingProxyType` with `str` keys, `tuple`, `str`, `bool`, `int`, `float`
   and `None`. The empty proxy `MappingProxyType({})` is accepted. The output of the module's deep-freeze
   step satisfies the predicate by construction, so `LskeRecord(r.collection_key, r.payload)` is accepted
   for every `LskeRecord` `r` obtained from `from_payload`.
4. **Rejected inputs.** Everything else, with no exception: `dict`; `list`; `set`; `frozenset`; `bytes`;
   `bytearray`; `datetime`; `Decimal`; a `MappingProxyType` containing any of those at any depth; a
   `MappingProxyType` with a non-`str` key at any depth; any other `Mapping` implementation, including a
   user-defined immutable mapping and a `Mapping` returned by a third-party library; and any non-mapping
   value, including `None`.
5. **Totality and determinism.** The predicate is defined for every Python object, returns exactly one
   of two results, terminates on every payload (an LSKE payload is a finite JSON tree; a proxy tree
   containing a cycle cannot be produced by the deep-freeze step and is a rejected input if a caller
   constructs one, because a cycle requires a mutable container at some node), and consults no clock, no
   environment and no store. The reported location is the **first node that fails its own node-local
   test**, never an ancestor that fails only because a descendant did: nodes are visited in pre-order,
   mapping keys are type-checked in the mapping's own iteration order, mapping values are recursed in
   ascending Unicode code-point order of their keys, and tuple items in index order (§9.13.4 cl. 2.4).
6. **The one observable behaviour.** The generated `__init__` performs exactly one check — the predicate
   of clauses 1–4 on `payload` — and performs it before any attribute is set. On satisfaction it
   constructs the instance and stores `collection_key` and `payload` as given. On failure it raises
   `SchemaViolation` whose `failures` tuple contains exactly one item:
   `(<RFC 6901 pointer to the reported node of clause 5>, "", "frozen", False)`, the pointer being `""`
   when the reported node is `payload` itself.
   The generated `__init__` performs no schema validation and no collection-key lookup: `validate` is
   reached only through `from_payload` (RB-04 cl. 5, R9-14), and a second validation site would give one
   payload two validation histories. `from_payload` remains the only public constructor, unchanged.

**Why this preserves the architecture.** The class, its fields, its equality, its two hashes, its
immutability direction and its single public constructor are unchanged. One sentence of cl. 2 becomes a
decidable predicate, and one rejection acquires the payload representation `RF-01` fixes.

**Sections reissued.** §9.13.4 cl. 2, §9.6 row 2, Appendix D.

## 0Y.8 RF-06 — The durable event writer (closes `IMP-BLK-07B`, amendment A-6)

**The defect.** RC-07 names `v2.lske.events` as the sole writer of `.ros/lske_events.jsonl`; §9.13.1
gives it the Phase-1 component "durable event log writer"; Appendix D row 20 maps it to "append of
`lifecycle` and `evidence` events" and `AC-P1-20` requires existence, append-only behaviour, single-writer
ownership and allocator use. No function name, signature, parameter list, return value, validation
behaviour or exception behaviour is defined anywhere, and "append of events" is an operation
description, not an API. The acceptance criterion therefore names no invocable surface.

**Ruling RF-06.** The writer has exactly one public callable, specified in full in §9.13.8. Seven
clauses:

1. **Public API — one callable.** `v2.lske.events.append_event` is the only public callable in
   `v2/lske/events.py`, the only public name it exports, and the only writer of
   `.ros/lske_events.jsonl` (RC-07). The module exposes no reader, no iterator, no path helper, no
   register and no class. Phase 1 adds no reader: `MEM-01` resolves its `event_id`s against this log, and
   the check that does so is `ros.store._check_memory`, whose build stage (§9.8 stage 4) is unchanged and
   outside Phase 1.
2. **Parameters.** `root: Path` — the repository root that contains `.ros/`; the log is exactly
   `root / ".ros" / "lske_events.jsonl"` and no other path is written. `event: Mapping[str, Any]` — the
   nine-key event body of §9.3.1: `kind`, `at`, `by`, `authority`, `target`, `record_id`, `from`, `to`,
   `cause`. All nine keys are present; no tenth key is accepted; `event_id` is **not** an input, because
   the writer allocates it.
3. **Return value.** `str` — the allocated `event_id` in the `LEV-<32 lowercase hex>` form of S-07,
   which is exactly the value written into the appended line. Nothing else is returned; there is no
   receipt, no path, no line number and no `None` return.
4. **Validation behaviour.** Evaluated in this order:
   1. key set — if `event`'s keys are not exactly the nine of clause 2, raise `SchemaViolation` whose
      `failures` contains `("", "", "required", False)` when a key is absent and
      `("", "", "additionalProperties", False)` when an undeclared key is present, both when both apply,
      ordered by §9.5.1 cl. 5; the message names the offending keys and no measured value (R9-9);
   2. kind — if `event["kind"]` is not `"lifecycle"` or `"evidence"`, raise `OntologyError` (RC-07: those
      are the only two kinds this module emits).
   `append_event` calls no schema: there is no event schema among the twenty-three (Appendix D row 20,
   schema `none`), the event body is fixed by §9.3.1, and R9-14 is not engaged because `append_event` is
   not a validation function and defines no public validator.
5. **Identifier and serialization.** `event_id` is `v2.lske.schema.allocate_event_id(event)` — the
   writer allocates no identifier and computes no hash of its own (RB-05 cl. 2). The appended line is
   `v2.lske.schema.canonical_json({**event, "event_id": event_id})` followed by exactly one `\n`
   (`0x0A`). One call appends exactly one line. UTF-8, no BOM, no pretty-printing, no trailing
   whitespace, no blank line, no header.
6. **Append semantics and storage behaviour.** The file is opened in binary append mode, the single line
   is written, and the file is closed. Existing bytes are never read, rewritten, truncated, reordered,
   reformatted or deleted; there is no seek, no in-place edit, and no temporary-file-and-rename — that
   discipline belongs to receipts (§9.3.1) and is not used here. A missing `.ros/` directory and a
   missing log file are created on first append; an existing file is never re-created. The append is not
   a commit point (§9.3.1, unchanged): a phase that wrote a record but failed to append leaves a
   transition whose `event_id` does not resolve, which `MEM-01` reports.
7. **Ownership and no de-duplication.** Two calls with equal bodies append two lines carrying the same
   content-addressed `event_id`; the writer performs no de-duplication and no re-emit check, because
   R9-7's no-re-emit rule is a transaction-phase rule and moving it into the writer would give one rule
   two enforcement sites. **Authority binding is unchanged and is not amended:** §6.8, test 4, `I-25` and
   RC-07 stand as written, no §6.8 row is added or removed, and the parameter list of cl. 2 admits no
   actor, so the check belongs to the calling phase — which is what §9.3.1 already states, the append
   being "the last step of the phase that wrote the record".

**Why this preserves the architecture.** No file, module, event kind, path, transaction phase, write
target or authority row is added. The component v1.1.1 already required Phase 1 to deliver acquires the
signature it lacked, inside the module §9.1 already lists, using the allocator and the canonical
serializer that already exist.

**Sections reissued.** §9.13.8 (new), §9.1 (Contents cell for `v2/lske/events.py`), §9.13.1 (the
`Durable event log writer` row), §9.6 row 2, Appendix A.2, Appendix A.3, Appendix D row 20.

## 0Y.9 What this release does not do

It adds no collection, relation type, dimension, dimension state, lifecycle state, write operation,
transaction phase, authority class, write target, human-only decision, gate, KPI, primitive, package
file, schema file, test file or build stage. It removes none of these either. It changes no schema field,
no schema keyword, no closure form, no composition mechanism, no identifier form, no hash algorithm, no
event kind, no test-file name and no build-stage boundary. It adds no module and no component: the two
public names it fixes — `append_event` and `SchemaViolation.failures` — are the names of components v1.1.1
already required Phase 1 to deliver, `v2/lske/events.py`'s writer and the payload R9-15 already required to
exist. Two declarations are
removed as duplicates (`v2/lske/__init__.py`'s `ONTOLOGY_VERSION` and its `__all__` entry, superseded by
the single site of §9.13.2); one register acquires its literal value; four contracts acquire their single
public representation; one rule acquires its tie-break; one sentence becomes a decidable predicate.


---

# PART 9 — Implementation Contract (amended sections)

R9-0 and R9-13 are unchanged and remain in force. This document is the v1.1.2 amendment issued under
R9-0 against v1.1.1 in response to `P1_V2_LSKE_V1.1.1_PHASE1_STRICT_CONFORMANCE_REVIEW.md`, as governed
by the Final Implementation Authority Review.

## 9.1 Frozen file layout (reissued rows only)

The layout is unchanged in membership: the same files, the same count, the same two run-time data paths,
the same single temporary file. Two *Contents* cells are reissued; no row is added, removed or renamed.
The `v2/lske/schema.py` row as reissued by v1.1.1 §9.1 stands unchanged.

| Path | Kind | Contents (reissued) |
|---|---|---|
| `v2/lske/errors.py` | new | The error taxonomy of §9.5 — seven classes, unchanged — together with the `SchemaViolation` failure payload contract of §9.5.1 (`RF-01`). Nothing else: no function, no module-level register, no additional class. |
| `v2/lske/events.py` | new | The durable LSKE event log writer: the single public callable `append_event` of §9.13.8 (`RF-06`); `lifecycle` and `evidence` kinds only (RC-07); the only writer of `.ros/lske_events.jsonl`. It allocates no identifier and computes no hash of its own: it calls `v2.lske.schema.allocate_event_id` (RB-05 cl. 2). |

`v2/lske/__init__.py` keeps its package version constant `__version__` and, per `RF-04` cl. 2, defines
no `ONTOLOGY_VERSION` and exports none. Every other row of §9.1, the two run-time data paths, and
R9-1's prohibition of a `__main__`, CLI, server or network client are unchanged.

**Rule R9-1.** Unchanged. **Rule R9-2.** Unchanged.

## 9.5.1 The `SchemaViolation` failure payload (new, `RF-01`)

§9.5's taxonomy table, its bases, its raise-site rule and R9-9 are unchanged. This section is the single
site of the public failure payload R9-15 requires, and the only public error representation in
`v2/lske/`.

**One sentence of §9.13.0 is reissued with it.** v1.1.1 §9.13.0 says that `v2.lske.errors` "holds no API
of its own — (the §9.5 taxonomy)". It is reissued as: *`v2.lske.errors` holds no function, no register and
no class of its own beyond the §9.5 taxonomy; the constructor signature and the one attribute of §9.5.1 are
part of that taxonomy's own contract, not a second API.* Nothing else in §9.13.0 changes: `v2.lske.schema`
still carries the Phase-1 API surface, the §6.8 row it added is untouched, and no module's disposition,
dependency boundary or count changes.

```python
class SchemaViolation(LskeError, ValueError):
    """A record or event violates its canonical schema."""

    failures: tuple[tuple[str, str, str, bool], ...]

    def __init__(
        self,
        message: str,
        failures: Iterable[tuple[str, str, str, bool]] = (),
    ) -> None: ...
        # self.args == (message,) exactly; str(self) == message.
        # self.failures is the normalized tuple of clause 5.
```

1. **Attribute.** `failures`, and no other public name. `args` is exactly `(message,)`, so `str(exc)` is
   the message of RB-05 cl. 1 — the instance pointer, the schema pointer and the failing keyword, in
   that order, and no measured value (R9-9). No failure information is carried in `args[1:]`, in a
   `__dict__` key other than `failures`, or in a subclass. The message contract is RB-05 cl. 1 and R9-9,
   unchanged and not amended here; the `failures` tuple is the machine-readable contract and is the only
   thing an acceptance criterion of this document asserts.
2. **Type.** `tuple[tuple[str, str, str, bool], ...]`. Never `None`, never a `list`, never a `dict`,
   never a generator, never a tuple of objects. An empty tuple is representable but is never produced by
   a raise site in `v2/lske/`: every `SchemaViolation` raised inside the package carries at least one
   item, so a caller may always inspect `failures[0]`.
3. **Item.** Exactly four positional elements, in this order:

   | # | Name | Type | Value space |
   |---|---|---|---|
   | 1 | `instance_pointer` | `str` | An RFC 6901 JSON Pointer into the validated payload, with `~0`/`~1` escaping. `""` is the document root. Array positions are decimal indices, e.g. `/revisions/0/at`. |
   | 2 | `schema_pointer` | `str` | The absolute keyword location: the `$id` of the schema resource containing the failing keyword, then `#`, then an RFC 6901 pointer from that resource's root to the keyword — e.g. `https://p1.local/schemas/lske/record.schema.json#/properties/id/pattern`. `""` exactly when no schema resource was evaluated (the constructor predicate of §9.13.4 cl. 2 and the two body-key checks of §9.13.5 and §9.13.8). |
   | 3 | `keyword` | `str` | The failing **assertion** keyword as written in the schema, per the reported-application rule of §9.13.3 (R9-15); applicator keywords are never reported. The three values that name no schema keyword are `required` and `additionalProperties` for a fixed body-key check (§9.13.5, §9.13.8) and `frozen` for the constructor predicate (§9.13.4 cl. 2). |
   | 4 | `derived` | `bool` | `True` for exactly the findings §9.13.3 R9-15.1 designates; `False` otherwise. No third state. |

4. **"At or below" is a string test.** Instance pointer `p` is *at or below* instance pointer `q` iff
   `p == q or p.startswith(q + "/")`. For `q == ""` this holds for every pointer. This is the only
   containment test used by R9-15.1.
5. **Normalization on construction, so the payload is canonical on every instance.** `__init__`
   (a) materializes the iterable into a `tuple`, (b) removes items equal to an earlier item, keeping the
   first occurrence, and (c) sorts by the total key `(derived, instance_pointer, schema_pointer,
   keyword)` — `derived` ascending so `False` precedes `True`, the three strings ascending by Unicode
   code point. After de-duplication the key admits no tie, so the resulting order is a function of the
   failure set alone and is identical for every raise site. `__init__` does not compute `derived`, does
   not rewrite an item, and does not validate item shape: producing well-formed items is the raiser's
   obligation, and `validate` is the only raiser that produces more than one.
6. **One representation only.** No other exception in the §9.5 taxonomy carries a failure payload; no
   callable in `v2/lske/` returns a validation error object, an error list, or a boolean in place of
   raising; and no second spelling of `failures` exists in `v2/lske/`.
7. **The raise sites, exhaustively.** Five sites in `v2/lske/` deliver a `SchemaViolation` in Phase 1 —
   four that raise and one that propagates — and each produces items of the shape above:

   | Raise site | Items | Specified in |
   |---|---|---|
   | `v2.lske.schema.validate` | one per false **assertion** keyword application, `schema_pointer` non-empty | §9.13.3 (R9-15, R9-15.1) |
   | `v2.lske.schema.LskeRecord.from_payload` | exactly those `validate` produced; the exception propagates unchanged | v1.1.1 §9.13.4 cl. 6, unchanged |
   | `v2.lske.schema.LskeRecord.__init__` | exactly one: `(<pointer to the reported node>, "", "frozen", False)` | §9.13.4 cl. 2.4 |
   | `v2.lske.schema.allocate_event_id` | exactly one: `("", "", "required", False)` when an event-body key is absent | v1.1.1 §9.13.5, unchanged in signature and condition |
   | `v2.lske.events.append_event` | `("", "", "required", False)` and/or `("", "", "additionalProperties", False)` | §9.13.8 cl. 4 |

   Later phases add raise sites; each conforms to this contract, and none adds a representation.


## 9.13.1 Ownership map (two rows reissued)

The map's membership, its twelve rows and its one-owner-per-component rule are unchanged. Two *Public
surface* cells are reissued so that the map names the surfaces this amendment freezes; no row is added,
removed, renamed or re-owned.

| Phase-1 component | Owning module | Public surface (reissued) |
|---|---|---|
| Exception taxonomy | `v2.lske.errors` | §9.5 (seven classes, unchanged) and §9.5.1 (the `SchemaViolation` failure payload) |
| Durable event log writer | `v2.lske.events` | `append_event` (§9.13.8); RC-07 unchanged; allocates no identifier of its own |

Every other row of §9.13.1 is unchanged, and every row still has exactly one owner with no component in
two rows.

## 9.13.2 Frozen literal registers (one line reissued, `RF-04`)

Every declaration of v1.1.1 §9.13.2 stands unchanged — `SCHEMA_DRAFT`, `SCHEMA_BASE_URI`, the eight
literal tuples, `CollectionSpec`, `COLLECTION_SPECS`, `COLLECTION_SPEC_BY_KEY`, and the imported-never-
restated rule of RB-05 cl. 5 — except that the `ONTOLOGY_VERSION` line is reissued with its literal:

```python
ONTOLOGY_VERSION: str = "1.1.2"   # the semver written into every record's ontology_version.
                                  # The only declaration of this value in v2/lske/ and
                                  # schemas/lske/ (RF-04 cl. 2).
                                  # Not v2.lske.__version__, which is the package version and is
                                  # written into no record (RF-04 cl. 3).
```

`v2/lske/__init__.py` defines no `ONTOLOGY_VERSION` and exports none. The value changes only by a
specification amendment under R9-0/R9-12 and then equals that amendment's version number (`RF-04` cl. 4).
The `ontology_version` field is constrained by the schema to the semver form, not to this value, so
records written under an earlier ontology remain valid.

## 9.13.3 Validation and schema access — reissued (`RF-02`, `RF-03`)

This section replaces v1.1.1 §9.13.3 in full. Signatures and names are unchanged; the accessor
representation and the failure ordering are now stated.

```python
def all_schemas() -> Mapping[str, dict[str, Any]]: ...
    # A fresh MappingProxyType over a fresh dict of 23 entries keyed by schema name:
    # "record", the 20 collection keys in section 1.2 order, "relation", "obs2" -- in that
    # key order. Each value is a fresh deep copy, produced exactly as the accessors below
    # produce theirs. The mapping rejects assignment and deletion; the values are mutable
    # copies. No mutation of any returned object can reach canonical module state.

def record_schema() -> dict[str, Any]: ...
def collection_schema(collection_key: str) -> dict[str, Any]: ...
def relation_schema() -> dict[str, Any]: ...
def obs2_schema() -> dict[str, Any]: ...
    # Each returns a fresh deep copy on every call: fresh dict at every mapping node,
    # fresh list at every array node, JSON types only. Distinct object identity on every
    # call; never the canonical object; never shared with another return value.
    # collection_schema raises OntologyError on an unknown collection_key (section 9.5).

def validate(payload: Mapping[str, Any], schema_name: str) -> None: ...
    # The single public validation entry point of v2/lske/ (RB-05 cl. 1).
    # schema_name is a key of all_schemas(). Returns None on success.
    # Raises SchemaViolation whose message names the instance pointer, the schema pointer
    # and the failing keyword, in that order, and whose failures tuple (section 9.5.1)
    # carries every failure; raises OntologyError when schema_name is unknown.
    # Never raises a bare ValueError or AssertionError (section 9.5).
```

**Accessor representation (`RF-03`).** Clauses 1–6 of `RF-03` are normative here: canonical objects are
module-private and built once at import; the four accessors return fresh deep mutable copies of JSON
types; `all_schemas` returns a fresh mapping proxy over fresh deep copies in the fixed key order; no
returned object is ever the canonical object or shared with another returned object; equality holds
between any two calls with the same subject and identity never does; and the v1.1.1 phrase
"deep-immutable views" means exactly that no mutation of a returned object can reach canonical module
state.

**Rule R9-14.** Unchanged.

**`schema_name` domain.** `schema_name` is any of the twenty-three keys of `all_schemas()`; an unknown key
raises `OntologyError`. Validating against `"record"` validates the envelope fragment on its own and is
**not** the record validation path: RB-01 cl. 6's single pass for a record is against its collection
schema, and RB-01 cl. 3 makes the twenty collection schemas the only validation targets for records. Both
statements are v1.1.1's, unchanged; this sentence only says which of them applies to which argument.

**Rule R9-15 (reissued).** `validate` reports **all** failures for the payload, not the first.
`SchemaViolation` carries them in its `failures` tuple (§9.5.1). The order is the total key
`(derived, instance_pointer, schema_pointer, keyword)`: primary findings first in ascending
instance-pointer order, ties broken by schema pointer then keyword, all derived findings last in the same
order. Identical findings are reported once. A validator that stops at the first failure makes a ten-field
record take ten runs to fix, and it makes a schema regression look smaller than it is; an order that is
not total makes the same failure set assertable two ways.

**What "all failures" counts, exactly.** The failure set is one item per **assertion keyword application
that evaluates to false and contributes to the instance's invalidity** — an assertion keyword being one
whose own evaluation yields a boolean result against the instance location (`type`, `enum`, `const`,
`pattern`, `required`, `minProperties`, `maxProperties`, `minItems`, `maxItems`, `uniqueItems`,
`minLength`, `maxLength`, `minimum`, `maximum`, `additionalProperties`, `unevaluatedProperties`,
`propertyNames`, and any other assertion the §9.2 schemas use). An **applicator** keyword — `allOf`,
`anyOf`, `oneOf`, `not`, `if`, `then`, `else`, `properties`, `patternProperties`, `items`, `prefixItems`,
`$ref`, `$defs` — is **never** reported: its result is a function of its subschemas' results, and the
subschema assertions that failed are reported instead. Reporting an applicator would report the same
defect twice at two pointers. Four conventions follow and are fixed:

1. **Contribution is a path test.** An application is reported iff it evaluates to false **and** every
   applicator on its evaluation path also evaluates to false. A false assertion inside an `if` condition,
   inside a `not`, or inside a passing `anyOf`/`oneOf` alternative is therefore **not** reported: the
   enclosing applicator did not fail because of it, and a record that is valid cannot carry a reported
   failure. A false `if` condition is the normal case for the conditional requirements of RB-01 cl. 5 and
   is silent.
2. One failing keyword occurrence at one instance location is **one** item, whatever the number of causes:
   a `required` listing three absent properties yields one item, not three, and the message names the
   properties (R9-9 permits field names).
3. `required`, `additionalProperties`, `unevaluatedProperties`, `propertyNames`, `minProperties` and
   `maxProperties` report at the pointer of the **object** they constrain, not at a child.
4. `instance_pointer` is the location of the instance the keyword was applied to; `schema_pointer` is that
   keyword's absolute location (§9.5.1 cl. 3). Together they make each item unique, which is what makes the
   ordering key of §9.5.1 cl. 5 total.

**Rule R9-15.1 (reissued and completed).** When any `allOf` branch fails, Draft 2020-12 discards that
branch's `properties` annotations, so the sibling `unevaluatedProperties: false` also fails and names
every property the failed branch declared. Such a finding is a consequence of the primary failure, not a
second defect. It is reported, never suppressed, marked `derived: True`, and ordered last. Precisely:

1. A finding is `derived` **iff** its `keyword` is exactly `"unevaluatedProperties"` **and** the failure
   set contains at least one finding whose `keyword` is not `"unevaluatedProperties"` and whose
   `instance_pointer` is at or below that finding's `instance_pointer` (§9.5.1 cl. 4).
2. For every finding whose `keyword` is not `"unevaluatedProperties"`, `derived` is `False`.
3. An `unevaluatedProperties` finding with no primary finding at or below its instance pointer — a
   genuinely undeclared key with both branches passing — has `derived` `False` and sorts in the primary
   block. This is the case `AC-P1-03` tests, and it must stay distinguishable from a cascade.
4. Derived findings are reported in full and never merged with their cause.
5. `derived` is computed once over the complete primary failure set, before ordering, and is not
   recursive.
6. Clause 1 is exactly the dialect's cascade condition, not an over-approximation of it: under RB-01's
   depth-two composition every property of a record is declared by one of the two branches, so any failing
   assertion at or below the composed object's pointer necessarily lies inside a branch and therefore
   discards that branch's `properties` annotations. A closure failure that coexists with a primary failure
   in the same subtree is a cascade in every case the LSKE schemas can produce; a closure failure with no
   such coexisting failure is cl. 3's genuine case.

This behaviour is a property of the dialect, was confirmed empirically (v1.1.1 Appendix C.1), and is
stated here so that an implementer does not read a cascade as a schema bug and "fix" it by removing the
closure keyword — which would reopen `BLK-P1-01`.

## 9.13.4 cl. 2 — the constructor (reissued, `RF-05`)

Clauses 1 and 3–7 of v1.1.1 §9.13.4, the class body, the field list, the properties, `as_dict`, `__eq__`
and `__hash__` are unchanged. Clause 2 is reissued:

> **2. Constructor.** `from_payload` is the only public constructor. The generated `__init__` accepts a
> `payload` **iff** it satisfies the frozen-payload predicate below, and raises `SchemaViolation`
> otherwise, so a live mutable payload cannot be installed by calling the dataclass directly
> (RB-04 cl. 5).
>
> **2.1 The frozen-payload predicate.** `payload` is accepted iff it is an instance of
> `types.MappingProxyType` and every node of its value tree satisfies: a **mapping node** is a
> `types.MappingProxyType` whose every key is a `str` and whose every value satisfies the rule; a
> **sequence node** is a `tuple` whose every item satisfies the rule; a **leaf node** is `None` or an
> instance of `str`, `bool`, `int` or `float`. No other node satisfies the rule.
>
> **2.2 Accepted.** Exactly those values. `MappingProxyType({})` is accepted. The deep-freeze step's
> output satisfies the predicate by construction, so `LskeRecord(r.collection_key, r.payload)` is accepted
> for every `r` obtained from `from_payload`.
>
> **2.3 Rejected.** Everything else, without exception: `dict`, `list`, `set`, `frozenset`, `bytes`,
> `bytearray`, `datetime`, `Decimal`, any of those at any depth inside a proxy, a non-`str` key at any
> depth, any other `Mapping` implementation including a user-defined immutable mapping, and any
> non-mapping value including `None`.
>
> **2.4 Behaviour.** The predicate is evaluated before any attribute is set, by this procedure, which
> reports the **first node that fails its own node-local test** and never reports a node merely because a
> descendant failed:
>
> 1. Test the node's own type against cl. 2.1 (mapping node → `types.MappingProxyType`; sequence node →
>    `tuple`; leaf node → `None`, `str`, `bool`, `int` or `float`). If it fails, report **this** node.
>    Applied to `payload` itself, this is cl. 2.1's top-level test: `payload` must be a
>    `types.MappingProxyType`, and anything else — a `dict`, a `list`, a `str`, `None` — is reported at
>    pointer `""`.
> 2. If the node is a mapping, test that every key is a `str`, examining keys in the mapping's own
>    iteration order. If one is not, report **this** node — a non-`str` key has no JSON Pointer of its own,
>    so the containing mapping is the reported location.
> 3. Recurse: into a mapping's values in ascending Unicode code-point order of their keys, and into a
>    tuple's items in index order.
>
> The procedure stops at the first report. On failure the raised `SchemaViolation` carries exactly one
> item, `(<RFC 6901 pointer to the reported node>, "", "frozen", False)`; the pointer is `""` when the
> reported node is `payload` itself. On success `collection_key` and `payload` are stored as given. The
> generated `__init__` performs no schema validation and no collection-key lookup: `validate` is reached
> only through `from_payload` (R9-14). The procedure's helper name and signature are §9.9 latitude; its
> behaviour is not.


## 9.13.8 The durable event writer (new, `RF-06`)

`v2.lske.events` owns the durable LSKE event log (RC-07, §9.13.1). This section is the single site of its
public API. The module's disposition, its two event kinds, its file path, its retention and its
single-writer status are unchanged.

```python
def append_event(root: Path, event: Mapping[str, Any]) -> str: ...
    # The only public callable in v2/lske/events.py and the only writer of
    # <root>/.ros/lske_events.jsonl (RC-07).
    #
    # event is the nine-key event body of section 9.3.1:
    #   {kind, at, by, authority, target, record_id, from, to, cause}
    # All nine present; no tenth key; no event_id input.
    #
    # Order of evaluation:
    #   1. key set not exactly the nine  -> SchemaViolation (section 9.5.1 items below)
    #   2. kind not in ("lifecycle", "evidence") -> OntologyError
    #   3. event_id = v2.lske.schema.allocate_event_id(event)
    #   4. append canonical_json({**event, "event_id": event_id}) + b"\n"
    #   5. return event_id
    #
    # Returns the allocated event_id, LEV-<32 lowercase hex> (S-07), exactly as written.
```

1. **Ownership.** One public callable, one written file, no reader, no iterator, no path helper, no
   register, no class. Phase 1 adds no reader: `MEM-01` resolves `event_id`s against this log, and the
   check that does so is `ros.store._check_memory`, whose build stage (§9.8 stage 4) is unchanged and
   outside Phase 1. The writer allocates no identifier and computes no hash of its own (RB-05 cl. 2).
2. **Parameters.** `root: Path` is the repository root containing `.ros/`; the log is exactly
   `root / ".ros" / "lske_events.jsonl"` and no other path is written. `event: Mapping[str, Any]` is the
   nine-key body above (§9.3.1 as enumerated by §9.13.5; RC-07 cl. 4's ten keys are the *written* line,
   which adds `event_id`).
3. **Return value.** The `event_id` `str`. Nothing else: no receipt, no path, no line number, no `None`.
4. **Validation behaviour.** A key-set mismatch raises `SchemaViolation` whose `failures` carries
   `("", "", "required", False)` when a key is absent and `("", "", "additionalProperties", False)` when
   an undeclared key is present — both items when both apply, ordered by §9.5.1 cl. 5. A `kind` outside
   the two of RC-07 raises `OntologyError`. R9-9 governs both messages, unchanged. No schema is consulted:
   there is no event schema among the twenty-three, and the body is fixed by §9.3.1. `append_event` is not
   a validation function and defines no public validator, so R9-14 is not engaged.
5. **Append semantics.** The file is opened in binary append mode, exactly one line is written, and the
   file is closed. One call appends exactly one line: `canonical_json(...)` bytes followed by one `\n`
   (`0x0A`), UTF-8, no BOM, no pretty-printing, no trailing whitespace, no blank line, no header.
6. **Storage behaviour.** Existing bytes are never read, rewritten, truncated, reordered, reformatted or
   deleted; no seek, no in-place edit, no temporary-file-and-rename (that discipline belongs to receipts,
   §9.3.1). A missing `.ros/` directory and a missing log file are created on first append; an existing
   file is never re-created. The append is not a commit point (§9.3.1, unchanged).
7. **No de-duplication.** Two calls with equal bodies append two lines carrying the same
   content-addressed `event_id`; R9-7's no-re-emit rule is enforced by the transaction phase, not here,
   because one rule with two enforcement sites has two ways to be satisfied.
8. **Authority binding is unchanged and is not amended here.** §6.8, test 4, `I-25` and RC-07 stand
   exactly as written; no §6.8 row is added or removed. The parameter list of clause 2 admits no actor, so
   the authority check belongs to the calling phase — which is what §9.3.1 already states: the append is
   "the last step of the phase that wrote the record".
9. **Totality at the boundaries.** Two error classes lie outside the §9.5 taxonomy's subject and are
   **not** re-wrapped, exactly as `ros.authority.AuthorityError` is not: an error raised by
   `ros.protocol.canonical_bytes` for a value it cannot serialize propagates as that module's own error,
   and an operating-system error raised by the filesystem — a missing or unwritable `root`, a permission
   failure, a full device — propagates unchanged. §9.5 governs violations the LSKE detects, not the
   operating system. `append_event` therefore produces exactly three outcomes of its own: the returned
   `event_id`, `SchemaViolation` under clause 4, and `OntologyError` under clause 4.

## 9.6 Test matrix (rows 1–2 reissued, `A-7`)

The matrix remains **twenty-three rows**; no test file is added, none is renamed, and no row is
reordered. Rows 1 and 2 have their *Asserts* cells reissued. The reissue is **additive with exactly one
substitution**: the whole of v1.1.1 §9.6 row 1's and row 2's *Asserts* cells is retained without
alteration and is not restated here, except that row 2's phrase "reports all failures ordered by instance
pointer" is read as the total key of R9-15 — the same order, with its tie-breaks and its derived-last rule
supplied. No other v1.1.1 assertion is weakened, removed, reworded or replaced, and no assertion is
dropped.

| # | Test file | Asserts appended to the retained v1.1.1 cell |
|---|---|---|
| 1 | `test_schema_generation.py` | **Appended by `RF-03`:** `all_schemas()` has exactly twenty-three entries in the fixed key order of §9.13.3 and rejects item assignment and deletion; two calls to any accessor return equal but non-identical objects, and `all_schemas()[k]` is equal to but not identical with the corresponding accessor's result; a mutation applied to any returned schema is absent from a subsequently returned schema, from `validate`'s behaviour and from the byte-match comparison of R9-2; every returned tree contains only `dict`, `list`, `str`, `bool`, `int`, `float` and `None`; `collection_schema` raises `OntologyError` on an unknown key. |
| 2 | `test_envelope.py` | **Appended by `RF-01`/`RF-02`:** a payload with two failures at one instance pointer yields a `failures` tuple that is a `tuple` of four-element primitive tuples, de-duplicated, ordered by `(derived, instance_pointer, schema_pointer, keyword)`, with `exc.args == (message,)`; no item names an applicator keyword; a payload failing one `allOf` branch yields at least one `derived` `True` `unevaluatedProperties` item positioned after every `derived` `False` item; a payload with a genuinely undeclared key and both branches passing yields an `unevaluatedProperties` item with `derived` `False`. **Appended by `RF-04`:** `v2.lske.schema.ONTOLOGY_VERSION == "1.1.2"`, `v2.lske` exposes no `ONTOLOGY_VERSION`, and the value has exactly one literal site in `v2/lske/`. **Appended by `RF-05`:** the dataclass constructor accepts the frozen payload of an existing `LskeRecord` and `MappingProxyType({})`, and rejects each of a `dict`, a `list` nested inside a proxy, a `set`, a non-`str` key and a non-mapping, raising `SchemaViolation` whose single item is `(<pointer to the reported node>, "", "frozen", False)` with the pointer identifying the offending node and not an ancestor. **Appended by `RF-06`:** `append_event` returns the `LEV-` identifier it wrote, appends exactly one line per call, leaves every previously written byte unchanged across appends, creates `.ros/lske_events.jsonl` on first append, raises `SchemaViolation` on a missing or extra body key and `OntologyError` on a third `kind`, and is the only public callable in `v2/lske/events.py`. |

Rows 3–23 are unchanged, including row 3's stage-2 clause and row 9's `MEM-01` resolution against
`.ros/lske_events.jsonl`.

## 9.9 What the implementer may decide (reissued)

Unchanged in substance. The list of what is **not** open gains, by this amendment: the `SchemaViolation`
failure payload of §9.5.1; the failure ordering and derived rule of §9.13.3 (R9-15, R9-15.1); the schema
accessor representation of §9.13.3 (`RF-03`); the `ONTOLOGY_VERSION` literal, owner and update rule of
§9.13.2 (`RF-04`); the frozen-payload predicate of §9.13.4 cl. 2 (`RF-05`); the durable event writer API
of §9.13.8 (`RF-06`); the rule `R9-19` (§9.14); and the rulings `RF-0`, `RF-0.1`, `RF-0.2`, `RF-0.3` and
`RF-01`…`RF-06`.

What remains open is exactly what §9.9 already listed, and no item is added to it by this amendment:
private helper names and signatures, internal data structures inside a function body, log wording outside
exception text, test fixture file names, the order of independent assertions within a test, and docstring
prose. Whether an engineering decision outside that list is latitude is determined by R9-19 (§9.14) and
not by this section, which is unchanged in substance.

**Rule R9-12.** Unchanged.

## 9.14 Phase 1 specification freeze (new)

**Rule R9-19 (Phase 1 Specification Freeze).** Upon publication of LSKE Specification v1.1.2, the
Phase 1 specification is permanently frozen.

1. Future implementation reviews SHALL identify only implementation defects, specification
   non-conformance, or implementation bugs.
2. They SHALL NOT request additional specification detail unless they demonstrate that two conforming
   implementations could produce different externally observable behaviour. The demonstration is part of
   the finding; a finding without it is out of order.
3. Internal implementation details — including helper functions, private algorithms, dependency
   selection, internal data structures, optimization strategies, and private module organization — are
   implementation latitude unless explicitly declared normative by the Constitution.
4. This rule does not weaken R9-0: a genuine contradiction between two normative sentences, or a
   normative sentence that no conforming implementation can satisfy, remains a Constitutional Change
   Request. What it forecloses is a request for detail where one observable behaviour is already fixed.

**Relation to §9.9.** §9.9 enumerates what the implementer may decide; R9-19 cl. 3 states the *principle*
by which an unenumerated engineering decision is classified. Where the enumeration of §9.9 and clause 3
differ in extent, **clause 3 governs**, as the later and more general rule, and §9.9's enumeration stands
as its non-exhaustive instance list. This is the one deliberate governance addition of this amendment, made
under the express direction of the Final Implementation Authority Review; it changes no existing rule's
text and no normative requirement on the specification's content.


---

# APPENDIX A — Rule matrix (amended entries)

## A.1C Final-amendment decision matrix (machine-readable)

Every decision point the strict conformance review named and the Final Implementation Authority Review
classified as a Normative Defect, with exactly one value. A value of `none` is a decision, not an
omission. `A.1B` of v1.1.1 is unchanged and remains in force with **one key reissued**, because this
amendment completes the value it carried:

```yaml
# A.1B, one key reissued (RF-02):
validation_reports: "every contributing assertion failure, ordered by (derived, instance_pointer, schema_pointer, keyword) ascending"
# v1.1.1 read: "all failures, ordered by instance pointer" -- the same order, now with its tie-breaks
# and its derived-last rule stated. Every other key of A.1B stands.
```

```yaml
lske_final_amendment_matrix:
  spec_version: "1.1.2"
  amends: "1.1.1"
  closes: ["IMP-BLK-03", "IMP-BLK-04", "IMP-BLK-05", "IMP-BLK-06", "IMP-BLK-07B"]
  permanently_implementation_latitude: ["IMP-BLK-01", "IMP-BLK-02", "IMP-BLK-07A"]

  # RF-01 / A-1
  schema_violation_payload_attribute: "failures"
  schema_violation_payload_type: "tuple[tuple[str, str, str, bool], ...]"
  schema_violation_item_fields: ["instance_pointer", "schema_pointer", "keyword", "derived"]
  schema_violation_item_access: "positional"
  schema_violation_args: "(message,) exactly"
  schema_violation_instance_pointer_form: "RFC 6901 JSON Pointer; \"\" is the document root"
  schema_violation_schema_pointer_form: "absolute keyword location <$id>#<RFC 6901 pointer>; \"\" when no schema was evaluated"
  schema_violation_derived_marker: "item element 4, bool"
  schema_violation_order_key: "(derived, instance_pointer, schema_pointer, keyword) ascending"
  schema_violation_string_order: "Unicode code point"
  schema_violation_duplicate_policy: "identical items collapsed, first occurrence kept"
  schema_violation_normalized_by: "SchemaViolation.__init__"
  schema_violation_minimum_items_from_package_raise_sites: 1
  schema_violation_reported_applications: "assertion keyword applications that evaluate to false on a wholly failing evaluation path"
  schema_violation_applicator_keywords_reported: none
  schema_violation_passing_branch_assertions_reported: none
  schema_violation_if_condition_failures_reported: none
  schema_violation_items_per_keyword_occurrence: 1
  schema_violation_object_keyword_pointer: "the object the keyword constrains"
  schema_violation_message_contract: "RB-05 cl. 1 and R9-9, unchanged"
  other_public_error_representations: none

  # RF-02 / A-2
  derived_definition: "keyword == unevaluatedProperties AND a non-unevaluatedProperties failure exists at or below its instance pointer"
  derived_containment_test: "p == q or p.startswith(q + \"/\")"
  derived_for_other_keywords: false
  derived_evaluation: "once, over the complete primary failure set, before ordering; not recursive"
  derived_placement: "last, by order key element 1"
  derived_suppression: none
  genuine_unevaluated_properties_failure_derived: false

  # RF-03 / A-3
  canonical_schema_ownership: "module-private state of v2.lske.schema, built once at import"
  accessor_return_type: "dict[str, Any]"
  all_schemas_return_type: "Mapping[str, dict[str, Any]] as types.MappingProxyType"
  accessor_copy_semantics: "fresh deep copy on every call"
  accessor_value_types: ["dict", "list", "str", "bool", "int", "float", "null"]
  returned_object_mutability: "mutable; mutation cannot reach canonical state"
  all_schemas_mutability: "mapping immutable; values mutable copies"
  all_schemas_key_order: "record, 20 collection keys in section 1.2 order, relation, obs2"
  accessor_identity: "distinct object on every call; never canonical; never shared"
  accessor_caching: none
  collection_schema_unknown_key: "OntologyError"
  deep_immutable_views_meaning: "no mutation of a returned object can reach canonical module state"

  # RF-04 / A-4
  ontology_version_value: "1.1.2"
  ontology_version_owner: "v2.lske.schema"
  ontology_version_literal_sites: 1
  ontology_version_literal_site_scope: "v2/lske/ and schemas/lske/; the specification and test 2's pinning assertion are not sources"
  ontology_version_in_package_init: none
  ontology_version_authority: "LSKE specification amendment under R9-0/R9-12"
  ontology_version_update_rule: "equals the version number of the amendment that changes it"
  package_version_owner: "v2/lske/__init__.py.__version__"
  package_version_written_into_records: none
  ontology_version_schema_constraint: "semver form only, not a single value"

  # RF-05 / A-5
  frozen_payload_predicate: "MappingProxyType tree of MappingProxyType(str keys) | tuple | str | bool | int | float | None"
  frozen_payload_accepted_empty_proxy: true
  frozen_payload_rejected: ["dict", "list", "set", "frozenset", "bytes", "bytearray", "datetime", "Decimal", "other Mapping implementations", "non-str keys", "non-mapping values"]
  frozen_payload_predicate_totality: "total over every Python object; two results"
  frozen_payload_traversal: "pre-order; keys type-checked in mapping iteration order; values recursed ascending by code point; tuple items by index"
  frozen_payload_reported_node: "the first node failing its own node-local test, never an ancestor"
  direct_constructor_failure_exception: "SchemaViolation"
  direct_constructor_failure_item: "(pointer to the reported node, \"\", \"frozen\", false)"
  direct_constructor_schema_validation: none
  direct_constructor_collection_key_lookup: none
  public_constructors: 1

  # RF-06 / A-6
  event_writer_api: "v2.lske.events.append_event(root, event)"
  event_writer_public_callables: 1
  event_writer_parameters: ["root: Path", "event: Mapping[str, Any]"]
  event_writer_body_keys: ["kind", "at", "by", "authority", "target", "record_id", "from", "to", "cause"]
  event_writer_event_id_input: none
  event_writer_return: "str, the allocated event_id (LEV-<32 lowercase hex>)"
  event_writer_key_set_failure: "SchemaViolation"
  event_writer_kind_failure: "OntologyError"
  event_writer_schema_validation: none
  event_writer_line_form: "canonical_json({**event, event_id}) + \"\\n\", UTF-8, LF"
  event_writer_lines_per_call: 1
  event_writer_open_mode: "binary append"
  event_writer_rewrite_or_truncate: none
  event_writer_creates_missing_path: true
  event_writer_deduplication: none
  event_writer_authority_parameter: none
  event_writer_authority_binding: "unchanged; sec 6.8, test 4, I-25 not amended; the check belongs to the calling phase"
  event_writer_serialization_error: "propagates from ros.protocol, not re-wrapped"
  event_writer_os_error: "propagates from the filesystem, not re-wrapped"
  event_writer_own_outcomes: 3
  event_writer_readers_added: none
  event_log_path: "<root>/.ros/lske_events.jsonl"

  # A-7 / A-8
  test_files_added: none
  test_matrix_rows: 23
  test_matrix_rows_reissued: [1, 2]
  build_stages_added: none
  traceability_rows: 27
  acceptance_criteria: 27
  traceability_rows_reissued: [14, 20]
  traceability_rows_added: [24, 25, 26, 27]
  files_added_to_frozen_layout: none
  modules_added: none
  public_names_added: ["v2.lske.events.append_event", "SchemaViolation.failures", "SchemaViolation.__init__"]
  public_names_removed: ["v2.lske.ONTOLOGY_VERSION"]
  sections_added: ["9.5.1", "9.13.8", "9.14", "A.1C"]
  sections_reissued: ["9.1 (2 cells)", "9.13.0 (1 sentence)", "9.13.1 (2 cells)", "9.13.2 (1 line)", "9.13.3", "9.13.4 cl. 2", "9.6 (rows 1-2, additively)", "9.9 (not-open list)", "A.2", "A.3", "C.3", "C.11", "D", "D.1"]
  rules_added: ["R9-19"]
  rules_changed: none
```

## A.2 Single-definition registers (amended and added rows only)

| Register | Size | Canonical section |
|---|---|---|
| Public exception failure payloads | 1 | §9.5.1 |
| Public error representations in `v2/lske/` | 1 | §9.5.1 |
| Failure ordering rules | 1 | §9.13.3 (R9-15) |
| Derived-marker producers | 1 | §9.13.3 (R9-15.1) |
| Schema accessor representations | 1 | §9.13.3 (`RF-03`) |
| Ontology version literal sites | 1 | §9.13.2 (`ONTOLOGY_VERSION`) |
| Immutable constructor predicates | 1 | §9.13.4 cl. 2.1 |
| Durable event writers | 1 | §9.13.8 |
| Final-amendment rulings | 6 (+ `RF-0`, `RF-0.1`, `RF-0.2`, `RF-0.3`) | Part 0Y |
| Phase-1 traceability rows | 27 | Appendix D |
| Phase-1 acceptance criteria | 27 | Appendix D.1 |

Every other row of A.2, including every row v1.1.1 amended, is unchanged. `Test matrix rows` remains
**23** and `Build stages` remains **9**: this amendment adds neither.

## A.3 API register (amended and added rows only)

| Module | Function | Authority / write target |
|---|---|---|
| `v2.lske.errors` | `SchemaViolation.__init__` and the `failures` attribute (§9.5.1) | none / none — an exception carries no authority and no write target |
| `v2.lske.events` | `append_event` (§9.13.8) | unchanged — §6.8 gains no row and is not amended (§9.13.8 cl. 8) |

No function above appears in a second module, and no module exposes a second spelling of any of them. The
`v2.lske.events` row supplements v1.1.0's descriptive `v2.lske.events` row, which named the module but no
function; together they name one module and one function, and the module still has exactly one row's worth
of API. Every other row of A.3, including every row v1.1.1 amended, is unchanged.

---

# APPENDIX C — Implementation-readiness audit (two count sentences reissued)

v1.1.1's Appendix C stands unchanged in method and result. Two of its sentences state counts that this
amendment changes; they are reissued here so that no surviving sentence contradicts an `RF` ruling
(`RF-0`). Nothing else in Appendix C is amended, and no check is re-run: Appendix G is this document's own
audit.

- **C.3, count sentence, reissued.** §9.13 adds **fourteen** public callables and classes — counted on
  v1.1.1 C.3's own basis, which counts callables and classes and not the frozen registers of §9.13.2: the
  thirteen of `v2.lske.schema` (`record_schema`, `collection_schema`, `relation_schema`, `obs2_schema`,
  `all_schemas`, `validate`, `allocate_record_id`, `allocate_event_id`, `canonical_json`, `content_hash`,
  `seal`, `LskeRecord`, `CollectionSpec`) and `append_event` in `v2.lske.events` (§9.13.8). None collides
  with a Part 6 name or with a name in `ros.*`. The registers `PRIMITIVES`, `DIMENSION_KEYS`,
  `DIMENSION_STATES`, `LIFECYCLE_STATES`, `LIFECYCLE_TRANSITIONS`, `CHANGE_KINDS`, `RELATION_TYPES`,
  `CONFIDENCE_BASES`, `SCHEMA_DRAFT`, `SCHEMA_BASE_URI`, `ONTOLOGY_VERSION`, `COLLECTION_SPECS` and
  `COLLECTION_SPEC_BY_KEY` are public data with one literal site each (§9.13.2, RB-05 cl. 5) and are
  counted there, not here. The remainder of C.3, including the reasoning for not using the name `Record`,
  is unchanged.
- **C.11, count sentence, reissued.** Appendix D is that mapping: **twenty-seven** rows, each with exactly
  one requirement, one module, one API, one schema, one test and one acceptance criterion. The remainder of
  C.11, including its method, is unchanged.

v1.1.1's Appendix F certification is superseded by this document's certification, as v1.1.2 supersedes
v1.1.1. v1.1.1's Appendix E (two deferred stage-2/stage-7 observations) is unchanged and remains in force.

---

# APPENDIX D — Phase-1 traceability (amended, `A-8`)

Appendix D stands at **twenty-seven rows**. Rows 1–23 are exactly v1.1.1's, save the cells of rows 14 and
20 reissued below. Rows 24–27 are traceability rows for the contracts `RF-01`, `RF-03`, `RF-04` and `RF-05`
freeze; each names a component §9.1 and §9.13 already required Phase 1 to deliver, and none introduces a
deliverable. Each row has exactly one requirement, one owning module, one API, one schema, one test and one
acceptance criterion. `none` is a decision, not an omission.

**Rows reissued:**

| # | Requirement | Module | API | Schema | Test | Acceptance criterion |
|---|---|---|---|---|---|---|
| 14 | RB-05 cl. 1 / R9-15 / R9-15.1 as completed by `RF-02` — one validation entry point reporting every failure in one total order | `v2.lske.schema` | `validate` | all 23 | test 2 | `AC-P1-14` |
| 20 | RC-07 / `RF-06` — durable LSKE event log | `v2.lske.events` | `append_event` | none — body fixed by §9.3.1 | test 2 | `AC-P1-20` |

**Rows added:**

| # | Requirement | Module | API | Schema | Test | Acceptance criterion |
|---|---|---|---|---|---|---|
| 24 | `RF-01` — the public `SchemaViolation` failure payload | `v2.lske.errors` | `SchemaViolation.failures` | none — an exception is not a record | test 2 | `AC-P1-24` |
| 25 | `RF-03` — schema accessor representation | `v2.lske.schema` | `all_schemas` | all 23 | test 1 | `AC-P1-25` |
| 26 | `RF-04` — the `ONTOLOGY_VERSION` register | `v2.lske.schema` | `ONTOLOGY_VERSION` | `record.schema.json` (`ontology_version`) | test 2 | `AC-P1-26` |
| 27 | `RF-05` — the immutable constructor predicate | `v2.lske.schema` | `LskeRecord.__init__` | `<collection>.schema.json` | test 2 | `AC-P1-27` |

Rows 1–13, 15–19 and 21–23 are unchanged in every cell. Row 21's subject remains §9.5's raise-site rule
and row 24's is §9.5.1's payload, so the two are not duplicates; row 22's version constant remains
`__version__` and row 26's is `ONTOLOGY_VERSION`, so those two are not duplicates either.

## D.1 Acceptance criteria (amended and added only)

Stage 1 is complete when, and only when, all **twenty-seven** hold. Each is a single decidable statement.
`AC-P1-01`…`AC-P1-13`, `AC-P1-15`…`AC-P1-19` and `AC-P1-21`…`AC-P1-23` are unchanged.

- `AC-P1-14` **(reissued)** `v2/lske/` exposes exactly one public validating callable, and its
  `SchemaViolation.failures` contains every failure exactly once, ordered by
  `(derived, instance_pointer, schema_pointer, keyword)` ascending, so that primary findings precede all
  derived findings.
- `AC-P1-20` **(reissued)** `v2.lske.events.append_event(root, event)` is the only public callable in
  `v2/lske/events.py`, returns the `allocate_event_id` identifier it wrote, appends exactly one line to
  `<root>/.ros/lske_events.jsonl` per call, and leaves every previously written byte unchanged.
- `AC-P1-24` `SchemaViolation.failures` is a tuple of four-element primitive tuples
  `(instance_pointer, schema_pointer, keyword, derived)`, de-duplicated and ordered by the §9.5.1 cl. 5
  key, with `args == (message,)` and no second public error representation in `v2/lske/`.
- `AC-P1-25` Every schema accessor returns a fresh, non-identical, deep, JSON-typed copy whose mutation
  reaches no canonical state, and `all_schemas()` returns a twenty-three-entry immutable mapping in the
  §9.13.3 key order.
- `AC-P1-26` `v2.lske.schema.ONTOLOGY_VERSION` is `"1.1.2"`, is the only declaration of that value in
  `v2/lske/` and `schemas/lske/`, and `v2.lske` exposes no `ONTOLOGY_VERSION`.
- `AC-P1-27` `LskeRecord`'s generated `__init__` accepts exactly the frozen-payload predicate of §9.13.4
  cl. 2.1 and raises `SchemaViolation` with the single `frozen` failure item on every other input.


---

# APPENDIX G — Self-audit (v1.1.2)

Each check states its method so that it can be re-run against this document plus v1.1.1 plus v1.1.0. A
check whose method cannot be re-run is an opinion. Appendix C of v1.1.1 (eleven checks) is unchanged and
is not re-run except where a check below names it.

## G.1 Every public API has exactly one definition — **Pass**

**Method.** Enumerate every public callable, class, attribute and register named in v1.1.0 Part 6, v1.1.1
§9.13 and this document; check for a second definition site, a second spelling, or a second signature
anywhere across the three documents.
**Result.** v1.1.1 Appendix C.3's thirteen `v2.lske.schema` names are unchanged in name and signature;
`RF-03` changes no annotation. Two public names are defined for the first time, each once:
`v2.lske.events.append_event` (§9.13.8) and `SchemaViolation.failures` with its `__init__` (§9.5.1). One
public name is removed as a duplicate: `v2.lske.ONTOLOGY_VERSION` (`RF-04` cl. 2), leaving
`v2.lske.schema.ONTOLOGY_VERSION` as the sole site. Each subject has exactly one specification site after
this amendment: `all_schemas`, the four accessors and `validate` in §9.13.3; `from_payload` in v1.1.1
§9.13.4 cl. 6 and its signature block, unchanged; `LskeRecord.__init__` in §9.13.4 cl. 2; `append_event` in
§9.13.8; `SchemaViolation` in §9.5 and its payload in §9.5.1. No name appears in two modules, and no
subject has two sites.

## G.2 Every acceptance criterion is executable — **Pass**

**Method.** For each of the twenty-seven criteria of Appendix D.1, name the callable or file it inspects
and the assertion form; mark any criterion that inspects no named surface.
**Result.** Twenty-seven criteria, twenty-seven named surfaces. **Twenty-five** are executable as written
against the surface their Appendix D row names, including the four the strict conformance review found
inexecutable and this amendment closes: `AC-P1-14` inspects `validate` and `SchemaViolation.failures`;
`AC-P1-20` invokes `append_event` and reads `.ros/lske_events.jsonl`; `AC-P1-12`'s constructor boundary is
supplied by `AC-P1-27` against `LskeRecord.__init__`; and the accessor and ontology-version contracts are
inspected by `AC-P1-25` and `AC-P1-26`. **Two** — `AC-P1-07` and `AC-P1-10` — stand exactly as v1.1.1 wrote
them, and the form in which each is tested is permanently implementation latitude by the classification of
the Final Implementation Authority Review (`IMP-BLK-02`, `IMP-BLK-07A`) and by R9-19 cl. 3. This document
neither amends them nor re-states their test form, and their latitude is not a gap in this audit but the
governing decision applied.

## G.3 Every observable behaviour has exactly one interpretation — **Pass**

**Method.** List every externally observable behaviour the five closed defects concerned; check each for a
second admissible reading.
**Result.** Failure payload — one attribute, one item shape, one order, one duplicate policy, one
reported-application rule that fixes the item set itself (§9.5.1, §9.13.3 R9-15). Derived marker — one
definition, one containment test, one placement, one soundness argument (§9.13.3 R9-15.1). Accessor —
one copy discipline, one identity rule, one key order, one meaning for "deep-immutable views" (§9.13.3).
Ontology version — one literal, one site, one authority, one update rule (§9.13.2). Constructor — one
predicate, one reporting procedure, one failure item, one accepted domain (§9.13.4 cl. 2). Event writer —
one
callable, one path, one line form, one return, one validation order (§9.13.8). No behaviour above admits a
second reading, and each is stated once.

## G.4 Every schema contract is deterministic — **Pass**

**Method.** Re-check RB-01's composition, closure, reference-resolution and serialization contract against
the accessor representation of `RF-03`; confirm that the byte-match test of R9-2 remains decidable and that
no schema value depends on a clock, a random source, an environment lookup or call order.
**Result.** Canonical objects are built once at import from literal registers; accessors return deep copies
of JSON types, so `json.dumps(..., sort_keys=True)` over any returned schema is byte-identical to the same
call over the canonical object, and R9-2's byte-match remains decidable. `all_schemas()`'s key order is
fixed. No accessor result depends on how many times it was called. `ONTOLOGY_VERSION` is a literal, not a
computed value. RB-01's composition, closure forms, offline registry and serialization are untouched.

## G.5 Every identifier has one owner — **Pass**

**Method.** Re-run v1.1.1 Appendix C.6 over this amendment: enumerate identifier allocation, parsing and
formatting sites, including any introduced by §9.13.8.
**Result.** Allocation: `allocate_record_id` and `allocate_event_id`, both in `v2.lske.schema` (R9-16).
Parsing: `ros.model`, unchanged. `receipt_id`: its single use site in `v2.lske.transaction`. §9.13.8 adds
no allocator and no format: `append_event` calls `allocate_event_id` and writes the value it returns. No
fourth site exists.

## G.6 Every ontology value has one owner — **Pass**

**Method.** For every frozen register of §9.13.2 and for `ONTOLOGY_VERSION`, count literal sites across
`v2/lske/`, the schemas, the generated files and the tests.
**Result.** RB-05 cl. 5's one-literal-site rule is unchanged for the eight tuples, `COLLECTION_SPECS` and
the imported ROS registers. `ONTOLOGY_VERSION` had two candidate sites and now has one (`RF-04` cl. 2);
`v2.lske.__version__` is a different quantity with its own single owner and is written into no record. No
register has two literal sites.

## G.7 Every public exception has one contract — **Pass**

**Method.** For each of the seven §9.5 classes, count contracts: base classes, raise conditions,
constructor signature and payload.
**Result.** Seven classes, seven contracts. `SchemaViolation` gains the one payload contract of §9.5.1 and
no other class gains a payload. `ros.authority.AuthorityError` is still not re-wrapped, and §9.13.8 cl. 9
records the same treatment for the two boundary error classes the taxonomy's subject excludes — a
serialization error from `ros.protocol` and an operating-system error from the filesystem — so every
outcome of every Phase-1 callable is accounted for without extending §9.5. R9-9 is unchanged and every
message form specified in this document names only keys, pointers and keywords — no measured value.

## G.8 Every immutable constructor has one behaviour — **Pass**

**Method.** Enumerate every constructor of `LskeRecord`; for each, state the accepted input domain, the
rejected domain and the exception.
**Result.** Two: `from_payload` (public, unchanged — validates then deep-freezes, `SchemaViolation` on an
invalid payload, `OntologyError` on an unknown `collection_key`) and the generated `__init__` (the
frozen-payload predicate of §9.13.4 cl. 2.1, `SchemaViolation` with one `frozen` failure item otherwise).
Both domains are total and disjointly specified; no third constructor, no `unsafe=`, no `validate=False`.

## G.9 Every event writer has one API — **Pass**

**Method.** Search v1.1.0, v1.1.1 and this document for any callable that writes
`.ros/lske_events.jsonl` or emits an LSKE event.
**Result.** Exactly one: `v2.lske.events.append_event` (§9.13.8). RC-07's single-writer rule is unchanged,
`ros.events` remains reuse-unchanged with no added kind, and no reader is introduced.

## G.10 Every acceptance criterion maps to exactly one implementation surface — **Pass**

**Method.** Join Appendix D's twenty-seven rows to Appendix D.1's twenty-seven criteria on criterion
identifier; check for a criterion with no row, a row with no criterion, a criterion naming two APIs, and an
API named by two criteria for the same requirement.
**Result.** Twenty-seven-to-twenty-seven, total and injective. Rows 14 and 20 name the surfaces their
criteria inspect; rows 24–27 each name one new frozen surface. Row 21 (taxonomy escape) and row 24 (failure
payload) name different subjects of the same class and are not duplicates. Every criterion is assigned to
exactly one of test 1, test 2 or test 3, and the reissued §9.6 rows 1–2 contain the corresponding
assertions.

---

# APPENDIX H — Non-regression audit

| # | Assertion | Evidence |
|---|---|---|
| 1 | **No new architecture has been introduced.** | No module, package file, schema file, collection, relation type, dimension, dimension state, lifecycle state, write operation, transaction phase, authority class, write target, gate, KPI, primitive, test file or build stage is added (§0Y.9, A.1C `modules_added: none`, `files_added_to_frozen_layout: none`, `test_files_added: none`, `build_stages_added: none`). The two new public members — `append_event` and `SchemaViolation.failures`, with the constructor signature of the existing `SchemaViolation` class — name components v1.1.1 already required Phase 1 to deliver, inside files §9.1 already lists. |
| 2 | **No existing architecture has changed.** | RB-01's composition, closure forms, inheritance depth, offline registry and serialization are untouched; the ten-field relation envelope and the derived `edge_state` rule are untouched; the thirty-two-entry nested catalogue is untouched; `LskeRecord`'s fields, equality, two hashes and immutability direction are untouched; §9.13.1's ownership map keeps every row, owner and component — only two *Public surface* cells are reissued to name the surfaces now frozen; the twenty-three-row test matrix and nine-stage build order keep their membership; `ros.*` is unmodified. |
| 3 | **No governance rule has changed.** | R9-0, R9-1, R9-2, R9-12, R9-13, R9-14, R9-16, R9-17, R9-18, RB-0…RB-06 and RC-0…RC-12 are unchanged in text and in effect. R9-15 and R9-15.1 are **completed**, not redirected: all failures are still reported, derived findings are still last, the closure keyword still never moves. Exactly one rule is **appended**, under the express direction of the Final Implementation Authority Review: R9-19 (§9.14). Its clause 3 declares internal implementation details latitude and therefore extends §9.9's enumeration in extent, as §9.14's *Relation to §9.9* paragraph states openly; it rewrites no existing sentence and imposes no new requirement on the specification's content. No other governance rule is added, amended or removed. |
| 4 | **No new features have been added.** | Every clause of `RF-01`…`RF-06` fixes the representation, value or signature of a behaviour v1.1.1 already required. No capability is reachable after this amendment that was not required before it: no reader, no de-duplication, no second validator, no second constructor, no new event kind, no new field, no new query token. |
| 5 | **No previously closed implementation-latitude issue has been reopened.** | §0Y.2 restates `IMP-BLK-01`, `IMP-BLK-02` and `IMP-BLK-07A` as permanently closed and amends no sentence concerning them. RB-01, RB-02 cl. 4, §9.2.4 note 2, Appendix D rows 1–11 and `AC-P1-01`…`AC-P1-11` stand as v1.1.1 issued them. §9.9's **open** list gains no item on their account: their classification rests on the Final Implementation Authority Review and on R9-19 (§9.14), the rule this document was ordered to append. |
| 6 | **The document remains backward compatible with v1.1.1 except for the approved amendments.** | Every section of v1.1.1 not named in the ruling index of §0Y.1 is unchanged and in force (Reading rule). The changes to v1.1.1's own text are exactly: §9.1 two Contents cells; §9.13.0 one sentence (the `v2.lske.errors` parenthetical); §9.13.1 two *Public surface* cells; §9.13.2 one line; §9.13.3 in full (same names, same signatures); §9.13.4 cl. 2; §9.6 rows 1–2 *Asserts* cells, additively; §9.9's not-open list, its open list being unchanged; Appendix A.1B's one key `validation_reports`; Appendix A.2 and A.3 added rows; Appendix C's C.3 and C.11 count sentences; Appendix D rows 14 and 20 plus rows 24–27; Appendix D.1's count sentence, `AC-P1-14`, `AC-P1-20` and `AC-P1-24`…`AC-P1-27`. Three sections are added: §9.5.1, §9.13.8 and §9.14 (rule R9-19). Four appendix sections are added: A.1C, G, H and J. One duplicate declaration is removed: `v2.lske.ONTOLOGY_VERSION`. Nothing else in v1.1.1 or v1.1.0 is touched. |

**Scope discipline.** No wording outside the paragraphs named in the ruling index was improved, no section
was refactored, reorganized or renumbered, and no sentence was rewritten for style.

---

# APPENDIX J — Implementation authority

**1. Does any remaining normative ambiguity exist?**

**No.** Appendix G records ten checks, each passing, over single API definition, criterion executability,
single interpretation of observable behaviour, schema determinism, identifier ownership, ontology-value
ownership, exception contracts, constructor behaviour, event-writer API, and criterion-to-surface mapping.
The five findings classified Normative Defect are closed by `RF-01`…`RF-06`; the three findings classified
Implementation Latitude are permanently closed and are not specification gaps.

Two things remain deliberately **bounded** rather than ambiguous, both unchanged from v1.1.1 and both
naming the authority that owns them: the interiors of `obs2` nodes, edges and overlay values belong to
`P1_OBSERVATORY_SCIENTIFIC_SPECIFICATION_v1.0.md` (§9.2.4 note 3, R7-2), and the two inherited
stage-2/stage-7 observations of v1.1.1 Appendix E belong to the stages that meet them. A boundary naming
its owner is a decision; only an unowned choice is an ambiguity.

**2. Authority determination.**

> **LSKE Specification v1.1.2 is the final authoritative Phase 1 specification.**
>
> **No further Constitutional Change Requests are required for Phase 1.**
>
> **No further specification reconciliation is authorized before implementation.**
>
> **All remaining engineering decisions are implementation latitude under R9-0 and §9.9.**
>
> **Phase 1 implementation is hereby authorized.**

**3. Standing condition (unchanged, not a blocker).**

The specification remains **Proposed / Unregistered** and `GOVERNANCE_REGISTRY.yaml` remains
`status: Draft`, so Phase 1 work is **engineering-only and produces no admissible scientific evidence**
(R0-3, §9.12, Article L-11). Every artifact generated carries
`GOVERNANCE: DRAFT — NO ADMISSIBLE EVIDENCE`. Building the LSKE does not raise Scientific Readiness; it
makes the transaction exist so that the first experiment producing admissible evidence can be carried.

## Certification

> **LSKE Specification v1.1.2 is implementation-complete and frozen for Phase 1. No architectural
> interpretation is required. Phase 1 implementation is authorized under R9-0, and the Phase 1
> specification is permanently frozen under R9-19.**

This certifies implementation-completeness of Phase 1, not scientific readiness and not registration. The
document confers no authority, amends no frozen subsystem, and where it appears to conflict with
`P1_V2_CONSTITUTION_LOCK_v1.0.md`, `ros.authority`, `ros.admissibility`, the Observatory specification or
the M1/P1-v2 runtime, they govern and this document is defective.

## Standing of this specification

- **Artifact:** `P1_V2_LSKE_SPECIFICATION_v1.1.2.md`, version 1.1.2, the final Phase-1 normative-defect
  correction of v1.1.1.
- **Status:** **Proposed / Unregistered.** Not entered in `GOVERNANCE_REGISTRY.yaml`.
- **Authority source:** **none.**
- **Architecture:** identical to v1.1.1 and therefore to v1.1.0. Twenty collections, fifteen relation
  types, ten dimensions, four dimension states, five lifecycle states, seven transitions, five write
  operations, nine transaction phases with exactly one human phase, eight envelope blocks, ten memory
  checks, three new gates, four new KPIs, twenty-three test rows, nine build stages, one canonical store,
  one writer.

**End of specification.**
