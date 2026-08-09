# P1-v2 Living Scientific Knowledge Engine — Engineering Specification

- **Artifact:** `P1_V2_LSKE_SPECIFICATION_v1.0.md`
- **Version:** 1.0.0
- **Status:** Proposed / Unregistered
- **Date:** 2026-07-30
- **Subsystem:** Living Scientific Knowledge Engine (LSKE)
- **Inherits without amendment:** `P1_V2_CONSTITUTION_LOCK_v1.0.md` v1.0.0; `ros.authority`;
  `ros.admissibility`; `P1_OBSERVATORY_SCIENTIFIC_SPECIFICATION_v1.0.md`; the M1/P1-v2 runtime
- **Closes:** `OPERATION_ZERO_UNKNOWN_FINAL_REPORT.md` blocker 5, findings 9 and 10
- **Authority source:** none

---

# PART 0 — Scope, Reconciliation, and Standing

## 0.1 Mandate

The audited repository stops at `Experiment → Artifacts`. Two VERIFIED findings state it exactly:

> 9. The M1 engine ends at artifacts, manifest, status, logs, and inventory.
> 10. No runtime continuation creates Evidence, Decision, SKB state, or Living Scientific Model
>     updates.

Blocker 5 names the missing subsystem and its closure evidence:

> No runtime-to-scientific-state transaction — `REPOSITORY_LIMITATION` — End-to-end run → Evidence
> → Decision → SKB → LSM test with human Decision boundary preserved.

The LSKE is that subsystem. It is the mechanism by which an executed run becomes recorded
scientific knowledge, and by which recorded knowledge is queried, explained, contradicted,
superseded, and rendered. It is the connective tissue between five frozen subsystems. It is not a
sixth opinion about any of them.

## 0.2 What this specification may not touch

Five subsystems are frozen inputs. The LSKE reads them, references them by identifier, and obeys
them. It redefines none of them.

| Frozen subsystem | Authority | LSKE relationship |
|---|---|---|
| Constitution | `P1_V2_CONSTITUTION_LOCK_v1.0.md`, Articles L-1…L-12 | Inherited verbatim in Part 8 |
| Authority | `ros/authority.py` — `AuthorityClass`, `AGENT_FORBIDDEN`, `HUMAN_ONLY` | Every LSKE write passes `ros.authority.require` |
| Admissibility | `ros/admissibility.py` — `assess`, `Verdict`, `Tier` | LSKE consumes verdicts; it never computes its own |
| Observatory | `P1_OBSERVATORY_SCIENTIFIC_SPECIFICATION_v1.0.md` | LSKE is a data source for plates; it adds no plate semantics |
| Runtime | M1/P1-v2 engine, `core/`, Tier R primitives | LSKE is strictly downstream and read-only |

## 0.3 The two-layer reconciliation (load-bearing)

The mission brief enumerates objects — `ResearchQuestion`, `Hypothesis`, `Theory`, `Observation`,
`Metric`, `Model`, `Publication`, `KnowledgeSnapshot` — that do not appear in the Constitution's
frozen primitive set, where `Claim` absorbs hypothesis, law, theory, Unknown and human annotation,
and `Measurement` absorbs every derived statistic. Naïvely reading Part 1 as a request for new
primitives would violate Article L-1 and the explicit prohibition on redesigning the Constitution.

There is no conflict, because the repository already operates two distinct layers, and
`ros/model.py` is the proof:

**Layer 1 — Constitution primitives.** 19 frozen primitives. Tier R (14): `Run`, `Environment`,
`Tick`, `Event`, `Snapshot`, `Neuron`, `Kind`, `Edge`, `Graph`, `DelayLine`, `EpisodicMemory`,
`Ledger`, `Policy`, `Intervention`. Tier E (5): `Protocol`, `Measurement`, `Claim`, `Evidence`,
`Decision`. Closed under Article L-1. Extended only through Article L-9 amendment by evidence.

**Layer 2 — SKB record collections.** The eleven collections in `ros/model.py::COLLECTIONS`:
`hypotheses` (HYP), `experiments` (EXP), `mechanisms` (MEC), `assumptions` (ASM), `unknowns` (UNK),
`scientific_debt` (SDEBT), `negative_results` (NEG), `observations` (OBS), `evidence` (EVD),
`decisions` (DEC), `theories` (THY). This is the *record* layer. Adding a collection here is not a
constitutional amendment; it is a schema extension of the writable store.

**The LSKE specifies Layer 2 only.** Every object in Part 1 is a record collection. Each record
carries a `primitive` field naming the frozen primitive it realizes, and references primitives by
identifier. A `hypotheses` record *is* a `Claim` in Layer 1 terms, at status Level 0–3, with
hypothesis-shaped fields. A `theories` record *is* a `Claim` at Level 4–5 with integrative scope.
An `unknowns` record *is* a `Claim` with no evidence relation. This is not a workaround; it is what
the Lock says these things are, made addressable.

**Rule R0-1.** Every LSKE record type declares exactly one `primitive` value from the 19. A
proposed record type that realizes no primitive is rejected at schema-validation time, not
negotiated.

**Rule R0-2.** Anything that genuinely requires primitive status — new state, new transition, new
runtime input — is out of LSKE scope and routes to `constitution.amendment` via
`ros.authority.escalation_for`, which returns `primitive_admission`.

## 0.4 The transaction already has a name

`ros/propagation.py` defines nine obligations and where each is discharged. ROS *audits* them after
the fact. The LSKE *executes* them. The LSKE transaction is not invented here; it is the
mechanization of `Obligation`:

| # | `Obligation` | Discharge site (existing) |
|---|---|---|
| 1 | `EXECUTION_VALIDITY` | experiment record: `validity` / `invalidity_reason` |
| 2 | `OBSERVATIONS` | `observations` collection, referenced by the experiment |
| 3 | `EVIDENCE_RELATIONS` | `evidence` collection, with direction and target |
| 4 | `INTERPRETATION` | `evidence.rationale` or an interpretation record |
| 5 | `DECISION` | `decisions` collection — **human write: `skb.decision`** |
| 6 | `DEPENDENT_STATUS` | status of every hypothesis and mechanism the experiment names |
| 7 | `ASSUMPTIONS_UNKNOWNS_DEBT` | `assumptions` / `unknowns` / `scientific_debt` |
| 8 | `ROADMAP` | `science/09_RESEARCH_ROADMAP_24_MONTHS.md` priority |
| 9 | `LIVING_MODEL` | `science/11_LIVING_SCIENTIFIC_MODEL.md` synthesis |

Obligation 5 is the human boundary. It is confirmed independently three times: the discharge site
string, `ros.authority.EVIDENCE_TARGETS` containing `skb.decision`, and the audit's remaining
scientific decision 5 — "All experiment outcome Decisions; engineering must not automate them."

## 0.5 Registration honesty (Article L-11)

This artifact is **Proposed / Unregistered**. `GOVERNANCE_REGISTRY.yaml` is `status: Draft`,
`active_domain_standards` is empty, `constitutional_steward` is empty, and both attestation slots
are `null`. The Constitution Lock is itself Unregistered.

Therefore: **this specification has no normative authority.** Implementation against it may proceed
only as engineering-only work producing no admissible scientific evidence, consistent with the
audit's GO WITH LIMITATIONS ruling. Building the LSKE does not make P1 confirmatory-ready; it makes
P1 *capable of recording* evidence once governance activates.

**Rule R0-3.** The LSKE must state its own registration status in every artifact it generates. A
generated Living Scientific Model rendered while governance is Draft carries the banner
`GOVERNANCE: DRAFT — NO ADMISSIBLE EVIDENCE` in its header. Removing that banner is a
`governance.registry` write, which no agent may perform.

## 0.6 Vocabulary constraint (Article L-4)

The words *energy, attention, thought, understanding, belief, curiosity, dream, emotion, intention,
consciousness* may not name state, events, fields or results. This specification's prose title
speaks of a "scientific brain" as a figure of speech; **no schema field, enum value, event kind,
API name, table name, or generated result label in Parts 1–9 uses a banned term.** The subsystem is
named the Living Scientific Knowledge Engine precisely so that no identifier needs one.

The word *confidence* is retained: it is already the Lock's own term for the ten dimensions, and it
denotes a recorded, evidence-derived assessment, not an internal state of the machine.

## 0.7 Derivation constraint (Article L-7)

> Anything computable from the primitives is computed, not stored. A stored copy of derivable
> structure is hidden state by definition.

This is the single most consequential constraint on the LSKE's design, and it decides three
questions before they are asked:

1. `ScientificState` is **not a stored object**. It is a pure function of the store at a content
   hash. Part 1 specifies it as a projection type, not a collection.
2. `KnowledgeSnapshot` stores **no knowledge**. It stores a store content hash, a commit, a
   timestamp and an ontology version — the coordinates needed to recompute. Part 3 specifies it as
   an addressing record.
3. Confidence values are **not stored on claims**. They are computed from the evidence relations
   that bear on the claim. Part 4 specifies the propagation function; it does not specify a
   `confidence` column that anyone could edit directly.

**Rule R0-4.** A field is admissible in an LSKE schema only if it records an input (something a
human or a run asserted) or an address (an identifier, hash, version). Derived quantities appear in
projections and query results, never in the store.

---

# PART 1 — Scientific Knowledge Ontology

## 1.1 Universal record contract

Every LSKE record, in every collection, carries the same eight-block envelope. A record missing any
required block is invalid; there is no partial admission.

### Block A — Identity

| Field | Type | Required | Rule |
|---|---|---|---|
| `id` | string | yes | Matches `ros.model.ID_PATTERN`: `^[A-Z]{3,5}-\d{4}-\d{4}$`. Immutable for the record's entire existence. |
| `type` | string | yes | The collection's `object_type` from `ros.model.Collection`. |
| `primitive` | string | yes | One of the 19 frozen primitives. See §1.3 mapping table. |
| `title` | string | yes | Human-readable. Not an identifier. Must not contain an Article L-4 term. |

Identifier allocation: `PREFIX-YYYY-NNNN` where `YYYY` is the allocation year and `NNNN` is the
next unused four-digit sequence within that prefix and year. Sequences are never reused, including
after deletion. An identifier is allocated at record creation and survives supersession, tombstoning
and deletion as a permanent address.

### Block B — Version

| Field | Type | Required | Rule |
|---|---|---|---|
| `record_version` | integer | yes | Starts at 1. Increments on every accepted mutation. |
| `ontology_version` | string | yes | Semver of the LSKE ontology under which this record was written. Records retain their original semantics (Constraint C-d). |
| `content_hash` | string | yes | SHA-256 over the canonical serialization of blocks A–G, excluding block H. |

### Block C — History

| Field | Type | Required | Rule |
|---|---|---|---|
| `created` | object | yes | `{at: ISO-8601, by: actor_name, authority: AuthorityClass, target: WriteTarget}` |
| `revisions` | array | yes | Append-only. Each entry: `{record_version, at, by, authority, target, change_kind, rationale, prior_content_hash}`. Never rewritten, never compacted. |
| `supersedes` | string\|null | yes | Identifier of the record this one replaces, or `null`. |
| `superseded_by` | string\|null | yes | Set exactly once, by the supersession transaction. Never unset. |

`change_kind` is drawn from: `create`, `amend`, `annotate`, `status_transition`, `supersede`,
`tombstone`, `restore`, `delete`. No other value exists.

### Block D — Provenance

| Field | Type | Required | Rule |
|---|---|---|---|
| `provenance.kind` | enum | yes | `human_assertion` \| `run_derived` \| `document_derived` \| `external_literature` \| `projection` |
| `provenance.run_ids` | array[string] | conditional | Required and non-empty when `kind = run_derived`. Each must resolve to a `Run` in the runtime event log. |
| `provenance.protocol_id` | string\|null | conditional | Required when `kind = run_derived` and the record bears on a claim. Must have a verified freeze (`ros.protocol.verify` returns `True`). |
| `provenance.source_paths` | array[string] | conditional | Required when `kind = document_derived`. Repo-relative paths plus content hashes. |
| `provenance.citation` | object\|null | conditional | Required when `kind = external_literature`. |
| `provenance.derivation` | string\|null | conditional | Required when `kind = projection`. Names the projection function. |

**Rule R1-1.** `provenance.kind = projection` records may only exist in the addressing collections
(`snapshots`). No decision-bearing record may be projection-derived; that would be a stored copy of
derivable structure (R0-4).

### Block E — Authority

| Field | Type | Required | Rule |
|---|---|---|---|
| `authority.write_target` | string | yes | The `WriteTarget` under which this record was written. Must be in `EVIDENCE_TARGETS ∪ ENGINEERING_TARGETS`. |
| `authority.committed_by` | string | yes | Actor name. |
| `authority.is_human` | boolean | yes | True for every record whose `write_target ∈ EVIDENCE_TARGETS`. |
| `authority.escalated_from` | string\|null | no | Agent that drafted this record, when a human committed an agent's draft. |

**Rule R1-2.** A record whose `write_target ∈ EVIDENCE_TARGETS` and whose `is_human = false` is
invalid. This is checked at write time by `ros.authority.require` and again at store-integrity
time, because two independent checks are the difference between a boundary and an intention.

### Block F — Confidence

Confidence is **not a scalar and not stored as a value**. Block F records the *inputs* to
confidence, not confidence itself.

| Field | Type | Required | Rule |
|---|---|---|---|
| `confidence.level` | integer\|null | conditional | Claim-realizing records only. 0–5 per Lock E3. Set only by a `Decision`. |
| `confidence.scope` | object\|null | conditional | Claim-realizing records only. `{population, regime, environment_ids, limits}`. Human-only write (`skb.claim_scope`). |
| `confidence.dimensions` | object | conditional | Claim-realizing records only. Ten keys, each `assessed` \| `unassessed` \| `failed`, each with an `evidence_ids` array. Never a number. |

The ten dimensions, fixed, in Lock order: `existence`, `measurement_validity`, `effect_existence`,
`magnitude`, `mechanism`, `robustness`, `generalisation`, `necessity_over_simpler`,
`resource_efficiency`, `observability_completeness`.

**Rule R1-3.** `confidence.level` may only be written by a transaction whose `write_target` is
`skb.claim_status`, which is in `EVIDENCE_TARGETS`, and therefore human-only. No computation
advances a level. The LSKE computes *eligibility* for a level and presents it; a human commits it.

### Block G — Lifecycle

| Field | Type | Required | Rule |
|---|---|---|---|
| `lifecycle.state` | enum | yes | `CANDIDATE` \| `ACTIVE` \| `DORMANT` \| `TOMBSTONED` \| `DELETED` (Article L-2, frozen) |
| `lifecycle.status` | string | yes | Collection-specific vocabulary. See §1.4. |
| `lifecycle.transitions` | array | yes | Append-only. Each entry `{from, to, at, by, event_id, cause}`. |

The frozen transition set, unmodified: `CANDIDATE → ACTIVE`, `ACTIVE ⇄ DORMANT`,
`ACTIVE → TOMBSTONED`, `DORMANT → TOMBSTONED`, `TOMBSTONED → DELETED`, `TOMBSTONED → ACTIVE`,
`CANDIDATE → DELETED`.

**Rule R1-4 (Article L-2 verbatim).** *A state reached without an event does not exist.* Every
entry in `lifecycle.transitions` carries an `event_id` resolving to an emitted `lifecycle` event in
`.ros/events.jsonl`. A transition without a resolvable event is a store-integrity error of severity
`error`, and it blocks the `store_integrity` gate.

### Block H — Immutability

| Field | Type | Required | Rule |
|---|---|---|---|
| `immutability.append_only` | boolean | yes | Copied from `ros.model.Collection.append_only`. Not independently settable. |
| `immutability.frozen_at` | string\|null | yes | ISO-8601 when the record became immutable, or `null`. |
| `immutability.seal` | string\|null | yes | SHA-256 of `content_hash` plus `frozen_at`, present iff `frozen_at` is set. |

**Rule R1-5.** An `append_only` collection's records are never edited in place once
`frozen_at` is set. Correction is by linked supersession: a new record with a new identifier,
`supersedes` pointing back, and the original's `superseded_by` set — the only in-place write ever
permitted on a sealed record, and the only one, because a supersession that could not be recorded
on the original would make the original silently wrong.

## 1.2 Collections

Twenty collections. Eleven exist in `ros/model.py` today and are specified unchanged in prefix and
`append_only` flag. Nine are new to the record layer, each realizing an already-frozen primitive.

| # | Key | Prefix | `object_type` | `primitive` | `append_only` | Status |
|---|---|---|---|---|---|---|
| 1 | `research_questions` | `RQ` | `research_question` | `Claim` | no | **new** |
| 2 | `hypotheses` | `HYP` | `hypothesis` | `Claim` | yes | existing |
| 3 | `protocols` | `PROT` | `protocol` | `Protocol` | yes | **new** |
| 4 | `experiments` | `EXP` | `experiment` | `Run` | yes | existing |
| 5 | `runs` | `RUN` | `run` | `Run` | yes | **new** |
| 6 | `observations` | `OBS` | `observation` | `Measurement` | yes | existing |
| 7 | `metrics` | `MET` | `metric` | `Measurement` | no | **new** |
| 8 | `datasets` | `DSET` | `dataset` | `Environment` | no | **new** |
| 9 | `artifacts` | `ART` | `artifact` | `Snapshot` | yes | **new** |
| 10 | `evidence` | `EVD` | `evidence` | `Evidence` | yes | existing |
| 11 | `decisions` | `DEC` | `decision` | `Decision` | yes | existing |
| 12 | `mechanisms` | `MEC` | `mechanism` | `Claim` | no | existing |
| 13 | `theories` | `THY` | `theory` | `Claim` | no | existing |
| 14 | `assumptions` | `ASM` | `assumption` | `Claim` | no | existing |
| 15 | `unknowns` | `UNK` | `unknown` | `Claim` | no | existing |
| 16 | `scientific_debt` | `SDEBT` | `scientific_debt` | `Claim` | no | existing |
| 17 | `negative_results` | `NEG` | `negative_result` | `Evidence` | yes | existing |
| 18 | `programs` | `PROG` | `research_program` | `Claim` | no | **new** |
| 19 | `sessions` | `SESS` | `research_session` | `Intervention` | yes | **new** |
| 20 | `snapshots` | `SNAP` | `knowledge_snapshot` | `Snapshot` | yes | **new** |

Deliberately **not** collections, and why:

- **`Model`** — a P1 model is runtime state (`Graph` + `Policy` + `EpisodicMemory` + `Ledger`).
  Recording it in the SKB would be a stored copy of runtime structure (R0-4, Article L-7). Models
  are referenced through `artifacts` (`Snapshot`) and `runs`.
- **`Publication`** — a publication is a document, not a scientific object. It is
  `provenance.kind = document_derived` on the records it cites, plus a path. A publication that
  disagreed with the store would create two truths.
- **`ScientificState`** — a projection (§1.5), never stored.
- **`ResearchDomain`** — the jurisdiction concept already lives in `GOVERNANCE_REGISTRY.yaml`
  `active_domain_standards`. Duplicating it in the SKB would let the two drift, and governance wins
  any such contest by construction.

**Rule R1-6.** `ros/model.py`'s module docstring says "thirteen top-level SKB collections" while
`COLLECTIONS` defines eleven. Implementation must correct the docstring to the actual count in the
same change that extends the tuple to twenty. A schema whose own comment miscounts it is exactly
the class of defect this store exists to prevent.

## 1.3 Primitive realization mapping

Six of the nineteen primitives are realized by record collections. Thirteen are runtime-only and
are referenced by identifier, never mirrored.

| Primitive | Tier | Realizing collections | LSKE access |
|---|---|---|---|
| `Protocol` | E | `protocols` | record |
| `Measurement` | E | `observations`, `metrics` | record |
| `Claim` | E | `research_questions`, `hypotheses`, `mechanisms`, `theories`, `assumptions`, `unknowns`, `scientific_debt`, `programs` | record |
| `Evidence` | E | `evidence`, `negative_results` | record |
| `Decision` | E | `decisions` | record |
| `Run` | R | `experiments`, `runs` | record (index over runtime `Run`) |
| `Snapshot` | R | `artifacts`, `snapshots` | record (address only) |
| `Environment` | R | `datasets` | record (address only) |
| `Intervention` | R | `sessions` | record |
| `Tick`, `Event`, `Neuron`, `Kind`, `Edge`, `Graph`, `DelayLine`, `EpisodicMemory`, `Ledger`, `Policy` | R | none | reference by id, read-only |

**Rule R1-7 (Article L-8).** Tier E records may never be inputs to runtime computation. The LSKE
enforces this structurally: the store is a separate file (`science/SKB_RECORDS_v1.0.yaml`, kernel
invariant K1), the runtime imports nothing from `ros.store`, and a CI check asserts that no module
under the runtime tree imports `ros.store`, `ros.model`, or any LSKE module. Enforcement by
import-graph assertion rather than by convention, because a convention is not a boundary.

## 1.4 Collection-specific schemas

Only fields beyond the universal envelope are listed. Every collection also carries blocks A–H.

### 1.4.1 `research_questions` (RQ) — `Claim`

| Field | Type | Required | Rule |
|---|---|---|---|
| `question` | string | yes | Interrogative. States what would count as an answer. |
| `decision_value` | enum | yes | `changes_roadmap` \| `changes_design` \| `changes_measurement` \| `none`. `none` is a valid and useful answer. |
| `program_id` | string | yes | Resolves to a `programs` record. |
| `hypothesis_ids` | array[string] | yes | May be empty; an empty array is an open question with no candidate answer, which is a real state. |
| `resolved_by` | string\|null | yes | A `decisions` identifier, or `null`. |

Status vocabulary: `Open`, `Partially Answered`, `Answered`, `Retired`, `Superseded`.

### 1.4.2 `hypotheses` (HYP) — `Claim`

Existing collection. `HYPOTHESIS_STATUSES` from `ros.model` is retained unchanged: `Proposed`,
`Exploratory`, `Under Validation`, `Validated`, `Rejected`, `Superseded`, `Archived`.

| Field | Type | Required | Rule |
|---|---|---|---|
| `statement` | string | yes | Declarative and falsifiable. |
| `falsifier` | string | yes | The observation that would refute it. Non-empty. A hypothesis without a falsifier is a `research_questions` record, not a hypothesis. |
| `question_id` | string | yes | Resolves to `research_questions`. |
| `mechanism_ids` | array[string] | yes | May be empty. |
| `discriminates_from` | array[string] | yes | Other `HYP` identifiers this hypothesis is designed to be distinguishable from. |
| `scope` | object | yes | Mirrors `confidence.scope`. Human-only write. |

**Rule R1-8.** `Validated` requires `confidence.level ≥ 4`, which per Lock E3 requires E24
cross-instance replication. The status vocabulary and the confidence level are checked for mutual
consistency at store-integrity time; either alone could be advanced by a slip, both together
require a deliberate act.

### 1.4.3 `protocols` (PROT) — `Protocol`

| Field | Type | Required | Rule |
|---|---|---|---|
| `path` | string | yes | Repo-relative, matching `ros.gates.PROTOCOL_GLOB` (`configs/protocols/*.yaml`). |
| `digest` | string | yes | From `ros.protocol.digest`. |
| `freeze` | object | yes | The `ros.protocol.Freeze` payload: digest, commit, frozen-at. |
| `hypothesis_ids` | array[string] | yes | Non-empty. A protocol tests something or does not exist. |
| `intent` | enum | yes | `exploratory` \| `confirmatory` |
| `determinism_tier` | enum | yes | `D0` \| `D1` \| `D2` |
| `stopping_rule` | string | yes | Preregistered. Non-empty. |
| `sesoi` | object | yes | Smallest effect size of interest, with units. |
| `exclusion_rules` | array[string] | yes | Preregistered. |
| `declared_null` | string | yes | Lock E2. Non-empty. |
| `frozen_before_first_run` | boolean | yes | Computed once at freeze and sealed. |

**Rule R1-9.** `intent = confirmatory` with `determinism_tier = D2` is refused at write time. Lock:
D2 runs may never be offered as confirmatory evidence. Mechanical refusal, not a warning.

**Rule R1-10.** A `protocols` record is written under `protocol.draft` (engineering) until frozen;
freezing is `protocol.freeze`, which is in `EVIDENCE_TARGETS` and therefore human-only.

### 1.4.4 `experiments` (EXP) — `Run`

Existing collection; existing fields (`validity`, `invalidity_reason`, `executions`, `limitations`,
`execution_gate`, `unavailable_primary_metrics`) are retained because `ros.propagation` reads them.

| Field | Type | Required | Rule |
|---|---|---|---|
| `protocol_id` | string | conditional | Required once status leaves `Designed`. |
| `run_ids` | array[string] | yes | `RUN` identifiers. |
| `validity` | enum | conditional | `valid` \| `invalid` \| `partially_valid`. Required once executed. |
| `invalidity_reason` | string | conditional | Required when `validity ≠ valid`. |
| `hypothesis_ids` | array[string] | yes | Non-empty. |
| `observation_ids` | array[string] | conditional | Required once executed. |
| `evidence_ids` | array[string] | conditional | Required once executed. |
| `treatment_activated` | boolean | conditional | Required once executed. `false` means the treatment did not occur, which is E0's exact defect and must be recordable without pretending it was a test. |

Status vocabulary: `Designed`, `Blocked`, `Blocked Confirmatory`, `Planned`, `Executed`,
`Invalidated`, `Retired`. `ros.propagation.NOT_YET_EXECUTED` governs whether propagation is due; the
vocabulary here is a superset normalized through `ros.model.normalise_term`.

### 1.4.5 `runs` (RUN) — `Run`

The bridge record. One per runtime execution. This is where the audit's missing continuation begins.

| Field | Type | Required | Rule |
|---|---|---|---|
| `experiment_id` | string | yes | Resolves to `experiments`. |
| `protocol_id` | string | yes | Resolves to a frozen `protocols` record. |
| `runtime_run_id` | string | yes | The Tier R `Run` identifier from the event log. |
| `manifest_path` | string | yes | Repo-relative. |
| `manifest_digest` | string | yes | SHA-256. |
| `admissibility` | object | yes | The serialized `ros.admissibility.Verdict`: `{admissible, tier, ceiling, reasons}`. |
| `determinism_tier` | enum | yes | Must equal the protocol's. Mismatch is an error. |
| `event_log_path` | string | yes | Path to the run's authoritative `obs/2` event stream. |
| `artifact_ids` | array[string] | yes | `ART` identifiers. |
| `environment` | object | yes | From `ros.events.environment()`. |
| `clean_checkout` | boolean | yes | False forces the admissibility ceiling to `exploratory-admissible` at most. |

**Rule R1-11.** The `admissibility` block is **copied from** `ros.admissibility.assess`, never
computed by the LSKE. The LSKE stores the verdict as an input (permitted by R0-4: it is an
assertion by another subsystem), and re-derives it during integrity checks to detect tampering. A
stored verdict that disagrees with a recomputed one is an `error` finding.

**Rule R1-12.** `admissibility` must be derived from run artifacts, not caller flags. This is
audit finding 4 ("ROS admissibility is constructed from caller flags, not run artifacts") and
blocker 3. A `runs` record whose admissibility inputs cannot be reproduced from `manifest_path` +
`manifest_digest` + `event_log_path` is rejected.

### 1.4.6 `observations` (OBS) — `Measurement`

Existing collection.

| Field | Type | Required | Rule |
|---|---|---|---|
| `run_ids` | array[string] | yes | Non-empty. An observation with no run is an assertion, and belongs in a `Claim`. |
| `metric_id` | string | yes | Resolves to `metrics`. |
| `value` | number\|string\|null | yes | `null` is legal and means unmeasured, which is scientific state, not absence. |
| `uncertainty` | object | yes | `{kind, interval, n, method}`. |
| `coverage` | object | yes | `{measured, expected, missing_reason}`. |
| `validity` | enum | yes | `valid` \| `invalid` \| `unavailable`. |
| `declared_null_comparison` | object\|null | yes | Result against the protocol's declared null. |
| `blinded` | boolean | yes | Whether the outcome was concealed during collection. |

**Rule R1-13 (missingness).** `value = null` with `validity = unavailable` and a non-empty
`coverage.missing_reason` is a complete, valid observation. The LSM currently records "Five of six
declared primary metrics were unavailable, which is itself a major finding" — the schema must be
able to say that, or it destroys the finding.

### 1.4.7 `metrics` (MET) — `Measurement`

| Field | Type | Required | Rule |
|---|---|---|---|
| `formula` | string | yes | Exact. |
| `units` | string | yes | Non-empty. |
| `direction` | enum | yes | `higher_is_better` \| `lower_is_better` \| `none` |
| `estimator_version` | string | yes | Semver. Changing the formula requires a new version. |
| `aggregation_rule` | string | yes | How runs combine. |
| `declared_null` | string | yes | Lock E2. |
| `validity_status` | enum | yes | `validated` \| `provisional` \| `defective` |
| `known_defects` | array[string] | yes | May be empty. |

Status vocabulary: `Active`, `Provisional`, `Defective`, `Retired`, `Superseded`.

### 1.4.8 `datasets` (DSET) — `Environment`

| Field | Type | Required | Rule |
|---|---|---|---|
| `content_digest` | string | yes | SHA-256 of the canonical content. |
| `generator` | object\|null | yes | For synthetic environments: seed, config, code version. |
| `leakage_audit` | object | yes | `{audited, at, by, findings}`. |
| `splits` | object | yes | Named partitions with digests. |
| `provenance_reliability` | enum | yes | `reconstructable` \| `archived` \| `legacy_uncertain` \| `unrecoverable` |

**Rule R1-14.** `provenance_reliability ∈ {legacy_uncertain, unrecoverable}` caps every downstream
claim at `confidence.level ≤ 1` regardless of statistics. The LSM's "mixed legacy provenance" debt
becomes mechanical rather than remembered.

### 1.4.9 `artifacts` (ART) — `Snapshot`

| Field | Type | Required | Rule |
|---|---|---|---|
| `run_id` | string | yes | Resolves to `runs`. |
| `path` | string | yes | Repo-relative. |
| `digest` | string | yes | SHA-256. |
| `kind` | enum | yes | `manifest` \| `metrics` \| `events` \| `checkpoint` \| `log` \| `figure` \| `inventory` |
| `integrity` | enum | yes | `verified` \| `failed` \| `absent` |
| `retention` | enum | yes | `permanent` \| `evidence_bearing` \| `transient` |

**Rule R1-15.** `retention = evidence_bearing` artifacts may never be deleted while any `evidence`
record cites the run that produced them. Deletion of an evidence-bearing artifact requires a
`decisions` record with `action = delete` — which Lock §68 recognizes as a scientific success when
justified, but never as a cleanup.

### 1.4.10 `evidence` (EVD) — `Evidence`

Existing collection. `EVIDENCE_DIRECTIONS` from `ros.model` is retained unchanged: `supports`,
`opposes`, `null`, `indeterminate`, `invalid`, `requires-assumption`, `depends-on`.

| Field | Type | Required | Rule |
|---|---|---|---|
| `source_observation_ids` | array[string] | yes | Non-empty. Orphan evidence is a Lock-named defect. |
| `run_ids` | array[string] | yes | Non-empty. |
| `target_id` | string | yes | The `Claim`-realizing record this evidence bears on. |
| `direction` | enum | yes | From `EVIDENCE_DIRECTIONS`. |
| `dimensions` | array[string] | yes | Which of the ten confidence dimensions this evidence speaks to. Non-empty. |
| `eligibility` | enum | yes | `exploratory-admissible` \| `confirmatory-admissible` \| `ineligible` |
| `assumptions_relied_upon` | array[string] | yes | `ASM` identifiers. May be empty only with an explicit `none_declared` marker. |
| `unexcluded_alternatives` | array[object] | yes | Each `{statement, why_not_excluded}`. **Human-only content.** |
| `rationale` | string | yes | The interpretation. `ros.propagation` reads this field for obligation 4. |
| `independence_group` | string | yes | Evidence sharing an `independence_group` may not be counted as independent replication. |

**Rule R1-16.** `unexcluded_alternatives` is written under `skb.evidence_relation`, which is in
`EVIDENCE_TARGETS`. `ros.authority.escalation_for("skb.evidence_relation")` returns
`alternative_explanations`, one of the four `HUMAN_ONLY` decisions: "enumerating candidates is
mechanical, judging exclusion is not." An agent may populate `statement`; only a human may commit
`why_not_excluded`.

**Rule R1-17.** Three defects are detected mechanically and block the `store_integrity` gate:
orphan evidence (empty `source_observation_ids`), circular support (a cycle in the
`supports`-projected graph), and shared-evidence dependence counted as independent replication
(two evidence records with the same `independence_group` both cited as replications of one claim).

### 1.4.11 `decisions` (DEC) — `Decision`

Existing collection. `DECISION_ACTIONS` from `ros.model` is retained unchanged:
`accept_within_scope`, `reject`, `revise`, `narrow`, `split`, `merge`, `archive`, `no_change`,
`delete`.

| Field | Type | Required | Rule |
|---|---|---|---|
| `action` | enum | yes | From `DECISION_ACTIONS`. |
| `subject_ids` | array[string] | yes | Non-empty. What the decision is about. |
| `evidence_ids` | array[string] | yes | May be empty only for `action = no_change`. |
| `rationale` | string | yes | Non-empty. |
| `scope_after` | object\|null | conditional | Required for `accept_within_scope` and `narrow`. |
| `level_after` | integer\|null | conditional | Required when the decision changes `confidence.level`. |
| `alternatives_considered` | array[string] | yes | Non-empty. |
| `dissent` | array[object] | yes | May be empty. Recorded dissent is never removed. |
| `human_committer` | string | yes | Non-empty. |
| `propagation_receipt_id` | string | yes | The transaction that discharged the remaining obligations. |

**Rule R1-18.** `authority.is_human` is `true` and `authority.write_target` is `skb.decision` for
every record in this collection, without exception, checked at write and at integrity. This is the
single invariant the whole subsystem exists to protect.

### 1.4.12 `mechanisms` (MEC) — `Claim`

| Field | Type | Required | Rule |
|---|---|---|---|
| `statement` | string | yes | How the effect is produced. |
| `hypothesis_ids` | array[string] | yes | Non-empty. |
| `bundled_with` | array[string] | yes | Other mechanisms not separated by any current experiment. Non-empty means the causal object is the bundle, not this mechanism. |
| `identifiability` | enum | yes | `identified` \| `bundled` \| `unidentified` |
| `operability` | enum | yes | `demonstrated` \| `undemonstrated` \| `failed` |

**Rule R1-19.** `operability = failed` blocks every experiment naming this mechanism from
transitioning to `Executed` with `treatment_activated = true`. The LSM's "Scientific stop:
repeating E0 before growth-trigger operability is established" becomes a gate rather than a note.

### 1.4.13 `theories` (THY) — `Claim`

| Field | Type | Required | Rule |
|---|---|---|---|
| `statement` | string | yes | The integrative relation. |
| `constituent_hypothesis_ids` | array[string] | yes | Level 4 requires ≥ 2 independently validated. |
| `integrated_principle` | string\|null | yes | Level 5 requires an independent principle. |
| `risky_prediction` | object\|null | yes | Level 5 requires a novel risky prediction and its outcome. |
| `outperforms` | array[string] | yes | Alternative accounts this theory beats, with the evidence. |

Level 5 eligibility is computed and displayed; it is committed by a `decisions` record only.

### 1.4.14 `assumptions` (ASM) — `Claim`

| Field | Type | Required | Rule |
|---|---|---|---|
| `statement` | string | yes | |
| `load_bearing_for` | array[string] | yes | Non-empty. An assumption nothing depends on is not tracked. |
| `test_status` | enum | yes | `untested` \| `supported` \| `opposed` \| `refuted` |
| `opposing_evidence_ids` | array[string] | yes | May be empty. |
| `failure_consequence` | string | yes | What breaks if it is false. |

### 1.4.15 `unknowns` (UNK) — `Claim`

Per Lock E3, an Unknown is a `Claim` with no evidence relation.

| Field | Type | Required | Rule |
|---|---|---|---|
| `statement` | string | yes | |
| `expected_decision_value` | enum | yes | Drives ranking. `changes_roadmap` \| `changes_design` \| `changes_measurement` \| `none` |
| `blocks_ids` | array[string] | yes | What cannot proceed. |
| `cheapest_resolving_experiment` | string\|null | yes | |

**Rule R1-20.** An `unknowns` record that acquires an `evidence` relation must transition — to a
`hypotheses` record via supersession, or be resolved by a `decisions` record. An Unknown with
evidence is a contradiction in terms, and the integrity check says so.

### 1.4.16 `scientific_debt` (SDEBT) — `Claim`

| Field | Type | Required | Rule |
|---|---|---|---|
| `statement` | string | yes | |
| `severity` | enum | yes | `blocks_validation` \| `blocks_program_decision` \| `scientific_stop` \| `advisory` |
| `blocks_ids` | array[string] | yes | |
| `discharge_condition` | string | yes | What would clear it. |
| `incurred_by` | array[string] | yes | |

**Rule R1-21.** `severity = scientific_stop` blocks the named work at the gate level. Severity is
an evidence-bearing field: lowering it is a `skb.claim_status` write, human-only. Debt that an
agent could downgrade is not debt.

### 1.4.17 `negative_results` (NEG) — `Evidence`

| Field | Type | Required | Rule |
|---|---|---|---|
| `statement` | string | yes | What did not happen. |
| `hypothesis_id` | string | yes | |
| `scope` | object | yes | The scope within which the negative holds. |
| `equivalence_established` | boolean | yes | Whether the interval was tight enough to claim equivalence. |
| `retry_prohibited` | boolean | yes | Article L-10: nulls may not be retried with new margins. |
| `evidence_ids` | array[string] | yes | Non-empty. |

**Rule R1-22.** `retry_prohibited = true` refuses any new `protocols` record naming the same
hypothesis with a changed `sesoi`. Overriding it requires a `decisions` record citing new
measurement-validity evidence, not a new margin.

### 1.4.18 `programs` (PROG) — `Claim`

| Field | Type | Required | Rule |
|---|---|---|---|
| `statement` | string | yes | The program's governing claim. |
| `gate` | enum | yes | `G1` \| `G2` \| `G3` \| `G4` \| `G5` (Article L-10 order of work) |
| `question_ids` | array[string] | yes | |
| `entry_condition` | string | yes | |
| `exit_condition` | string | yes | |

**Rule R1-23.** A `protocols` record whose hypotheses belong to gate `Gn` is refused while any
`programs` record at gate `Gm < n` has an unmet `exit_condition`. Article L-10's sequencing becomes
mechanical, which is what Blocking contradiction #22 (sequencing inversion) demands.

### 1.4.19 `sessions` (SESS) — `Intervention`

The record of human scientific work, so that annotation and analysis are traceable rather than
ambient.

| Field | Type | Required | Rule |
|---|---|---|---|
| `actor` | string | yes | |
| `authority` | integer | yes | `AuthorityClass` value. |
| `opened` / `closed` | string | yes | ISO-8601; `closed` may be `null` while open. |
| `records_touched` | array[string] | yes | |
| `annotations` | array[object] | yes | Each `{at, target_id, text}`. Enters as a Level-0 `Claim` per Lock E3. |
| `blinding_state` | enum | yes | `blinded` \| `unblinded` \| `not_applicable` |

**Rule R1-24.** Annotations are Level-0 Claims with an author and may never appear as
computational facts (Article L-8). The LSKE renders them visually distinct from evidence-derived
content in every projection, and the query language returns them only when explicitly requested.

### 1.4.20 `snapshots` (SNAP) — `Snapshot`

The addressing record for time travel. Stores coordinates, never content (R0-4).

| Field | Type | Required | Rule |
|---|---|---|---|
| `store_content_hash` | string | yes | From `ros.store.Store.content_hash()`. |
| `commit` | string | yes | Git SHA. |
| `at` | string | yes | ISO-8601. |
| `ontology_version` | string | yes | |
| `record_count` | integer | yes | For fast integrity triage only. |
| `cause` | enum | yes | `decision` \| `gate_run` \| `scheduled` \| `manual` |
| `caused_by` | string\|null | yes | Identifier of the causing record. |

**Rule R1-25.** A snapshot is valid only if the store at `commit` hashes to `store_content_hash`. A
snapshot that cannot be reconstructed is `integrity = failed` and is excluded from time travel
rather than silently approximated.

## 1.5 Projection types (computed, never stored)

Four types exist only as query results. They have no collection, no identifier, and no write path.

| Projection | Signature | Definition |
|---|---|---|
| `ScientificState` | `(Store) → ScientificState` | The complete current position: every claim with computed confidence, every open unknown, every active debt, every contradiction. Recomputed on every request. |
| `ConfidenceProfile` | `(Store, claim_id) → ConfidenceProfile` | The ten dimensions with their assessed state and contributing evidence, plus the maximum level the evidence supports. |
| `EvidenceTrace` | `(Store, claim_id) → EvidenceTrace` | The full derivation tree from claim to runs to protocols to artifacts. |
| `KnowledgeDiff` | `(Store, snap_a, snap_b) → KnowledgeDiff` | What changed between two snapshots, by record and by dimension. |

**Rule R1-26.** No projection may be serialized into the store. Generated documents rendered from
projections carry `ros.projections._GENERATED_BANNER` and live under
`ros.projections.GENERATED_DIR` (`docs/ros/generated`), where `ros.projections.drift` detects
divergence. A generated file edited by hand is drift, and drift blocks a gate.

---

# PART 2 — Relationship Ontology

## 2.1 Where relationships live

`ros/store.py` already defines `Relation` with `source`, `target`, `kind`, `direction`, `note`, read
from the store's `relations` key. Part 2 specifies the closed `kind` vocabulary, the semantics of
each, and the structural rules that make the graph checkable.

**Rule R2-1.** `relations` carries no identifiers of its own (`ros.model.NON_RECORD_KEYS`). A
relation is addressed by the triple `(source, kind, target)`, which is therefore unique: two
relations with the same triple are one relation, and a second declaration is a `warning` finding,
not a second edge.

**Rule R2-2.** Every relation's `source` and `target` must resolve to a record in the store.
Dangling relations are `error` findings. This falls out of `ros.model.iter_id_references` already
being structural rather than allow-listed.

## 2.2 The relation envelope

| Field | Type | Required | Rule |
|---|---|---|---|
| `from` | string | yes | Source record identifier. |
| `to` | string | yes | Target record identifier. |
| `type` | string | yes | From the closed vocabulary in §2.3. |
| `direction` | enum | conditional | Required for `evidential` class relations. From `ros.model.EVIDENCE_DIRECTIONS`. |
| `semantic_note` | string | yes | Non-empty. Why this edge exists. |
| `established_by` | string | yes | A `decisions` or `runs` identifier, or `document_derived` with a path. |
| `established_at` | string | yes | ISO-8601. |
| `record_version_at` | object | yes | `{source: int, target: int}` — the record versions when this edge was asserted. |
| `retracted_by` | string\|null | yes | A `decisions` identifier, or `null`. Edges are retracted, never deleted. |
| `confidence_basis` | enum | yes | `evidence` \| `human_assertion` \| `structural`. See R2-5. |

**Rule R2-3 (edge versioning).** `record_version_at` is the mechanism by which an edge knows
whether it still means what it meant. When either endpoint's `record_version` advances past the
recorded value, the edge is marked **stale** by computation (never by storage) and appears in the
`relation_staleness` query. A stale edge is not wrong; it is unreviewed, and the difference matters.

**Rule R2-4 (edge lifecycle).** Edges use the Article L-2 subset **without `TOMBSTONED`**:
`CANDIDATE → ACTIVE ⇄ DORMANT`, `ACTIVE → DELETED`, `DORMANT → DELETED`, `CANDIDATE → DELETED`.
This is the Lock's own rule for `Edge`, applied here unchanged.

**Rule R2-5 (no edge carries a confidence number).** An edge's `confidence_basis` names *how* it
was established; the strength of the relation is computed from the evidence records attached to it,
never stored on it. A number on an edge would be a stored derivation (R0-4) and, worse, an editable
one.

## 2.3 The closed relation vocabulary

Fifteen relation types in four classes. The vocabulary is closed: a relation with an unlisted `type`
is an `error` finding. Adding a type is an ontology-version change with a cross-version mapping
(Constraint C-d).

### Class 1 — Evidential (4 types)

These are the only relations that can change a confidence dimension. Each requires
`confidence_basis = evidence` and a resolvable `evidence` record.

| Type | Source → Target | Multiplicity | Semantics |
|---|---|---|---|
| `supports` | `EVD` → `Claim`-realizing | many→many | Evidence raises the assessed state of one or more named dimensions, within the target's scope. Never raises `confidence.level` by itself. |
| `refutes` | `EVD` → `Claim`-realizing | many→many | Evidence is inconsistent with the target within its declared scope. The Lock's `opposes` direction; `refutes` is the relation name, `opposes` is the evidence direction. |
| `contradicts` | `Claim` → `Claim` | many→many | Two claims cannot both hold in the intersection of their scopes. Symmetric: asserting one direction implies the other, and the store materializes both for query symmetry. |
| `validated_by` | `Claim` → `EXP` \| `RUN` | many→many | The named execution is the specific test that bears on this claim. Requires the run's admissibility verdict to permit the claim's target level. |

**Rule R2-6.** `supports` and `refutes` may only originate from an `evidence` or `negative_results`
record. A `supports` edge from an `observations` record directly to a `hypotheses` record skips
interpretation — obligation 4 — and is refused. Observation is not interpretation.

**Rule R2-7.** `contradicts` between two claims whose scopes do not intersect is an `error`. Two
claims that hold in different regimes do not contradict; recording them as contradictory
manufactures a conflict, and the LSKE's contradiction register must contain only real ones.

**Rule R2-8.** `validated_by` to a run whose `admissibility.tier` is below the level being claimed
is refused. D2 determinism can never satisfy a confirmatory `validated_by`.

### Class 2 — Derivational (5 types)

Provenance structure. `confidence_basis = structural`. These edges are computed from record fields
where possible and asserted only where a field cannot express them.

| Type | Source → Target | Multiplicity | Semantics |
|---|---|---|---|
| `generated` | `RUN` → `ART` \| `OBS` | one→many | The run produced this artifact or observation. Inverse is implied, never stored separately. |
| `observed` | `OBS` → `RUN` | many→one | This observation was taken during that run. The inverse of `generated` for observations, asserted from the observation side when the run record predates it. |
| `measured` | `OBS` → `MET` | many→one | The observation instantiates this metric definition at this estimator version. |
| `derived_from` | any → any | many→many | The source's content was computed from the target. Transitive for tracing; the transitive closure is computed, never stored. |
| `depends_on` | any → `ASM` \| `DSET` \| `MET` \| `PROT` | many→many | The source is invalid if the target is invalid. The propagation channel for invalidation (Part 4.6). |

**Rule R2-9.** `derived_from` must be acyclic. A cycle is an `error` finding, because a cyclic
derivation means nothing was actually derived.

**Rule R2-10.** `depends_on` is the *only* edge along which invalidity propagates. Making
invalidation travel along `supports` would let a defective metric silently un-support a claim
without anyone deciding to; making it travel along `depends_on` forces the dependency to have been
declared.

### Class 3 — Structural (3 types)

Organization. `confidence_basis = structural`.

| Type | Source → Target | Multiplicity | Semantics |
|---|---|---|---|
| `belongs_to` | any → `PROG` \| `RQ` | many→one | Organizational membership. Exactly one parent per level. |
| `extends` | `Claim` → `Claim` | many→one | The source adds scope or detail while preserving the target's content. The target remains true. |
| `predicts` | `Claim` \| `THY` → `OBS`-shaped spec | one→many | The claim entails a specific measurable outcome. Requires a declared observable and a declared null. |

**Rule R2-11.** `extends` requires the target to remain `ACTIVE`. Extending a `TOMBSTONED` claim is
refused; the correct edge is `supersedes` on a new record.

**Rule R2-12.** `predicts` edges asserted *before* the predicting run executes are the only ones
eligible for a Level-5 "novel risky prediction". `established_at` is compared against the run's
start, and an edge established afterward is marked `post_hoc` in every projection. Prediction after
the fact is explanation, and the distinction is the whole value of the edge.

### Class 4 — Historical (3 types)

Time and change. `confidence_basis = human_assertion` — each requires a `decisions` record.

| Type | Source → Target | Multiplicity | Semantics |
|---|---|---|---|
| `supersedes` | any → same type | one→one | The source replaces the target. The target retains its original semantics and remains readable forever. |
| `explains` | `MEC` \| `THY` → `Claim` \| `OBS` | many→many | The source accounts for the target's content by a stated mechanism. Explanatory, not evidential: an `explains` edge changes no confidence dimension. |
| `causes` | `MEC` → `Claim` \| `OBS` | many→many | The strongest available assertion. Requires an `Intervention`-bearing run: manipulation, not correlation. |

**Rule R2-13 (`causes` gate).** A `causes` edge requires (a) a run with a recorded `intervention`
event, (b) `mechanisms.identifiability = identified` — not `bundled`, and (c) a `decisions` record
citing the intervention evidence. Absent any of the three, the correct edge is `explains`. The Lock
names causal restraint explicitly; this is where it is enforced rather than hoped for.

**Rule R2-14 (`supersedes` is one→one).** Splitting one record into several is `split` in
`DECISION_ACTIONS` plus multiple `supersedes` edges from each new record to the same target, which
makes the target's `superseded_by` ambiguous — so for `split` and `merge`, `superseded_by` holds the
`decisions` identifier instead of a record identifier, and the decision enumerates the results. One
field, two readings, disambiguated by the decision's `action`.

## 2.4 Multiplicity summary

| Relation | Source cardinality | Target cardinality |
|---|---|---|
| `supports`, `refutes`, `contradicts`, `validated_by` | many | many |
| `generated` | one | many |
| `observed`, `measured`, `belongs_to`, `extends` | many | one |
| `derived_from`, `depends_on`, `explains`, `causes` | many | many |
| `predicts` | one | many |
| `supersedes` | one | one |

## 2.5 Prohibited relation shapes

Eight shapes are refused at write time and re-checked at integrity time.

1. Any edge to or from a `DELETED` record.
2. `supports`/`refutes` not originating from `EVD` or `NEG` (R2-6).
3. A cycle in `derived_from` (R2-9).
4. A cycle in `supports` — circular support, a Lock-named defect.
5. `contradicts` between non-intersecting scopes (R2-7).
6. `causes` without intervention evidence (R2-13).
7. `validated_by` to an inadmissible run, or to a run whose tier is below the claimed level (R2-8).
8. Two `supports` edges to one claim, cited as independent replication, sharing an
   `independence_group` (R1-17).

---

# PART 3 — Scientific Memory

## 3.1 The one-sentence rule

**Nothing is ever destroyed; things become non-current.** Every operation that appears to remove
knowledge is an operation that marks knowledge non-current while leaving it fully readable, fully
addressed, and fully attributed.

## 3.2 Write algebra

Exactly five write operations exist. There is no sixth, and no combination.

| Operation | Effect | Permitted on | Authority |
|---|---|---|---|
| `CREATE` | New record, `record_version = 1`, `lifecycle.state = CANDIDATE` | any collection | per collection |
| `AMEND` | `record_version += 1`, revision appended | non-`append_only`, or `append_only` before `frozen_at` | per collection |
| `ANNOTATE` | Appends a Level-0 Claim to `sessions.annotations`; touches no field of the target | any record, any state | `skb.observation_draft` |
| `TRANSITION` | Appends to `lifecycle.transitions` with an `event_id` | any record | per target state |
| `SUPERSEDE` | Creates a successor; sets predecessor's `superseded_by` | any record | `skb.decision` |

**Rule R3-1.** `AMEND` on a sealed (`frozen_at` set) record is refused. The store's own
`correction_policy` names the alternative: linked supersession.

**Rule R3-2.** `ANNOTATE` is the only write permitted on a `TOMBSTONED` record. A tombstoned claim
can still be discussed; it cannot be quietly revised into relevance.

**Rule R3-3.** There is **no `DELETE` operation in the algebra.** `DELETED` is a lifecycle state
reached by `TRANSITION` from `TOMBSTONED` or `CANDIDATE`, and a `DELETED` record retains blocks A–H
in full. What is removed is currency, not content. Physical removal of record content requires a
`decisions` record with `action = delete` plus a `governance.registry` write, and it produces a
tombstone stub retaining `id`, `content_hash`, and the deleting decision — so that every reference
to it still resolves. A dangling reference is the one thing this store may never contain.

## 3.3 Superseded knowledge behavior

A superseded record's behavior is fully determined, in six clauses.

1. **Readable forever.** `Store.get(id)` returns it. Always.
2. **Original semantics retained.** Its `ontology_version` governs its interpretation, not the
   current one (Constraint C-d).
3. **Excluded from current state.** `ScientificState` omits it. It contributes no confidence to any
   claim.
4. **Its evidence survives it.** Evidence records that supported a superseded claim remain valid
   evidence records; they are re-targeted by the successor only if the successor's `decisions`
   record explicitly cites them. Evidence is never silently inherited, because inherited evidence is
   how a rejected claim comes back to life without a decision.
5. **Its edges become `DORMANT`, not deleted.** Queries default to excluding dormant edges and can
   include them explicitly.
6. **Its lineage is queryable in both directions.** `lineage(id)` walks `supersedes` backward to the
   origin and `superseded_by` forward to the current record, returning the full chain with each
   link's decision.

## 3.4 Obsolete knowledge representation

Four distinct kinds of obsolescence, deliberately not collapsed into one status, because they carry
different scientific meaning:

| Kind | Lifecycle | Status | Meaning | Reversible |
|---|---|---|---|---|
| **Superseded** | `TOMBSTONED` | `Superseded` | A better formulation exists. The content may still be true. | via successor |
| **Refuted** | `ACTIVE` | `Rejected` | Evidence opposes it within its scope. **Stays `ACTIVE`** — see R3-4. | only by new evidence |
| **Dormant** | `DORMANT` | context-specific | Not currently under investigation. No epistemic claim. | yes, `DORMANT → ACTIVE` |
| **Archived** | `TOMBSTONED` | `Archived` | Withdrawn without resolution — e.g. the Lock's withdrawn E08 and E17. | via `TOMBSTONED → ACTIVE` |

**Rule R3-4 (refuted claims stay `ACTIVE`).** A refuted claim is a *result*, not a retired object.
`HYP-2026-0005` and `HYP-2026-0006` are rejected within scope and are among P1's most reliable
current findings. The LSM says it plainly:

> These are durable scientific results and constraints on future design, not embarrassing artifacts
> to delete.

Tombstoning a refuted claim would remove it from `ScientificState` and thereby erase the finding.
So refutation changes `lifecycle.status` to `Rejected` and leaves `lifecycle.state = ACTIVE`, and
the negative result appears in the current position where it belongs.

## 3.5 Time travel

**Rule R3-5.** Historical state is *reconstructed*, never stored (R0-4). `state_at(snapshot_id)`
resolves the snapshot's `commit`, loads the store at that commit, verifies
`store_content_hash`, and computes `ScientificState` under the snapshot's `ontology_version`.

**Rule R3-6.** Reconstruction under a prior `ontology_version` uses that version's semantics. Where
the current ontology cannot express a prior meaning, the cross-version mapping's **loss-of-meaning
statement** (Constraint C-d) is returned alongside the state, and the affected records are flagged
`semantics_degraded`. Silent reinterpretation of old records under new rules is the failure this
clause exists to prevent.

**Rule R3-7.** A snapshot whose store hash does not verify is `integrity = failed` and time travel
to it **fails loudly**. It does not return an approximation. Approximate history is worse than no
history, because it is indistinguishable from real history.

## 3.6 Memory integrity checks

Extends `ros.store.Store.check()` with six checks, all severity `error`, all blocking the
`store_integrity` gate:

| Code | Check |
|---|---|
| `MEM-01` | Every `lifecycle.transitions` entry has a resolvable `event_id` (R1-4). |
| `MEM-02` | Every `revisions` entry's `prior_content_hash` matches the preceding entry's computed hash — the revision chain is unbroken. |
| `MEM-03` | Every `superseded_by` has a reciprocal `supersedes` (or a `split`/`merge` decision per R2-14). |
| `MEM-04` | No sealed record's `content_hash` differs from its recomputed hash. |
| `MEM-05` | No `supersedes` chain contains a cycle. |
| `MEM-06` | Every reference in every record resolves, including into `DELETED` stubs (R3-3). |

`ros.store` already has `_check_supersession`; `MEM-03` and `MEM-05` extend it rather than
duplicate it.

---

# PART 4 — Learning Engine

## 4.1 The prohibition, stated as a design rule

**There is no machine learning in the LSKE.** No model is fitted, no parameter is estimated from the
knowledge graph, no weight is tuned, no embedding is computed, no similarity is learned, no
threshold is optimized against outcomes.

**Rule R4-1.** Every change to any confidence dimension of any claim is caused by exactly one thing:
an `evidence` record whose eligibility permits it, accepted by a `decisions` record. There is no
other cause. A confidence value that changed without an evidence record and a decision is a defect
of the highest severity, detectable by replaying the decision log against the current state.

**Rule R4-2.** The learning engine is a **pure function**. `confidence(claim, store) → ConfidenceProfile`
with no state, no memory between calls, no accumulator, and no randomness. Two calls on the same
store content hash return byte-identical results. This is testable, and Part 9 requires the test.

## 4.2 Confidence is a ten-dimensional lattice, not a number

**Rule R4-3.** No dimension is ever a real number. Each of the ten dimensions holds one of exactly
four states:

| Dimension state | Meaning |
|---|---|
| `unassessed` | No eligible evidence bears on this dimension. The default, and the honest one. |
| `assessed_supported` | Eligible evidence supports it; no eligible evidence opposes it. |
| `assessed_contested` | Eligible evidence both supports and opposes it. |
| `assessed_failed` | Eligible evidence opposes it and none supports it. |

There is no score, no average, no weighted sum. A weighted sum would require weights, weights would
have to come from somewhere, and the only honest sources are a fitted model (prohibited) or a human
guess dressed as arithmetic (worse).

**Rule R4-4 (dimension resolution).** For dimension *d* on claim *c*, gather every `evidence` record
`e` where a `supports` or `refutes` edge connects `e → c` and `d ∈ e.dimensions` and
`e.eligibility ≠ ineligible` and `e.retracted_by is null`. Then:

- no such `e` → `unassessed`
- all `supports` → `assessed_supported`
- all `refutes` → `assessed_failed`
- both present → `assessed_contested`

`null` and `indeterminate` evidence directions count as *present but neither*: they move a dimension
from `unassessed` to `assessed_contested` only if support also exists; alone they leave it
`unassessed` with a recorded `null_evidence_ids` list. A null result is not weak support, and it is
not opposition. It is a measured absence, and it belongs in `negative_results`.

## 4.3 Level eligibility (computed) versus level (committed)

**Rule R4-5.** The engine computes `eligible_level`, the highest level the current evidence could
justify. It never writes `confidence.level`. The gap between `eligible_level` and the committed
`confidence.level` is displayed everywhere as `level_gap`, and a positive gap is a queue of pending
human decisions, not a discrepancy.

Eligibility rules, from Lock E3, mechanically:

| Level | Requires |
|---|---|
| 0 | Record exists. A human annotation with an author enters here. |
| 1 | ≥1 `assessed_supported` dimension from `exploratory-admissible` evidence; `existence` assessed. |
| 2 | `existence`, `measurement_validity`, `effect_existence` all `assessed_supported`; ≥1 confirmatory-admissible evidence record; a frozen protocol hash-matched before the first run. |
| 3 | Level 2 plus `magnitude` and `robustness` `assessed_supported`; ≥1 within-instance replication in a distinct `independence_group`. |
| 4 | Level 3 plus **E24 cross-instance replication** — evidence from ≥2 `independence_group`s on materially distinct instances. The only route. |
| 5 | Level 4 plus `integrated_principle` non-null plus a `predicts` edge with `established_at` before the run, whose outcome is `assessed_supported`. |

**Rule R4-6.** `eligible_level` is capped by `min` over four ceilings: the weakest contributing
run's `admissibility.tier`; the `datasets.provenance_reliability` cap (R1-14); any
`assessed_failed` dimension caps at the highest level not requiring that dimension; and any
`scientific_debt` with `severity = blocks_validation` naming the claim caps at 1.

**Rule R4-7.** No `assessed_contested` dimension may be treated as supported for eligibility. A
contested dimension caps `eligible_level` at the highest level not requiring it, and surfaces in the
contradiction register.

## 4.4 Evidence propagation

Propagation is **breadth-first along declared edges, single-pass, and terminating**. There is no
iteration to convergence, because iteration to convergence is a fitting procedure.

**Rule R4-8 (the four propagation channels, and only these four):**

| Channel | Edge | Effect |
|---|---|---|
| **Evidential** | `supports` / `refutes` | Sets dimension state on the direct target only. **Does not traverse further.** |
| **Constituent** | `constituent_hypothesis_ids` on `theories` | A theory's `eligible_level` is capped by the minimum committed level of its constituents. |
| **Dependency** | `depends_on` | Invalidity propagates. See §4.6. |
| **Scope** | `extends` | An extension inherits nothing. It must earn its own dimensions. |

**Rule R4-9 (no transitive support).** Evidence supporting claim A does not support claim B because
A `explains` B, `predicts` B, or `contradicts` B's rival. Support crosses exactly one edge. Multi-hop
support is how a single measurement comes to appear as a body of evidence, and the Lock names that
defect: shared-evidence dependence counted as independent replication.

**Rule R4-10 (`extends` inherits nothing).** Stated separately because it is the most tempting
exception. A claim that extends a validated claim into a new regime has *no* evidence in that
regime by definition. `generalisation` starts `unassessed` and is earned.

## 4.5 Contradiction accumulation

**Rule R4-11.** Contradictions accumulate; they never cancel. The contradiction register is a
computed set with one entry per detected conflict, and each entry persists until a `decisions`
record resolves it. Contradiction count is a first-class health number and appears in
`ros.kpi.compute` output.

Five detected contradiction kinds:

| Kind | Detection |
|---|---|
| `dimension_contested` | A dimension is `assessed_contested` (R4-4). |
| `claim_conflict` | An `ACTIVE` `contradicts` edge between two `ACTIVE` claims with intersecting scopes. |
| `status_inconsistency` | `lifecycle.status` inconsistent with `confidence.level` (R1-8). |
| `level_unsupported` | Committed `confidence.level` exceeds computed `eligible_level`. |
| `assumption_undermined` | An `assumptions` record with `test_status ∈ {opposed, refuted}` that is `load_bearing_for` an `ACTIVE` claim at level ≥ 2. |

**Rule R4-12.** `level_unsupported` is the only contradiction kind that can arise from evidence
being *removed from eligibility* — for example when a metric becomes `defective`. It is severity
`error` and blocks the `store_integrity` gate, because a committed level with no supporting evidence
is a false statement standing in the current scientific position.

## 4.6 Invalidation propagation

The one place where change travels far. It travels along `depends_on` only (R2-10).

**Rule R4-13.** When a record becomes invalid — `metrics.validity_status = defective`,
`datasets.provenance_reliability = unrecoverable`, `protocols` freeze verification failing,
`runs.admissibility.admissible = false`, `observations.validity = invalid` — every record reachable
by following `depends_on` **into** it has its dependent evidence marked `eligibility = ineligible`
by computation, its dimensions recomputed, and a contradiction raised if a committed level becomes
unsupported.

**Rule R4-14.** Invalidation **never** changes a `lifecycle.status`, **never** retracts a
`decisions` record, and **never** lowers a `confidence.level`. It changes eligibility, which changes
`eligible_level`, which raises `level_unsupported`, which queues a human decision. A machine may
discover that a conclusion no longer stands. Only a human may unconclude it.

## 4.7 Uncertainty evolution

**Rule R4-15.** Uncertainty is recorded, not modeled. Every `observations` record carries
`uncertainty` and `coverage` as measured facts. The engine aggregates them only by the metric's
declared `aggregation_rule` — never by an inferred one, and never by pooling across metrics with
different estimator versions.

**Rule R4-16 (missingness is state).** `coverage.measured < coverage.expected` propagates to
`observability_completeness` as `assessed_failed` when the shortfall exceeds the protocol's declared
coverage requirement. Five of six primary metrics unavailable is a major finding, and the engine
must report it as one rather than computing over the sixth.

**Rule R4-17.** Uncertainty never shrinks by aggregation across `independence_group`s that are not
actually independent. Two runs sharing an `independence_group` contribute one effective replication.

## 4.8 Knowledge, hypothesis, and theory evolution

**Rule R4-18 (hypothesis evolution).** A hypothesis changes status only by a `decisions` record.
Permitted transitions and their required actions:

| From | To | Decision action | Required |
|---|---|---|---|
| `Proposed` | `Exploratory` | `no_change` or `revise` | A frozen protocol exists. |
| `Exploratory` | `Under Validation` | `revise` | `eligible_level ≥ 2`. |
| `Under Validation` | `Validated` | `accept_within_scope` | `eligible_level ≥ 4`; `scope_after` set. |
| any | `Rejected` | `reject` | ≥1 dimension `assessed_failed` from eligible evidence; a `negative_results` record created. |
| any | `Superseded` | `revise`/`split`/`merge` | Successor exists; `supersedes` edge set. |
| any | `Archived` | `archive` | Rationale stating why it is withdrawn unresolved. |

**Rule R4-19 (theory evolution).** A theory's `eligible_level` is capped by the minimum committed
level of its constituents (R4-8). Adding a constituent can *lower* a theory's eligibility, which is
correct: an integration is only as strong as its weakest member.

**Rule R4-20 (no automatic promotion, ever).** The engine's output for every claim includes
`eligible_level`, `level_gap`, and `blocking_reasons`. It writes nothing. The queue of eligible
promotions is a work list for a human, and its length is a health metric — a long queue means
science is waiting on review, which is worth seeing.

## 4.9 What the engine returns

`learn(store) → LearningReport`, a pure projection:

| Field | Content |
|---|---|
| `profiles` | `ConfidenceProfile` per `Claim`-realizing record. |
| `contradictions` | The full register (§4.5), with kind, subjects, and detection basis. |
| `promotion_queue` | Claims where `eligible_level > confidence.level`, with `blocking_reasons` empty. |
| `demotion_queue` | Claims where `confidence.level > eligible_level` — the `level_unsupported` set. |
| `invalidation_cascade` | Records whose evidence became ineligible, with the `depends_on` path. |
| `store_content_hash` | The hash this report is valid for. Reports are never cached across hashes. |

---

# PART 5 — Reasoning Engine

All reasoning is **deductive over recorded structure**. Nothing is inferred, predicted, or guessed.
Every answer the engine gives is accompanied by the records it was derived from, and every answer is
reproducible from the store content hash alone.

**Rule R5-1.** Every reasoning result carries `store_content_hash` and a `basis` array of record
identifiers. A result that cannot name its basis is not returned.

**Rule R5-2.** The reasoning engine writes nothing, ever. It holds `AuthorityClass.OBSERVER`. This
is not a policy; it is the actor class the API is constructed with.

## 5.1 Evidence tracing

`trace_evidence(claim_id, depth) → EvidenceTrace`

Returns the complete derivation from a claim down to bytes on disk:

```
claim → evidence records → observations → runs → protocols (with freeze verification)
                                       → artifacts (with integrity status)
                                       → datasets (with provenance reliability)
                                       → metrics (with estimator version, validity)
```

**Rule R5-3.** The trace reports the **weakest link explicitly**: the minimum admissibility tier,
any failed artifact integrity, any defective metric, any unverifiable protocol freeze. A trace that
showed only the path and not its weakest point would let a claim inherit the appearance of its
strongest support.

**Rule R5-4.** Every node in a trace is annotated `eligible` or `ineligible` with a reason. An
ineligible node does not remove the branch from the trace; hiding a disqualified path is how the same
disqualification gets rediscovered.

## 5.2 Dependency tracing

`trace_dependencies(record_id, direction) → DependencyTrace`

- `direction = upstream`: what this record depends on, transitively along `depends_on` and
  `derived_from`.
- `direction = downstream`: **what breaks if this record is wrong** — the invalidation blast radius.

**Rule R5-5.** `downstream` results are ordered by the committed `confidence.level` of the affected
claims, descending. The most consequential breakage is reported first, because that is the one that
changes what a human does next.

## 5.3 Scientific explanation

`explain(record_id) → Explanation`

A structured account, not prose generation, with six fixed fields:

| Field | Content |
|---|---|
| `what_it_says` | The record's statement, verbatim. |
| `why_it_is_believed` | Every `supports` edge with its evidence, run, and admissibility tier. |
| `why_it_might_be_wrong` | Every `refutes` edge, every `assessed_contested` dimension, every unexcluded alternative from every contributing evidence record, every opposed assumption it depends on. |
| `what_it_rests_on` | The `depends_on` closure. |
| `what_rests_on_it` | The reverse closure. |
| `what_would_change_it` | The falsifier, plus which dimension each unassessed dimension needs. |

**Rule R5-6.** `why_it_might_be_wrong` is never empty for a claim below Level 5. If no refuting
evidence and no contested dimension exist, the field lists the `unassessed` dimensions and the
unexcluded alternatives — which always exist, because `evidence.unexcluded_alternatives` is a
required field. An explanation with no doubts is a presentation, not an explanation.

## 5.4 Contradiction detection

`detect_contradictions(store) → list[Contradiction]`

Returns the register from §4.5. Each entry carries `kind`, `subjects`, `basis`, `detected_at_hash`,
and `resolving_decision_id` (`null` while open).

**Rule R5-7.** Detection is exhaustive over the five kinds and deterministic in ordering: by kind
in declaration order, then by subject identifier. Nondeterministic ordering in a register a human
reviews by working down the list means the bottom entries are reviewed at random.

## 5.5 Gap analysis

`analyse_gaps(store) → GapReport`

Seven gap kinds, each mechanically detected:

| Gap | Detection |
|---|---|
| `unassessed_dimension` | An `ACTIVE` claim with a dimension `unassessed` and no protocol targeting it. |
| `falsifier_uncovered` | A hypothesis with a `falsifier` but no `protocols` record testing it. |
| `unknown_unaddressed` | An `unknowns` record with `expected_decision_value ≠ none` and no `cheapest_resolving_experiment`. |
| `debt_undischarged` | `scientific_debt` blocking an `ACTIVE` claim with no discharge path. |
| `assumption_untested` | An `assumptions` record `load_bearing_for` a level-≥2 claim with `test_status = untested`. |
| `mechanism_bundled` | `identifiability = bundled` on a mechanism cited by a level-≥2 claim. |
| `replication_absent` | A claim at `eligible_level = 3` with only one `independence_group`. |

**Rule R5-8.** `falsifier_uncovered` count divided by hypothesis count is the falsifier-coverage
metric already referenced by the repository's agent definitions. It belongs in
`ros.kpi.compute`, not in a separate dashboard, so that one number has one definition.

## 5.6 Hypothesis ranking

`rank_hypotheses(store) → list[RankedHypothesis]`

**Rule R5-9.** Ranking is a **deterministic lexicographic sort over recorded fields**. It is not a
score, not a weighting, and not tunable. The key, in order:

1. `scientific_debt` severity blocking it — `scientific_stop` sorts last (cannot be worked).
2. Article L-10 gate order — `G1` before `G2` before `G3` before `G4` before `G5`.
3. `decision_value` of the parent research question — `changes_roadmap` > `changes_design` >
   `changes_measurement` > `none`.
4. `level_gap` descending — claims closest to a decision first.
5. Count of `unassessed` dimensions ascending — nearly-complete claims before barely-started ones.
6. Identifier ascending — for total order.

A weighted score would have free parameters. The Lock permits exactly one free parameter in the
entire program — the nats-per-evaluation exchange rate in Article L-5 — and it is not for sorting a
work list.

## 5.7 Experiment recommendation

`recommend_experiments(store) → list[Recommendation]`

**Rule R5-10.** A recommendation is a **statement of what the records already imply**, not a
generated idea. Each carries: the target claim, the specific dimension it would move, the gate it
belongs to, the blocking debt it must clear first, whether a protocol already exists, and the
`retry_prohibited` check.

**Rule R5-11.** Recommendations are refused, with a stated reason, when: Article L-10 sequencing
forbids the gate (R1-23); a `negative_results` record has `retry_prohibited = true` for that
hypothesis (R1-22); the mechanism's `operability = failed` (R1-19); or a `scientific_stop` debt names
it (R1-21). Four mechanical refusals — each one a case the LSM currently states in prose and no
instrument enforces.

**Rule R5-12.** The report includes a `smallest_uncertainty_reduction` field: the recommendation
whose target dimension appears in the most level-blocking positions across all claims, with ties
broken by gate order. This is the mechanized form of the LSM's section 10, which is currently
written by hand.

## 5.8 Knowledge impact analysis

`analyse_impact(proposed_change) → ImpactReport`

Answers "if I commit this, what changes?" **before** the write.

| Field | Content |
|---|---|
| `records_affected` | Direct and transitive. |
| `dimensions_changed` | Per claim, before → after. |
| `levels_unsupported` | Claims that would enter `level_unsupported`. |
| `contradictions_created` | New register entries. |
| `contradictions_resolved` | Cleared entries. |
| `edges_staleness` | Edges whose `record_version_at` would go stale (R2-3). |
| `gates_broken` | Which `ros.gates` gates would begin to block. |
| `authority_required` | The `WriteTarget` and whether a human is required. |

**Rule R5-13.** `analyse_impact` runs against a **shadow store** — an in-memory copy with the change
applied — and is guaranteed to leave the real store untouched. The API is constructed with an
`OBSERVER` actor, so the guarantee is structural rather than promised.

## 5.9 Scientific Query Language (SQL-P1)

A declarative, read-only, deterministic query language. No mutation, no side effect, no user-defined
function.

### 5.9.1 Grammar (frozen, EBNF)

```ebnf
query        = select clause* ;
select       = "SELECT" projection ;
projection   = "*" | field { "," field } | aggregate ;
aggregate    = ( "COUNT" | "MIN" | "MAX" ) "(" field ")" ;
clause       = from | where | traverse | at | order | limit | include ;
from         = "FROM" collection { "," collection } ;
where        = "WHERE" predicate ;
traverse     = ( "SUPPORTING" | "SUPPORTED_BY" | "DEPENDS_ON" | "DEPENDED_ON_BY"
               | "DERIVED_FROM" | "CONTRADICTING" | "SUPERSEDING" | "SUPERSEDED_BY" )
               [ "DEPTH" integer ] ;
at           = "AT" ( "SNAPSHOT" identifier | "COMMIT" string | "NOW" ) ;
order        = "ORDER BY" field [ "ASC" | "DESC" ] { "," field [ "ASC" | "DESC" ] } ;
limit        = "LIMIT" integer ;
include      = "INCLUDE" ( "DORMANT" | "TOMBSTONED" | "DELETED" | "ANNOTATIONS"
                         | "INELIGIBLE" | "SUPERSEDED" ) { "," ... } ;
predicate    = comparison | predicate "AND" predicate | predicate "OR" predicate
             | "NOT" predicate | "(" predicate ")" ;
comparison   = field operator literal | field "IN" "(" literal { "," literal } ")"
             | field "IS" ( "NULL" | "NOT NULL" ) ;
operator     = "=" | "!=" | "<" | "<=" | ">" | ">=" | "MATCHES" ;
field        = identifier { "." identifier } ;
```

### 5.9.2 Semantics rules

**Rule R5-14 (default exclusions).** Absent `INCLUDE`, every query excludes `DORMANT`,
`TOMBSTONED`, and `DELETED` records, retracted edges, ineligible evidence, and Level-0 annotations.
Defaults are the current, admissible, evidence-derived position. Everything else is opt-in, so that
seeing non-current knowledge is always a deliberate act.

**Rule R5-15 (`AT` defaults to `NOW`).** Absent `AT`, the query runs against the working store and
the result carries its content hash. A query result without a hash cannot be cited.

**Rule R5-16 (total ordering).** Every result is totally ordered. Absent `ORDER BY`, results sort by
identifier ascending. `LIMIT` without a total order would return a different subset per call.

**Rule R5-17 (derived fields are queryable, not stored).** `eligible_level`, `level_gap`,
`dimensions.*`, `contradiction_count`, and `staleness` are computed at query time (R0-4). They are
readable and never writable; an attempted write is a parse error, not a permission error, so it fails
at the earliest possible moment.

**Rule R5-18 (no aggregation over incommensurable units).** `MIN`/`MAX` over an `observations.value`
field spanning more than one `metric_id` is a query error naming the conflicting metrics. `COUNT` is
always permitted. Averaging is deliberately absent from the grammar: there is no `AVG`, because the
aggregation rule belongs to the metric definition, not to the query.

### 5.9.3 Reference queries

```
SELECT * FROM hypotheses WHERE lifecycle.status = "Rejected"
SELECT * FROM hypotheses WHERE level_gap > 0 ORDER BY level_gap DESC
SELECT * FROM claims SUPPORTING "HYP-2026-0001" DEPTH 1
SELECT * FROM evidence WHERE eligibility = "ineligible" INCLUDE INELIGIBLE
SELECT COUNT(id) FROM unknowns WHERE expected_decision_value = "changes_roadmap"
SELECT * FROM hypotheses AT SNAPSHOT "SNAP-2026-0001"
SELECT * FROM metrics WHERE validity_status = "defective" DEPENDED_ON_BY DEPTH 3
```

---

# PART 6 — LSKE APIs

Interfaces only. No implementation. Every signature below is **frozen**: an implementer may not
change a name, add a parameter, alter a return type, or widen an authority requirement.

## 6.0 Module layout and the extension rule

**Rule R6-1.** The LSKE extends existing ROS modules rather than paralleling them. Nine modules
already exist and are reused unchanged; six are new.

| Module | Status | Role |
|---|---|---|
| `ros.model` | **extend** | `COLLECTIONS` grows 11 → 20; docstring count corrected (R1-6) |
| `ros.store` | **extend** | `Store.check()` gains `MEM-01`…`MEM-06` |
| `ros.authority` | **reuse unchanged** | Every write gated by `require()` |
| `ros.admissibility` | **reuse unchanged** | `assess()` is the only source of verdicts |
| `ros.events` | **reuse unchanged** | Every lifecycle transition emits |
| `ros.protocol` | **reuse unchanged** | `freeze`, `verify`, `digest`, `lint` |
| `ros.propagation` | **extend** | Gains `execute()` beside existing `audit()` |
| `ros.projections` | **extend** | Gains the LSM renderer |
| `ros.gates` | **extend** | Gains three LSKE gates |
| `ros.governance` | **reuse unchanged** | `load_registration()` |
| `ros.kpi` | **extend** | Gains four LSKE metrics |
| `lske.confidence` | **new** | Part 4 learning engine |
| `lske.reasoning` | **new** | Part 5 reasoning engine |
| `lske.transaction` | **new** | Part 9 transaction |
| `lske.query` | **new** | SQL-P1 |
| `lske.memory` | **new** | Part 3 supersession and time travel |
| `lske.render` | **new** | Part 7 visualization data |

**Rule R6-2.** No LSKE module imports from the runtime tree, and no runtime module imports from
`ros.*` or `lske.*`. Enforced by an import-graph test (R1-7), not by review.

## 6.1 `lske.confidence` — the learning engine

```python
# All functions pure. No I/O. No state. No randomness.

class DimensionState(str, Enum):
    UNASSESSED = "unassessed"
    ASSESSED_SUPPORTED = "assessed_supported"
    ASSESSED_CONTESTED = "assessed_contested"
    ASSESSED_FAILED = "assessed_failed"

DIMENSIONS: tuple[str, ...]                    # the ten, in Lock order, frozen

@dataclass(frozen=True)
class DimensionAssessment:
    dimension: str
    state: DimensionState
    supporting_evidence_ids: tuple[str, ...]
    opposing_evidence_ids: tuple[str, ...]
    null_evidence_ids: tuple[str, ...]

@dataclass(frozen=True)
class ConfidenceProfile:
    claim_id: str
    dimensions: tuple[DimensionAssessment, ...]     # exactly ten, in DIMENSIONS order
    committed_level: int | None
    eligible_level: int
    level_gap: int
    ceilings: tuple[tuple[str, int, str], ...]      # (source_id, ceiling, reason)
    blocking_reasons: tuple[str, ...]
    store_content_hash: str

def profile(store: Store, claim_id: str) -> ConfidenceProfile: ...
def profile_all(store: Store) -> tuple[ConfidenceProfile, ...]: ...
def eligible_level(store: Store, claim_id: str) -> int: ...
def ceilings_for(store: Store, claim_id: str) -> tuple[tuple[str, int, str], ...]: ...

@dataclass(frozen=True)
class LearningReport:
    profiles: tuple[ConfidenceProfile, ...]
    contradictions: tuple["Contradiction", ...]
    promotion_queue: tuple[str, ...]
    demotion_queue: tuple[str, ...]
    invalidation_cascade: tuple[tuple[str, tuple[str, ...]], ...]   # (record_id, depends_on path)
    store_content_hash: str

def learn(store: Store) -> LearningReport: ...
```

**Rule R6-3.** `lske.confidence` exposes **no setter of any kind**. There is no `set_level`, no
`assess`, no `update`. The module is import-safe against accidental writes because no write function
exists in it.

## 6.2 `lske.reasoning` — the reasoning engine

```python
@dataclass(frozen=True)
class TraceNode:
    record_id: str
    object_type: str
    eligible: bool
    ineligibility_reason: str | None
    children: tuple["TraceNode", ...]

@dataclass(frozen=True)
class EvidenceTrace:
    claim_id: str
    root: TraceNode
    weakest_link: tuple[str, str]          # (record_id, reason)
    minimum_admissibility_tier: str
    store_content_hash: str

def trace_evidence(store: Store, claim_id: str, depth: int = 0) -> EvidenceTrace: ...

@dataclass(frozen=True)
class DependencyTrace:
    record_id: str
    direction: str                          # "upstream" | "downstream"
    nodes: tuple[TraceNode, ...]
    highest_affected_level: int | None
    store_content_hash: str

def trace_dependencies(store: Store, record_id: str, direction: str) -> DependencyTrace: ...

@dataclass(frozen=True)
class Explanation:
    record_id: str
    what_it_says: str
    why_it_is_believed: tuple[str, ...]
    why_it_might_be_wrong: tuple[str, ...]      # never empty below level 5 (R5-6)
    what_it_rests_on: tuple[str, ...]
    what_rests_on_it: tuple[str, ...]
    what_would_change_it: tuple[str, ...]
    basis: tuple[str, ...]
    store_content_hash: str

def explain(store: Store, record_id: str) -> Explanation: ...

@dataclass(frozen=True)
class Contradiction:
    kind: str                               # the five kinds of section 4.5
    subject_ids: tuple[str, ...]
    basis: tuple[str, ...]
    severity: str                           # "error" | "warning"
    resolving_decision_id: str | None
    detected_at_hash: str

def detect_contradictions(store: Store) -> tuple[Contradiction, ...]: ...

@dataclass(frozen=True)
class Gap:
    kind: str                               # the seven kinds of section 5.5
    subject_id: str
    detail: str
    blocking: bool

@dataclass(frozen=True)
class GapReport:
    gaps: tuple[Gap, ...]
    falsifier_coverage: float
    store_content_hash: str

def analyse_gaps(store: Store) -> GapReport: ...

@dataclass(frozen=True)
class RankedHypothesis:
    hypothesis_id: str
    rank: int
    sort_key: tuple[int, int, int, int, int, str]     # the six keys of R5-9
    justification: str

def rank_hypotheses(store: Store) -> tuple[RankedHypothesis, ...]: ...

@dataclass(frozen=True)
class Recommendation:
    target_claim_id: str
    target_dimension: str
    gate: str
    existing_protocol_id: str | None
    blocking_debt_ids: tuple[str, ...]
    refused: bool
    refusal_reason: str | None

@dataclass(frozen=True)
class RecommendationReport:
    recommendations: tuple[Recommendation, ...]
    smallest_uncertainty_reduction: Recommendation | None
    store_content_hash: str

def recommend_experiments(store: Store) -> RecommendationReport: ...

@dataclass(frozen=True)
class ProposedChange:
    operation: str                          # CREATE | AMEND | ANNOTATE | TRANSITION | SUPERSEDE
    collection_key: str
    record_id: str | None
    payload: dict[str, Any]

@dataclass(frozen=True)
class ImpactReport:
    records_affected: tuple[str, ...]
    dimensions_changed: tuple[tuple[str, str, str, str], ...]   # (claim, dim, before, after)
    levels_unsupported: tuple[str, ...]
    contradictions_created: tuple[Contradiction, ...]
    contradictions_resolved: tuple[Contradiction, ...]
    edges_staleness: tuple[tuple[str, str, str], ...]           # (from, kind, to)
    gates_broken: tuple[str, ...]
    authority_required: str
    human_required: bool
    store_content_hash: str

def analyse_impact(store: Store, change: ProposedChange) -> ImpactReport: ...
```

## 6.3 `lske.memory` — supersession and time travel

```python
@dataclass(frozen=True)
class LineageLink:
    record_id: str
    record_version: int
    decision_id: str | None
    at: str

@dataclass(frozen=True)
class Lineage:
    record_id: str
    ancestors: tuple[LineageLink, ...]      # oldest first
    descendants: tuple[LineageLink, ...]    # nearest first
    current_id: str

def lineage(store: Store, record_id: str) -> Lineage: ...

@dataclass(frozen=True)
class ReconstructedState:
    snapshot_id: str
    ontology_version: str
    semantics_degraded_ids: tuple[str, ...]
    loss_of_meaning: tuple[str, ...]        # Constraint C-d statements (R3-6)
    state: "ScientificState"

def state_at(root: Path, snapshot_id: str) -> ReconstructedState: ...
    # Raises SnapshotIntegrityError when the store hash does not verify (R3-7).

class SnapshotIntegrityError(RuntimeError): ...

@dataclass(frozen=True)
class KnowledgeDiff:
    from_snapshot: str
    to_snapshot: str
    records_added: tuple[str, ...]
    records_superseded: tuple[str, ...]
    records_transitioned: tuple[tuple[str, str, str], ...]      # (id, from_state, to_state)
    dimensions_changed: tuple[tuple[str, str, str, str], ...]
    levels_changed: tuple[tuple[str, int | None, int | None], ...]
    contradictions_opened: tuple[Contradiction, ...]
    contradictions_closed: tuple[Contradiction, ...]

def diff(root: Path, from_snapshot: str, to_snapshot: str) -> KnowledgeDiff: ...

def snapshot(actor: Actor, root: Path, cause: str, caused_by: str | None) -> str: ...
    # Requires AuthorityClass.ENGINEER (write target "projection.render").
    # Returns the allocated SNAP identifier. Stores coordinates only (R0-4).
```

## 6.4 `lske.transaction` — the propagation transaction

```python
class Phase(str, Enum):
    """The nine obligations as executable phases; values equal ros.propagation.Obligation."""
    EXECUTION_VALIDITY = "execution_validity"
    OBSERVATIONS = "observations"
    EVIDENCE_RELATIONS = "evidence_relations"
    INTERPRETATION = "interpretation_and_alternatives"
    DECISION = "scientific_decision"
    DEPENDENT_STATUS = "dependent_status"
    ASSUMPTIONS_UNKNOWNS_DEBT = "assumptions_unknowns_debt"
    ROADMAP = "roadmap_priority"
    LIVING_MODEL = "living_scientific_model"

#: Phases an agent may complete. Phase 5 is absent, by construction.
AGENT_COMPLETABLE: frozenset[Phase]

#: The one phase requiring a human commit. Frozen at exactly one member.
HUMAN_REQUIRED: frozenset[Phase]    # {Phase.DECISION}

@dataclass(frozen=True)
class PhaseOutcome:
    phase: Phase
    state: str                      # "completed" | "drafted" | "awaiting_human" | "refused"
    records_written: tuple[str, ...]
    records_drafted: tuple[str, ...]
    detail: str

@dataclass(frozen=True)
class Receipt:
    receipt_id: str
    run_id: str
    experiment_id: str
    actor: str
    started_at: str
    ended_at: str
    outcomes: tuple[PhaseOutcome, ...]
    store_hash_before: str
    store_hash_after: str
    halted_at: Phase | None
    event_ids: tuple[str, ...]

    @property
    def complete(self) -> bool: ...
    @property
    def awaiting_human(self) -> bool: ...

class TransactionRefused(RuntimeError): ...

def ingest(actor: Actor, root: Path, run_id: str) -> Receipt: ...
    # Phases 1-4: drafts and writes non-evidence records; refuses on inadmissible runs.

def commit_decision(actor: Actor, root: Path, receipt_id: str,
                    decision: dict[str, Any]) -> Receipt: ...
    # Phase 5. Requires actor.is_human and AuthorityClass.SCIENTIST.
    # Raises AuthorityError via ros.authority.require(actor, "skb.decision").

def propagate(actor: Actor, root: Path, receipt_id: str) -> Receipt: ...
    # Phases 6-9. Refuses unless phase 5 is committed.

def receipt(root: Path, receipt_id: str) -> Receipt: ...
def outstanding(root: Path) -> tuple[Receipt, ...]: ...
```

**Rule R6-4.** `ingest` **cannot** write a `decisions` record. Not "will not" — the function has no
code path to `skb.decision`, and `commit_decision` is the only entry point that names it. The
boundary is in the API's shape, so that it survives a careless implementer.

**Rule R6-5.** `HUMAN_REQUIRED` is frozen at exactly one member. A change to its cardinality is a
governance breach, mirroring `ros.authority`'s own statement: "Reducing the count below four is not
an efficiency win, it is a governance breach."

## 6.5 `lske.query` — SQL-P1

```python
@dataclass(frozen=True)
class QueryResult:
    columns: tuple[str, ...]
    rows: tuple[tuple[Any, ...], ...]
    store_content_hash: str
    snapshot_id: str | None
    included: tuple[str, ...]           # which INCLUDE flags were active
    truncated: bool

class QueryError(ValueError): ...       # parse errors, unit-mismatch errors (R5-18)

def parse(text: str) -> "Query": ...            # frozen AST; no execution
def execute(store: Store, text: str) -> QueryResult: ...
def execute_at(root: Path, text: str) -> QueryResult: ...    # honours AT SNAPSHOT / AT COMMIT
def explain_query(text: str) -> str: ...        # the resolution plan; no store access
```

**Rule R6-6.** `execute` takes a `Store`, never a path, and returns immutable rows. There is no
`execute_write`, no parameter binding to a mutation, and no transaction handle. The language cannot
express a write, so no permission check is needed to prevent one.

## 6.6 `lske.render` — visualization data

```python
@dataclass(frozen=True)
class RenderPayload:
    schema: str                         # "obs/2"
    plate: str                          # V01..V36
    phase: str                          # obs/2 required field
    subject: str                        # obs/2 required field
    cause: str                          # obs/2 required field
    zoom_level: int                     # 1..8
    primitive: str                      # the one primitive this zoom addresses
    nodes: tuple[dict[str, Any], ...]
    edges: tuple[dict[str, Any], ...]
    overlays: dict[str, dict[str, Any]]     # exactly the eight overlay keys
    store_content_hash: str
    snapshot_id: str | None
    governance_banner: str | None           # R0-3

def render(store: Store, plate: str, zoom_level: int,
           snapshot_id: str | None = None) -> RenderPayload: ...
def render_living_model(store: Store, root: Path) -> Path: ...
    # Writes docs/ros/generated/ under _GENERATED_BANNER. Write target "projection.render".
def overlays_for(store: Store, plate: str) -> tuple[str, ...]: ...
```

## 6.7 Gate and metric extensions

```python
# ros.gates — three additional gates, all blocking
def _gate_lske_transaction(...) -> GateResult: ...
    # Blocks when any executed run has an outstanding receipt (phases 1-4 incomplete).
def _gate_confidence_support(...) -> GateResult: ...
    # Blocks on any level_unsupported contradiction (R4-12).
def _gate_relation_integrity(...) -> GateResult: ...
    # Blocks on any prohibited relation shape (section 2.5).

# ros.kpi — four additional metrics
#   lske_open_contradictions        (target 0 for error-severity)
#   lske_level_gap_total            (queue depth awaiting human review)
#   lske_falsifier_coverage         (R5-8; single definition)
#   lske_outstanding_receipts       (target 0)
```

**Rule R6-7.** The three new gates are **blocking**, not advisory. The audit's finding 14 — "`ros
gates` passes blocking gates, but the protocol result is vacuous and registration/vocabulary remain
advisory" — is the failure mode: a gate that cannot fail is not a gate. Each new gate must have a
test proving it blocks on a constructed violation, per R9-6.

## 6.8 Authority requirement per API

| API | Write target | Minimum authority | Human required |
|---|---|---|---|
| `lske.confidence.*` | none | `OBSERVER` | no |
| `lske.reasoning.*` | none | `OBSERVER` | no |
| `lske.query.*` | none | `OBSERVER` | no |
| `lske.memory.lineage`, `state_at`, `diff` | none | `OBSERVER` | no |
| `lske.memory.snapshot` | `projection.render` | `ENGINEER` | no |
| `lske.transaction.ingest` | `skb.observation_draft` | `ENGINEER` | no |
| `lske.transaction.commit_decision` | `skb.decision` | `SCIENTIST` | **yes** |
| `lske.transaction.propagate` | `skb.claim_status` | `SCIENTIST` | **yes** |
| `lske.render.render` | none | `OBSERVER` | no |
| `lske.render.render_living_model` | `projection.render` | `ENGINEER` | no |

**Rule R6-8.** `propagate` requires a human because phase 6 writes `lifecycle.status` on
hypotheses and mechanisms, which is `skb.claim_status`, which is in `EVIDENCE_TARGETS`. An agent may
draft every field; the commit is human. This is not an extra restriction added here — it is what
`ros.authority` already says, applied without exception.

---

# PART 7 — Visualization Architecture

The visualization is a **projection of the store and nothing else**. It has no database, no cache
that outlives a store hash, and no field the store cannot produce. This is not a preference; under
Art. L-7 a stored copy of derivable structure is hidden state by definition, and a visual layer with
its own state would be exactly that.

**Rule R7-1.** Every rendered surface is produced by `lske.render.render` from a `Store` plus a
`plate` plus a `zoom_level`. A surface that cannot be regenerated from those three inputs does not
ship. Any client-side state is limited to viewport, selection, and filter settings — none of which
may alter a value.

**Rule R7-2.** The LSKE does not add plates, overlays or zoom levels. It supplies the scientific
half of the object contract for the surface the Observatory specification already froze: 30 plates
(V01–V36 reconciled), 8 overlays, 8 zoom levels. Wanting a new plate is an Observatory amendment,
routed through `constitution-clerk`, not a rendering decision.

## 7.1 Schema: `obs/2`

**Rule R7-3.** Every payload declares `schema: "obs/2"` and carries the three fields audit finding 11
names as missing from `obs/1`:

| Field | Meaning | Source |
|---|---|---|
| `phase` | the research phase the surface depicts | `skb` header `scientific_phase`, or the snapshot's |
| `subject` | the record or population the surface is *about* | the addressed record id, never a label |
| `cause` | why this surface exists now | the `event_id` or `decision_id` that produced the change |

**Rule R7-4.** `cause` is an identifier, not prose. A surface whose `cause` cannot be resolved to an
event in `.ros/events.jsonl` or a `decisions` record renders with `cause: "unattributed"` and is
marked visually as unattributed. This is the visual form of Art. L-2: a state reached without an
event does not exist, so a change shown without a cause is shown as suspect.

**Rule R7-5.** An `obs/1` payload is not upgraded in place. `obs/1` and `obs/2` coexist; a consumer
declares which it reads. Retro-fitting `phase`, `subject` and `cause` onto historical `obs/1`
payloads would fabricate attribution that was never recorded.

## 7.2 The zoom model, bound to primitives

The Observatory's eight zoom levels each address exactly one primitive. The LSKE supplies the record
set for each, and refuses to render a level from anything else.

| Level | Primitive | LSKE record set | Plates |
|---|---|---|---|
| 1 | `Run` | `runs`, `experiments` | V01, V02, V03 |
| 2 | subsystem | `runs` partitioned by subsystem address | V07, V08, V10 |
| 3 | population | `metrics` + `observations` partition | V06, V09, V11 |
| 4 | object | `observations` addressed to one `Neuron`/`Edge` | V12, V13, V14 |
| 5 | `Event` | `.ros/events.jsonl` window | V04, V05, V16 |
| 6 | history | `Tick` range across `snapshots` | V19 |
| 7 | `Protocol` | `protocols` | V03, V17, V18 |
| 8 | `Claim` | `research_questions`, `hypotheses`, `mechanisms`, `theories` | V01, V15, V20 |

**Rule R7-6.** Zoom level 8 is `Claim` at every status level 0–5. There is no separate "theory" zoom;
a theory is a `Claim` at level 5 and renders on the same surface with the same fields. A distinct
theory view would let a level-5 claim display differently from a level-2 one, and the visual
difference would start doing epistemic work the record does not support.

**Rule R7-7.** Cross-level continuity: a selection at any level carries its `subject` identifier
unchanged to every other level. Zooming from a `Claim` to the `Event` that produced its evidence
never re-resolves through a label, a title or a name. Titles change; identifiers do not.

## 7.3 Clusters and hierarchy

**Rule R7-8.** Clustering is by **recorded relation**, never by computed similarity. The permitted
cluster keys are exactly:

| Cluster key | Edge or field | Level |
|---|---|---|
| Program | `belongs_to` → `programs` | 1 |
| Research question | `belongs_to` → `research_questions` | 2 |
| L-10 gate | `protocol.gate` / `experiment.gate` | 2 |
| Claim lineage | `supersedes` chain | 3 |
| Evidence group | `independence_group` | 3 |
| Dimension | the ten `confidence.dimensions` keys | 3 |

There is no embedding, no learned similarity, no clustering algorithm with a distance threshold. A
threshold would be a second free parameter, and Art. L-5 permits exactly one in the whole program.

**Rule R7-9.** Hierarchy is the `belongs_to` tree and nothing else: `programs` → `research_questions`
→ `hypotheses` → `experiments` → `runs` → `observations`. The tree is rendered from edges; a record
with no `belongs_to` parent renders at the root as **orphaned**, visibly, rather than being placed
somewhere plausible. A plausible placement is an invented fact.

## 7.4 Confidence display

**Rule R7-10.** Confidence renders as a **ten-cell lattice**, never as a bar, gauge, percentage,
score or single colour intensity. The ten cells are the ten Lock dimensions in Lock order; each cell
shows one of four states (R4-3). A gauge would require a scalar, a scalar would require weights, and
Part 4 establishes there is no legitimate source for weights.

**Rule R7-11.** The committed level and the eligible level render as two distinct marks, never merged.
Where they differ, the surface shows `level_gap` as a pending human decision — the queue of R4-5 —
and not as an error. Rendering the eligible level alone would show a promotion that no human made.

**Rule R7-12.** `unassessed` is visually distinct from `assessed_failed`, and both are distinct from
empty space. Observatory §2.3 makes missingness scientific state; a dimension nobody has looked at
and a dimension that was looked at and failed are opposite findings, and a shared grey renders them
identical.

**Rule R7-13.** No surface displays a confidence value for a `Claim` that has no `evidence` relation.
An Unknown renders with all ten dimensions `unassessed` and an explicit "no evidence" marker, never
with a low value. A low value implies measurement; there was none.

## 7.5 Timeline and version history

**Rule R7-14.** The timeline axis is **event-ordered, not clock-ordered**, at levels 5 and 6. Wall
time is available as a secondary axis and is labelled as such. Ticks are the runtime's own ordering;
substituting wall time introduces an ordering the runtime never had.

**Rule R7-15.** Version history renders Block C directly: each `revisions` entry as one row with
`change_kind`, `prior_content_hash`, actor, and the `event_id`. The rows are the record's own
history, not a diff computed at render time. A computed diff can disagree with the recorded history;
the recorded history wins, so it is what is shown.

**Rule R7-16.** A superseded record renders in the timeline at its original position with its
original semantics, marked `non-current`, and links forward to its successor. It is never removed
from the timeline and never re-rendered under the successor's meaning. Constraint C-d requires old
records to keep their original semantics, and a timeline that silently updates them destroys the
only evidence of what was believed at the time.

**Rule R7-17.** Where a reconstruction crosses an `ontology_version` boundary, the surface displays
the C-d loss-of-meaning statement inline, and marks affected records `semantics_degraded`. It does
not translate the older record into the newer vocabulary.

## 7.6 Filtering

**Rule R7-18.** Default filters match SQL-P1's default exclusions (R5-14): dormant, tombstoned,
deleted, retracted, ineligible and annotation records are hidden. Every active filter is displayed
as a visible chip with a count of what it hides. A hidden count of zero and a hidden count of forty
must not look the same.

**Rule R7-19.** No filter can hide a `contradicts` edge between two visible records, and no filter
can hide an `error`-severity contradiction on a visible record. Filtering away the conflict while
leaving both sides visible would present a coherent picture that the store does not support.

**Rule R7-20.** Annotations are opt-in (R1-24) and, when shown, render in a visually distinct
register from evidence-derived content — different container, not merely different colour. Observatory
§20.4 is annotation discipline; a human note that looks like a measurement is the failure it exists
to prevent.

## 7.7 Animation

**Rule R7-21.** Animation interpolates **position only** — layout, camera, opacity. It never
interpolates a value, a level, a dimension state, a count or a confidence cell. Interpolating an
epistemic quantity displays states that were never true.

**Rule R7-22.** Every animated transition is driven by a sequence of recorded events or snapshots.
Frames are drawn *at* recorded coordinates; there are no synthetic in-between frames carrying data.
Where two snapshots are far apart, the animation shows a discontinuity rather than a smooth ramp,
because the smooth ramp is fiction.

**Rule R7-23.** Nothing animates on load by default, and no surface animates while a human is
reading a decision brief. Motion draws attention, and Observatory §2.7 requires uncertainty before
salience.

## 7.8 Interactive navigation

**Rule R7-24.** Selection is by identifier and is global: selecting `HYP-2026-0001` on V01 selects it
on every open plate. Selection never writes. There is no "edit in place" affordance anywhere in the
visual layer; the render module has no write path to the store except `projection.render`.

**Rule R7-25.** Every displayed value is traceable in at most two interactions: value → its
`observations`/`evidence` record → its `runs` and `protocols`. A value that cannot reach its
provenance in two steps is a rendering defect, not a UX preference.

**Rule R7-26.** Outcome-access protection (Observatory §20.5): where a `protocols` record declares
`blinding` and the run is not yet unblinded, outcome-bearing fields render as withheld, with the
protocol id and the unblinding condition shown. Withheld is a displayed state, not an omission —
the scientist must be able to see that something is being withheld and why.

**Rule R7-27.** Every surface carries the governance banner when the store is unregistered (R0-3).
The banner is part of the payload, not a layout decoration, so a screenshot cannot lose it.

## 7.9 Time travel

**Rule R7-28.** Time travel is `lske.memory.state_at(root, snapshot_id)` and nothing else. The
control offers only snapshot coordinates that exist in the `snapshots` collection. There is no
free-form date picker, because a date that lands between snapshots would have to be interpolated,
and R7-22 forbids interpolating data.

**Rule R7-29.** A snapshot whose recorded store hash does not verify is **excluded from the
control**, with the reason displayed. It is not offered as approximate (R3-7). Approximate history is
indistinguishable from real history, which makes it worse than an absent option.

**Rule R7-30.** In a past view, every write affordance is absent from the payload — not disabled in
the client. `RenderPayload` from a snapshot carries no mutable handle at all, so a client bug cannot
produce a write against a reconstructed past.

**Rule R7-31.** Comparing two points in time renders `KnowledgeDiff` (§6.3) directly: what was added,
superseded, transitioned, which dimensions changed, which levels changed, which contradictions opened
and closed. The diff is the scientific history of the interval, and it is the only comparison the
surface offers between two snapshots.

## 7.10 The Living Scientific Model as a projection

**Rule R7-32.** `science/11_LIVING_SCIENTIFIC_MODEL.md` becomes a generated artifact under
`ros.projections.GENERATED_DIR` with `_GENERATED_BANNER`, rendered by
`lske.render.render_living_model`. Its twelve sections are the output contract; each maps to a
projection:

| LSM section | Rendered from |
|---|---|
| 1 Present scientific position | `ScientificState` levels by count |
| 2 Most reliable current findings | claims by `eligible_level` desc, with `EvidenceTrace` weakest link |
| 3 Current hypothesis state | `hypotheses` grouped by status |
| 4 Mechanism state | `mechanisms` with `ConfidenceProfile` mechanism dimension |
| 5 Critical assumptions | `assumptions` ordered by dependent count |
| 6 Highest-priority unknowns | `rank_hypotheses` over `unknowns` (R5-9) |
| 7 Scientific debt blocking claims | `scientific_debt` by `severity` and blocked target |
| 8 Negative knowledge retained | `negative_results` + `ACTIVE` refuted claims (R3-4) |
| 9 Theory status | `theories` against the level-5 eligibility table |
| 10 Smallest experiment | `recommend_experiments().smallest_uncertainty_reduction` |
| 11 Current scientific conclusion | **human-authored section, preserved verbatim** |
| 12 Change log | `snapshots` in order, with `cause` |

**Rule R7-33.** Section 11 is the one hand-authored block. The renderer preserves it between markers
and never generates it. Everything above it is derived; the conclusion is a scientific judgement, and
`ros.authority` reserves judgement to humans.

**Rule R7-34.** Drift between the generated LSM and the store is detected by `ros.projections.drift`
and blocks the `projection_drift` gate. Hand-editing a generated section is drift, and drift blocks
a gate — which is the mechanism that stops the model and the store from telling two stories.

## 7.11 Vocabulary compliance

**Rule R7-35.** No plate name, overlay key, payload field, node attribute, control label, tooltip or
legend entry uses a term frozen by Art. L-4: *energy, attention, thought, understanding, belief,
curiosity, dream, emotion, intention, consciousness*.

**Rule R7-36.** Plate `V14` is referenced by identifier throughout the LSKE. Its LSKE-facing
description is **"routing allocation over inputs"**, and its payload fields are named for what is
measured — `allocation_share`, `selected_input_ids`, `allocation_event_ids`. The Observatory
specification's own prose name for the plate is left untouched, since the LSKE does not amend the
Observatory; what the LSKE controls is every field, key and result label it emits, and none of those
carry the banned term.

**Rule R7-37.** Vocabulary compliance of render payloads is checked by the existing `vocabulary` gate
extended over `lske.render` field names, so a banned term added later fails CI rather than review.

---

# PART 8 — LSKE Constitution

This part adds no authority. It states the invariants the LSKE must hold, and for each one names the
rule that enforces it and the check that detects violation. An invariant with no detector is an
intention, and this part contains none.

**Rule R8-0.** Every invariant below is subordinate to `P1_V2_CONSTITUTION_LOCK_v1.0.md`. Where a
reading of this part would conflict with Articles L-1…L-12, the Lock governs and this part is
defective. Amendment of the Lock is `constitution.amendment`, which `ros.authority` places in
`EVIDENCE_TARGETS` and `escalation_for` routes to `primitive_admission`.

## 8.1 Truth preservation

| # | Invariant | Enforced by | Detected by |
|---|---|---|---|
| I-1 | Nothing recorded is ever destroyed; records become non-current | R3-1, R3-3 | `MEM-01`, `store_integrity` |
| I-2 | No reference ever dangles, including into deleted records | R3-3 stub | `ros.store._check_references` |
| I-3 | A superseded record keeps its original semantics forever | R3-3 cl. 2, R7-16 | `MEM-04` |
| I-4 | Every state was reached by a recorded event | R1-4 | `MEM-02`, `lifecycle` events |
| I-5 | A displayed change without a resolvable cause is marked unattributed | R7-4 | render payload assertion |
| I-6 | Reconstructed history verifies by hash or fails loudly | R3-7, R7-29 | `SnapshotIntegrityError` |

**I-1 rationale.** The store is the only writable scientific artifact in the program (kernel invariant
K1). A deletion in it is not a lost row; it is a lost finding, and the audit's negative results are
the most valuable holdings the program currently has.

## 8.2 Evidence preservation

| # | Invariant | Enforced by | Detected by |
|---|---|---|---|
| I-7 | Evidence is never silently inherited by a successor claim | R3-3 cl. 4 | `MEM-05` |
| I-8 | `supports`/`refutes` originate only from `evidence`/`negative_results` | R2-6 | `_gate_relation_integrity` |
| I-9 | Every evidence record names the alternatives it fails to exclude | R1-16 | `store_integrity` error |
| I-10 | Shared-evidence dependence is never counted as independent replication | R1-17, R4-17 | `detect_contradictions` |
| I-11 | Refuted claims remain `ACTIVE` and remain in `ScientificState` | R3-4 | `MEM-06` |
| I-12 | A null result is neither weak support nor opposition | R4-4 | `profile` unit test |
| I-13 | Missingness is a complete observation, not an absent one | R1-13, R7-12 | schema validation |

**I-9 rationale.** `ros.authority.HUMAN_ONLY` names `alternative_explanations` with the reason that
"enumerating candidates is mechanical, judging exclusion is not." An agent may fill `statement`; only
a human may commit `why_not_excluded`. An evidence record without that field is evidence whose
strength nobody has bounded.

## 8.3 Scientific integrity

| # | Invariant | Enforced by | Detected by |
|---|---|---|---|
| I-14 | Confidence is a ten-dimensional lattice, never a scalar | R4-3, R7-10 | schema: no numeric confidence field |
| I-15 | Confidence changes only from an accepted evidence record | R4-1 | decision-log replay test |
| I-16 | The learning engine is a pure function of the store | R4-2 | byte-identical determinism test (R9-5) |
| I-17 | No model is fitted, no parameter estimated, no threshold optimized | §4.1 | code review + dependency assertion |
| I-18 | Support crosses exactly one edge; `extends` inherits nothing | R4-9, R4-10 | `profile` unit tests |
| I-19 | Contradictions accumulate and never cancel | R4-11 | `lske_open_contradictions` metric |
| I-20 | Hypothesis ranking is lexicographic over recorded keys, not scored | R5-9 | `rank_hypotheses` determinism test |
| I-21 | No aggregation across incommensurable units; there is no `AVG` | R5-18 | `QueryError` on unit mismatch |
| I-22 | Every reasoning result names its basis and store hash | R5-1 | dataclass field required |
| I-23 | Clustering is by recorded relation, never computed similarity | R7-8 | render payload assertion |
| I-24 | Animation interpolates position only | R7-21, R7-22 | render contract test |

**I-16 rationale.** A confidence engine that could return two answers for one store hash would make
every citation unverifiable, because the reader could not reproduce what the citer saw. The
determinism test is therefore not a quality measure; it is the precondition for citation.

## 8.4 Authority boundaries

| # | Invariant | Enforced by | Detected by |
|---|---|---|---|
| I-25 | Every write calls `ros.authority.require` and fails closed | §6.8 | write-path test per API |
| I-26 | Unregistered write targets are refused by default | `ros.authority.refusal` | existing behaviour |
| I-27 | No agent authority class can reach a runtime lever | `AGENT_FORBIDDEN` order | `ros.authority` unit test |
| I-28 | Reasoning and confidence modules hold `OBSERVER` and expose no setter | R5-2, R6-3 | absence of write functions |
| I-29 | SQL-P1 cannot express a write; a write attempt is a parse error | R5-17, R6-6 | grammar + `QueryError` test |
| I-30 | No LSKE module is importable from the runtime tree, or vice versa | R1-7, R6-2 | import-graph CI assertion |
| I-31 | Impact analysis runs against a shadow store as `OBSERVER` | R5-13 | `analyse_impact` test |
| I-32 | The Observatory writes no model state, memory, threshold, seed or config | Art. L-8, R7-24 | `AGENT_FORBIDDEN` + R6-2 |

**I-30 rationale.** Art. L-8's separation is the single invariant most easily lost by an ordinary,
well-intentioned refactor: a runtime module importing `ros.store` "just to log a claim" makes Tier E
a runtime input and ends the program's evidential standing. A convention cannot stop that; an
import-graph assertion in CI can.

## 8.5 Human decision boundaries

| # | Invariant | Enforced by | Detected by |
|---|---|---|---|
| I-33 | `decisions` records are `is_human = true`, `write_target = skb.decision`, always | R1-18 | write check + `store_integrity` |
| I-34 | `ingest` has no code path to `skb.decision` | R6-4 | API shape + test |
| I-35 | `HUMAN_REQUIRED` is frozen at exactly one phase | R6-5 | cardinality test |
| I-36 | Claim status and level are human writes under `skb.claim_status` | R1-3, R6-8 | `require` refusal |
| I-37 | Automatic promotion never occurs; the queue is a health metric | R4-20 | `lske_level_gap_total` |
| I-38 | Invalidation changes eligibility, never status, decision or level | R4-14 | `learn` unit test |
| I-39 | Claim scope is human-only; no measurement sets its own generalisation | `HUMAN_ONLY` | `require` refusal |
| I-40 | LSM section 11 is preserved verbatim and never generated | R7-33 | renderer test |
| I-41 | Protocol freeze is human-only; drafting is not freezing | R1-10 | `require` refusal |

**I-35 rationale.** `ros.authority` states the design target as a number: a complete research cycle
has fourteen steps, four require human judgement, and "reducing the count below four is not an
efficiency win, it is a governance breach." The LSKE's transaction touches one of those four. Widening
`AGENT_COMPLETABLE` by one member would automate the scientific decision, which is the exact failure
the audit's remaining scientific decision 5 forbids: "All experiment outcome Decisions; engineering
must not automate them."

## 8.6 Admissibility

| # | Invariant | Enforced by | Detected by |
|---|---|---|---|
| I-42 | Admissibility comes only from `ros.admissibility.assess` | R1-11 | re-derivation at integrity |
| I-43 | A verdict is reproducible from manifest digest + event log | R1-12 | `store_integrity` error |
| I-44 | D2 runs are mechanically refused as confirmatory evidence | R1-9, R2-8 | write refusal + gate |
| I-45 | `validated_by` is refused to a run below the claimed tier | R2-8 | `_gate_relation_integrity` |
| I-46 | Level 4 requires ≥2 independence groups (E24) | §4.3 table | `eligible_level` test |
| I-47 | Level 5 requires a pre-run `predicts` edge; later edges are `post_hoc` | R2-12 | edge timestamp check |
| I-48 | Legacy or unrecoverable provenance caps claims at level ≤ 1 | R1-14 | ceiling computation |
| I-49 | Ineligible nodes stay visible in traces, marked ineligible | R5-4 | `trace_evidence` test |
| I-50 | Every generated artifact carries the governance banner while unregistered | R0-3, R7-27 | `projection_drift` gate |

**I-43 rationale.** Audit finding 4 records that ROS admissibility is currently constructed from
caller flags rather than run artifacts, and blocker 3 is the missing manifest bridge. A verdict that
originates in a flag is a verdict the caller chose. Re-deriving it from `manifest_digest` and
`event_log_path` at integrity time is what turns it back into a measurement.

## 8.7 Knowledge immutability

| # | Invariant | Enforced by | Detected by |
|---|---|---|---|
| I-51 | The write algebra has exactly five operations | R3-2 | `lske.transaction` API surface |
| I-52 | There is no `DELETE` operation | R3-3 | absence of the function |
| I-53 | `AMEND` on a sealed record is refused | R3-1 | write refusal test |
| I-54 | `ANNOTATE` is the only write permitted on a `TOMBSTONED` record | R3-2 | write refusal test |
| I-55 | Correction of a sealed record is by linked supersession only | R1-5 | `_check_supersession` |
| I-56 | `content_hash` covers blocks A–G and excludes H | R1 §1.1 | hash recomputation test |
| I-57 | Lifecycle states and transitions are the frozen L-2 sets | R1 Block G | vocabulary gate |
| I-58 | Edges use the L-2 subset without `TOMBSTONED` | R2-4 | `_check_relations` |
| I-59 | A relation is addressed by the triple `(source, kind, target)` | R2-1 | duplicate warning |
| I-60 | No stored derived quantity anywhere; projections only | R0-4, Art. L-7 | schema review + drift gate |

**I-52 rationale.** A store with a delete operation eventually has a deleted record, and the first
question asked of any surviving claim becomes "what was removed?" — a question the store can no
longer answer about itself. `DELETED` as a lifecycle state answers it permanently. Physical removal
remains possible for legal or credential reasons, requires a `decisions` record plus a
`governance.registry` write, and leaves a stub retaining `id`, `content_hash` and the deleting
decision, so every reference still resolves.

## 8.8 What this part does not do

**Rule R8-1.** This part creates no new authority class, no new write target, no new human-only
decision and no new primitive. Every boundary cited above already exists in
`P1_V2_CONSTITUTION_LOCK_v1.0.md`, `ros.authority`, `ros.admissibility` or the Observatory
specification. The LSKE's contribution is to make each one **detectable at a named site**.

**Rule R8-2.** No invariant in this part may be relaxed to make an implementation pass. A failing
invariant is either a defect in the implementation or a case for a Constitutional Change Request. It
is never a case for editing the invariant, and Art. L-9 lists the reasons that are not evidence:
elegance, biological precedent, engineering convenience, visual appeal, implementation momentum.

---

# PART 9 — Implementation Contract

This part is addressed to the engineering model or engineer who builds the LSKE. It is written so
that **no architectural decision remains**. Where a choice existed, it has been made here and the
reason is stated. Where a choice is genuinely open (variable names inside a function body, the
internal shape of a private helper, log phrasing), that is stated too, so the boundary between
"frozen" and "your call" is never guessed.

**Rule R9-0.** If the implementer finds an underspecified point, the resolution is **not** to choose.
It is to raise a Constitutional Change Request via `constitution-clerk` against this document, which
is then amended and re-issued at v1.1.0. An implementer's silent choice becomes an architectural fact
nobody decided, which is the class of defect this part exists to prevent.

## 9.1 Frozen file layout

Every path below is frozen. No file is created outside this list; no listed file is omitted.

| Path | Kind | Contents |
|---|---|---|
| `ros/model.py` | modify | `COLLECTIONS` 11 → 20; docstring count corrected (R1-6) |
| `ros/store.py` | modify | add `_check_memory` implementing `MEM-01`…`MEM-06` |
| `ros/propagation.py` | modify | unchanged `audit`; add nothing (execution lives in `lske`) |
| `ros/gates.py` | modify | add the three gates of §6.7 to the gate tuple |
| `ros/kpi.py` | modify | add the four metrics of §6.7 |
| `ros/projections.py` | modify | expose `render_target(path)` for the LSM renderer |
| `lske/__init__.py` | new | version constant, no logic |
| `lske/schema.py` | new | the JSON Schemas of §9.2, as module-level dicts |
| `lske/confidence.py` | new | Part 4; pure functions only |
| `lske/reasoning.py` | new | Part 5 |
| `lske/memory.py` | new | Part 3 |
| `lske/transaction.py` | new | the nine-phase transaction |
| `lske/query.py` | new | SQL-P1 parser and evaluator |
| `lske/render.py` | new | Part 7 payloads and the LSM renderer |
| `lske/errors.py` | new | the error taxonomy of §9.5 |
| `schemas/lske/record.schema.json` | new | the universal envelope |
| `schemas/lske/<collection>.schema.json` | new | 20 files, one per collection |
| `schemas/lske/relation.schema.json` | new | the relation envelope |
| `schemas/lske/obs2.schema.json` | new | the `RenderPayload` contract |
| `tests/lske/` | new | the test matrix of §9.6 |
| `docs/ros/generated/living_scientific_model.md` | generated | R7-32 |

**Rule R9-1.** `lske/` contains no `__main__`, no CLI, no HTTP server and no network client. The CLI
surface is `ros`, extended with subcommands in a later change that is out of this document's scope.
An LSKE that can serve requests is an LSKE that can be written to by something the authority model
never saw.

**Rule R9-2.** `lske.schema` holds the schemas as Python dicts and `schemas/lske/*.json` holds them
as files, generated from the dicts by a test that fails on divergence. Two hand-maintained copies of
one schema drift; one generated from the other cannot.

## 9.2 Schema contract

### 9.2.1 The universal envelope

`schemas/lske/record.schema.json` — every record in every collection validates against this before
its collection-specific schema is applied. Draft 2020-12. `additionalProperties: false` at the top
level; collection schemas extend by `allOf`.

| Field | Type | Req | Constraint |
|---|---|---|---|
| `id` | string | yes | `^[A-Z]{3,5}-\d{4}-\d{4}$`; prefix must equal the collection's `prefix` |
| `type` | string | yes | equals the collection's `object_type` |
| `primitive` | string | yes | enum of the 19 Lock primitives (R0-1) |
| `title` | string | yes | non-empty; no L-4 term (R7-35) |
| `record_version` | integer | yes | ≥ 1; increments on `AMEND` only |
| `ontology_version` | string | yes | `^\d+\.\d+\.\d+$` |
| `content_hash` | string | yes | `^[0-9a-f]{64}$`; SHA-256 over blocks A–G, H excluded |
| `created` | object | yes | `{at, by, is_human, decision_id?}` |
| `revisions` | array | yes | append-only; may be empty; item schema below |
| `supersedes` | string\|null | yes | record id or null |
| `superseded_by` | string\|null | yes | record id or null |
| `provenance` | object | yes | `{kind, source_ids, manifest_digest?, document_path?, note}` |
| `write_target` | string | yes | enum of `EVIDENCE_TARGETS ∪ ENGINEERING_TARGETS` |
| `committed_by` | string | yes | actor name |
| `is_human` | boolean | yes | `false` with an `EVIDENCE_TARGETS` write_target is invalid (R1-2) |
| `escalated_from` | string\|null | yes | actor name or null |
| `confidence` | object\|null | yes | null only where the collection's `confidence` column is `no` |
| `lifecycle` | object | yes | `{state, entered_at, event_id, history[]}` |
| `append_only` | boolean | yes | equals the collection's `append_only` |
| `frozen_at` | string\|null | yes | ISO-8601 or null |
| `seal` | string\|null | yes | `^[0-9a-f]{64}$` or null; non-null implies `frozen_at` non-null |

`revisions[]` item: `{at, by, is_human, change_kind, prior_content_hash, decision_id|null, note}` —
`change_kind` enum `{create, amend, annotate, status_transition, supersede, tombstone, restore,
delete}`.

`confidence` object: `{level: integer 0..5|null, scope: string, dimensions: object}` where
`dimensions` has exactly the ten `DIMENSIONS` keys, each
`{state: DimensionState, evidence_ids: array<string>}`. No numeric field exists anywhere under
`confidence` other than `level` (R1-3, I-14).

`lifecycle` object: `state` enum `{CANDIDATE, ACTIVE, DORMANT, TOMBSTONED, DELETED}`;
`history[]` item `{from, to, at, event_id, decision_id|null}`.

**Rule R9-3.** `content_hash` is computed over the canonical JSON serialization of blocks A–G:
`json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")`,
SHA-256 hex. Block H is excluded because sealing changes H, and a hash that changed on sealing could
never verify a sealed record against its pre-seal content. This is the same canonicalization
`ros.protocol.canonical_bytes` already uses; the implementer reuses that function rather than
re-deriving it.

### 9.2.2 Collection schemas

Twenty files, `schemas/lske/<collection_key>.schema.json`, each `allOf: [record.schema.json, {…}]`.
The per-collection required fields are exactly those tabulated in §1.4; this section adds the typing
that §1.4 stated in prose.

| Collection | Additional required | Notable constraints |
|---|---|---|
| `research_questions` | `question`, `gate`, `open` | `gate` enum `G1..G5` (L-10) |
| `hypotheses` | `statement`, `status`, `falsifier`, `sesoi` | `status` ∈ `HYPOTHESIS_STATUSES`; `Validated` requires `confidence.level ≥ 4` (R1-8) |
| `protocols` | `path`, `digest`, `frozen_before_run`, `rigor_intent` | `digest` 64-hex; `rigor_intent` ∈ `{exploratory, confirmatory}`; freeze human-only (R1-10) |
| `experiments` | `program_id`, `gate`, `status`, `validity`, `protocol_id` | gate order enforced (R1-23) |
| `runs` | `run_id`, `manifest_path`, `manifest_digest`, `event_log_path`, `determinism`, `admissibility` | `determinism` ∈ `{D0, D1, D2}`; confirmatory + D2 refused at write (R1-9); `admissibility` re-derived (R1-11, R1-12) |
| `observations` | `metric_id`, `value`, `validity`, `coverage`, `run_ids` | `value: number\|null`; null requires `validity = unavailable` and `coverage.missing_reason` (R1-13) |
| `metrics` | `units`, `direction`, `formula`, `estimator_version`, `aggregation`, `declared_null` | `direction` ∈ `{higher_is_better, lower_is_better, none}` |
| `datasets` | `identity`, `digest`, `provenance_reliability` | `provenance_reliability ∈ {verified, legacy_uncertain, unrecoverable}`; latter two cap level ≤ 1 (R1-14) |
| `artifacts` | `path`, `digest`, `retention`, `produced_by_run` | `retention = evidence_bearing` ⇒ undeletable while cited (R1-15) |
| `evidence` | `direction`, `target_id`, `measurement_ids`, `run_ids`, `rationale`, `unexcluded_alternatives`, `independence_group` | `direction` ∈ `EVIDENCE_DIRECTIONS`; `unexcluded_alternatives[].why_not_excluded` human-written (R1-16) |
| `decisions` | `action`, `subject_ids`, `rationale`, `evidence_ids` | `action` ∈ `DECISION_ACTIONS`; `is_human = true`, `write_target = "skb.decision"`, no exception (R1-18) |
| `mechanisms` | `statement`, `status` | never `Validated` without a mechanism-dimension assessment |
| `theories` | `statement`, `constituent_ids` | capped by weakest constituent (R4-19) |
| `assumptions` | `statement`, `relied_upon_by` | |
| `unknowns` | `statement`, `blocking` | acquiring evidence forces a transition (R1-20) |
| `scientific_debt` | `statement`, `severity`, `blocks` | `severity` is evidence-bearing (R1-21) |
| `negative_results` | `statement`, `sesoi`, `retry_prohibited`, `evidence_ids` | changed `sesoi` refused (R1-22) |
| `programs` | `name`, `gates`, `status` | |
| `sessions` | `actor`, `started_at`, `ended_at`, `intent` | `primitive = Intervention` |
| `snapshots` | `snapshot_id`, `store_content_hash`, `at`, `cause`, `caused_by` | coordinates only, never state (R0-4, R1-25) |

### 9.2.3 The relation envelope

`schemas/lske/relation.schema.json`. Required: `from`, `to`, `type`, `direction`, `semantic_note`
(non-empty), `established_by`, `established_at`, `record_version_at`
(`{source: integer, target: integer}`), `confidence_basis` ∈ `{evidence, human_assertion,
structural}`. Optional: `retracted_by`, `independence_group`, `post_hoc` (boolean, default `false`).
`type` enum is exactly the fifteen of §2.3. **No numeric confidence field is permitted** (R2-5); the
schema enforces this by `additionalProperties: false`, which is the reason that flag is set rather
than a stylistic preference.

**Rule R9-4.** `direction` is stored even though it is derivable from `type`, because the store's
existing `Relation` dataclass reads it and Art. L-7 forbids only stored *derived scientific
quantities*, not the restatement of an addressing field a reader already depends on. This is the one
place in the LSKE where redundancy is permitted, and it is permitted here and nowhere else.

## 9.3 Transaction specification

The nine-phase transaction of §6.4 is the only writer of scientific state. This section fixes its
mechanics completely.

### 9.3.1 Storage

Receipts live in `.ros/receipts/<receipt_id>.json`, one file per receipt, never rewritten in place
except by the two documented appends (`commit_decision`, `propagate`), each of which writes a new
temporary file and renames it over the old — atomic on POSIX, and the rename is the commit point.
`receipt_id` has the form `RCPT-<run_id>-<n>` where `n` is the count of prior receipts for that run,
zero-padded to three digits. Receipt ids are not SKB record ids and carry no `PREFIX-YYYY-NNNN` form,
deliberately: a receipt is engineering bookkeeping, not a scientific record, and giving it a record id
would make it appear in `iter_id_references` as a dangling reference.

### 9.3.2 Phase order and halting

Phases execute in the declared `Phase` order, 1 through 9. Execution halts at the first phase whose
outcome state is `awaiting_human` or `refused`, and `Receipt.halted_at` records it. Phases after a
halt are absent from `outcomes` — not present with a placeholder state. An absent phase is
distinguishable from a completed one; a placeholder is not.

| # | Phase | Writer | Target | Halt condition |
|---|---|---|---|---|
| 1 | `EXECUTION_VALIDITY` | `ingest` | `skb.observation_draft` | run not admissible for the declared intent → `refused` |
| 2 | `OBSERVATIONS` | `ingest` | `skb.observation_draft` | metric undeclared → `refused` |
| 3 | `EVIDENCE_RELATIONS` | `ingest` | `skb.observation_draft` | no target claim → `refused` |
| 4 | `INTERPRETATION` | `ingest` | `skb.observation_draft` | never halts; drafts `unexcluded_alternatives[].statement` only |
| 5 | `DECISION` | `commit_decision` | `skb.decision` | always `awaiting_human` under `ingest` |
| 6 | `DEPENDENT_STATUS` | `propagate` | `skb.claim_status` | non-human actor → `refused` |
| 7 | `ASSUMPTIONS_UNKNOWNS_DEBT` | `propagate` | `skb.observation_draft` | — |
| 8 | `ROADMAP` | `propagate` | `repo.doc` | — |
| 9 | `LIVING_MODEL` | `propagate` | `projection.render` | drift unresolvable → `refused` |

**Rule R9-5** *(the determinism test, forward-referenced by R4-2 and I-16)*.
`tests/lske/test_determinism.py` must contain a test that loads a fixture store, calls
`lske.confidence.learn` twice, serializes both `LearningReport`s with the canonicalization of R9-3,
and asserts the two byte strings are equal; a second test asserts the same for
`lske.reasoning.rank_hypotheses`, `detect_contradictions`, `analyse_gaps` and
`recommend_experiments`; a third asserts that shuffling the record order in the fixture YAML changes
neither result. The third test is the one that matters: it is what catches an implementation that
happened to iterate a dict in insertion order and appeared deterministic within a process.

**Rule R9-6** *(the gate tests, forward-referenced by R6-7)*. Each of the three new gates
(`_gate_lske_transaction`, `_gate_confidence_support`, `_gate_relation_integrity`) must have a test
that constructs a store containing exactly one violation of that gate and asserts
`GateResult.blocked is True` and that the finding names the violating record id; and a companion test
on a clean store asserting the gate passes. A gate with only a passing test is audit finding 14
repeated inside the subsystem built to close it.

### 9.3.3 Suspension and resumption

Between phase 4 and phase 5 the transaction is **suspended, not failed**. The receipt is on disk with
`halted_at = Phase.DECISION` and `awaiting_human is True`. It remains valid indefinitely. Resumption
is `commit_decision(actor, root, receipt_id, decision)`, which:

1. Re-reads the store and compares `Store.content_hash()` to `receipt.store_hash_after`.
2. On mismatch, raises `TransactionRefused` naming both hashes. The decision was formed against a
   state that no longer exists, and committing it would attach a human judgement to evidence the human
   did not see. The remedy is a fresh `ingest`, not a force flag; there is no force flag.
3. Calls `ros.authority.require(actor, "skb.decision")`, which refuses any non-human actor.
4. Validates `decision` against `decisions.schema.json`.
5. Writes the record, emits an `evidence`-tier event, and appends a `PhaseOutcome` for phase 5.

`propagate` performs the same hash check against the post-decision hash and requires
`skb.claim_status`, human. Phases 6–9 are one unit: either all four append outcomes or the receipt
records the halt and the store is unchanged for the phases not reached.

### 9.3.4 Failure, rollback and idempotency

There is no multi-record rollback, and none is needed, because of how the store is written: a phase
that writes assembles its records in memory, validates all of them, and then performs a single
write of `science/SKB_RECORDS_v1.0.yaml` via temp-file-plus-rename. A phase either wrote or did not.
A crash between two phases leaves a receipt whose `outcomes` end at the last completed phase, and
re-invoking the same entry point with the same `receipt_id` resumes from there.

**Rule R9-7.** Idempotency key is `(receipt_id, phase)`. Re-running a completed phase is a no-op that
returns the existing `PhaseOutcome` unchanged; it does not re-write, re-hash or re-emit. An
implementation that re-emits an event on retry would inflate the event log, and the event log is the
sole evidence that a lifecycle state was legitimately reached (I-4).

**Rule R9-8.** `TransactionRefused` is raised, never returned as a state, for: store hash mismatch,
authority refusal, schema violation, and gate-blocking violation detected mid-phase. `refused`
appears as a `PhaseOutcome.state` only for the scientific refusals tabulated in §9.3.2 — an
inadmissible run, an undeclared metric, a missing target claim, unresolvable drift. The distinction is
load-bearing: a scientific refusal is a recorded finding about the experiment, and an exception is a
statement that the transaction could not be evaluated at all.

## 9.4 ROS extension mechanics

### 9.4.1 `ros.model`

`COLLECTIONS` grows from 11 to 20 entries, in the §1.2 order, with `append_only` set exactly as that
table's column states. The docstring "The thirteen top-level SKB collections" becomes "The twenty
top-level SKB collections" **in the same commit** (R1-6) — a count comment that disagrees with the
tuple beneath it is how a reader learns not to trust comments in this repository.

`COLLECTION_BY_PREFIX` gains nine keys. No existing prefix changes. `ID_PATTERN` is unchanged and
already admits all nine new prefixes, including the five-character `SDEBT`; the implementer verifies
this with a test rather than by inspection, because `DSET` and `SNAP` are new four-character prefixes
and a regression there would silently stop reference discovery for two collections.

`NON_RECORD_KEYS` is unchanged.

### 9.4.2 `ros.store`

`Store.check()` gains a seventh composed check, `_check_memory`, returning `MEM-01`…`MEM-06` as
`Finding`s at severity `error`. Placement is after `_check_supersession` so that supersession findings
appear before the memory findings that depend on the same structures. The six checks:

| Code | Detects |
|---|---|
| `MEM-01` | a record present in a prior snapshot's manifest and absent now without a `DELETED` stub |
| `MEM-02` | a lifecycle state with no resolvable `event_id` in `.ros/events.jsonl` |
| `MEM-03` | a `revisions[]` entry whose `prior_content_hash` does not match the preceding entry |
| `MEM-04` | a record whose `ontology_version` was rewritten without a C-d mapping entry |
| `MEM-05` | a superseding record citing evidence held only by its predecessor |
| `MEM-06` | a claim with a `refutes` edge whose lifecycle state is not `ACTIVE` |

`Record` gains read-only properties `lifecycle_state`, `record_version` and `confidence_level`, each
returning `None` when the field is absent, so that legacy records that predate the envelope do not
raise. `Store` gains `relations_for(record_id)` and `snapshots()`. No method on `Store` writes; the
module's closing docstring sentence — "This module performs validation only. It never writes" —
remains true after the change, and a test asserts the module contains no `open(..., "w")`.

### 9.4.3 `ros.gates` and `ros.kpi`

Three gates appended to the gate tuple, after `_gate_store_integrity` and before
`_gate_projection_drift`, since a relation-integrity failure makes drift meaningless. Four metrics
appended to `ros.kpi.compute`: `lske_open_contradictions` (target 0, status from `_status_of`),
`lske_level_gap_total` (target 0), `lske_falsifier_coverage` (target 100 %), and
`lske_outstanding_receipts` (target 0). All four are computed from the store, never cached.

## 9.5 Error taxonomy

`lske/errors.py`, frozen. Every raise site in `lske/` uses one of these; no bare `ValueError`,
`RuntimeError` or `AssertionError` escapes the package.

| Exception | Base | Raised when |
|---|---|---|
| `LskeError` | `Exception` | never raised directly; the package root |
| `SchemaViolation` | `LskeError`, `ValueError` | a record fails its schema |
| `TransactionRefused` | `LskeError`, `RuntimeError` | §9.3.4 |
| `SnapshotIntegrityError` | `LskeError`, `RuntimeError` | reconstruction hash mismatch (R3-7) |
| `QueryError` | `LskeError`, `ValueError` | SQL-P1 parse or evaluation failure, including a write attempt (R5-17) |
| `OntologyError` | `LskeError`, `ValueError` | a record declares a `primitive` outside the 19 (R0-1) |
| `RelationError` | `LskeError`, `ValueError` | a prohibited relation shape (§2.5) |

`ros.authority.AuthorityError` is **not** re-wrapped. An authority refusal must surface as the
authority module's own exception type, so that a grep for `AuthorityError` finds every governance
refusal in the codebase without needing to know that `lske` exists.

**Rule R9-9.** No exception message contains a measured value, a metric magnitude or a p-value. Error
text names records and fields. A value in an exception string is a scientific result delivered through
a channel with no provenance, no units and no validity status.

## 9.6 Test matrix

The implementation is complete when every row passes. Rows are not optional and none is satisfiable by
a mock: each requires a constructed store.

| # | Test file | Asserts |
|---|---|---|
| 1 | `test_schema_generation.py` | `schemas/lske/*.json` byte-match the dicts in `lske.schema` (R9-2) |
| 2 | `test_envelope.py` | all eight blocks required; `content_hash` excludes block H (R9-3) |
| 3 | `test_collections.py` | 20 collections; prefixes unique; `ID_PATTERN` matches all 20 |
| 4 | `test_authority_binding.py` | every write path in `lske/` calls `require` before writing; `EVIDENCE_TARGETS` + non-human refused (I-25) |
| 5 | `test_import_graph.py` | no `lske.*` module imports the runtime tree; no runtime module imports `ros.*` or `lske.*` (R6-2, I-30) |
| 6 | `test_no_setters.py` | `lske.confidence` exposes no callable whose name starts with `set_`/`update_`/`assess_` (R6-3) |
| 7 | `test_determinism.py` | R9-5, all three cases |
| 8 | `test_gates.py` | R9-6, six cases (three blocking, three clean) |
| 9 | `test_memory_checks.py` | `MEM-01`…`MEM-06` each fire on one constructed violation |
| 10 | `test_no_delete.py` | no function in `lske/` deletes a record; `DELETED` reachable only as a lifecycle state (R3-3, I-52) |
| 11 | `test_lattice.py` | resolution of the ten dimensions per R4-4, including `null` counted as present-but-neither |
| 12 | `test_ceilings.py` | four ceilings applied by `min`; legacy provenance caps at 1 (R4-6, R1-14) |
| 13 | `test_no_transitive_support.py` | support crossing two edges does not propagate (R4-9, I-18) |
| 14 | `test_contradiction_accumulation.py` | opposing evidence does not cancel (R4-11, I-19) |
| 15 | `test_query_readonly.py` | every write-shaped input raises `QueryError` at parse time (R5-17) |
| 16 | `test_query_grammar.py` | the seven reference queries of §5.9 parse and execute; no `AVG` token exists |
| 17 | `test_render_payload.py` | `obs/2` carries `phase`, `subject`, `cause`; unresolvable cause becomes `"unattributed"` (R7-4) |
| 18 | `test_vocabulary.py` | no L-4 term in any payload field, node attribute or plate name emitted by `lske.render` (R7-35, R7-37) |
| 19 | `test_lsm_section_11.py` | the human-authored section survives regeneration byte-for-byte (R7-33, I-40) |
| 20 | `test_transaction_boundary.py` | `ingest` cannot reach `skb.decision` under any input (R6-4, I-34) |
| 21 | `test_transaction_hash_guard.py` | a store mutated between `ingest` and `commit_decision` raises `TransactionRefused` |
| 22 | `test_idempotency.py` | re-running a completed phase writes nothing and emits nothing (R9-7) |
| 23 | `test_end_to_end.py` | **blocker 5 closure**, specified in §9.7 |

## 9.7 Blocker 5 closure test

`tests/lske/test_end_to_end.py` is the artifact the ZERO UNKNOWN report asks for: *"End-to-end run →
Evidence → Decision → SKB → LSM test with human Decision boundary preserved."* Its shape is frozen.

1. **Fixture.** A temporary root with a frozen protocol YAML under the guarded path, a run manifest
   binding protocol path, digest, `rigor_intent = exploratory`, `determinism = D1` and claim scope; an
   event log; one artifact with a digest. No network, no runtime execution — the run's outputs are
   fixture files, because the LSKE's contract is with the artifacts, not with the engine that made them.
2. **Ingest.** `transaction.ingest(engineer, root, run_id)` returns a receipt with phases 1–4
   `completed` and `halted_at = Phase.DECISION`. Assert `awaiting_human is True`, and assert the store
   now contains a `runs` record, at least one `observations` record and one `evidence` record, and
   **zero** `decisions` records.
3. **The boundary.** Call `transaction.commit_decision` with a **non-human** actor at `SCIENTIST`
   authority and assert `AuthorityError`. Then with a human at `ENGINEER` and assert `AuthorityError`.
   Only a human at `SCIENTIST` proceeds. These two negative assertions are the test; the positive path
   alone would pass against an implementation with no boundary at all.
4. **Decision.** Commit a human decision with `action = "reject"` and a rationale citing the evidence
   id. Assert the receipt now shows phase 5 `completed`.
5. **Propagate.** `transaction.propagate(scientist_human, root, receipt_id)` completes phases 6–9.
   Assert the target hypothesis' status changed, that its `confidence.level` was written under
   `skb.claim_status`, and that `ros.propagation.audit(store, experiment_id).complete is True` — the
   pre-existing auditor, unmodified, agreeing that all nine obligations are discharged.
6. **Projection.** Assert `docs/ros/generated/living_scientific_model.md` regenerates with the new
   state and that `ros.gates` reports `projection_drift` not blocked.
7. **Immutability.** Assert every record written carries a resolvable `event_id`, that no record was
   overwritten (every `content_hash` in `revisions` chains), and that `Store.check()` returns no
   `error` findings.

**Rule R9-10.** This test does not permit a `--force`, a fixture flag that skips the authority check,
or a monkeypatch of `ros.authority.require`. A test that patches out the boundary is evidence that the
boundary is patchable, which is the opposite of what it was written to demonstrate.

## 9.8 Build order and migration

Nine stages. Each stage ends with the full gate suite passing, so that a partial LSKE never leaves the
repository in a state where the existing store is unreadable.

| Stage | Deliverable | Exit condition |
|---|---|---|
| 1 | `lske.schema` + `schemas/lske/*` + the envelope | tests 1–3 pass; **no** change to `ros.model` yet |
| 2 | `ros.model` 11 → 20, docstring fixed | existing store still loads; test 3 passes |
| 3 | Migration of existing records to the envelope | §9.8.1; `Store.check()` clean |
| 4 | `ros.store._check_memory` | tests 9–10 pass |
| 5 | `lske.confidence` | tests 6, 7, 11–14 pass |
| 6 | `lske.reasoning` + `lske.memory` | determinism holds across all five reasoning functions |
| 7 | `lske.query` | tests 15–16 pass |
| 8 | `lske.transaction` + the three gates + four KPIs | tests 4, 8, 20–22 pass |
| 9 | `lske.render` + the LSM renderer | tests 17–19 pass, then test 23 |

Stage 3 before stage 5 is not negotiable: computing confidence over records that lack the envelope
would require a default, and a default confidence state is a manufactured scientific fact.

### 9.8.1 Migrating the existing eleven collections

The current store holds records without the eight-block envelope. Migration is a **one-time, recorded,
human-authorized** act, not a script anyone may re-run.

1. Each existing record gains the envelope with `record_version = 1`, `ontology_version` set to the
   new version, `created.at` taken from the record's existing dated field where one exists and
   otherwise from the governance registry's artifact date, and `created.is_human = true` — because
   every record currently in the store was written by a human editing YAML.
2. `provenance.kind` is `document_derived` and `provenance_reliability` is `legacy_uncertain` unless a
   manifest digest can be produced. Under R1-14 this caps those records at `confidence.level ≤ 1`.
   That is the correct outcome and must not be worked around: the existing store cannot demonstrate
   the provenance of its own numbers.
3. `lifecycle.state` derives from the existing `status` field by the frozen mapping — `Proposed` →
   `CANDIDATE`; `Exploratory`, `Under Validation`, `Validated`, `Rejected` → `ACTIVE`; `Superseded`,
   `Archived` → `DORMANT`. `Rejected` mapping to `ACTIVE` is deliberate and is R3-4 / I-11 applied to
   history: `HYP-2026-0005` and `HYP-2026-0006` are rejected within scope and remain live scientific
   results, and the Living Scientific Model already says so — *"These are durable scientific results
   and constraints on future design, not embarrassing artifacts to delete."*
4. `lifecycle.event_id` cannot be synthesized. Migration emits one `lifecycle` event per record at
   migration time, with `cause` naming the migration decision id, and every migrated record is flagged
   `provenance.note = "state predates event logging"`. Under R7-4 these render as attributed to the
   migration, not to an experiment. Fabricating a plausible historical event id would corrupt the one
   channel I-4 depends on.
5. Migration requires a `decisions` record, human, `write_target = "skb.decision"`, citing this
   document, plus a `governance.registry` entry recording the ontology version transition and the C-d
   loss-of-meaning statement.

**Rule R9-11.** The migration script lives in `tools/` and not in `lske/`, is idempotent by refusing
to run against a store whose records already carry `ontology_version`, and is deleted from the
repository after it has run. A migration tool retained in the tree is a second writer of scientific
state, and K1 permits one.

## 9.9 What the implementer may decide

Exhaustively: private helper names and signatures; the internal data structures used inside a function
body; log message wording outside exception text; test fixture file names; the order of independent
assertions within a test; docstring prose. Nothing else.

Not open, and therefore not to be "improved" during implementation: the twenty collections and their
prefixes; the fifteen relation types; the ten confidence dimensions and their four states; the five
lifecycle states and their transition set; the five write operations; the nine transaction phases and
which one is human; the eight-block envelope; the SQL-P1 grammar; the eight zoom levels and thirty
plates; every rule `R0-1`…`R9-11`; every invariant `I-1`…`I-60`.

**Rule R9-12.** A change to any frozen item is an amendment to this document, requiring a
Constitutional Change Request and a new version number. Implementation momentum is explicitly listed
by Art. L-9 among the things that are not evidence.

## 9.10 Standing of this specification

- **Artifact:** `P1_V2_LSKE_SPECIFICATION_v1.0.md`, version 1.0.0.
- **Status:** **Proposed / Unregistered.** Not entered in `GOVERNANCE_REGISTRY.yaml`.
- **Authority source:** **none.** This document confers no authority on anyone and amends nothing.
- **Inherited without amendment:** the Constitution Lock v1.0.0, `ros.authority`,
  `ros.admissibility`, the Observatory specification, and the M1/P1-v2 runtime. Where this document
  appears to conflict with any of them, they govern and this document is defective.

The registry currently records `status: Draft`, `active_domain_standards: []`,
`constitutional_steward: []`, `adopter_attestation: null` and
`independent_reviewer_attestation: null`. Until those are populated, **building the LSKE is
engineering-only work that produces no admissible evidence.** Every artifact it generates carries the
banner required by R0-3:

```
GOVERNANCE: DRAFT — NO ADMISSIBLE EVIDENCE
```

Completing this implementation closes ZERO UNKNOWN blocker 5 and findings 9 and 10 — the gap between
`Experiment → Artifacts` and `Evidence → Decision → Scientific Knowledge Base → Living Scientific
Model`. It closes nothing else. It does not raise Scientific Readiness, because no experiment has yet
produced admissible evidence to carry through the transaction; it makes the transaction exist so that
the first experiment which does can be carried. The distinction is the whole point of the subsystem:
the LSKE is the instrument that records scientific consequence. It is not, and must never be permitted
to become, a source of it.

**End of specification.**

