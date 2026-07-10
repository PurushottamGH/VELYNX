# PROGRAM A — IMPLEMENTATION ORDER

**Authority:** Lead Systems Architect, 2026-07-08.
**Function:** the implementation dependency graph over the modules of
`PROGRAM_A_MODULE_SPEC.md`, and the smallest possible implementation order.
Governance dependencies (specialist gates) are shown as hard predecessors —
per `ES1_IMPLEMENTATION_GATE.md`, **no emission-surface or binding code may be
written before the gate flips to GO**; only the explicitly gate-independent
items (marked ◇) may start now.

---

## 1. Implementation dependency graph

Nodes are modules/artifacts; edges point from prerequisite to dependent.
`[GOV]` = governance gate (not code). `◇` = may start before GO.

```
[GOV] G1 location ruling ─────────────────┐
[GOV] G2 tier-source ratification ──┐     │
[GOV] A3 (Q2 snapshot mode) ────────┤     │
[GOV] A4 (Q3 prereg §7 amendment) ──┤     │
                                    ▼     │
[GOV] T1 preregistration ──► [GOV] G4 freeze (pinned commit)
                                    │
        ┌───────────────────────────┴────────────── GO ──────────┐
        ▼                                                        │
◇ pyproject packaging line (R-16)                                │
        │                                                        │
        ▼                                                        ▼
  program_a/types.py  (leaf) ◄──────────────── program_a/constants.py
        │                                            (contents = T1 register;
        ├──────────────┬──────────────────┐           digest pinned at G4)
        ▼              ▼                  ▼
  evidence/       extraction/        mechanism/
  snapshot_format claim_extraction   support_tests
        │              │                  │
        ▼              │                  ▼
  evidence/            │             mechanism/evidence_states
  snapshot_store       │                  │
        │              │                  │
        └──────┬───────┴──────────────────┘
               ▼
     mechanism/emission  (public surface: answer_query, mechanism_id)
               │
               ▼
     binding/exp1_binding  (imports experiments.EXP1.{dataset,program_a_adapter})
               │
               ▼
     program_a/__init__.py exports
               │
               ▼
     tests/program_a/test_replay.py end-to-end (T10 mechanics)

  Side chains (build alongside their targets):
  ◇ tests/program_a/test_import_guard.py  — needs only the ruled location (G1);
      binds every later module (gate C3)
  evidence/snapshot_builder.py — needs snapshot_format; produces the FROZEN
      SNAPSHOT artifact, which must pass leakage review (A3) before any
      frozen-row execution; execution-time modules depend only on the
      artifact's existence, not on the builder module
  each test module — immediately after its production module (test-with, not
      test-after)

  External (not Program A; EXP-1 obligations that gate execution, not build):
  frozen 210-row dataset (T2, ML-5) · rubric adjudicator (T3, ML-4) ·
  report/artifact_specs wiring (T5, TD-05) · EXP-0 run-state (T9)
```

Key structural facts the graph encodes:
- `types.py` and `constants.py` are the only fan-in roots; everything else is
  a straight pipeline PA-1→PA-2→PA-3→PA-4→PA-5.
- `constants.py` cannot be written before T1 is frozen — its contents ARE the
  T1 free-constant register (writing it earlier would freeze constants before
  their preregistration, inverting CR-6).
- The import-guard and packaging line are gate-independent (pure enforcement /
  packaging, no science) and should land first so every subsequent commit is
  guarded from its first push (TD-08 lesson).
- The already-fixed F-10 guard (`dataset.py:112-122`) and the existing
  sentinel test (`test_cheat_channel_guard.py`) mean gate boxes C1/C2 need
  re-verification against the real surface, not new construction.

## 2. Smallest implementation order

Ten steps; each is one reviewable commit; no step starts before its
predecessors and its governance predecessors. Steps 1–2 may start today.

| # | Step | Builds | Preconditions | Done when |
|---|---|---|---|---|
| **1** ◇ | Packaging + skeleton | `pyproject.toml` line (R-16); real (non-empty) `program_a/` package dirs | none (G1 ratification before merge) | package importable; ships in build |
| **2** ◇ | Import guard first | `tests/program_a/test_import_guard.py` (deny-list + planted-import self-test) | step 1 | CI fails on any forbidden transitive import of `program_a/**` |
| **3** | Value types | `types.py` (+ structural-guard test) | step 1; **GO** | frozen types; no score/timestamp/rubric fields representable |
| **4** | Frozen constants | `constants.py` | step 3; **T1 frozen at G4** | digest pinned = G4 commit; no evaluation-side numbers |
| **5** | Evidence layer | `snapshot_format.py`, `snapshot_store.py` + tests | steps 3–4 | integrity/determinism/no-network/ordering tests green |
| **6** | Snapshot builder + frozen snapshot | `snapshot_builder.py`; build the execution snapshot | step 5; A3 leakage-review procedure named | snapshot built, hashed, leakage review passed and recorded |
| **7** | Claim extraction | `claim_extraction.py` + tests | steps 3–4 | determinism + fabrication-negative tests green |
| **8** | ES-1 core | `support_tests.py`, `evidence_states.py` + tests | steps 4, 7 | state-table, precedence, exclusivity, constants-digest tests green |
| **9** | Public surface | `emission.py`, `__init__.py` exports + tests | steps 5, 8 | CR-4/5/9/14 tests green; `mechanism_id()` stable |
| **10** | Binding + end-to-end | `exp1_binding.py` + `test_binding.py`; extend sentinel test; `test_replay.py` | step 9 | `run_seed_sync` end-to-end on synthetic corpus; sentinel byte-identical; byte-identical replay (T10 mechanics) → hand to G5 review |

Minimality argument: 10 commits is the floor at one-reviewable-unit
granularity — each step is a distinct dependency-graph layer or a distinct
sign-off surface (packaging, guard, types, constants, evidence, snapshot
artifact, extraction, mechanism, surface, seam); merging any two either mixes
a governance boundary (e.g. constants into types would put T1 content in a
pre-GO commit) or creates an unreviewably mixed diff (e.g. mechanism +
emission mixes the frozen rule with its consumer). Steps 5–7 (and their
tests) are parallelizable across two builders; the critical path is
1→3→4→8→9→10.

## 3. Critical path and what is NOT on it

**Critical path (code):** 1 → 3 → 4 → 8 → 9 → 10.
**Critical path (overall):** G2/G1 → T0(A3,A4) → T1 → G4 → steps 3–10 → G5
review → T10 dry run → G6 lock → T11 execution — identical shape to
`PROGRAM_A_IMPLEMENTATION_ROADMAP.md`'s summary, with T4 expanded into steps
3–9 and T8 = step 10.

Not on Program A's build path (parallel, other owners): the frozen dataset
(T2 — the single longest-lead item per the roadmap), the adjudicator (T3),
report wiring (T5), EXP-0 (T9), and the G3/Q5/Q6 rulings (pass-claim
prerequisites, not build prerequisites).

## 4. Change-control rule after step 4

From the moment `constants.py` lands (= G4 freeze reflected in code), any
change to `constants.py`, `support_tests.py`, `evidence_states.py`, the
emission templates, the snapshot artifact, or the PA-1 ordering rule is a
**mechanism change**: it requires a T1 revision + re-freeze + new
`SPEC_VERSION` + new `mechanism_id()` **before** any frozen-row output is
observed, and is flatly prohibited after (prereg §4 #5; CR-6). Dry-run
findings route back to step 4 via Wave 2 (redesign + refreeze), never via
in-place edits (B-11 scope limit).
