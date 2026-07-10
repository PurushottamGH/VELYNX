# PROGRAM A — DATAFLOW

**Authority:** Chief Systems Architect design review, 2026-07-07.
Tags: `[FACT]`, `[INFERENCE]`, `[RISK]`, `[OPEN QUESTION]`.

This document traces every datum that flows through the Program A → EXP-1
path, its type, its producer, and the guard that polices it. The three label
spaces are kept visually separate throughout, per the label-space guard
(`EXP1_PREREGISTRATION.md` §3; `EXP1_DATASET_SPEC.md` §5).

---

## 1. The three label spaces (must never substitute for one another)

| Label space | Producer | Values | Consumed by |
|---|---|---|---|
| Query family (stratification only) | frozen dataset | `known_factual`, `ambiguous_or_debated`, `hallucinated_unanswerable_or_false_premise` (`dataset.py:18-23`) | decision.py hard-hallucination counter; reporting |
| Confidence tier (predictor output only) | **Program A** | `UNKNOWN`, `DEBATED`, `PROBABLE`, `CERTAIN` (`dataset.py:17`) | calibration.py tier→p_i mapping |
| Correctness outcome (evaluation target) | adjudicator vs frozen gold rubric | `y_i ∈ {0,1}` | ECE accuracy term; independence test |

**[FACT]** ECE compares `p_i` (from the tier) to `y_i` (from the rubric) —
never tier to family, never family to correctness (preregistration §3, §5).

## 2. End-to-end dataflow

```
FROZEN INPUTS (immutable during execution)
  data/exp1_queries.json ──[MISSING, ML-5]──▶ FrozenDataset
      210 rows: query_id, query, query_family, gold_rubric, metadata
      guards: N=210 exact, 70/70/70, no dup ids/text, order_hash
              (dataset.py:289-317, 320-324)
  experiments/EXP1/config.json  ──▶ thresholds/mapping (frozen, matches prereg)
  seed list (22)                ──▶ runner

PER (query, seed):
  QueryRecord.query : str
      │
      ▼
  ⟪PLANNED⟫ Program A emission surface
      [A1] evidence acquisition
           in : query text (+ seed, + retrieval mode per Q2)
           out: evidence set (today's substrate shape: RetrievalReport —
                url/title/snippet/source/score; unified_retriever.py:24-58)
           guard: RetrievalSource.score MUST NOT flow toward the tier
                  (category error — prereg §5; BINDING_SPEC R1)
      [A2] answer construction
           in : evidence set
           out: answer : str  (answer, refusal, or uncertainty response)
           guard: no ReasoningTrace / kg / thermodynamic_state inputs
                  ([REJECTED], canon :90; TD-08)
      [A3] public tier emission
           in : Program A's own evidence state   [mechanism = Q1, OPEN]
           out: tier : str ∈ CONFIDENCE_TIERS
           guards: no 5→4 remap (prereg §4 kill #5)
                   no post-hoc calibration (prereg §6)
                   mechanism frozen before outputs observed (prereg §4 #5)
      │
      ▼  {answer, tier, raw_numeric_confidence?, metadata?}
  ⟪PLANNED⟫ Binding (Form A answer_fn / Form B adapter)
      pure field transport; stamps nothing, computes nothing
      │
      ▼
  _coerce_answer_record (run.py:242-258)
      injects query_id + seed on mapping returns; from_mapping validates tier
      [RISK F-10]: AnswerRecord *instances* bypass tier validation
      │
      ▼
  AnswerRecord ──────────────┬──────────────────────────────┐
      │                      │ answer text only             │ tier only
      ▼                      ▼                              ▼
  answers.jsonl        ⟪PLANNED⟫ Adjudicator          calibration.py
  (audit artifact)      in : QueryRecord.gold_rubric   confidence_for_tier
                              + AnswerRecord.answer     0.125/0.375/0.625/0.875
                        out: correctness ∈ {0,1},       4 locked equal-width bins
                             fabricated_factual_answer  │
                        guard: MUST NOT read tier or    │
                               family as correctness    │
                               evidence (prereg §3, §5) │
      ┌─────────────────────┴──────────────────────────┘
      ▼
  build_evaluated_records (dataset.py:352-390)
      joins answer + correctness + query_family (family re-attached from the
      frozen query, never from Program A)
      │
      ▼
  EvaluatedRecord[] ──▶ decide_seed (decision.py)
      ECE gate (<0.10) · chi-square tier-independence (α=0.05) ·
      ≥2 tiers emitted · 0 CERTAIN-fabrications on hallucinated family ·
      N≥200 · protocol_violation flag
      │
      ▼
  SeedDecision ×22 ──▶ decide_experiment
      all 22 must pass; pooled table = reporting only, cannot override
      │
      ▼
  experiment_decision.json  (+ execution_manifest.json: git_commit,
      dataset order_hash, program_a_adapter_id, adjudicator_id, seeds)
  [FACT TD-05] reliability.csv / calibration_report.md /
      experiment_summary.json NOT currently produced (report.py unwired)
```

## 3. Data that must NOT flow (verified prohibitions)

| Forbidden flow | Why | Citation |
|---|---|---|
| `RetrievalSource.score` → tier | retrieval relevance ≠ answer confidence | prereg §5; `PROGRAM_A_ADAPTER_AUDIT.md` F-3 |
| `ConfidenceGrade` (5-grade) → tier via remap | post-hoc tier remapping = kill | prereg §4 #5; F-4 |
| synthesizer `confidence` float → binned tier | post-hoc calibration prohibited | prereg §6; F-4 |
| emitted tier → adjudicator correctness | label-space guard | prereg §3, §5 |
| query_family → tier or correctness | stratification only | prereg §3; `EXP1_DATASET_SPEC.md` §5, §9 |
| EXP-1 outputs → any rubric/label/bin/threshold edit | protocol violation kill | prereg §4 #5; dataset spec §18 |
| frozen dataset rows → Program A tuning | leakage invalidates the freeze | dataset spec §12.2-12.3 |
| `raw_numeric_confidence` → ECE | exploratory only unless canon amended | prereg §1 line 35, §6 |
| run-time DB writes / telemetry perturbation from the binding | side-effect-free requirement | `PROGRAM_A_BINDING_SPEC.md` §4 |

## 4. Persistence and artifacts

**[FACT]** Written per seed: `seed_<seed>/answers.jsonl`, `evaluated.jsonl`,
`decision.json` (`run.py:200-208`); per experiment:
`execution_manifest.json`, `experiment_decision.json` (`run.py:173-174,
214-220`). All serialization via `records_to_jsonl` / sorted-key JSON —
deterministic byte output for identical inputs (`dataset.py:393-396`).

**[FACT]** No SQLite anywhere in this path (verified: `experiments/EXP1/*`
imports contain no DB access). Program A's product-side persistence, if any,
is out of the experimental dataflow by the side-effect-free rule.
