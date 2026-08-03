# P1-v2 LSKE — Deferred Normative Obligations

**GOVERNANCE: DRAFT — NO ADMISSIBLE EVIDENCE.**

**Purpose.** This register carries normative requirements that a governing LSKE
specification has assigned to a build stage later than the one currently
implemented. It exists so that no deferral is informal: `P1_V2_LSKE_SPECIFICATION_v1.1.3.md`
rule **R9-20** (`RG-05`) forbids any engineering document from deferring,
narrowing, reassigning, or waiving a frozen normative requirement, and permits a
deferral only where an R9-0 amendment names the requirement, the layer, the
check, and the stage. Every entry below cites such an amendment.

**Scope rule.** An entry appears here only while its stage is unbuilt. It is
removed when the named check exists at the named site and its acceptance
criterion is evidenced. This register does not authorize implementation and does
not itself defer anything.

---

## OBL-01 — `MEM-11`, the ascending-interval invariant

| Field | Value |
|---|---|
| **Requirement** | `N-18`, semantic half: for every `observations` record whose `uncertainty.kind ∈ {ci95, iqr}`, `uncertainty.interval[0] <= uncertainty.interval[1]`. |
| **Authorizing amendment** | `P1_V2_LSKE_SPECIFICATION_v1.1.3.md` — `RG-01` cl. 1–2 (ownership test), `RG-02` (row split), `RG-03` (register entry), `RG-05` (R9-20). |
| **Layer** | Store integrity. **Not** the Stage-1 JSON Schema layer — the comparison spans two instance locations and is unrepresentable as a single-location Draft 2020-12 assertion (`v1.1.3` §0Z.4 proof). |
| **Check** | `MEM-11`, the eleventh sentence of the canonical store-integrity register (`v1.1.0` §3.6 as ruled by `RC-03`, extended by `RG-03`). |
| **Site** | `ros.store._check_memory` (§9.4.2). |
| **Severity** | `error`. |
| **Gate** | Blocks `store_integrity`. |
| **Stage** | **Stage 4** of the §9.8 nine-stage build order. Not Stage 1; not Stage 2, which is `ros.model` 11 → 20 collections and nothing else. |
| **Acceptance criterion** | **`AC-P1-28`** (`v1.1.3` §0Z.12). Explicitly **not** one of the twenty-seven Stage-1 criteria, and not evaluable by a Stage-1 certification. |
| **Required Stage-4 behaviour** | `_check_memory` must, for every `observations` record with `uncertainty.kind ∈ {ci95, iqr}` and non-null `interval`, emit a `MEM-11` finding of severity `error` when `interval[0] > interval[1]`, and emit none when `interval[0] <= interval[1]`. The relation is **non-strict** (`RG-02` cl. 3): `[1.0, 1.0]` is admissible, because a zero-width `ci95` or `iqr` is a real empirical outcome — identical bootstrap resamples, or `Q1 == Q3`. A non-null `interval` under any other `kind`, and a null `interval` under `ci95`/`iqr`, are already rejected structurally at Stage 1 and are not `MEM-11`'s subject. |
| **Current implementation state** | **Absent.** `grep -rn "MEM-11" ros/ v2/` returns 0. `ros.store._check_memory` does not exist at this commit. Stage 4 is unbuilt. |
| **Stage-1 counterpart, already pinned** | `tests/lske/test_envelope.py::test_n18_stage1_accepts_every_ordering_of_two_numbers` records that `[2.0, 1.0]` is a structural PASS at Stage 1. That test is correct only for as long as this obligation stands open and `MEM-11` will close it. If this register loses the entry without `MEM-11` being built, the scientific invariant is silently lost. |
| **Status** | **OPEN.** Not implemented by the transaction that recorded it, by direction. |
| **Recorded** | 2026-08-03, N-18 Amendment Closure — `outputs/P1_V2_PHASE1_STAGE1_ACCEPTANCE_RECORD.md` Part III. |

---

**Register extent:** one obligation, `OBL-01`. No other entry is open.
