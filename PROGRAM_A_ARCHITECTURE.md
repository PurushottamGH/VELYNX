# PROGRAM A — ARCHITECTURE

**Authority:** Chief Systems Architect design review, 2026-07-07. Derives from
`PROGRAM_A_MASTER_SPECIFICATION.md`; every component classification verified
against disk this session. Tags: `[FACT]`, `[INFERENCE]`, `[RISK]`,
`[OPEN QUESTION]`.

---

## 1. Component inventory and disposition

| # | Component | Location | State on disk | Disposition for Program A |
|---|---|---|---|---|
| 1 | Adapter framework (`ProgramAAdapter`, `CallableProgramAAdapter`, `coerce_program_a_adapter`, `callable_identity`) | `experiments/EXP1/program_a_adapter.py` | **[FACT]** implemented, 25 unit + 3 integration tests passing | **REUSE UNCHANGED** — no new adapter class required (`PROGRAM_A_ADAPTER_AUDIT.md` §1) |
| 2 | `AnswerRecord` / `QueryRecord` / `EvaluatedRecord` schemas | `experiments/EXP1/dataset.py` | **[FACT]** implemented | **REUSE UNCHANGED** (F-10 guard fix is a separate reviewed change) |
| 3 | EXP-1 runner, ECE, decision, manifest | `experiments/EXP1/{run,calibration,decision,manifest}.py` | **[FACT]** implemented, preregistration-compliant (`EXP1_TRACE.md` Links 2,4,5) | **REUSE UNCHANGED** |
| 4 | Report + artifact-spec generators | `experiments/EXP1/{report,artifact_specs}.py` | **[FACT]** implemented but NOT wired into `run.py` (TD-05) | **REUSE — requires wiring** (separate reviewed change) |
| 5 | Retrieval substrate | `backend/retrieval/unified_retriever.py` | **[FACT]** live engineering code, sources-only | **REUSE AS SUBSTRATE** behind the new emission surface; determinism caveat (R-06) |
| 6 | Answer synthesizer | `backend/cognition/answer_synthesizer.py` | **[FACT]** live, 5-grade taxonomy, `[REJECTED]` deps (ReasoningTrace, thermodynamic_state, kg) | **NEVER REUSE in the EXP-1 path** (F-4, F-5, TD-08; kill criteria R2/R3) |
| 7 | Reasoning engine | `backend/cognition/reasoning_engine.py` | **[FACT]** live | **NEVER REUSE** — type-lifting `[REJECTED]` (canon `:90`) |
| 8 | Soul graph + 32 concepts | `backend/soul/` | **[FACT]** live | **NEVER REUSE — ISOLATE** (canon `:90`) |
| 9 | Self-model / identity | `backend/self_model/` | **[FACT]** live | **NEVER REUSE — ISOLATE** (canon `:90`) |
| 10 | Free-energy policy | `research/policies/free_energy.py` | **[FACT]** live | **NEVER REUSE — ISOLATE** (canon `:90`, R1 p=0.866) |
| 11 | C8 Replay Engine / dream_state / memory scheduler | `backend/cognition/{replay_engine,dream_state,memory_scheduler}.py` | **[FACT]** live | **OUT OF SCOPE** — no role in the EXP-1 path (replay.md §8) |
| 12 | Canonical answer+tier emission surface | — | **[FACT]** does not exist | **BUILD** — the one new component; requires preregistered mechanism spec + ScientificAuditor sign-off |
| 13 | Concrete binding (Form A/B) | — | **[FACT]** does not exist | **BUILD** — ~20-line field transport, blocked on #12 + Architect location decision |
| 14 | Rubric adjudicator | — | **[FACT]** does not exist (`rubric.py:3-4` validates only) | **BUILD** — separate spec (EXP-1 link 3, not a Program A component) |
| 15 | Frozen 210-row dataset | `data/exp1_queries.json` | **[FACT]** does not exist | **BUILD** per `EXP1_DATASET_SPEC.md` (not a Program A component) |

## 2. Layer placement

**[FACT]** Boundary rules (`.agents/skills/velynx-core/architecture.md` §4):
`core/` is a leaf; `experiments/` must not import `backend/` except via the
documented `research/` composition layer; `backend/` may import `core/` but
never the reverse.

**[FACT]** Candidate lawful homes for the new emission surface + binding
(`PROGRAM_A_BINDING_SPEC.md` §5 Step 4 — Architect decision pending):
1. `research/` composition layer — already composes backend components
   side-effect-free without mutating them (architecture.md §4 evidence 4).
2. `program_a/` — currently empty; using it means actually populating the
   Program A package (consistent with canon §9-DeepSeek's intended split, but
   `program_a/` is not in `pyproject.toml` packages.find, so shipping
   requires a packaging change).
3. `scripts/` — a runner-argument constructor only; weakest option for a
   durable surface.

**[INFERENCE]** Options 1 and 2 are both boundary-legal. Option 3 is legal
but leaves the product surface homeless. The decision is reserved to the
Architect (`PROGRAM_A_BINDING_SPEC.md` open item 1) — **[OPEN QUESTION]** Q4.

## 3. Target architecture (implied, not invented)

```
                         ┌──────────────────────────────────────────────┐
                         │  PROGRAM A (to be built, location per Q4)    │
                         │                                              │
   query.query ─────────▶│  [A1] Evidence acquisition                   │
                         │       (reuses backend UnifiedRetriever       │
                         │        behind the composition boundary;      │
                         │        snapshot/live mode = Q2)              │
                         │            │ evidence                        │
                         │            ▼                                 │
                         │  [A2] Answer construction                    │
                         │       (no ReasoningTrace, no kg, no          │
                         │        thermodynamic state)                  │
                         │            │ answer: str                     │
                         │            ▼                                 │
                         │  [A3] Public tier emission                   │
                         │       tier ∈ {UNKNOWN,DEBATED,PROBABLE,      │
                         │       CERTAIN}; mechanism preregistered      │
                         │       & frozen before execution (Q1)         │
                         └────────────┬─────────────────────────────────┘
                                      │ (answer, tier, raw_numeric?, metadata)
                                      ▼
                     [A4] Binding — Form A answer_fn or Form B adapter
                          pure transport → AnswerRecord.from_mapping
                                      │
                                      ▼
        experiments/EXP1/run.py  run_experiment(program_a_adapter=..., ...)
             (existing, unchanged: coercion → adjudicator → ECE → decision)
```

**[FACT]** A1-A3 constitute the "canonical Program A answer+tier emission
component" of `PROGRAM_A_BINDING_SPEC.md` §6 (row NEW). A4 is its §5 Step 3.

## 4. Isolation requirements for [REJECTED] systems

**[FACT]** Canon `:90` permanently removes (live use forbidden): the 32 soul
concepts, hand-authored ontology, self-model, reasoning-engine type-lifting,
"resonance / sleep-replay / thermodynamic state", `E = λH+μS+νA`.

**[FACT]** TD-08 records that these persist as importable live code with **no
CI guard** preventing `experiments/` or the future Program A surface from
importing them.

**[INFERENCE]** Required isolation, in strength order:
1. The new emission surface must not import `backend.cognition.{
   answer_synthesizer, reasoning_engine, dream_state}`, `backend.soul.*`,
   `backend.self_model.*`, or `research.policies.free_energy`.
2. **[RISK → recommended]** An import-guard test (deny-list on the emission
   surface's transitive imports) is the cheapest mechanical enforcement;
   none exists today (TD-08). This is an engineering control, not a
   scientific rule — it needs Reviewer sign-off only.

## 5. What already protects the architecture

- **[FACT]** Tier whitelist at the mapping boundary
  (`dataset.py:140-141`; `from_mapping` rejects the 5-grade taxonomy —
  tested: `test_from_mapping_rejects_non_canonical_synthesizer_grades`).
- **[FACT]** Manifest identity checks (`run.py:143-164`) reject
  adapter/adjudicator/dataset substitutions against a provided manifest.
- **[FACT]** `validate_answer_records` enforces exactly-one-answer-per-row
  (`dataset.py:327-349`).
- **[FACT]** Label-space guard encoded in `build_evaluated_records`
  docstring + structure (`dataset.py:352-390`).

## 6. Known architectural defects to carry

- **[FACT]** F-10: `AnswerRecord.__init__` does not validate tier; a
  direct-constructed record with a non-canonical tier propagates to a
  `KeyError` in `calibration.confidence_for_tier`
  (`PROGRAM_A_ADAPTER_AUDIT.md` §7). Fix = production change requiring
  Reviewer + ScientificAuditor sign-off.
- **[FACT]** TD-05: `report.py`/`artifact_specs.py` unwired — a compliant run
  today would not emit `reliability.csv`, `calibration_report.md`,
  `experiment_summary.json`, or the `.spec.json` schemas the
  `EXECUTION_GUIDE.md:64-76` contract requires.
- **[FACT]** `ARCHITECTURE_MAP.md:54` row 6 still claims `program_a/` is
  LIVE — documentation correction is open item 5 of the binding spec.
