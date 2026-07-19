# PROGRAM A — IMPLEMENTATION ROADMAP

**Authority:** Chief Scientist / Chief Systems Architect design review,
2026-07-07. This roadmap sequences existing obligations from the repository;
it introduces no new scientific rules. Gates marked **G** are sign-off
gates that this review cannot discharge (specialists required — R-08).
Standing conditions from `RESEARCH_DIRECTOR_DECISION.md` §8 apply throughout:
C-1 landed (integrity), E0-v2 tracked separately, **EXP-0 must run before or
alongside EXP-1 and before any external Program-A honesty claim**.

---

## Phase 0 — Decisions (no code)

| # | Task | Owner | Blocked by | Exit criterion |
|---|---|---|---|---|
| **G1** | Adjudicate the lawful location of the emission surface + binding (`research/` vs `program_a/` vs `scripts/`; packaging implication R-16) | Architect | specialist availability (R-08) | written location decision (BINDING_SPEC open item 1) |
| **G2** | Rule on tier-source lawfulness: confirm no existing surface lawfully emits canonical tiers; future surface must emit them natively | ScientificAuditor | R-08 | PASS/FAIL ratifying the Director's provisional conclusion (BINDING_SPEC open item 2) |
| **G3** | Ratify or overturn the Goodhart-guard categorization (passive + flag vs active detector EXP1-05) | ScientificAuditor | R-08 | `EXP1_TRACE.md` ML-14 dissent resolved (R-12) |
| **T0** | Resolve Q2 (frozen retrieval snapshot vs live web) and Q3 (seed-variance source) as written design decisions | Architect + ScientificAuditor | G1, G2 | decisions recorded in the mechanism spec (T1) |

## Phase 1 — The mechanism specification (the scientific-path item)

| # | Task | Owner | Blocked by | Exit criterion |
|---|---|---|---|---|
| **T1** | Author the **Program A tier-emission mechanism specification**: the frozen rule mapping Program A's evidence state → one of the four tiers, plus the answer/refusal construction rule. Must not reference EXP-1 outcomes, bins, or the tier→probability mapping. | Builder (spec draft) + ScientificAuditor (approval) | G2, T0 | preregistration-style document committed; ScientificAuditor sign-off (`PROGRAM_A_ADAPTER_AUDIT.md` §6 item 6) |
| **G4** | Freeze the mechanism spec before any frozen-row output is observed | Release Manager | T1 | pinned commit recorded |

*Note: this review deliberately does not draft the tier rule — inventing
confidence-tier semantics is forbidden (canon §1 rule 5 territory; brief
prohibition). Q1 in `PROGRAM_A_OPEN_QUESTIONS.md` frames the decision space
without deciding it.*

## Phase 2 — Dataset freeze (parallel with Phase 1; independent team)

| # | Task | Owner | Blocked by | Exit criterion |
|---|---|---|---|---|
| **T2** | Author, review, audit, hash, and freeze the 210-row dataset + rubrics per `EXP1_DATASET_SPEC.md` §17 (10-step protocol) | Experiment Engineer → Reviewer → ScientificAuditor → Release Manager | none (spec exists) | `data/exp1_queries.json` present, `load_frozen_dataset` passes, manifest + checksums frozen (clears ML-5) |
| **T3** | Implement the frozen-rubric adjudicator (EXP-1 link 3) per prereg §3 + dataset-spec §8; separate spec, not a Program A component | Builder + Reviewer + ScientificAuditor | T2 | adjudicator returns `{correctness, fabricated_factual_answer}` vs rubric only; leakage of tier/family into correctness structurally impossible (clears ML-4; guards FM-12) |

## Phase 3 — Build (small, mechanical once Phase 1 exists)

| # | Task | Owner | Blocked by | Exit criterion |
|---|---|---|---|---|
| **T4** | Implement the emission surface exactly per the frozen T1 spec, in the G1 location; reuse `UnifiedRetriever` per T0 mode; stateless, seeded, side-effect-free | Builder | G1, G4 | determinism + purity tests pass; no forbidden imports |
| **T5** | Wire `report.py` + `write_artifact_specifications` into `run.py` (TD-05 / ML-9 / ML-10) | Builder + Reviewer | none (independent) | a dry run emits `reliability.csv`, `calibration_report.md`, `experiment_summary.json` + `.spec.json` per `EXECUTION_GUIDE.md:64-76` |
| **T6** | Fix F-10: enforce tier validation on direct `AnswerRecord` construction (or re-validate in `_coerce_answer_record`) | Builder + Reviewer + ScientificAuditor | none (independent) | `test_direct_construction_does_not_validate_tier` inverted to a rejection test |
| **T7** | Add the import-guard test enforcing `PROGRAM_A_DEPENDENCY_GRAPH.md` §4 deny-list (TD-08 mitigation) | Builder + Reviewer | G1 | CI fails on any forbidden transitive import |
| **T8** | Implement the ~20-line binding (Form A or B per Architect preference), `adapter_id="program-a-public-v1"`; construct records via `from_mapping` | Builder | T4, G1 | binding passes end-to-end through `run_seed_sync` on a synthetic corpus (test pattern already exists: `tests/EXP1/test_program_a_adapter_integration.py`) |
| **G5** | Reviewer PASS on T4-T8 code | Reviewer | T4-T8 | recorded review (BINDING_SPEC open item 4) |

## Phase 4 — Execution

| # | Task | Owner | Blocked by | Exit criterion |
|---|---|---|---|---|
| **T9** | Run EXP-0 (paraphrase precondition, ~1 day, frozen code) if not yet run | Experiment Engineer | none | Research Director condition 3 satisfied (`RESEARCH_DIRECTOR_DECISION.md` §8) |
| **T10** | Dry run: full pipeline on a synthetic (non-frozen) corpus; verify artifacts, manifest, determinism/replay | Experiment Engineer | T3, T5, T8 | byte-identical re-run; all `EXECUTION_GUIDE.md` outputs present |
| **G6** | Pre-run lock verification: dataset hash, config, mechanism-spec commit, adapter/adjudicator identities | Release Manager | T2, G4, T10 | `EXECUTION_GUIDE.md` prerequisites all checked; Research Director spot-check of frozen rubric (condition 4) |
| **T11** | Execute EXP-1: 22 preregistered seeds over the frozen 210-row set; no post-output changes of any kind | Experiment Engineer | G6, T9 | 22 `SeedDecision`s + `ExperimentDecision` + full artifact set; outcome reported faithfully (pass or kill) |

## Dependency summary

```
G1 ─┬─▶ T4 ─▶ T8 ─▶ G5 ─▶ T10 ─▶ G6 ─▶ T11
G2 ─┴─▶ T0 ─▶ T1 ─▶ G4 ────────────▲    ▲
T2 ─▶ T3 ───────────────────────────┘    │
T5, T6, T7 (independent) ────────────────┘
G3 — must resolve before any PASS claim (not before execution)
T9 — before or alongside T11
```

**[INFERENCE]** Critical path: **G1/G2 → T1 → G4 → T4 → T8 → T10 → G6 →
T11**. Everything else parallelizes. The single longest-lead item is T2
(authoring 210 publication-quality rows + rubrics with provenance).
