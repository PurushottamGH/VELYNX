# P1-v2 Living Scientific Knowledge Engine — Engineering Specification

**GOVERNANCE: DRAFT — NO ADMISSIBLE EVIDENCE**

- **Artifact:** `P1_V2_LSKE_SPECIFICATION_v1.1.3.md`
- **Version:** 1.1.3
- **Release kind:** **Single-conflict enforcement-boundary reconciliation.** No redesign, no new
  capability, no scope change, no new architectural module, no new collection, no new phase, no new
  primitive, no new authority class, no new write target, no new transaction phase, no new gate, no new
  KPI, no new package file, no new schema file, no new test file, no new build stage, no weakening of
  determinism, and no change to any scientific meaning. One normative conflict — `SPEC-CONFLICT-01`,
  the unrepresentable ascending-interval constraint of §9.2.4 `N-18` — is closed by the five rulings
  `RG-01`…`RG-05`. The scientific invariant is preserved in full and acquires exactly one enforcement
  owner.
- **Supersedes:** `P1_V2_LSKE_SPECIFICATION_v1.1.2.md` v1.1.2 — retained, readable, non-current
- **Carries forward unchanged:** the whole of v1.1.2, and through it the whole of v1.1.1 and v1.1.0,
  except the sections this document names. Part 0R (`RC-0`…`RC-12`), Part 0X (`RB-0`…`RB-06`) and
  Part 0Y (`RF-0`…`RF-06`) stand in force in their entirety. `RF-01` is **not** amended.
- **Status:** Proposed / Unregistered
- **Date:** 2026-08-03
- **Subsystem:** Living Scientific Knowledge Engine (LSKE)
- **Inherits without amendment:** `P1_V2_CONSTITUTION_LOCK_v1.0.md` v1.0.0; `ros.authority`;
  `ros.admissibility`; `ros.protocol`; `ros.events`; `ros.propagation`;
  `P1_OBSERVATORY_SCIENTIFIC_SPECIFICATION_v1.0.md`; the M1/P1-v2 runtime
- **Closes:** `SPEC-CONFLICT-01`, raised by
  `outputs/P1_V2_PHASE1_STAGE1_ACCEPTANCE_RECORD.md` Part II and sustained as a terminal Stage-1
  blocker by `outputs/P1_V2_STAGE1_INDEPENDENT_CERTIFICATION_AA7F751.md` §10, §11, §16
- **Authority source:** R9-0 (Constitutional Change Request route), as preserved by R9-19 cl. 4

**Reading rule.** This document is an amendment. Where a section number appears below, the text under it
**replaces** the corresponding text of v1.1.2 — or, where v1.1.2 did not reissue that section, of v1.1.1,
or failing that of v1.1.0 — in full. Every section not named here is unchanged and remains in force. No
sentence of v1.1.2, v1.1.1 or v1.1.0 is amended silently. Where this document and an earlier version
disagree on a named section, this document governs; where they do not disagree, both stand.

---

# PART 0Z — Enforcement-Boundary Reconciliation Record (v1.1.3)

## 0Z.1 Standing of this part

`outputs/P1_V2_STAGE1_INDEPENDENT_CERTIFICATION_AA7F751.md` returned
**STAGE-1 CERTIFICATION FAILED — REMEDIATION REQUIRED** on exactly one ground: §9.2.4 `N-18` states an
ascending-order constraint on `observations.uncertainty.interval`; the Stage-1 implementation accepts a
descending interval; `AC-P1-08` forbids a partial catalogue entry; and v1.1.2 authorized no deferral.
The certification further ruled — correctly — that an Acceptance Record is an engineering record and
cannot amend a frozen normative requirement.

This part records the single authoritative resolution of that conflict and nothing else. The rulings are
numbered `RG-01`…`RG-05`.

**Rule RG-0.** An `RG` ruling has the same standing as the `R`-series rule or the `RC`, `RB` or `RF`
ruling it completes. Every section affected by a ruling is reissued in this document so that only the
ruled text exists. If a reader finds surviving v1.1.2, v1.1.1 or v1.1.0 text that contradicts an `RG`
ruling, the ruling governs and the surviving sentence is a defect to be reported under R9-0, not a
second reading.

**Rule RG-0.1.** No ruling in this part creates an authority class, a write target, a human-only
decision, a primitive, a collection, a relation type, a confidence dimension, a lifecycle state, a
write operation, a transaction phase, a gate, a KPI, a package file, a schema file, a test file, a
phase, a build stage, or a schema field that v1.1.2 did not already require. Each ruling either
(a) names the enforcement layer of a requirement v1.1.2 stated without naming its layer, (b) selects one
of two readings already present in v1.1.2, or (c) supplies the check code and acceptance criterion that
carry an existing requirement to the layer that owns it. The architecture of v1.1.2 is identical after
this release.

**Rule RG-0.2.** This part deletes no scientific requirement. The ascending-interval invariant is
mandatory before this amendment and mandatory after it. What changes is that it acquires a named owner,
a check code, a blocking gate, an acceptance criterion and a test — none of which it had.

## 0Z.2 The exact conflict

Three frozen sentences cannot all be satisfied by any conforming Stage-1 implementation.

| # | Governing text | Sentence |
|---|---|---|
| 1 | v1.1.1 §9.2.4 `N-18`, row `interval` | "Exactly two items, ascending, when `kind ∈ {ci95, iqr}`; `null` otherwise" |
| 2 | v1.1.2 §9.5.1 cl. 3 item 3 (`RF-01`) | `keyword` is "the failing **assertion** keyword as written in the schema"; the only three values naming no schema keyword are `required` and `additionalProperties` for a fixed body-key check and `frozen` for the constructor predicate |
| 3 | v1.1.1 §9.2.0 cl. 1 / RB-01 | Dialect is JSON Schema Draft 2020-12, standard vocabulary only |

Sentence 1 requires a comparison between two locations of one instance. Sentence 3 supplies no
vocabulary that can express it (§0Z.4 proves this). Sentence 2 forecloses reporting it procedurally,
because a procedural ascending finding must carry a `keyword` string, and `ascending` is outside the
closed value space that sentence 2 fixes.

This is precisely the case R9-19 cl. 4 preserves for R9-0: **"a normative sentence that no conforming
implementation can satisfy remains a Constitutional Change Request."** The conflict is therefore
resolvable only by amendment, and the amendment must be authoritative rather than an engineering note.

**The candidate's own artifacts corroborate the conflict rather than excuse it.** `D-03` was closed by
deleting a `_cross_value_failures` function that emitted `ascending`, `creation` and `transitionState` —
"names outside the `RF-01` cl. 3 item 3 value space". The independent certification verified `D-03`
closed on the express finding that no `ascending` output was observed. Implementing the ascending
comparison inside `validate` under the present text would therefore reopen `D-03`, which this amendment
forbids.

## 0Z.3 Governing texts consulted

| Subject | Site | Bearing |
|---|---|---|
| `N-18` `interval` constraint | v1.1.1 §9.2.4 | The requirement in dispute |
| `AC-P1-08` | v1.1.1 Appendix D.1; carried forward unchanged by v1.1.2 Appendix D.1 | Names four dimensions: "properties, required sets, types and nullability" |
| Appendix D row 8 | v1.1.1; unchanged in v1.1.2 | Maps `AC-P1-08` to `record_schema` and `record.schema.json` `$defs` — a **schema** surface |
| `RB-03` | v1.1.1 §0X.5 | §9.2.4 is a catalogue of nested objects, "each with its properties, required set, types, nullability and constraints" |
| `RF-01` cl. 3 | v1.1.2 §9.5.1 | Closed `keyword` value space; closed `schema_pointer` value space |
| `R9-15` / reported-application rule | v1.1.2 §9.13.3 | The failure set is one item per **false assertion keyword application** |
| `RB-05` cl. 1 | v1.1.1 §0X.7 | `validate` is the single public validation entry point of `v2/lske/` |
| `MEM-01`…`MEM-10` | v1.1.0 §3.6 (canonical, `RC-03`) | Ten store-integrity checks, severity `error`, blocking `store_integrity` |
| `MEM` implementation site | v1.1.0 §9.4.2 | `ros.store._check_memory`; §9.4.2 "fixes only their implementation site, their severity, and their ordering" |
| Build order | v1.1.0 §9.8 | `ros.store._check_memory` is **Stage 4**; Stage 2 is `ros.model` 11 → 20 only |
| Test 9 | v1.1.0 §9.6 | `test_memory_checks.py` — each `MEM` code fires on one constructed violation |
| `R9-0` | v1.1.0 §9.0 | Underspecification routes to amendment, never to implementer choice |
| `R9-19` | v1.1.2 §9.14 | Phase-1 freeze; cl. 4 preserves R9-0 for unsatisfiable sentences |
| `R4-15` | v1.1.0 Part 4 | LSKE **records** uncertainty rather than modelling it |

**Two `MEM` correction notes, both material.**

1. The Acceptance Record assigned enforcement to "the store-level layer owning `MEM-01`…`MEM-06`". The
   canonical register is `MEM-01`…**`MEM-10`**, fixed by `RC-03` §3.6; `MEM-01`…`MEM-06` has been a
   non-current numbering since v1.1.0. This amendment uses the canonical register.
2. The Acceptance Record, the committed test comment and this operation's own framing all call the
   destination "**Stage 2**". Under the frozen build order of §9.8 that is **wrong**: Stage 2 is
   `ros.model` 11 → 20 and nothing else, while `ros.store._check_memory` is **Stage 4**. Naming the
   wrong stage would have created an obligation nobody was scheduled to discharge. The owner is the
   **store-integrity / `MEM` layer, delivered at Stage 4**, and every clause below says so.

## 0Z.4 Mechanism feasibility — the constraint is unrepresentable in Draft 2020-12

**Claim.** No finite JSON Schema in standard Draft 2020-12, over the vocabulary RB-01 permits, accepts
`[u, v]` for every `u ≤ v` and rejects `[u, v]` for every `u > v`, where items are `number`.

**Proof.** Fix any such schema `S` and consider its evaluation against a two-item numeric array
`[a, b]`.

1. **No keyword compares two instance locations.** Every assertion keyword in Draft 2020-12 —
   `type`, `enum`, `const`, `pattern`, `minimum`, `maximum`, `exclusiveMinimum`, `exclusiveMaximum`,
   `multipleOf`, `minLength`, `maxLength`, `minItems`, `maxItems`, `uniqueItems`, `minProperties`,
   `maxProperties`, `required`, `dependentRequired`, `additionalProperties`, `unevaluatedProperties`,
   `unevaluatedItems`, `propertyNames`, `contains`, `minContains`, `maxContains` — compares the instance
   *at the location the keyword is applied to* against a value **written literally in the schema**. None
   takes a second instance location as an operand. Draft 2020-12 has no `$data` reference (that is an Ajv
   extension), no relative instance pointer, and no expression language. `$ref`, `$dynamicRef`, `allOf`,
   `anyOf`, `oneOf`, `not`, `if`/`then`/`else`, `properties`, `prefixItems` and `items` are applicators:
   they relocate or combine subschema evaluation and introduce no new comparison of their own.
2. **Therefore every atom is one of three shapes.** Evaluating `S` against `[a, b]` decomposes into
   finitely many subschema applications, each at the root, at `/0`, or at `/1`. An application at `/0`
   yields a predicate `P(a)` depending on `a` alone; an application at `/1` yields `Q(b)` depending on
   `b` alone; an application at the root yields either a predicate of the array's type/length (identical
   for `[u,v]` and `[v,u]`) or one of the permutation-invariant keywords `uniqueItems`, `contains`,
   `minContains`, `maxContains`, whose value is a function of the **multiset** `{a, b}`.
3. **Swap invariance.** Let `L` be the finite set of numeric literals appearing anywhere in `S`
   (in `enum`, `const`, `minimum`, `maximum`, `exclusiveMinimum`, `exclusiveMaximum`, `multipleOf`), and
   let `Π` be the finite set of `pattern` regexes and remaining single-location predicates `S` applies at
   `/0` or `/1`. Define `x ≈ y` iff `x` and `y` agree on every predicate in `Π` and on membership of every
   comparison induced by `L`. `≈` has finitely many classes; the reals are infinite; so some class
   contains two distinct numbers `u < v`.
4. **Contradiction.** For that pair, `[u, v]` and `[v, u]` agree on every atom of step 2: the
   single-location atoms because `u ≈ v` makes `P(u) = P(v)` and `Q(u) = Q(v)`, and the root atoms
   because the multiset `{u, v}` and the array type and length are identical. Since the atoms agree and
   the applicators are functions of the atoms, `S` accepts both or rejects both. But `u < v` requires
   acceptance and `v > u` requires rejection. Contradiction. ∎

**Corollary — the three escape routes are all closed.** A custom keyword is forbidden (standard
vocabulary only, RB-01). Enumerating admissible pairs by `enum` is impossible over an infinite domain and
would in any case be a schema redesign. Restructuring `interval` as an object with `lower`/`upper` keys
does not help — no keyword compares two sibling properties either — and would amend `N-18`'s declared
type, which is a change to the frozen catalogue rather than a boundary clarification.

**Determination.** `interval[0] <= interval[1]` is **not expressible** in standard Draft 2020-12 under
the frozen vocabulary. The requirement is not merely unimplemented; it is unimplementable at the schema
layer. Under R9-19 cl. 4 it therefore routes to R9-0 amendment, which is this document.

## 0Z.5 `RG-01` — Ownership of a §9.2.4 *Constraint* cell

**The defect.** §9.2.4's tables carry five columns — *Field*, *Type*, *Present*, *Nullable*,
*Constraint*. `AC-P1-08` names four dimensions: "properties, required sets, types and nullability". The
*Constraint* column is not among them, and no sentence of v1.1.0, v1.1.1 or v1.1.2 states which layer
enforces a *Constraint* cell. Most such cells are ordinary Draft 2020-12 assertions and are plainly
Stage-1's; at least two are cross-location semantic invariants that the schema layer cannot express, and
the frozen text already routes those elsewhere without ever stating the rule. The independent
certification read `AC-P1-08` as reaching the *Constraint* column; the implementation read it as not
reaching it. Both readings are available on the present text, which is the defect.

**Ruling RG-01.** Enforcement of a §9.2.4 *Constraint* cell is assigned per cell by its expressive
class, and by nothing else:

1. **Stage-1-owned (schema layer).** A *Constraint* cell is enforced by `v2.lske.schema` — in the
   generated Draft 2020-12 schema, reported through `validate` — **iff** it is expressible as a standard
   Draft 2020-12 assertion over a **single instance location**, using only the vocabulary RB-01 permits.
   This is the ordinary case and covers every `enum`, `pattern`, `minItems`, `minimum`, non-empty-string
   and `if`/`then` presence rule in §9.2.4. No such cell is relaxed by this amendment.
2. **Store-integrity-owned (`MEM` layer, Stage 4).** A *Constraint* cell whose satisfaction requires
   comparing **two or more distinct locations** — within one record or across records — is enforced by
   `ros.store._check_memory` under a named `MEM` code, at severity `error`, blocking the
   `store_integrity` gate, before the record is admitted to the store.
3. **Exactly one owner per cell.** No cell is enforced at both layers, and no cell is enforced at
   neither. A cell in class 2 that has no `MEM` code is a defect under R9-0 and must be reported, not
   deferred.
4. **This rule is descriptive of the frozen architecture, not new policy.** §9.2.4 already routes two
   cells this way without stating the rule: `N-02`'s `prior_content_hash` cell — "`null` only on the
   first entry; thereafter the preceding entry's computed hash" — is annotated **`(MEM-02)`** in the
   catalogue itself, and `N-11`'s `transitions` cell — "`state` equals the last item's `to`" — is
   annotated **`(MEM-01)`**. Both are cross-location comparisons; both are owned by the `MEM` layer;
   neither was ever a Stage-1 obligation, and no reviewer has ever called `N-02` or `N-11` partial on
   that account. `RG-01` states the principle those two annotations already instance, and `RG-02` applies
   it to the one cell §9.2.4 left unannotated.
5. **Bounded audit obligation.** Stage 4 shall, before its exit, confirm that every class-2 *Constraint*
   cell in §9.2.4 carries a `MEM` code. This amendment names the cells it has identified — `N-02`
   (`MEM-02`), `N-11` (`MEM-01`), `N-18` (`MEM-11`, below) — and does not assert that enumeration is
   exhaustive. Any further class-2 cell found by that audit routes to R9-0 for a `MEM` code; it does not
   authorize a Stage-1 relaxation, and it does not reopen Stage 1.

**Why this preserves the architecture.** No schema changes. No Stage-1 surface gains or loses a
capability. Two cells that were already `MEM`-owned stay `MEM`-owned; one cell that had no owner acquires
the owner its own expressive class dictates.

**Sections reissued.** Appendix D.1 `AC-P1-08` (§0Z.8 below); §9.2.4 `N-18` `interval` row (§0Z.6).

## 0Z.6 `RG-02` — `N-18` reissued: structural representation and semantic invariant

**Ruling RG-02.** The `N-18` `interval` row of §9.2.4 is reissued as two statements with distinct owners.
The declared type, presence and nullability are **unchanged**.

**`N-18` `observations.uncertainty`** — fixed-key. Required: all four. The `interval` row now reads:

| Field | Type | Present | Nullable | Constraint |
|---|---|---|---|---|
| `interval` | array[number] \| null | yes | yes | **Structural (Stage 1, schema-enforced):** exactly two items, both `number`, when `kind ∈ {ci95, iqr}`; `null` otherwise. **Semantic (Stage 4, `MEM-11`-enforced):** the two items are in ascending order — `interval[0] <= interval[1]`. The ordering comparison is not expressible in Draft 2020-12 (§0Z.4) and is owned by `MEM-11` under `RG-01` cl. 2 |

1. **Structural half — Stage 1, unchanged in substance.** `validate` enforces: `interval` is present;
   it is `null` exactly when `kind ∉ {ci95, iqr}`; it is a two-item array of `number` exactly when
   `kind ∈ {ci95, iqr}`. This is what the candidate schema already does. `AC-P1-08` is satisfied by it.
2. **Semantic half — Stage 4, `MEM-11`.** The ascending relation is enforced by
   `ros.store._check_memory` before admission, per `RG-03`.
3. **`ascending` means non-strict: `interval[0] <= interval[1]`. Equal bounds are admissible.** This
   ruling selects between the two readings the single word "ascending" permits, and is required because
   the test contract is otherwise undecidable. It is grounded in scientific meaning, not convenience:
   a zero-width `ci95` or `iqr` is a **real empirical outcome** — every bootstrap resample can yield the
   same statistic, and `Q1 = Q3` whenever the middle half of a sample carries no spread. Rejecting
   `[1.0, 1.0]` would force an implementer either to fabricate width or to misreport `kind = none`, and
   R4-15 requires the LSKE to **record** uncertainty rather than to model it. No frozen sentence requires
   positive width; reading one in would add a requirement the text does not state, which R9-19 forbids.
   "Ascending" is therefore an **orientation** rule — the pair is stored `[lower, upper]` and the lower
   bound never exceeds the upper — and not a strict-separation rule.
4. **Nothing else in `N-18` changes.** `kind`, `n` and `method` are untouched, as are `N-19` and `N-20`.

**Sections reissued.** §9.2.4 `N-18`, the `interval` row only.

## 0Z.7 `RG-03` — `MEM-11`, the ascending-interval store-integrity check

**Ruling RG-03.** The canonical `MEM` register of §3.6 gains **one** code. `MEM-01`…`MEM-10` are
unchanged in text, in numbering and in effect.

| Code | Check |
|---|---|
| `MEM-11` | No `observations` record has an `uncertainty.interval` whose first item exceeds its second — for every record where `uncertainty.kind ∈ {ci95, iqr}`, `interval[0] <= interval[1]` (§9.2.4 `N-18` semantic half, `RG-02`). |

1. **Implementation site.** `ros.store._check_memory`, exactly as §9.4.2 fixes for `MEM-01`…`MEM-10`.
   No new module, no new callable, no new writer, no new gate.
2. **Severity and gate.** Severity `error`; blocks the `store_integrity` gate. A record violating
   `MEM-11` cannot be admitted to the store and can therefore bear no scientific weight.
3. **Ordering.** Findings are emitted in code order, so `MEM-11` follows `MEM-10`; within the code, by
   record identifier ascending, per §9.4.2.
4. **Build stage.** Stage 4, with the rest of `_check_memory` (§9.8). Stage 4 is **not** advanced,
   started or rescheduled by this amendment; one check code is added to a stage that already exists and
   already delivers ten.
5. **Count sentences reissued.** Every "ten checks" / "`MEM-01`…`MEM-10`" count sentence becomes
   **eleven** / "`MEM-01`…`MEM-11`" at: v1.1.0 §0R.4 (`RC-03` closing paragraph), §3.6, §9.4.2, §9.6
   test 9, and Part 8's detector table where it states the register's extent. No individual check's text
   changes, and `RC-03`'s ruling that each code has exactly one meaning and one definition site is
   preserved: `MEM-11` is defined in §3.6 and nowhere else.
6. **Test 9 widened.** §9.6 test 9 (`test_memory_checks.py`) asserts that each of `MEM-01`…**`MEM-11`**
   fires on one constructed violation.

**Why this preserves the architecture.** §9.4.2 already declares itself the site that fixes only
implementation site, severity and ordering for a register defined in §3.6. Adding a code to that register
is the mechanism v1.1.0 built for exactly this case; `RC-03` itself added `MEM-07`…`MEM-10` to the
register by the same move.

## 0Z.8 `RG-04` — `AC-P1-08` reissued

**The defect.** `AC-P1-08` reads: "All thirty-two catalogue entries are implemented with their stated
properties, required sets, types and nullability; none is partial." The four named dimensions map
one-to-one onto four of §9.2.4's five columns and omit *Constraint*, which supports the implementation's
reading. But "with their stated properties" is loose enough to be read as "everything the table states",
which supports the certification's reading. A Stage-1 completion criterion that admits two readings is
itself a defect under R9-19 cl. 2, and it is the proximate cause of this operation.

**Ruling RG-04.** `AC-P1-08` is reissued as one decidable sentence:

> `AC-P1-08` All thirty-two catalogue entries of §9.2.4 are implemented in the generated schemas with
> their stated **fields**, **required sets**, **declared types**, **nullability**, and every
> *Constraint* cell of Stage-1 expressive class under `RG-01` cl. 1; none is partial in any of those
> dimensions. A *Constraint* cell of store-integrity expressive class under `RG-01` cl. 2 is **not** a
> Stage-1 obligation and its absence from the schemas is not partiality; it is discharged by its named
> `MEM` code and asserted by that code's own acceptance criterion.

1. **This is a narrowing of wording, not of obligation.** Stage 1 owes every schema-expressible property
   of all thirty-two entries, which is what it owed before. What is removed is a demand the schema layer
   cannot satisfy at all.
2. **`AC-P1-08` is now decidable.** Under the prior wording, whether the candidate satisfied it depended
   on which reading of "stated properties" a reviewer chose. It no longer does.
3. **Appendix D row 8 is unchanged** and continues to name `record_schema` / `record.schema.json` `$defs`
   — a schema surface — which is consistent with, and corroborative of, this reading.
4. **Stage-1 criteria count is unchanged at twenty-seven.** No criterion is added or removed here.

**Sections reissued.** Appendix D.1 `AC-P1-08`.

## 0Z.9 `RG-05` — Informal deferral is prohibited

**The defect.** An Acceptance Record disclosed `SPEC-CONFLICT-01` candidly and then assigned enforcement
to a future layer on its own authority. That assignment happened to point at approximately the right
layer — though it named the wrong stage and a non-current `MEM` range — but the **mechanism** was
illegitimate, and the independent certification was right to refuse it. Had the certification not caught
it, a mandatory scientific invariant would have left Stage 1 with no owner, no code, no gate, no
criterion and no test, recorded only in a comment.

**Ruling RG-05 (Rule R9-20, appended to §9.14).**

> **Rule R9-20 (No informal deferral).** No Acceptance Record, implementation note, code comment,
> roadmap, checklist, traceability matrix, test, review, audit or other engineering document may defer,
> narrow, reassign, waive or suspend a frozen normative requirement. Only a specification amendment
> issued under R9-0 may do so, and only by naming the requirement, the receiving layer, the enforcing
> check or criterion, and the stage at which it is discharged.
>
> 1. An engineering document that discovers an unsatisfiable or unowned normative requirement **shall**
>    raise it — as this operation's Acceptance Record correctly did — and **shall not** dispose of it.
>    Raising is mandatory and is not a defect; disposing is the defect.
> 2. A requirement disposed of without an amendment is **not** discharged, however candidly the
>    disposal was disclosed. Disclosure is a virtue and is not authority.
> 3. A test that encodes the absence of a required check **shall** cite the amendment that moved the
>    requirement. A test asserting an unenforced requirement is absent, with no amendment behind it,
>    is itself a conformance defect.
> 4. This rule binds reviewers as well as implementers: a certification may not accept a deferral that
>    no amendment authorizes, and may not reject an implementation for failing an obligation an
>    amendment has assigned elsewhere.

**Sections reissued.** §9.14 (rule appended; R9-19 unchanged in text and effect).

## 0Z.10 Why this is boundary clarification and not architecture change

| Test | Result |
|---|---|
| New module, file, package or callable? | None. `MEM-11` lands in `ros.store._check_memory`, which §9.4.2 already specifies and §9.8 already schedules. |
| New collection, primitive, authority class, write target, gate, KPI, transaction phase or build stage? | None. |
| New schema field, or any change to a declared type, presence or nullability? | None. `N-18`'s type, presence and nullability are reissued verbatim. |
| Any scientific meaning changed? | None. Ascending is still mandatory; `RG-02` cl. 3 fixes the one reading that preserves real zero-width intervals under R4-15. |
| Any capability reachable after that was not required before? | None. Every clause names the layer of an existing requirement or supplies the code that carries it. |
| Anything relaxed? | One thing, deliberately: Stage 1 is no longer required to do what §0Z.4 proves it cannot do. The requirement itself is not relaxed — it is enforced, at a blocking gate, before admission. |
| Precedent in frozen text? | `N-02`/`MEM-02` and `N-11`/`MEM-01` are the same move, already in §9.2.4 and already annotated there. |

## 0Z.11 Sections superseded by this amendment

| Section | Version superseded | Change |
|---|---|---|
| §9.2.4, `N-18` `interval` row | v1.1.1 | Split into structural (Stage 1) and semantic (`MEM-11`) halves; type/presence/nullability unchanged (`RG-02`) |
| §3.6 | v1.1.0 | `MEM-11` appended; `MEM-01`…`MEM-10` unchanged; count ten → eleven (`RG-03`) |
| §9.4.2 | v1.1.0 | Register extent ten → eleven; site, severity, ordering rules unchanged (`RG-03`) |
| §9.6 test 9 | v1.1.0 | Asserts `MEM-01`…`MEM-11` (`RG-03`) |
| §0R.4 (`RC-03`) count sentence | v1.1.0 | "Ten checks total" → eleven; every merge and renumbering decision unchanged (`RG-03`) |
| Part 8 detector table, register extent sentence | v1.1.0 | `MEM-01`…`MEM-11`; individual detector mappings unchanged (`RG-03`) |
| Appendix D.1 `AC-P1-08` | v1.1.1, carried by v1.1.2 | Reissued as one decidable sentence (`RG-04`) |
| §9.14 | v1.1.2 | R9-20 appended; R9-19 unchanged (`RG-05`) |
| §9.8 Stage 4 row | v1.1.0 | Exit condition reads `MEM-01`…`MEM-11` (`RG-03` cl. 4) |

Nothing else in v1.1.2, v1.1.1 or v1.1.0 is touched. `RF-01`…`RF-06`, `RB-01`…`RB-06`, `RC-0`…`RC-12`,
`R9-15`, `R9-15.1`, `R9-19` and Appendix D rows 1–27 stand as issued. `D-01`…`D-06` remain closed and are
not reopened by any clause of this document.

## 0Z.12 Acceptance tests for both stages

### Stage 1 — schema layer, executable now

`tests/lske/test_envelope.py`, the `N-18` vectors. For `kind` in both `ci95` and `iqr`:

| Payload `interval` | Stage-1 expectation | Reason |
|---|---|---|
| `[1.0, 2.0]` | `validate` reports no `/uncertainty/interval` failure | Structurally valid |
| `[1.0, 1.0]` | `validate` reports no `/uncertainty/interval` failure | Structurally valid; `RG-02` cl. 3 |
| `[2.0, 1.0]` | `validate` reports **no** `/uncertainty/interval` failure | **Stage-1 boundary, asserted positively.** Ordering is `MEM-11`'s (`RG-02` cl. 2); a Stage-1 failure here would mean `validate` invented a keyword outside `RF-01` cl. 3 and reopened `D-03` |
| `[1.0]` / `[1.0, 2.0, 3.0]` | `minItems` / `items` failure at `/uncertainty/interval` | Structural |
| `["1.0", 2.0]` | `type` failure at `/uncertainty/interval/0` | Structural |
| `null` with `kind = ci95` | `type` failure | Conditional presence |
| `[1.0, 2.0]` with `kind = none` | `type` failure at `/uncertainty/interval` | Must be `null` |

The existing `[2.0, 1.0]` assertion is **retained and its meaning inverted**: it stops being a recorded
limitation and becomes the positive assertion of a ruled boundary. Under `RG-05` cl. 3 its comment must
cite `RG-02` / `MEM-11` / v1.1.3 in place of `SPEC-CONFLICT-01` and the non-current `MEM-01…MEM-06`.

### Stage 4 — store-integrity layer, executable when Stage 4 is built

`tests/lske/test_memory_checks.py` (§9.6 test 9), carried by a new acceptance criterion:

> `AC-P1-28` `MEM-11` fires at severity `error` on one constructed `observations` record whose
> `uncertainty.kind ∈ {ci95, iqr}` and whose `uncertainty.interval` is `[2.0, 1.0]`, blocks the
> `store_integrity` gate, and does **not** fire on `[1.0, 2.0]` or on `[1.0, 1.0]`, nor on any record
> whose `uncertainty.interval` is `null`.

`AC-P1-28` is a **Stage-4** criterion. It does not join the twenty-seven Stage-1 criteria of Appendix D.1
and does not affect Stage-1 completion. Appendix D gains one row mapping `MEM-11` → `ros.store` →
`_check_memory` → `observations.schema.json` `N-18` → test 9 → `AC-P1-28`. This is the executable
obligation that carries the invariant forward; without it the deferral would be exactly the loophole
`RG-05` prohibits.

## 0Z.13 Self-attack

| Attack | Result |
|---|---|
| Does the ruling weaken `N-18`? | **No.** Before: mandatory, zero owners, zero checks, zero tests, unenforceable at the only layer named. After: mandatory, one owner, one blocking check, one acceptance criterion, one test. Enforcement strictly increases. |
| Does it create an untested semantic invariant? | **No.** `AC-P1-28` and §9.6 test 9 are executable statements. The invariant is untested only for as long as Stage 4 is unbuilt, exactly as `MEM-01`…`MEM-10` are — which is the frozen build order, not a gap this amendment opens. |
| Does it contradict `AC-P1-08`? | **No.** `RG-04` reissues `AC-P1-08` under R9-0. Its scope is now stated rather than inferred, and it is decidable. |
| Does it violate `RF-01`? | **No.** `RF-01` is untouched. The ruling is what makes it possible to *comply* with `RF-01` cl. 3: no keyword outside the closed value space is emitted, and `D-03` stays closed. |
| Does it expand Stage 1? | **No.** Zero schema changes, zero new Stage-1 surfaces. Stage 1 contracts by exactly the unsatisfiable clause. |
| Does it silently start Stage 2? | **No** — and the question mislabels the destination. Stage 2 is `ros.model` 11 → 20; the owner is Stage **4**. No `ros/` code is written by this amendment; `ros.model` still holds eleven collections. |
| Does it change scientific meaning? | **No.** `interval` still means an ordered `[lower, upper]` pair. `RG-02` cl. 3 chooses the reading that keeps genuine zero-width intervals recordable, which R4-15 requires; the strict reading would have *changed* meaning by making a real measurement unrecordable. |
| Two owners for one invariant? | **No.** Structural shape → Stage 1. Ordering → `MEM-11`. Disjoint predicates, one owner each. `RG-01` cl. 3 forbids double ownership explicitly. |
| Zero owners? | **No.** `MEM-11` is defined in §3.6, sited in §9.4.2, gated by `store_integrity`, scheduled at Stage 4, asserted by `AC-P1-28`, tested by test 9. |
| Could a descending interval reach a scientific claim? | **No.** `validate` may build a record in memory, but admission requires `Store.check()`, and `MEM-11` blocks `store_integrity` at severity `error`. Nothing descending is admitted, so nothing descending can bear scientific weight — which is the invariant's actual purpose. |
| Is the amendment larger than necessary? | **No smaller one exists.** §0Z.4 forecloses a schema fix; `RF-01` cl. 3 forecloses a procedural fix without amending `RF-01`, which would be strictly larger and would reopen `D-03`. Five rulings, one new check code, one reissued criterion, one appended rule, zero new files. |
| Is `RG-05` self-serving — does this document defer anything? | **No.** It defers nothing. It *assigns*, by amendment, naming layer, code, gate, stage, criterion and test. That is the mechanism `RG-05` requires. |

**Exactly one enforcement owner:** `MEM-11`, `ros.store._check_memory`, Stage 4, blocking
`store_integrity`.
