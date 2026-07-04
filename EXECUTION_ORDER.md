# PROGRAM D — EXECUTION ORDER

**Authority:** Derives from `PROGRAM_D_CANONICAL.md`. Sequences the tasks in `IMPLEMENTATION_BACKLOG.md` to minimize **engineering risk, scientific risk, merge conflicts, and dependency cycles**, while keeping the build **continuously runnable** (`pytest -m "not slow"` green at every commit).
**Ordering principles (canonical §1 rule 4):** scientific correctness > reproducibility > simplicity > performance > features. Therefore reconciliation (M0) and the compliant core (M1) precede all experiments, and no experiment result is trusted while a Tier-0 gap (`IMPLEMENTATION_GAPS.md`) is open.
**Generated:** 2026-07-03.

---

## 1. The ordering constraints (why this sequence)

1. **Canon before code (§9).** Eight docs + two registries still assert [REJECTED] objects. Writing code against them builds the wrong program. → **M0 first.**
2. **Keystone before claims (§4, §11).** Program D's viability = making **I2** true before "emergence" is used. The null-referenced `M` and the derived `λ_model` must exist and be correct before E0 runs. → **core (M1-E1) before E0 (M4).**
3. **Cheap precondition early (§11).** EXP-0 tests the *existing* system on frozen code; it does not need the new `core/`. It runs against a frozen build in parallel with core work, the moment M0 lands. → **M2 parallel to M1.**
4. **Runnable builds always.** All moves use the dual-import shim (checklist Phase 3+); the codemod that deletes shims (INFRA-08) is a single late, isolated, high-risk commit on a clean tree.
5. **Merge-conflict minimization.** Doc-only tasks (M0) are batched first (they touch markdown/YAML, not code). Code extraction (CORE-*) is isolated from bulk moves (INFRA-*) so a predictor extraction never collides with a directory move.

---

## 2. Topological task DAG (dependency-ordered)

```
STAGE 0 — Reconciliation (docs/registries only; no code risk)
  RC-01 ─┐
  RC-02 ─┤ (H3/EXP-3 purge)
  RC-03  │ (SPEC H2 + ECE gate)
  RC-04 ─┤ (repo_v2: EXP3/4, self_model, soul-dep)
  RC-05 ─┤ (migration + checklist de-dup)
  RC-06 ─┤ (experiment_registry)
  RC-07  │ (parameter_registry: λ pin, free-energy REJECTED)
  RC-08 ─┘ (coverage matrix)
        │
        ▼
STAGE 1 — Compliant core (scientific primitives; high value, isolated files)
  CORE-02 (log score)            ─┐
  CORE-04 (null-referenced M)     │  (independent, parallel)
  CORE-01 (Dirichlet predictor) ──┼─▶ CORE-03 (λ_model=k·b+n·log₂N)
                                  │        │
  CORE-05 (C1/C2/C3) ◀────────────┘        │
        │                                   │
        └───────────────┬───────────────────┘
                        ▼
                  CORE-TEST (canon-exactness + CI grep-gate)
                        │
        ┌───────────────┼───────────────────────────┐
        ▼               ▼                           ▼
  CORE-06 (archive   INFRA-01..06 (skeleton +     [enables M2/M3/M5
   rejected)          shimmed moves)               once relevant
  CORE-07 (rename)          │                        core lands]
        │                   ▼
        │             INFRA-07 (dedup → import core/)
        │                   │
        └─────────┬─────────┘
                  ▼
            INFRA-08 (codemod: delete shims)  ← single isolated high-risk commit
                  │
STAGE 2 — Experiments (each self-contained, parallelizable after its deps)
                  │
   ┌──────────────┼───────────────┬───────────────────┐
   ▼              ▼               ▼                   ▼
 EXP-0 (M2)     EXP-1 (M3)      E0 (M4)            EXP-2 (M5)
 needs: M0 +    needs: M0 +     needs: full        needs: M0 +
 frozen build   CORE-02/metrics CORE-01..05        CORE-06/07 decouple
   │              │               │                   │
 EXP0-01..06    EXP1-01..06     E0-01..14          EXP2-01..05
   │              │               │                   │
   └──────────────┴───────┬───────┴───────────────────┘
                          ▼
STAGE 3 — Publication & reproducibility (needs results)
                   PUB-01..05 (M6)
```

**No cycles.** The only cross-stage edge that could cycle — experiments importing `core/` while `core/` is still being extracted from `program_c/` — is broken by the shim strategy: `core/` is authored as *new* files (Stage 1), and legacy sites are refactored to import from it (INFRA-07) *after* CORE-TEST is green.

---

## 3. Recommended execution waves

Each wave ends on a green suite and a runnable build. Waves are the unit of review/merge.

### Wave A — Reconciliation (M0) · ~1.5 days · risk: Low
- **Tasks:** RC-01 → RC-08 (batch; markdown/YAML only).
- **Order within wave:** RC-01, RC-02 (hypothesis/protocol) → RC-03 (spec) → RC-04, RC-05, RC-06, RC-07 (engineering/registries) → RC-08 (coverage).
- **Gate:** `TRACEABILITY_MATRIX.md` rejected-object rows all have live-target ∅; `grep` gates in `IMPLEMENTATION_GAPS.md` G-05/G-13/G-14/G-20 pass.
- **Why first:** removes the contradictions that would otherwise misdirect every code task; zero code risk; no merge conflicts with later code waves.

### Wave B — Compliant core (M1-E1) · ~3 days · risk: High (scientific semantics)
- **Tasks:** CORE-02 ∥ CORE-04 (independent) → CORE-01 → CORE-03 → CORE-05 → CORE-TEST.
- **Gate:** CORE-TEST proves `λ_model==k·b+n·log₂N` (non-configurable), `E[M|H₀]≈0`, log-loss reference match, no banned symbol in `core/`. Closes G-02, G-08 (metric exists), G-21.
- **Why second:** the keystone machinery must be correct before any experiment consumes it. Isolated new files → no conflict with Wave A or moves.

### Wave C — Archive + skeleton (M1-E2/E3, shimmed) · ~3 days · risk: Medium
- **Tasks:** CORE-06, CORE-07 (archive/rename) ∥ INFRA-01..06 (skeleton + shimmed moves) → INFRA-07 (dedup to `core/`).
- **Gate:** suite green via shims at every commit; `grep` gate G-07/G-19 pass; G-22 closed by INFRA-07.
- **Why here:** moves are mechanical and backward-compatible; keeping them after core means INFRA-07 can point legacy sites at a *finished* `core/`.

### Wave D — EXP-0 precondition (M2) · ~2 days · risk: Medium · **parallelizable with Wave B/C**
- **Tasks:** EXP0-01 → EXP0-02 → EXP0-04 (leakage) → EXP0-03 (state reset) → EXP0-05 → EXP0-06.
- **Dependency:** only Wave A (M0) + a **frozen build of the existing system** — *not* the new `core/`. A second engineer can run this concurrently with Waves B/C.
- **Gate:** per-trial `graph_wiped:true`, leakage-free certificate, original-vs-paraphrase delta with CI. Closes G-03, G-04.
- **Scientific payoff:** retires the headline claim (canonical §11) at the earliest possible point.

### Wave E — Codemod (INFRA-08) · ~1 day · risk: Very-High · **isolated commit**
- **Task:** INFRA-08 (bulk import rewrite; delete all shims).
- **Preconditions:** Waves B, C complete; clean working tree; pre/post `from backend.` count gate.
- **Gate:** full `pytest` green; `from backend.*` resolves to zero.
- **Why isolated:** highest blast radius in the program; must not share a commit with any semantic change so a revert is surgical.

### Wave F — EXP-1 calibration gate (M3) · ~2 days · risk: Medium · **parallelizable after Wave B**
- **Tasks:** EXP1-01 → EXP1-02 → (EXP1-03 ∥ EXP1-04) → EXP1-05 → EXP1-06.
- **Dependency:** M0 + `core/measurement` (CORE-02/metrics) — does **not** need CORE-01/03. Can start once Wave B's scoring lands, in parallel with Wave C/E.
- **Gate:** ECE on ≥200 queries; control present; PASS iff ECE<0.10. Closes G-14/G-15/G-16; wires kill G-11 (EXP-1 part).
- **Priority note:** this is canonical **deliverable #1** — schedule its engineer as soon as scoring exists.

### Wave G — E0, the H\* decider (M4) · ~5 days · risk: High (keystone) · **needs full Wave B**
- **Ordered tasks:**
  1. E0-01 (nonlinear env) → E0-02 (offline nonlinearity check) — closes G-09.
  2. E0-09 (purge free-energy) — closes G-01, *do this before wiring conditions so the path is clean*.
  3. E0-03 (T) → E0-04 (C1) → E0-05 (C2) → E0-06 (C3) — closes G-10.
  4. E0-07 (DV-a held-out LL) ∥ E0-08 (DV-b `M`) — closes G-08 integration, G-12 (LL).
  5. E0-10 (observability) → E0-11 (PRNG) → E0-12 (snapshots) — closes G-12, G-18.
  6. E0-13 (decision, ≥5 seeds, p<0.01) → E0-14 (two-attempts, falsification string) — closes G-11 (E0 part).
- **Gate:** machine-checked pass/kill from frozen code, DV-a + null-referenced DV-b, ≥5 seeds, ≥1 previously-unmeasurable metric measured, zero rejected math in path.
- **Why after B, not blocking D/F:** E0 needs the *entire* compliant core; EXP-0/EXP-1 don't. Running D and F in parallel keeps the critical path on E0.

### Wave H — EXP-2 affective indexing (M5) · ~2 days · risk: Medium · **parallelizable after Wave C**
- **Tasks:** EXP2-01 → EXP2-02 (decouple from soul concepts) → EXP2-03 → EXP2-04 → EXP2-05.
- **Dependency:** M0 + CORE-06/07 (soul decoupling). Independent of E0; can run parallel to Wave G.
- **Gate:** third-party task provenance (zero soul-concept overlap), objective task-score observable, pre-registered significance test. Closes G-06 (code side), G-17; wires kill G-11 (EXP-2 part).

### Wave I — Publication & reproducibility (M6) · ~2 days · risk: Low–Medium
- **Tasks:** (PUB-01 → PUB-02 → PUB-03) ∥ (PUB-04 → PUB-05).
- **Dependency:** results from Waves D/F/G/H.
- **Gate:** novelty verdict enforced, owning prior art cited, negative-result/methodology bundle + Docker repro build. Closes G-23.

---

## 4. Parallelization plan (2-engineer view)

| Calendar | Engineer 1 (core/experiments) | Engineer 2 (moves/precondition) |
|---|---|---|
| Days 1–2 | Wave A (RC-01..08, shared) | Wave A review + freeze existing build for EXP-0 |
| Days 3–5 | Wave B (CORE-*) | Wave D (EXP-0) — runs on frozen build |
| Days 6–8 | Wave F (EXP-1) after scoring lands | Wave C (archive/rename + shimmed moves) |
| Day 9 | — | Wave E (codemod, isolated) |
| Days 10–14 | Wave G (E0) | Wave H (EXP-2) |
| Days 15–16 | Wave I (publication) | Wave I (repro/Docker) |

**Single-engineer path:** A → B → D → C → E → F → G → H → I (EXP-0 slotted after core-scoring so it still runs on a frozen build snapshot taken at end of Wave A).

---

## 5. Continuous-runnability invariants

- **Every commit** keeps `pytest -m "not slow"` green (shims guarantee backward-compat until Wave E).
- **No experiment reports a result while any Tier-0 gap is open** (`IMPLEMENTATION_GAPS.md`): G-01/G-02 (core) and G-03/G-04 (EXP-0) and G-05 (docs) must be closed first.
- **CI grep-gate** (from CORE-TEST) blocks re-entry of `free_energy`, graph-isomorphism `M`, hand-set `λ`, and anthropomorphic live names on every push.
- **Code freeze during experiments (§7):** once a wave's experiment starts a scored run, `core/` is frozen — no commits to primitives until the run's artifact is written.

---

## 6. Order rationale against the four minimization targets

| Target | How this order minimizes it |
|---|---|
| **Engineering risk** | Highest-blast task (INFRA-08 codemod) is isolated to Wave E on a clean tree with a pre/post count gate; all other moves are shimmed and reversible per commit. |
| **Scientific risk** | Reconciliation (A) removes [REJECTED] misdirection before code; the keystone core (B) is proven canon-exact (CORE-TEST) before E0 consumes it; no "emergence" metric ships until null-referenced `M` passes `E[M|H₀]≈0`. |
| **Merge conflicts** | Doc-only wave (A) is disjoint from code waves; core extraction (B, new files) is disjoint from moves (C); the codemod (E) is a solo commit. Parallel engineers touch disjoint trees (`core/`+`experiments/` vs `backend/`→`infra/`). |
| **Dependency cycles** | Broken by construction: `core/` authored as new files, legacy refactored to import it (INFRA-07) only after CORE-TEST; experiments depend on `core/`, never the reverse. |

**First action (canonical §11):** begin **Wave A** now; take a frozen build snapshot at its end so **Wave D (EXP-0)** — the immediate scientific next step — can start immediately and in parallel with **Wave B (core)**.
