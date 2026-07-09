# PROGRAM A — T1 MECHANISM PREREGISTRATION (ES-1)

**Title:** Program A Tier-Emission Mechanism Preregistration — the T1 / G4 Freeze Object (ES-1)
**Authority:** Chief Scientific Architect, authoring the T1 preregistration for G4 freeze. This document is the freeze object itself — the single artifact the Release Manager pins at G4 (`ES1_IMPLEMENTATION_GATE.md` §B1/B3).
**Date:** 2026-07-09
**Status:** DRAFT — pending ScientificAuditor sign-off (B2) and ReleaseManager G4 freeze (B3).

---

## 0. Purpose, posture, and binding firewall

### 0.1 Purpose
This is the T1 mechanism preregistration for Program A's confidence-emission
surface. It is the **freeze object itself**: the single document the Release
Manager pins to a commit at governance gate G4 (`ES1_IMPLEMENTATION_GATE.md`
:28-37; B1/B3). It specifies the frozen rule mapping Program A's evidence
state to exactly one of the four confidence tiers and the answer form coupled
to that state. It is authored by the Architect; it does not self-authorize — it
becomes binding only when the ScientificAuditor signs (B2) and the Release
Manager freezes (B3/G4). Until then `ES1_IMPLEMENTATION_GATE.md` remains
NO-GO and the standing prohibition (no emission-surface or binding code, no
frozen-row output observed) is in force.

### 0.2 Prior decisions consolidated (discharged upstream; recorded, not re-derived)
This document consumes — and does not re-derive — the following already-
discharged gate decisions:

- **G1 (A1) — Location ruling.** Program A lawfully lives in `program_a/`
  (peer product package, application layer). Permitted imports: `core/`,
  `backend.retrieval` (builder-side only, via `program_a/evidence/
  snapshot_builder.py`), and `experiments.EXP1.{dataset, program_a_adapter}`
  via the PA-5 binding subpackage only. A 14-entry import deny-list is in
  force for gate C3 (`PROGRAM_A_DEPENDENCY_GRAPH.md` §4, extended in
  `PROGRAM_A_FINAL_ARCHITECTURE.md` §7). The CR-8/L8 firewall has been
  verified intact on disk: no evaluation-side probability constant, bin
  boundary, ECE pass/kill logic, or tier→probability mapping is present in
  `program_a/`.
- **G2 (A2) — Tier-source lawfulness.** The four tiers
  (UNKNOWN/DEBATED/PROBABLE/CERTAIN) are **structural corroboration-state
  labels**, not probabilities. `STATE_TIER_MAP` (S0→UNKNOWN, S1→DEBATED,
  S2→PROBABLE, S3→CERTAIN) is structural. No evaluation probabilities live in
  `program_a/`. Label-equality with the EXP-1 `CONFIDENCE_TIERS` constant is
  lawful conformance (same labels, no probability mirroring).
- **T0 (A3) — Retrieval mode = FROZEN SNAPSHOT.** The execution-time
  substrate is `program_a/evidence/snapshot_store.py` + `snapshot_format.py`
  (read-only). `snapshot_builder.py` is builder-side-only (sole sanctioned
  `backend.retrieval` consumer, offline pre-freeze). The corpus freezes at T2
  (dataset-freeze) under a CF-R4 leakage review — a ScientificAuditor-owned
  human gate that runs at T2 before any frozen-row output. Defense in depth:
  a 3-field document schema `{origin_domain, title, text}` (rubric/family/
  metadata unrepresentable), the C1 sentinel-substitution test (byte-identical
  output when rubric/family are replaced by sentinels), and the Q7 read-scope
  clause (query.query + query.query_id echo only). The emission surface
  (post-GO) reads only the frozen `SnapshotStore`, never live.
- **T0 (A4) — Seed-variance = NONE.** ES-1 on a frozen snapshot is fully
  deterministic; the `seed` argument is accepted for interface uniformity and
  is otherwise unused. The 22 seeds verify byte-identical replay integrity;
  any divergence is a protocol-violation kill. No manufactured fake seed
  variance is introduced (CR-11). The EXP-1 preregistration §7 power
  amendment for the deterministic case has been DRAFTED (not yet adjudicated);
  it must complete before G6/T11, but its adjudication is not required for GO
  at this gate.

### 0.3 Binding firewall (CR-8/L8) — statement of conformance
This document conforms to the CR-8/L8 firewall **by construction**. It
contains **no evaluation-side probability constant**, **no EXP-1 bin
boundary**, **no ECE pass/kill logic**, and **no tier→probability mapping**.
Those objects live exclusively in the EXP-1 evaluation layer
(`experiments/EXP1/calibration.py`, `experiments/EXP1/decision.py`,
`EXP1_PREREGISTRATION.md`), frozen at G6/T11 — never in the T1 mechanism.
Where this document must name those objects to mark them excluded (§2), it
names them by their evaluation-layer symbols and file locations and
**intentionally does not reproduce their numeric values**. The mechanism
described here is purely ordinal/structural: corroboration states S0–S3 and
one fixed tier per state, with zero numeric constants drawn from the
evaluation side.

---

## 1. Freeze scope (T1 inventory, rows 1–8) — the single T1/G4 freeze event

The T1/G4 freeze is **one event, one document, one pinned commit**. The
eight mandatory T1 objects (the inventory) frozen together at G4 are:

| Row | Frozen object | One-line |
|---|---|---|
| 1 | ES-1 states, coupling, tier map, precedence | The four corroboration states S0–S3, `STATE_TIER_MAP` (S0→UNKNOWN, S1→DEBATED, S2→PROBABLE, S3→CERTAIN), and the frozen precedence/exclusivity rule S0 → S1 → (S2 \| S3) (§3). |
| 2 | Per-tier semantic argument (CR-2) | An a-priori justification, grounded in corroboration structure (not probabilities), for each tier's estimated rubric-correctness (§4). |
| 3 | Free-constant register (B-13/CR-11) | Every free constant the mechanism needs, named with an a-priori justification, none data-fitted, none ever tunable (§5). |
| 4 | `frozen_constants_digest()` + `SPEC_VERSION` pin | SHA-256 over the frozen constant set, asserted equal to the G4-pinned value (drift tripwire); `SPEC_VERSION` is the frozen identity (§6). |
| 5 | Resolved Q2/Q3 (CR-15) | Q2 retrieval mode = frozen snapshot; Q3 seed-variance = none (deterministic); §7 amendment drafted (§7). |
| 6 | Input restriction incl. Q7 read scope (B-4/B-14/CR-3) | Program A reads only `query.query` (+ `query.query_id` echo); rubric/family/metadata forbidden; C1 sentinel test + Q7 read-scope clause (§8). |
| 7 | Identity clause (B-8/CR-12 interim) | `adapter_id`/`mechanism_id` encode the frozen T1 `SPEC_VERSION` + frozen-constants digest, anchored to the snapshot aggregate SHA-256; interim pre-Q8 (§9). |
| 8 | Two requested rulings (B-10, B-11) | M12-fallback L8-scope ruling and dev-corpus lawfulness ruling, requested for adjudication (§10). |

At G4 the Release Manager pins a single commit carrying this document plus
the transcribed `program_a/constants.py`; that commit's hash and the
resulting `frozen_constants_digest()` are the freeze anchors.

---

## 2. Non-T1 / excluded (CR-8/L8 boundary)

The following are **explicitly excluded** from the T1 freeze. They live in
the EXP-1 evaluation layer and are frozen later, at G6/T11 — never in the T1
mechanism:

- **The EXP-1 tier→probability mapping**
  (`experiments/EXP1/calibration.py:TIER_TO_CONFIDENCE`): the four
  probability values assigned to the four tiers. **Numeric values not
  reproduced here.** Excluded.
- **The EXP-1 equal-width bin boundaries**
  (`experiments/EXP1/calibration.py:BIN_BOUNDARIES`): the calibration bin
  edges. **Numeric values not reproduced here.** Excluded.
- **The EXP-1 aggregate-calibration pass/kill logic and its ECE threshold**
  (`experiments/EXP1/decision.py` `ECE_PASS_THRESHOLD` / "ECE gate failure";
  `EXP1_PREREGISTRATION.md`): the pass/kill decision on the aggregate
  calibration metric. **Numeric threshold not reproduced here.** Excluded.
- **Any EXP-1 outcome, frozen-row, or adjudicator signal** as an input to or
  tuning target of the mechanism. Excluded (prereg §4 #5; §6; CR-6/CR-7).

Also **excluded from the T1 freeze event** (built later, post-GO, then frozen
at their own gates):

- **Emission-surface code** (`program_a/mechanism/emission.py`),
  **binding code** (`program_a/binding/exp1_binding.py`), the live
  **`mechanism_id()`** string, and the **`frozen_constants_digest()`**
  implementation are built in **Wave 4** (post-GO, roadmap T4/T8) and then
  frozen. The T1 freeze fixes the *specification* they must conform to (the
  register values, `STATE_TIER_MAP`, templates, identity *format*, and the
  digest *definition*); the code that implements them is written after GO and
  is itself subject to G5 review and G6 lock. No emission-surface or binding
  code is written, merged, or prototyped-in-place before GO (standing
  prohibition, `ES1_IMPLEMENTATION_GATE.md`:91-93).

---

## 3. ES-1 states, answer coupling, tier map, and frozen precedence (inventory row 1)

### 3.1 The four corroboration states (frozen, ordinal)
ES-1 partitions the corroboration structure of retrieved evidence with
respect to the selected claim into exactly four states. States are
structural and ordinal; they carry no probability.

| State | Definition (frozen, ordinal) | Answer-construction rule | Tier (`STATE_TIER_MAP`) |
|---|---|---|---|
| **S0** | No retrieved content supports any candidate claim (support test fails everywhere — includes empty, junk, and topically-related-but-non-supporting results from the never-fail retriever). | Explicit unsupported / unknown / false-premise response; **asserts no fact**. | `UNKNOWN` |
| **S1** | Material contradiction: independent sources support materially incompatible claims (contradiction set non-empty and material). | Qualified answer that **represents the alternatives** and **asserts no single resolution**. | `DEBATED` |
| **S2** | Support from exactly one independent origin; no material contradiction. | Single answer, hedged, source-attributed. | `PROBABLE` |
| **S3** | Support from ≥2 independent origins; no material contradiction. | Single answer, asserted, source-attributed. | `CERTAIN` |

Source: `PROGRAM_A_CONFIDENCE_MECHANISM.md` §7.2 (state table, verbatim
structure); `PROGRAM_A_CONFIDENCE_DECISION_TREE.md` Tree 2 (emission tree).

### 3.2 `STATE_TIER_MAP` (structural, one tier per state, exclusive)
The frozen state→tier map is **structural** — it labels a corroboration
state, it does not assign a probability:

```
STATE_TIER_MAP = {
    "S0": "UNKNOWN",
    "S1": "DEBATED",
    "S2": "PROBABLE",
    "S3": "CERTAIN",
}
```

Coupling is one-tier-per-state and exclusive: exactly one state fires per
query, and the answer form and the tier are produced from the **same**
`EvidenceStateResult` (CR-9 answer–tier consistency, structural). There is
no code path that sets answer and tier independently. Consequently:

- A factual assertion can only co-occur with `PROBABLE` or `CERTAIN` (never
  with `UNKNOWN` or `DEBATED`).
- `CERTAIN` requires multi-source independent support **for the emitted
  claim** (the zero-tolerance FM-1 guard: a fabricated factual answer with
  tier `CERTAIN` can occur only if the claim-support test false-positives on
  a fabricated claim — CF-R2, the dominant residual risk, never a design
  permission).

The tier label set `CONFIDENCE_TIERS = ("UNKNOWN", "DEBATED", "PROBABLE",
"CERTAIN")` is the structural label set; its equality with
`experiments.EXP1.dataset.CONFIDENCE_TIERS` is lawful conformance (same
labels, no probability mirroring — G2/A2).

### 3.3 Frozen precedence and exclusivity
States are exhaustive and mutually exclusive over the corroboration
structure, and are evaluated in the frozen precedence order:

```
S0  →  S1  →  ( S2  |  S3 )
```

- **S0 first:** if no candidate claim is supported by any retrieved content,
  the state is S0 regardless of what else is present.
- **S1 next:** if independent sources support materially incompatible claims
  (contradiction set non-empty and material), the state is S1.
- **(S2 | S3) last:** otherwise the state is S2 (exactly one independent
  origin) or S3 (≥2 independent origins), decided by the
  `MIN_INDEPENDENT_ORIGINS_FOR_S3` threshold (§5).

Exactly one state fires per query (Tree 2 invariant: *state exhaustiveness
and mutual exclusion*). This precedence is frozen in this order; any change
requires a T1 revision + re-freeze + new `SPEC_VERSION` + new `mechanism_id`
(CR-6/CR-12).

---

## 4. Per-tier semantic argument (CR-2) (inventory row 2)

The tier is Program A's estimate of `P(answer_i passes its EXP-1 rubric)`
(prereg §1 pinned semantics). Corroboration structure is the **only** lawful
information Program A has about that event; the per-tier argument below is
a-priori and grounded entirely in corroboration structure (no support /
material contradiction / single-origin support / ≥2-independent-origin
support). It invokes **no probability number** and no evaluation-side
constant.

- **S0 → UNKNOWN.** When nothing supports any candidate claim, the lawful
  answer is an explicit unsupported/unknown/false-premise response that
  asserts no fact. The a-priori rubric-correctness of such a refusal is
  genuinely uncertain: it is highest precisely when the answer truly was
  unavailable (refusing-when-unavailable is rubric-correct), but it is wrong
  whenever the answer *was* available in the corpus and the support detector
  failed to find it (refusal-despite-availability is rubric-incorrect —
  prereg §3 row 1). The designer's a-priori estimate for S0 is therefore the
  *lowest* of the four states — matching the lowest-ordinal tier — with the
  uncertainty honestly retained rather than suppressed.

- **S1 → DEBATED.** When independent sources support materially incompatible
  claims, the lawful answer is a qualified answer that represents the
  alternatives and asserts no single resolution. Its a-priori
  rubric-correctness is *moderate*: it can still omit a required alternative
  or misrepresent the shape of the disagreement, but representing the
  disagreement is exactly the rubric-facing behavior the qualified-answer
  form exists to reward. The ordinal rank of `DEBATED` (above `UNKNOWN`,
  below `PROBABLE`) reflects that a correctly-constructed qualified answer is
  more likely rubric-correct than a refusal-that-might-still-be-wrong, and
  less likely than a singly-corroborated factual assertion.

- **S2 → PROBABLE.** When exactly one independent origin supports the
  selected claim and there is no material contradiction, the lawful answer
  is a single hedged, source-attributed factual assertion. Its a-priori
  rubric-correctness is *high but not maximal*: a single independent origin
  can still be wrong (the source can err or the extraction can misattribute),
  so the assertion is hedged and attributed rather than asserted flatly. The
  ordinal rank (above `DEBATED`, below `CERTAIN`) reflects that
  single-origin support is stronger evidence of a rubric-correct factual
  answer than representing-a-disagreement, but weaker than multi-origin
  corroboration.

- **S3 → CERTAIN.** When ≥2 independent origins support the selected claim
  and there is no material contradiction, the lawful answer is a single
  asserted, source-attributed factual assertion. Its a-priori
  rubric-correctness is *maximal of the four states*: independent
  corroboration is the strongest structural evidence available to Program A
  that the asserted fact will pass its rubric, because independent origins
  agreeing on the same claim is the corroboration pattern least likely to
  arise from a single-source error or a fabrication. The ordinal rank
  (highest) reflects this; the `≥2` threshold is the smallest count that
  constitutes corroboration *at all* (§5, `MIN_INDEPENDENT_ORIGINS_FOR_S3`).

**Ordinality is by construction:** more/stronger corroboration → higher
tier, matching the tier order, with **no numeric constant taken from the
evaluation side**. The honest exposure the experiment exists to measure is
whether these four a-priori structural estimates land near enough to the
EXP-1 evaluation's locked targets for the evaluation's aggregate
calibration metric to pass — that is exactly hypothesis H1, it is untested
by design, and a kill there is a valid scientific outcome (FM-4). The EXP-1
pass/kill logic and its threshold live in the EXP-1 layer; they are not part
of this mechanism and are not reproduced here.

---

## 5. Free-constant register with a-priori justifications (B-13/CR-11) (inventory row 3)

Every free constant the mechanism needs is named below with an a-priori
justification. **None is data-fitted; none is tuned on EXP-1 outcomes, frozen
rows, or any observed output; none may ever be tuned after freeze.** These
constants **are** the mechanism (CR-6/CR-11/CR-12): a change to any one of
them is a mechanism change and requires a T1 revision + re-freeze + a new
`SPEC_VERSION` + a new `mechanism_id()` before any frozen-row output is
observed, and is flatly prohibited after (prereg §4 #5; CR-6).

Each entry below is a **register entry**: name + role + a-priori
justification + intended value/source. Each is marked **"to be transcribed
verbatim into `program_a/constants.py` at G4."** Where the architecture
supplies an example value, that value is recorded; where the corpus does not
supply a concrete value, the structural form is recorded and the exact value
is fixed at G4 from this register (no unfounded numeric is invented).

| # | Constant | Role | A-priori justification | Intended value / source | Transcribe at G4 |
|---|---|---|---|---|---|
| 5.1 | `MIN_INDEPENDENT_ORIGINS_FOR_S3` | Separates S2 from S3: the minimum number of independent origins required for the `CERTAIN` tier. | Structural: 2 is the smallest count that is corroboration *at all* — one origin is not corroboration, two is. Hand-set in the F2 sense; preregistered here, never tuned. (MECHANISM §7.4; `constants.py` TODO comment: "architecture example: 2".) | `MIN_INDEPENDENT_ORIGINS_FOR_S3: int = 2` | yes, verbatim |
| 5.2 | `INDEPENDENCE_RELATION` | The source-independence relation that prevents mirror/syndication domains from being counted as independent origins. | Structural: corroboration counts *independent origins*, not mirror copies. Mirror domains must be de-duplicated to a single origin so a syndicated copy does not inflate S3. (MECHANISM §7.4; ARCHITECTURE PA-1.) | A frozen structural definition: two evidence items are independent iff they have distinct `origin_domain` provenance, with mirror/syndication domains counted once (exact relation text fixed at G4 from this register). | yes, verbatim |
| 5.3 | `SUPPORT_TEST_PARAMS` | Parameters of the deterministic claim-support test (decides "supports"/"contradicts" a claim). | Structural + deterministic: the load-bearing sub-component (MECHANISM §7.4); its failure modes dominate the risk register (CF-R2). Must be deterministic and entity-level (not topic-level) so fabrication-pressure and topically-related-but-non-supporting evidence yield no claim. | The frozen deterministic claim-support test parameters (entity-level matching; exact parameters fixed at G4 from this register). No probability numbers. | yes, verbatim |
| 5.4 | `CONTRADICTION_MATERIALITY_PARAMS` | Parameters of the materiality rule that separates S1 (material contradiction) from trivial variation/noise. | Structural: a trivial phrasing variation is not a material contradiction; only incompatible claims count. Freezing the materiality threshold here is what makes S1-vs-noise a frozen rule, not a runtime judgment. (MECHANISM §7.4.) | The frozen materiality-rule parameters (exact parameters fixed at G4 from this register). No probability numbers. | yes, verbatim |
| 5.5 | `EVIDENCE_ORDERING_KEY` | PA-1's frozen total order over the evidence set, so identical `(query_text, snapshot)` yields byte-identical `EvidenceSet` bytes. | Structural + deterministic: a frozen total order is required for replay (L6) and removes wall-clock/score-order as a determinism leak. (ARCHITECTURE PA-1; the architecture's example key.) | `EVIDENCE_ORDERING_KEY`: lexicographic on `(origin_domain, doc_id)` (architecture example value; the frozen total-order key). | yes, verbatim |
| 5.6 | `EXTRACTION_PARAMS` | PA-2's deterministic candidate-claim extraction parameters. | Structural + deterministic: pure text mechanics, no model calls (M8 unlawful), no randomness; entity-level extraction so fabricated-entity probes yield no claim (CF-R2 first line). (ARCHITECTURE PA-2; MECHANISM §7.1.) | The frozen deterministic extraction parameters (exact parameters fixed at G4 from this register). No probability numbers, no model calls. | yes, verbatim |
| 5.7 | `ANSWER_TEMPLATES` | PA-4's frozen answer-text templates per state — the rubric-facing wording patterns for "explicit unsupported/unknown", "represents the alternatives", "hedged source-attributed", and "asserted source-attributed". | Structural + determinism: the answer form coupled to each state (CR-9) must be frozen, not improvised at runtime, so the rubric-facing elements are reproducible and auditable. (ARCHITECTURE PA-4; MECHANISM §7.2.) | A frozen template string per state `{S0, S1, S2, S3}` (exact template text fixed at G4 from this register). The `UNKNOWN`/`DEBATED` forms assert no fact; the `PROBABLE`/`CERTAIN` forms are source-attributed. | yes, verbatim |
| 5.8 | `SPEC_VERSION` | The T1 spec version identity — the frozen identity string of this mechanism specification. | Structural: the version anchor that ties the frozen code (`mechanism_id()`, `frozen_constants_digest()`) to this frozen spec; any mechanism change forces a new `SPEC_VERSION`. (CR-6/CR-12; `constants.py` `SPEC_VERSION`.) | `SPEC_VERSION: str = "es1-t1-2026-07-09"` (draft identity for this document; ratified to its final frozen value at the G4 freeze commit). | yes, verbatim (final value set at G4) |

Additionally, `STATE_TIER_MAP` (§3.2) and `CONFIDENCE_TIERS` (§3.2) are frozen
structural constants transcribed into `constants.py` from §3. They carry no
probability and are not tunable; their edit triggers the same change-control
rule as the register above.

**Forbidden in `constants.py` (CR-8/L8, asserted by conformance tests):** no
member of `constants.py` may equal any EXP-1 tier→probability value, any
EXP-1 bin boundary, or any EXP-1 ECE threshold; `experiments.EXP1.calibration`
is on the deny-list and may not be imported (`PROGRAM_A_MODULE_SPEC.md` §2;
`PROGRAM_A_FINAL_ARCHITECTURE.md` §7).

---

## 6. `frozen_constants_digest()` + `SPEC_VERSION` pin (inventory row 4)

### 6.1 `frozen_constants_digest()` — drift tripwire
`frozen_constants_digest() -> str` is a **SHA-256 digest over the frozen
constant set**: the canonical, ordered serialization of every register entry
in §5 (`MIN_INDEPENDENT_ORIGINS_FOR_S3`, `INDEPENDENCE_RELATION`,
`SUPPORT_TEST_PARAMS`, `CONTRADICTION_MATERIALITY_PARAMS`,
`EVIDENCE_ORDERING_KEY`, `EXTRACTION_PARAMS`, `ANSWER_TEMPLATES`,
`SPEC_VERSION`) together with the structural `STATE_TIER_MAP` and
`CONFIDENCE_TIERS`. The digest is computed once at the G4 freeze commit, and
the resulting hex string is **pinned** (recorded in `constants.py` as
`CONSTANTS_HASH` and asserted by `tests/program_a/test_evidence_states.py`).

The pin is a **drift tripwire**: any change to any frozen constant changes
the digest, which fails the asserted-equality test, which fails CI —
surfacing the change as a mechanism change requiring T1 revision + re-freeze
+ new `SPEC_VERSION` + new `mechanism_id` (CR-6/CR-11/CR-12). Silent in-place
constant edits after freeze are therefore mechanically impossible to land
green.

### 6.2 `SPEC_VERSION` — frozen identity
`SPEC_VERSION` is the frozen identity string of this mechanism specification
(§5.8). It is encoded into `mechanism_id()` (§9) and folded into the digest
inputs. At G4 the Release Manager pins the commit and ratifies the final
`SPEC_VERSION` value; thereafter the value is immutable for the frozen
mechanism. `SPEC_VERSION` is the anchor that binds the frozen code to this
frozen spec.

### 6.3 Implementation status (post-GO)
`frozen_constants_digest()` is **defined here** (its inputs, its algorithm =
SHA-256 over the ordered frozen-constant serialization, and its G4-pinned
value) but **implemented post-GO** in Wave 4 (`program_a/constants.py`), per
the standing prohibition. The T1 freeze fixes the specification the
implementation must conform to; the implementation is written after GO and
is itself subject to G5 review and G6 lock.

---

## 7. Resolved Q2/Q3 (CR-15) (inventory row 5)

### 7.1 Q2 — Retrieval mode = FROZEN SNAPSHOT (T0/A3)
**Decision:** Program A retrieves from a **frozen retrieval snapshot** at
execution time, never from the live web. The execution-time substrate is
`program_a/evidence/snapshot_store.py` (load + `evidence_for`) backed by
`snapshot_format.py` (on-disk schema + SHA-256 integrity verify).
`snapshot_builder.py` is **builder-side only** — the sole sanctioned
`backend.retrieval.unified_retriever` consumer — and runs offline, pre-freeze,
outside the execution path.

**Corpus freeze and leakage review.** The snapshot corpus freezes at T2
(dataset-freeze) under a **CF-R4 leakage review**: a ScientificAuditor-owned
human gate that runs at T2 before any frozen-row output is observed. A
snapshot curated *after* seeing the frozen queries would be adjacent to
tuning; the leakage review is the guard against that. Defense in depth:
(i) a 3-field document schema `{origin_domain, title, text}` in which
rubric/family/metadata fields are unrepresentable; (ii) the C1
sentinel-substitution test (§8) asserting byte-identical output when
rubric/family are replaced by sentinels; (iii) the Q7 read-scope clause (§8).
The emission surface (post-GO) reads only the frozen `SnapshotStore`, never
live.

### 7.2 Q3 — Seed-variance = NONE (T0/A4)
**Decision:** ES-1 on a frozen snapshot is **fully deterministic**; the
`seed` argument is accepted for interface uniformity
(`answer_query(query_text, seed)`) and is otherwise **unused**. The 22 EXP-1
seeds therefore verify **byte-identical replay integrity**: all 22 replicates
of a given frozen row are byte-identical, and any divergence across seeds is
a **protocol-violation kill** (not a data point). No manufactured fake seed
variance is introduced to dodge this — manufacturing apparent variance would
be an undeclared constant of exactly the kind CR-11 forbids (CR-11).

### 7.3 EXP-1 preregistration §7 power amendment — draft status
Because the deterministic case leaves all 22 replicates byte-identical, the
EXP-1 preregistration's own §7 amendment clause ("…this preregistration is
underpowered and must be amended before outputs are observed") **must be
invoked before execution**. The §7 power amendment for the deterministic case
has been **DRAFTED** (T0/A4). It is **not yet adjudicated**; its
adjudication is **not required for GO** at this gate, but it **must complete
before G6/T11** (before any frozen-row execution). This document records
that status; it does not adjudicate the amendment (the ScientificAuditor
adjudicates, before G6).

---

## 8. Input restriction incl. Q7 read scope (B-4/B-14/CR-3) (inventory row 6)

### 8.1 The L11/CR-3 input restriction
Program A reads **only** `query.query` (and `query.query_id` for echo /
manifest identity). The `QueryRecord` carries `gold_rubric`,
`query_family`, and `metadata` into `adapter.answer(query, seed)`
(`experiments/EXP1/dataset.py`:33-41; `run.py`:84,181); a mechanism that read
any of those could trivially fake calibration. They are therefore
**forbidden / invisible to the surface**.

The restriction is enforced **structurally**, not merely by discipline:

- **PA-5 binding** (`program_a/binding/exp1_binding.py`) is the *only* module
  that ever sees a `QueryRecord`, and it reads only `query.query` and
  `query.query_id`.
- **PA-1..PA-4** are typed **below** the level at which `gold_rubric` /
  `query_family` exist: their inputs are `query_text: str`, `EvidenceSet`,
  `CandidateClaims`, `EvidenceStateResult` — none of which has a rubric,
  family, or metadata field. The cheat channel is **unreachable by
  construction** (`PROGRAM_A_FINAL_ARCHITECTURE.md` §4 PA-3;
  `PROGRAM_A_MODULE_SPEC.md` §1 `types.py`).
- The retrieval-relevance `score` field is **structurally absent** from
  `EvidenceItem`/`EvidenceSet` (M1 lawfulness condition; DATAFLOW §3 row 1).

### 8.2 C1 sentinel-substitution test (CR-3 / gate C1)
The C1 sentinel-substitution test verifies the restriction: run the surface
with `gold_rubric` and `query_family` replaced by sentinel values and assert
**byte-identical output**. If the output changes when those fields change,
the surface is reading them and the test fails. The test exists on disk
(`tests/EXP1/test_cheat_channel_guard.py`) and is re-bound to PA-5 at build
time (gate C1; `ES1_IMPLEMENTATION_GATE.md`:41-42).

### 8.3 Q7 read-scope clause
Q7 (`PROGRAM_A_OPEN_QUESTIONS.md` Q7) asks whether Program A may *read* (not
write) backend stores during execution. The T0 resolution folds the answer
into this T1 spec: **reads of frozen assets are permitted; reads of mutable
stores are not.** Concretely:

- **Frozen assets readable:** the frozen `SnapshotStore` (content-addressed,
  SHA-256-verified, read-only) is the sanctioned execution-time read.
- **Mutable stores not readable:** no live web, no env-keyed sources, no
  mutable DB/telemetry reads in the EXP-1 path. Any read that could smuggle
  hidden state past the determinism requirement (L6) is forbidden.

This is the Q7 read-scope clause: **frozen assets readable, mutable stores
not.** It is enforced by PA-1's no-network / no-wall-clock / no-env-var
invariants and the import-guard test (gate C3).

---

## 9. Identity clause (B-8/CR-12 interim) (inventory row 7)

### 9.1 Interim identity (pre-Q8)
Until the Q8 ruling (`PROGRAM_A_OPEN_QUESTIONS.md` Q8; decider: Architect +
Release Manager, in G1/G4) finalizes Program A's identity-string and
versioning discipline, the following **interim** identity clause is binding:

- `mechanism_id()` (the public identity string re-exported by
  `program_a/__init__.py` and passed by the EXP-1 runner as
  `program_a_adapter_id`) MUST encode:
  1. the frozen **T1 `SPEC_VERSION`** (§5.8/§6.2), and
  2. the **frozen-constants digest** (`frozen_constants_digest()`, §6.1),
  and MUST be **anchored to the frozen snapshot aggregate SHA-256 + the T1
  spec version**.
- The interim format is:

  ```
  mechanism_id() = "program-a-public-v1+es1-{SPEC_VERSION}+const-{frozen_constants_digest[:8]}+snap-{snapshot_aggregate_hash[:8]}"
  ```

  where `snapshot_aggregate_hash` is the frozen snapshot's
  `SnapshotManifest.aggregate_hash` (`PROGRAM_A_MODULE_SPEC.md` §3
  `snapshot_format.py`).

### 9.2 Why this satisfies CR-12
- `adapter_id == mechanism_id()` is recorded in the execution manifest
  (`manifest.py`:29) and identity-equality is checked on replay
  (`run.py`:147-148); therefore any mechanism drift (a changed constant, a
  changed spec version, or a changed snapshot) forces a new `mechanism_id()`
  and is detected as a manifest mismatch. This binds the identity string to
  the frozen spec commit, which is the open question Q8 asks.
- Encoding the digest means a silent constant edit (which changes the
  digest) also changes the id — two independent drift detectors for the
  price of one.
- Anchoring to the snapshot aggregate hash means a snapshot swap is detected
  even if the spec is unchanged.

### 9.3 Interim scope and Q8 hand-off
This clause is **interim**. The Q8 ruling may replace this format with a
refined one; until then this format is the frozen identity for the T1/G4
freeze. Any change to the identity format after G4 is itself a
mechanism-change event requiring a new `SPEC_VERSION`. The Q8 ruling is owed
before any PASS claim, not before execution.

---

## 10. Requested rulings (B-10, B-11) (inventory row 8)

These two rulings are **requested for ScientificAuditor adjudication**. They
are recorded here so the fallback path and the dev-corpus regime are
adjudicated *before* they are ever needed, not after. They are not
pre-emptively activated.

### 10.1 B-10 — L8 scope of the M12 fallback path
**Background.** M12 (`PROGRAM_A_CONFIDENCE_MECHANISM.md` §4, Class IV) is the
designated fallback if the ScientificAuditor later rules that the ES-1
structural states are insufficiently tied to the `p_i` semantics. M12 posits
per-source error rates fixed a priori and computes a probability of
correctness from `(n support, m contradict)`, then emits the tier whose
locked interval contains it. M12's lawfulness is **conditional** on two open
questions: (a) the provenance of the error-rate constant (the canon §8
designer-injection pattern), and (b) the **L8-scope question**: whether
discretizing an a-priori internal probability at the EXP-1 locked bin
boundaries constitutes forbidden "mirroring" of the evaluation constants
(`PROGRAM_A_MASTER_SPECIFICATION.md` §7 item 3) or is the most faithful
possible implementation of the tier semantics.

**M12 is NOT adopted now.** ES-1 is the adopted mechanism (§3–§6). The G2
ScientificAuditor noted that the M12 internal-probability question is
**moot** while M12 is not adopted, and **re-adjudicates only if M12 is
activated**.

**Ruling requested (B-10).** The Architect requests that the
ScientificAuditor adjudicate, in advance of any activation, the following:

1. **If M12 is ever activated, it MUST preserve the CR-8/L8 firewall.** No
   evaluation-side probability constant, no EXP-1 bin boundary, no ECE
   pass/kill logic, and no tier→probability mapping may be introduced into
   `program_a/` by M12. M12's per-source error rates and any discretization
   must be a-priori, frozen, and must not numerically equal or be fitted to
   the EXP-1 evaluation constants.
2. **The L8-scope question must be resolved before activation.**
   Specifically: whether an internal probability discretized at the EXP-1
   locked bin boundaries is forbidden "mirroring" (`PROGRAM_A_MASTER_
   SPECIFICATION.md` §7 item 3) or a faithful implementation. The ruling
   must be issued before M12 is ever used, so that the fallback is lawful
   before it is ever exercised.
3. **Until the ruling is issued, M12 remains not-adopted and not-built.**
   The standing prohibition applies: no M12 code may be written, merged, or
   prototyped-in-place while ES-1 is the adopted mechanism.

This ruling does not change ES-1; it pre-adjudicates the fallback so that a
future switch to M12 is not a governance gap.

### 10.2 B-11 — Dev-corpus lawfulness and scope limits
**Background.** M13 (MECHANISM §4, Class IV) is the dev-set-calibrated rule
fit on a non-frozen development corpus before freeze. It is not adopted
(ES-1 needs no dev fitting). But pre-freeze synthetic/dev sanity checks of
the ES-1 mechanism (the T10 dry run and PA-6 conformance-guard corpora) are
required by the roadmap, and their lawfulness must be adjudicated.

**Ruling requested (B-11).** The Architect requests that the
ScientificAuditor adjudicate that **pre-freeze synthetic/dev sanity checks of
the ES-1 mechanism are lawful, subject to the following scope limits:**

1. **Disjointness.** Any dev corpus MUST be synthetic and **disjoint from
   the frozen EXP-1 dataset** (`EXP1_DATASET_SPEC.md` §12.2–§12.3). The dev
   corpus must not be, overlap, or be derived from the frozen 210-row set.
2. **No frozen-row output observed.** No frozen-row output may be observed
   by anyone in any capacity during dev checks (standing prohibition;
   `ES1_IMPLEMENTATION_GATE.md`:91-93). Dev checks run only on the synthetic
   non-frozen corpus.
3. **Mechanics verification only — no in-place tuning.** Dev-check results
   verify mechanics only. **No constant may change in response to dev-check
   results except by returning to Wave 2 (T1 redesign + re-freeze + new
   `SPEC_VERSION` + new `mechanism_id`) before any frozen-row exposure.**
   In-place constant edits triggered by dev-check outcomes are forbidden
   (B-11 scope limit; CR-6/CR-11).
4. **T10 dry run within B-11 scope.** The T10 dry run
   (`PROGRAM_A_IMPLEMENTATION_ROADMAP.md` T10; `ES1_CORRECTION_PLAN.md` W4.2)
   is within B-11 scope. Its verification targets are: (a) no `CERTAIN` on
   fabricated-claim probes (CF-R2 / FM-1 guard); (b) ≥2 tiers reachable
   across the synthetic three-family corpus (CF-R6, the degenerate-tier
   guard); (c) byte-identical replay (determinism); (d) full artifact set
   present. **T10 is a mechanics check on a synthetic non-frozen corpus; it
   is not a calibration tuning loop, and its results may not tune constants
   in place.** T10 completes before G6/T11 (it is a precondition of G6
   lock), not before GO at this gate.
5. **No Goodhart leakage.** Dev-check corpora must be constructed without
   reference to the frozen queries/rubrics (the CF-R4 leakage-review
   discipline applied to dev corpora too), so that a dev corpus is not a
   held-out proxy for the frozen set.

This ruling confirms that the engineering verification regime (PA-6
conformance guard + T10 dry run on synthetic corpora) is lawful, and bounds
it so it cannot become a covert calibration loop.

---

## 11. Change-control rule (CR-6/CR-12)

From the moment `constants.py` lands at G4 (= the freeze reflected in code),
any change to `constants.py`, `support_tests.py`, `evidence_states.py`, the
emission templates, the snapshot artifact, or the PA-1 ordering rule is a
**mechanism change**: it requires a T1 revision + re-freeze + new
`SPEC_VERSION` + new `mechanism_id()` **before** any frozen-row output is
observed, and is flatly prohibited after (prereg §4 #5; CR-6). Dev-check
findings route back to §5 via Wave 2 (redesign + re-freeze), never via
in-place edits (B-11 scope limit, §10.2). The `frozen_constants_digest()`
tripwire (§6.1) and the manifest identity-equality check (§9.2) mechanically
enforce this.

---

## 12. Sign-off (BLANK — human authority ratifies at GO)

No approval is fabricated by this document's author. The following blocks
are left blank for the named human authorities to sign.

- **B2 — ScientificAuditor T1 sign-off.**
  ScientificAuditor: ____________________ , date: __________

- **B3 / G4 — ReleaseManager freeze.**
  ReleaseManager: ____________________ , pinned commit: ____________________ , date: __________

---

## 13. References (read-only grounding)

- `ES1_IMPLEMENTATION_GATE.md` (B1 verbatim, §B1:28-34; standing prohibition:91-93).
- `ES1_CORRECTION_PLAN.md` (Waves 1–4; W4.2 T10 scope).
- `PROGRAM_A_CONFIDENCE_MECHANISM.md` §7.1–§7.4 (states, coupling, register, L8).
- `PROGRAM_A_CONFIDENCE_DECISION_TREE.md` Tree 1 (lawfulness), Tree 2 (ES-1 emission), Tree 3 (governance).
- `PROGRAM_A_FINAL_ARCHITECTURE.md` §2 (location), §4 PA-1..PA-4 (mechanism), §6 (determinism), §7 (deny-list).
- `PROGRAM_A_MODULE_SPEC.md` §1 (`types.py`), §2 (`constants.py`), §3–§10 (modules).
- `program_a/constants.py` (the placeholder register this document formally specifies; transcribed verbatim at G4).
- `PROGRAM_A_OPEN_QUESTIONS.md` Q2/Q3/Q7/Q8.
- `PROGRAM_A_IMPLEMENTATION_ROADMAP.md` (T0/T1/G4/T10/G6/T11).
- `EXP1_PREREGISTRATION.md` §1/§3/§4/§6/§7 (pinned semantics, kills, prohibitions, §7 amendment clause).
- `experiments/EXP1/calibration.py` (the EXP-1 evaluation layer — `TIER_TO_CONFIDENCE`, `BIN_BOUNDARIES`; referenced, not reproduced).
- `experiments/EXP1/decision.py` (the EXP-1 evaluation layer — `ECE_PASS_THRESHOLD`, degenerate-tier gate; referenced, not reproduced).

---

*End of T1 mechanism preregistration. This document is the freeze object for gate G4.*
