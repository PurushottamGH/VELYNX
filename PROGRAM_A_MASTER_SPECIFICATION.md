# PROGRAM A — MASTER SPECIFICATION

> [!NOTE]
> **Reconciliation Note (Package Layout Resolution):** The empty stub layout references are stale. The package layout has been resolved to the 4-package design documented in `PROGRAM_A_FINAL_ARCHITECTURE.md`.

**Authority:** Chief Scientist / Chief Systems Architect design review, 2026-07-07.
**Method:** Every claim verified against the file on disk this session and cited
to `file:line` or document section. Epistemic tags are binding:
`[FACT]` (verified), `[INFERENCE]` (derived from verified facts),
`[RISK]`, `[OPEN QUESTION]`, `[SPECULATION]` (none permitted load-bearing).
**Relationship to canon:** This document derives from `PROGRAM_D_CANONICAL.md`
(§2, §3, §6-H1, §7) and `EXP1_PREREGISTRATION.md`. It invents no scientific
rule, no confidence-tier semantics, no calibration logic, and no replay logic.
Where the repository does not determine a behavior, that behavior is recorded
as `[OPEN QUESTION]`, not specified.
**Companion documents:** `PROGRAM_A_ARCHITECTURE.md`,
`PROGRAM_A_SEQUENCE_DIAGRAM.md`, `PROGRAM_A_DATAFLOW.md`,
`PROGRAM_A_PUBLIC_API.md`, `PROGRAM_A_DEPENDENCY_GRAPH.md`,
`PROGRAM_A_RISK_REGISTER.md`, `PROGRAM_A_FAILURE_ANALYSIS.md`,
`PROGRAM_A_IMPLEMENTATION_ROADMAP.md`, `PROGRAM_A_OPEN_QUESTIONS.md`.

---

## 1. What Program A actually is

**[FACT]** The canon defines Program A as the "live-truth retrieval engine.
Scientific claim: **honest uncertainty (calibration)**. Status: engineering
product, *not* the research center" (`PROGRAM_D_CANONICAL.md:42`).

**[FACT]** It is surviving deliverable #1 of the 2026-07-02 PI REDESIGN
decision: "Program A as an honest product — gated strictly on EXP-1
(calibration, ECE < 0.10). Currently **[REJECTED]**-state: emits `CERTAIN` on
hallucinated content (`soul_test_report.md` Q6)" (`PROGRAM_D_CANONICAL.md:55`).

**[FACT]** On disk, Program A **does not exist as code**. `program_a/` contains
exactly two 0-byte files: `program_a/retrieval/__init__.py` and
`program_a/nlp/__init__.py` (verified this session; matches
`PROGRAM_A_ADAPTER_AUDIT.md` F-1). `ARCHITECTURE_MAP.md:54` row 6 claims
`program_a/` is "LIVE" — that claim is recorded as inaccurate by
`PROGRAM_A_ADAPTER_AUDIT.md` F-2 and re-verified false this session.

**[FACT]** The functional fragments that *approximate* Program A live in
`backend/` (not shipped, `pyproject.toml` excludes `backend*`):
- `backend/retrieval/unified_retriever.py:61-202` — `UnifiedRetriever`, a
  never-fail multi-source web retrieval chain (Wikipedia, DuckDuckGo, Brave,
  Tavily, arXiv). Emits `RetrievalReport` (sources only: url/title/snippet/
  source/score). **No answer text, no confidence tier**
  (`unified_retriever.py:24-58`).
- `backend/cognition/answer_synthesizer.py:83-247` — `AnswerSynthesizer`, a
  deterministic formatter over a `ReasoningTrace`. Emits a **5-grade** label
  `{CERTAIN, PROBABLE, UNCERTAIN, SPECULATIVE, INSUFFICIENT}` from hand-set
  numeric bands 0.90/0.70/0.50/0.25/0.00 (`answer_synthesizer.py:32-47`) and
  depends on the reasoning engine, a knowledge graph, and a
  "thermodynamic state" (`answer_synthesizer.py:106-165`) — all `[REJECTED]`
  as load-bearing science by `PROGRAM_D_CANONICAL.md:90`.

**[INFERENCE]** What Program A must become, as implied by the repository: a
**canonical answer+tier emission surface** — a component that, given a query,
produces exactly one natural-language answer (or refusal/uncertainty response)
and exactly one public confidence tier in `{UNKNOWN, DEBATED, PROBABLE,
CERTAIN}`, deterministically per `(query, seed)`, side-effect-free, with a
stable manifest identity — connected to EXP-1 through the existing,
fully-tested adapter framework (`experiments/EXP1/program_a_adapter.py`).
This is the exact missing object named by `PROGRAM_A_BINDING_SPEC.md` §4-§6
and `EXP1_TRACE.md` ML-1.

---

## 2. Scientific purpose

**[FACT]** Program A carries exactly one live hypothesis: **H1 — Retrieval
Uncertainty Calibration** (`PROGRAM_D_CANONICAL.md:104-111`): the public
confidence tiers report empirical correctness matching the tier.
- Observable: Expected Calibration Error (ECE).
- Pass gate: **ECE < 0.10**; kill: ECE ≥ 0.10 or tier-independence
  (single gate, no 0.10–0.15 dead zone — canon §10 Issue-4).
- Protocol: EXP-1, preregistered in `EXP1_PREREGISTRATION.md` (22 seeds,
  N=210 frozen queries, 4 locked equal-width bins, locked tier→probability
  mapping 0.125/0.375/0.625/0.875).

**[FACT]** H1's current status is **[REJECTED]** (canon `:111`): the deployed
system emitted `CERTAIN` on hallucinated content (Q6 anchor, canon `:146`).
EXP-1 is the only path by which Program A can shed that status.

**[FACT]** Program A is explicitly **not** the research center (canon `:42`).
Its scientific role is limited to H1. It carries no part of H\* (E0) or H2
(EXP-2).

---

## 3. Engineering purpose

**[FACT]** Program A is the product deliverable: a retrieval-plus-synthesis
question-answering surface whose selling claim is honesty about its own
uncertainty (canon §3 deliverable 1). `PROGRAM_D_MASTER_ROADMAP.md:127`
records it as "priority-1 among the three surviving deliverables."

**[INFERENCE]** Its engineering purpose within the current sprint is narrower:
provide the injected `answer_fn`/adapter that lets EXP-1 execute end-to-end.
Every other EXP-1 component (runner, ECE, decision, manifest, adapter
framework) is implemented and preregistration-compliant (`EXP1_TRACE.md`
Links 2, 4, 5, 6a-b; 64 passing tests per `PROGRAM_A_ADAPTER_TEST_PLAN.md` §6).

---

## 4. Public interfaces (all already exist; Program A must satisfy them)

**[FACT]** The EXP-1-facing contract is fixed and tested:

| Interface | Location | Contract |
|---|---|---|
| `ProgramAAdapter` Protocol | `experiments/EXP1/program_a_adapter.py:18-27` | `adapter_id: str` property + `answer(query: QueryRecord, seed: int) -> ProgramAAnswer` |
| `ProgramAAnswer` | `program_a_adapter.py:15` | `AnswerRecord \| Mapping \| Awaitable` |
| `CallableProgramAAdapter` | `program_a_adapter.py:30-44` | frozen dataclass wrapping any `answer_fn`; no new adapter class needed |
| `AnswerRecord` | `experiments/EXP1/dataset.py:101-151` | `query_id`, `answer: str`, `tier ∈ CONFIDENCE_TIERS`, optional `seed`, `raw_numeric_confidence`, `metadata` |
| `CONFIDENCE_TIERS` | `dataset.py:17` | `("UNKNOWN", "DEBATED", "PROBABLE", "CERTAIN")` — the only accepted values |
| Runner injection | `experiments/EXP1/run.py:50-70, 114-134` | `answer_fn` / `program_a_adapter` / `program_a_adapter_id` |
| Manifest identity | `experiments/EXP1/manifest.py` (`program_a_adapter_id`) | stable adapter identity recorded per run |

**[FACT]** The internal public surface Program A itself must expose — the
canonical answer+tier emission component — **does not exist** and is the
single blocking object (`PROGRAM_A_BINDING_SPEC.md` §5 Step 2: BLOCKED;
§6 row "NEW"). Its required signature is specified in
`PROGRAM_A_PUBLIC_API.md`; its tier-decision *mechanism* is an
`[OPEN QUESTION]` requiring its own preregistration + ScientificAuditor
sign-off (`PROGRAM_A_ADAPTER_AUDIT.md` §6 item 6).

---

## 5. Internal pipeline

**[INFERENCE]** (from `PROGRAM_A_BINDING_SPEC.md` §2, the retriever/synthesizer
surfaces, and the EXP-1 contract) the implied internal pipeline is:

```
query text
   │
   ▼
[1] Retrieval          — evidence gathering (candidate reuse:
                          UnifiedRetriever, engineering-clean, sources-only)
   │  RetrievalReport (sources)
   ▼
[2] Answer synthesis   — produce answer text / refusal from evidence.
                          MUST NOT route through ReasoningTrace /
                          thermodynamic_state / kg ([REJECTED], canon :90)
   │  answer: str
   ▼
[3] Tier emission      — produce tier ∈ {UNKNOWN, DEBATED, PROBABLE, CERTAIN}
                          as a PUBLIC emission from Program A's own evidence
                          state. MUST NOT be retrieval-relevance rebadged
                          (kill: EXP1_PREREGISTRATION §5), a 5→4 remap
                          (kill: §4 #5), or a post-hoc binning of a float
                          fit to outcomes (kill: §6). Mechanism: [OPEN QUESTION]
   │  (answer, tier)
   ▼
[4] Binding            — pure field transport into AnswerRecord via
                          from_mapping (≈20 lines, BINDING_SPEC §5 Step 3)
   │  AnswerRecord(query_id, answer, tier, seed, ...)
   ▼
EXP-1 runner (existing, wired)
```

Stages [2] and [3] are the missing scientific-adjacent design work; stage [4]
is trivial once they exist; stage [1] has a reusable engineering substrate
with determinism caveats (`PROGRAM_A_RISK_REGISTER.md` R-06).

---

## 6. Canonical AnswerRecord production

**[FACT]** Per `EXP1_PREREGISTRATION.md` §1 and `dataset.py:101-151`, for every
frozen query row Program A emits exactly one record:

| Field | Rule | Source |
|---|---|---|
| `query_id` | echo `query.query_id` | preregistration §1 |
| `answer` | the natural-language answer or refusal/uncertainty response returned to the user | preregistration §1 |
| `tier` | the emitted **public symbolic** tier; the only input to ECE | preregistration §1 ("not any hidden retrieval score, embedding distance, source count, or post-hoc evaluator score") |
| `seed` | the injected replicate seed; `_coerce_answer_record` (`run.py:242-258`) enforces the match | run.py:249-251 |
| `raw_numeric_confidence` | optional; **ignored for primary ECE** unless canon is amended before implementation | preregistration §1 line 35, §6 |
| `metadata` | optional dict | dataset.py:110 |

**[FACT]** Construction must go through `AnswerRecord.from_mapping` (or
guarantee a canonical tier), because direct construction bypasses tier
validation — the F-10 guard gap (`PROGRAM_A_ADAPTER_AUDIT.md` §7;
`dataset.py:113-141`: `validate()` is called in `from_mapping` but not in
`__init__`).

---

## 7. Canonical confidence-tier production

**[FACT]** What the repository fixes about tier production:
1. The tier set is exactly `{UNKNOWN, DEBATED, PROBABLE, CERTAIN}`
   (`dataset.py:17`; canon §6-H1).
2. The tier must be Program A's **public confidence emission** — "not
   retrieval relevance, not a post-hoc remap"
   (`PROGRAM_A_BINDING_SPEC.md` §4 table; `EXP1_PREREGISTRATION.md` §1, §5).
3. The tier→probability mapping (0.125/0.375/0.625/0.875) and 4 equal-width
   bins are **evaluation constants owned by EXP-1**
   (`experiments/EXP1/calibration.py`; `EXP1_DATASET_SPEC.md` §4 "evaluation
   constants, not dataset tunables"). Program A must not implement, mirror,
   or fit to them.
4. Post-hoc calibration is **prohibited** (`EXP1_PREREGISTRATION.md` §6).
5. The mechanism must be frozen before EXP-1 outputs are observed
   (frozen-code rule, canon §7 line 130; preregistration §4 kill #5).

**[FACT]** What the repository does **not** fix: the internal rule by which
Program A maps its evidence state to one of the four tiers. No document
specifies it, and inventing it here is forbidden. **[OPEN QUESTION]** — this
is the primary open design decision; see `PROGRAM_A_OPEN_QUESTIONS.md` Q1.
`PROGRAM_A_ADAPTER_AUDIT.md` §6 item 6 and `PROGRAM_A_BINDING_SPEC.md` open
item 3 both route it through its own preregistration + ScientificAuditor
sign-off.

---

## 8. Determinism guarantees

**[FACT]** Required by `PROGRAM_A_BINDING_SPEC.md` §4: the binding must be
"deterministic (explicit seed, no hidden state), side-effect free within the
experiment (no DB writes, no telemetry perturbation of the run), and
replay-compatible."

**[FACT]** Engineering invariant 7 (`.agents/skills/velynx-core/
architecture.md` §6): "Determinism first. Every randomized path takes an
explicit seed."

**[FACT]** The adapter framework already enforces seed plumbing: `seed` is
passed to `answer(query, seed)` (`run.py:84,181`) and validated on the
returned record (`run.py:249-251`). Adapter determinism given a deterministic
`answer_fn` is tested (`tests/EXP1/test_program_a_adapter.py`
`test_answer_is_deterministic_and_side_effect_free`).

**[RISK]** `UnifiedRetriever` is **not** deterministic: it queries the live
web with per-source timeouts, wall-clock timestamps
(`unified_retriever.py:31,156`), and env-var-gated sources
(`:346,362`). A Program A built directly on live retrieval cannot satisfy
per-`(query, seed)` determinism or byte-identical replay.
`EXP1_PREREGISTRATION.md` §7 *anticipates* "seed-level stochasticity in
retrieval" (that is why 22 seeds exist), so live retrieval is not banned by
the preregistration — but reproducibility policy (`EXP1_DATASET_SPEC.md` §15
"Provider independence" for dataset/rubrics) and the replay requirement pull
toward a frozen retrieval snapshot. **[OPEN QUESTION]** Q2.

---

## 9. Replay compatibility

**[FACT]** The backend Replay Engine (`backend/cognition/replay_engine.py`)
is the C8 memory-consolidation sandbox simulator (see
`.agents/skills/velynx-core/replay.md`). **It has no role in Program A's
EXP-1 path.** "There is no replay engine in `core/`" (replay.md §8), and the
research replay harness wraps consolidation policy studies, not question
answering.

**[INFERENCE]** "Replay compatibility" for Program A means **experiment
re-execution**, not the C8 simulator: given the frozen dataset (verified by
`order_hash`, `dataset.py:320-324`), the frozen config, the recorded
`program_a_adapter_id` and `adjudicator_id`
(`experiments/EXP1/manifest.py`), and the seed list, a re-run must reproduce
the recorded answers and decisions. This requires §8 determinism and the
stable manifest identity the framework already records. No new replay logic
may be invented (forbidden by the brief; none is needed).

---

## 10. SQLite interactions

**[FACT]** Backend rule: all `backend/` SQLite goes through
`backend/memory/_sqlite.py` (architecture.md §4 rule 3, §6 invariant 9).
**[FACT]** Within an EXP-1 run the binding must be side-effect-free — **no DB
writes** (`PROGRAM_A_BINDING_SPEC.md` §4).
**[INFERENCE]** Therefore Program A's EXP-1 execution surface performs **zero
SQLite writes**. If the eventual product surface persists state
(`velynx_identity.db`, `velynx_state.db` exist at repo root — TD-15), that
persistence must be disabled or isolated during EXP-1 execution
(`VELYNX_TEST_MODE`-style isolation exists for tests, architecture.md
invariant 10). Reads are not explicitly prohibited by any document;
mutation is.

## 11. Telemetry interactions

**[FACT]** Invariant 8 (architecture.md §6): "Telemetry is non-blocking. A
telemetry fault must never crash or perturb the system it observes."
**[FACT]** The binding must cause "no telemetry perturbation of the run"
(`PROGRAM_A_BINDING_SPEC.md` §4).
**[INFERENCE]** Program A's EXP-1 surface emits no run-perturbing telemetry;
any product telemetry must be fire-and-forget and outside the measured path.

## 12. Memory interactions

**[FACT]** `backend/memory/`, `backend/cognition/memory_scheduler.py`, and the
C8 consolidation pipeline are engineering subsystems of the old stack.
**[INFERENCE]** The EXP-1 surface must be **stateless across queries**: the
binding-spec "no hidden state" requirement plus the frozen-dataset held-out
rule (`EXP1_DATASET_SPEC.md` §12.3 — any exposure of frozen rows to tuning
invalidates the run) forbid cross-query learning or memory accumulation
during execution. EXP-0's per-trial memory-wipe rule (canon §7) is the
established precedent for this discipline.

## 13. Identity interactions

**[FACT]** The identity/self-model subsystem (`backend/self_model/`:
`identity_store.py`, `self_model.py`, `health_monitor.py`,
`baseline_tracker.py`) is `[REJECTED]` as science (canon `:90`;
`TECHNICAL_DEBT.md` TD-08).
**[INFERENCE]** Program A's EXP-1 path must have **zero identity-subsystem
dependency**. The only "identity" in the path is the manifest's
`program_a_adapter_id` string (`manifest.py`; `program_a_adapter.py:47-52`
`callable_identity`).

## 14. Predictive Processing interactions

**[FACT]** The canonical predictive-processing machinery
(`core/predictors/`, `core/mdl/`, `core/emergence/`) serves H\*/E0, not
Program A (architecture.md §5, §8). The only shared primitive is measurement:
the ECE primitive `core/measurement/proper_scoring.py:42`
(`expected_calibration_error`), consumed by EXP-1 via
`experiments/EXP1/calibration.py:102` (`EXP1_TRACE.md` ML-15).
**[INFERENCE]** Program A neither imports nor feeds the predictive core.
`backend/cognition/predictive_core.py` / `predictive_engine.py` are old-stack
engineering and are not required by any EXP-1 link.

---

## 15. Failure modes

See `PROGRAM_A_FAILURE_ANALYSIS.md` for the full analysis. Headline set:

- **[FACT]** Historical: `CERTAIN` emitted on hallucinated content (Q6) — the
  anchor that put H1 in `[REJECTED]` state (canon `:146`); now a
  zero-tolerance kill (`EXP1_PREREGISTRATION.md` §4 hard
  hallucination-honesty; `decision.py` `HARD_HALLUCINATION_FAILURES_TOLERATED
  = 0`).
- **[FACT]** F-10 tier-validation bypass on direct `AnswerRecord`
  construction (`PROGRAM_A_ADAPTER_AUDIT.md` §7) — observed, documented,
  unfixed.
- **[FACT]** Category errors foreclosed by preregistration §5: retrieval
  relevance as answer confidence; source confidence as answer confidence;
  tier scored against query family.
- **[RISK]** Degenerate tier use (one-tier output) — preregistered kill #3.
- **[RISK]** Nondeterministic live retrieval breaking seed replication /
  replay (§8 above).

## 16. Threat model

Adversary = the experimenters themselves (Goodhart pressure), plus ambient
drift. Assets = validity of the EXP-1 pass claim.

- **[FACT]** Bin-boundary hacking — guarded passively by locked equal-width
  bins (`calibration.py`) + the `protocol_violation` kill flag
  (`decision.py`); an **active** detector (EXP1-05) is unimplemented and its
  canonical necessity is disputed (`STATISTICAL_AUDIT.md:188` dissent;
  `EXP1_TRACE.md` ML-14). Unresolved.
- **[FACT]** Post-hoc calibration / tier remapping / outcome-contingent
  relabeling — preregistered kills (§4 #5, §6).
- **[FACT]** Dataset leakage into Program A tuning — invalidates the frozen
  version (`EXP1_DATASET_SPEC.md` §12.2-12.3).
- **[FACT]** Adjudicator contamination — correctness must not depend on
  emitted tier (label-space guard, preregistration §3, §5;
  `dataset.py:358-363` docstring encodes this).
- **[FACT]** Fabricated approvals — every Program A document this session
  explicitly disclaims specialist sign-off (specialist runtime failure, R8);
  a pass claim without real ScientificAuditor sign-off is itself a threat.

## 17. Scientific assumptions

- **[FACT]** H1 as preregistered assumes the four symbolic tiers are the
  honest public confidence channel; numeric confidence is exploratory only
  (`EXP1_PREREGISTRATION.md` §1).
- **[INFERENCE]** Assumes a tier-emission mechanism can be specified from
  Program A's evidence state without fitting to EXP-1 outcomes — untested;
  if false, H1 is untestable as scoped. (Analogue of the I2 keystone pattern:
  the mechanism must be distinguishable from a hand-tuned artifact.)
- **[FACT]** Assumes 22 seeds capture seed-level stochasticity ≥10%
  (§7 power rule); if the implementation is fully deterministic, the
  preregistration's own amendment clause triggers (**[OPEN QUESTION]** Q3).

## 18. Engineering assumptions

- **[FACT]** The adapter framework, runner, ECE math, decision rules, and
  manifest are complete and preregistration-compliant (`EXP1_TRACE.md`
  Verdict; 64 EXP-1 tests passing).
- **[FACT]** `experiments/` must not import `backend/` except via the
  `research/` composition layer (architecture.md §4 rule 2) — so the concrete
  binding lives outside `experiments/EXP1/`.
- **[INFERENCE]** `UnifiedRetriever` is engineering-clean (no `[REJECTED]`
  symbols in it) and reusable as the retrieval substrate, subject to the
  determinism caveat.

## 19. Explicit non-goals

Program A (this specification) is **not**:
- the research center (canon `:42`);
- a carrier of H\* or H2;
- a new hypothesis (constitutional rule 1, canon `:32`);
- a consumer of the C8 Replay Engine, soul graph, self-model, reasoning
  engine, thermodynamic state, or free-energy policy (`[REJECTED]`, canon
  `:90`);
- an owner of ECE, bins, tier→probability mapping, rubric adjudication, or
  decision rules (owned by `experiments/EXP1/`);
- a modification of any frozen constant, preregistration, or canonical
  document.

## 20. Long-term evolution

- **[FACT]** Roadmap items after the first gate: EXP1-04 (BM25/TF-IDF control
  with randomly assigned confidence — the H1 H₀ control, canon §6-H1) and
  EXP1-05 (active Goodhart detector) — both DEFERRED-BACKLOG
  (`PROGRAM_D_MASTER_ROADMAP.md:132`; `EXP1_TRACE.md` ML-13/ML-14).
- **[FACT]** Numeric confidence may join the primary metric only via a canon
  amendment before implementation (`EXP1_PREREGISTRATION.md` §1 line 35).
- **[INFERENCE]** If EXP-1 passes, Program A graduates from `[REJECTED]` to
  the shippable honest product; if it kills, the honest-uncertainty claim is
  rejected and the product claim must be withdrawn — either outcome is a
  publishable, canon-compliant result (canon §8 honest publication path).
- **[SPECULATION — not load-bearing]** A later migration could move the
  answer+tier surface from its initial location into a populated
  `program_a/` package, completing the §9-DeepSeek split. Nothing depends on
  this.
