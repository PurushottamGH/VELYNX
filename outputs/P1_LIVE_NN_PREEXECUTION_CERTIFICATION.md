# P1-LN-DEC Pre-Execution Integration + Hostile Launch Certification

**Assessment date:** 2026-08-08  
**Repository:** `C:\Users\Purushottam\Documents\P1`  
**Scope:** NN-0 nucleus, Playgarden, DEC evaluator, guardianship gates, and the protected repository boundary.  
**Decision:** pre-execution only. The decisive NN-0 experiment was not run.

## Executive verdict

**FINAL LAUNCH VERDICT: D — NN-0 / PLAYGARDEN INTERFACE DEFECT**

The components do not compose into one executable, scientifically valid experiment:

1. `experiments/DEC/` uses its own integer grammar and does not import or consume `p1/live/neural/playgarden/`.
2. `NN0Trainer` is not an implementation of `core.protocols.Model`; it has no `predict`, `score`, `learn`, `state_dict`, or `load_state_dict` boundary for the DEC engine.
3. NN-0's `reset_state()` clears only recurrent hidden state. The Playgarden memory-zero harness calls `reset()`, which NN-0 does not provide and which would not clear KV memory.
4. The current Playgarden composition holdout is underdetermined: three distinct probe contexts each have two different expected continuations.
5. The DEC abstraction holdout targets nine symbols that never occur in training. The candidate cannot infer an arbitrary hidden permutation onto output symbols it has never observed; `Bref` receives that hidden permutation directly.

These are design/interface failures, not a lack of unit tests. The smallest repair is to select one generator as the canonical benchmark, make its query and target unambiguous, define a learnable symbol-calibration exposure (or remove the impossible OOV abstraction family), implement a typed NN-0 adapter with explicit episode and memory-reset semantics, then freeze the protocol/statistics and rerun this certification. No runner or protocol was added because Sections 3, 6, 9, and 10 did not pass.

**P1-LN-DEC PRE-EXECUTION NOT CERTIFIED**  
**PROTOCOL SHA256: NOT ISSUED**  
**DECISIVE EXPERIMENT NOT YET RUN**  
**READY FOR CONTROLLED LAUNCH: NO**

## 1. Repository safety freeze

### 1.1 Exact environment

| Item | Observed value |
|---|---|
| Git HEAD | `d5ae8f29d7fc010abfa88a37a76824c159d848c2` |
| Branch | `p1-v2-stage2-model-20260805` |
| Python | 3.11.9 (`C:\Users\Purushottam\AppData\Local\Programs\Python\Python311\python.exe`) |
| PyTorch | 2.6.0+cu118 |
| CUDA runtime | 11.8; `torch.cuda.is_available() == True` |
| GPU | NVIDIA GeForce GTX 1070 |
| Driver | 582.66 |
| VRAM | 8,192 MiB total; 7,216 MiB free at inspection |
| CUDA devices | 1 |
| `.ros/lske_events.jsonl` | absent |
| Canonical `Store.content_hash()` | `e8c1ab3825e7ee0a99eb5cd0db124efd81dd6c0c608db6a3151b684445e08670` |
| Store integrity | 0 errors, 8 warnings |

### 1.2 Git and write surface

`git diff --stat` and `git diff --name-only` were empty: no tracked file was modified at inspection. The worktree nevertheless contained **39,907** porcelain status entries, overwhelmingly untracked tool state. The relevant neural/DEC implementation files and tests are also untracked and are not present in `git ls-files` at this HEAD, including:

- `p1/live/neural/`
- `experiments/DEC/`
- `tests/live/test_playgarden_*.py`
- `tests/unit/test_dec_*.py`
- the existing Live-NN output reports

This means the current HEAD alone cannot reproduce the inspected experiment components. It is an additional PF-1 repository-pin defect, although the specific launch verdict is D because the component contract fails even before pinning.

The protected surface was defined as:

~~~text
science/
ros/
v2/lske/
schemas/
GOVERNANCE_REGISTRY.yaml
REPOSITORY_CONSTITUTION.md
PROGRAM_D_CANONICAL.md
RESEARCH_PROTOCOL.md
SCIENTIFIC_OPERATING_SYSTEM.md
P1_V2_CONSTITUTION_LOCK_v1.0.md
P1_V2_SCIENTIFIC_CONSTITUTION.md
P1_V2_PROJECT_ENGINEERING_STANDARD_v1.0.md
p1/specifications/
experiments/EXP0/
experiments/EXP1/
experiment_registry.yaml
parameter_registry.yaml
reproducibility.yaml
outputs/P1_V2*
outputs/stage3*
~~~

The aggregate SHA-256 of 207 protected files and their relative-path/hash manifest was:

~~~text
BEFORE: a95aae1db3889b4c4ba967c38f69d00c0abe49fb3b8c9236e23f4fb3a217e007
~~~

No experiment runner was executed. The only intentional repository write in this transaction is this report under `outputs/`; no protected path is authorized for writes.

## 2. Inspected components

### NN-0

Inspected `p1/live/neural/nn0/nucleus.py` and its focused tests.

- Architecture is `Embedding(32) -> key projection(32) -> GRU(128) -> readout`.
- With the default `vocab_size=128`, the implementation has **99,232 parameters**.
- AdamW, `lr=1e-3`, `weight_decay=5e-4`.
- KV capacity 65,536, top-k 4; replay capacity 65,536, alpha 0.6, batch 64, every step.
- Deterministic CPU/CUDA seeding and a seven-file checkpoint bundle exist.
- Online updates are scalar `step(x_val, y_val)` updates. Replay stores only `(x, y, error)`.
- KV values are target-token embeddings, so external memory can directly carry label information from training examples.
- `probe(xs, ys)` scores one continuous tensor sequence, not a collection of independently reset `(context, target)` items.
- Checkpoint metadata contains a parameter hash but `from_checkpoint()` does not verify that hash; a modified model checkpoint loads successfully.

### Playgarden

Inspected `p1/live/neural/playgarden/{alphabet,rules,worlds,probes,verification,memory,__main__}.py` and all four Playgarden test files.

- Deterministic anonymous symbols, sequence/composition/relation worlds, relabel/permutation probes, exact-lookup checks, and a memory-zero harness exist.
- The verifier proves only the exact `context + expected_first` contiguous match and vocabulary disjointness for disjoint relabels. It does not provide the full subsequence, n-gram, isomorphism, replay-source, or checkpoint contamination guards required by this certification.
- `MemoryZeroEvaluator` is a predictor-level harness for `predict(context)` plus optional `reset()`. It is not an NN-0 adapter.
- `python -m p1.live.neural.playgarden --seed 0` completes and reports its local proofs, but it never trains NN-0 or calls DEC.

### DEC evaluator

Inspected `experiments/DEC/{grammar,baselines,metrics,oracle,decision}.py` and the three DEC unit-test files.

- The grammar is a separate integer-token generator: `START=25`, `EOS=24`, body symbols `0..8`, abstraction symbols `9..17` for the default configuration.
- Baselines are uniform, B1 marginal, B2 order-1 `CountModel`, and B0 full-context exact lookup.
- There is no order-2/3 baseline, no finite-state or context-retrieval control, no NN adapter, no protocol module, no stats module, no power module, and no runner.
- `Bref` directly copies private grammar transition rows and the private abstraction permutation.
- The decision layer contains K1-K8 but no K9 implementation, no confidence intervals, no variance estimator, no frozen seed-set validation, and no claim-class firewall.

### Reports treated as evidence inputs

Read:

- `outputs/P1_LIVE_NN_GUARDIANSHIP_SAFETY_GATE.md`
- `outputs/P1_LIVE_NN_NEURAL_ARCHITECTURE.md`
- `outputs/P1_LIVE_NN_INTEGRATION_CONTRACTS.md`
- `outputs/P1_LIVE_NN_HOSTILE_ROADMAP.md`
- `outputs/P1_LIVE_NN_REPOSITORY_DEEP_CLEAN_AUDIT.md`

The reports describe intended contracts, but the actual code above is the authority for this certification. The guardianship report uses A1-A4 claim names, whereas this transaction's claim firewall requires only R0-R5. That mismatch is not silently accepted.

## 3. Composition trace

| Boundary | Actual implementation | Ruling |
|---|---|---|
| Playgarden experience -> evaluator | Playgarden emits string-token streams. DEC imports only `core.seeds` and `p1v0`; it never imports Playgarden. | **FAIL** |
| DEC experience -> NN-0 input | DEC emits `(tuple[int, ...] context, int target)`. NN-0 accepts only scalar `x_val, y_val`; no encoder or adapter exists. | **FAIL** |
| Token vocabulary | NN-0 output vocabulary is 128; DEC baselines score over 25 or 26 classes. No shared output-space contract exists. | **FAIL** |
| Episode boundaries | DEC contexts include `START`; NN-0 has no boundary-aware training method. A caller must infer `len(context)==1` and call `reset_state()`. | **UNKNOWN/FAIL** |
| Prediction | Repository `Model` requires `predict(context)` and `score(prediction,target)`. NN-0 exposes neither. | **FAIL** |
| Loss/update | NN-0 performs CE in `step`, but the evaluator has no way to route a full DEC context into it. | **FAIL** |
| Hidden state | `last_h` persists across scalar steps; `probe()` starts one hidden state for a whole probe sequence. No per-item frozen-probe state contract exists. | **FAIL** |
| KV memory | Read path is detached, but writes store target embeddings. There is no source ID or evaluation blacklist. | **UNKNOWN/FAIL** |
| Replay | Replay stores only scalar pairs and no episode/source provenance. Replay loss omits KV reads. | **FAIL** for the stated contract |
| Evaluation | `MemoryZeroEvaluator` calls `reset()`, while NN-0 has only `reset_state()` and that does not clear KV memory. | **FAIL** |
| Metrics | DEC metrics can score baselines but no common candidate/baseline runner or per-item paired record exists. | **FAIL** |
| Decision gate | DEC decision consumes synthetic loss tables, not a frozen run artifact. | **FAIL** |

## 4. Leakage attack matrix

`PASS` means the actual code and tests establish the stated property. A report assertion without an executable guard is not a pass.

| Attack | Status | Evidence |
|---|---|---|
| Exact sequence overlap | **FAIL** | DEC has an intentional memorization family overlapping training; no runner gates it away from decisive aggregation. Playgarden checks only the first expected token. |
| Subsequence overlap | **FAIL** | No all-contiguous-subsequence scan exists. Playgarden length/composition probes share many shorter sequences with training. |
| N-gram overlap | **FAIL** | DEC composition probes intentionally share local transitions; only an order-1 B2 exists and no order-2/3 audit is run. |
| Symbol-isomorphic overlap | **FAIL** | Disjoint relabel vocabulary is checked, but within-alphabet permutation equivalence is not exhaustively scanned. DEC abstraction is disjoint OOV, not a learnable permutation. |
| Rule-template leakage | **FAIL** | DEC hold templates are structurally separate, but Playgarden's composition holdout is not an identifiable input/output task; no unified generator proof exists. |
| RNG coupling | **FAIL** | DEC grammar uses one master `random.Random` stream for generator, training, and probes; no independent frozen substreams are wired to NN-0. |
| Held-out probe construction leakage | **FAIL** | No runner or source blacklist binds training, memory, replay, and probe construction. |
| Oracle information leaking into candidate | **UNKNOWN/FAIL** | No candidate path exists, but `Bref` reads private `_rows` and `_perm`; there is no process or object-boundary guard. |
| Baseline receiving less context than NN | **FAIL** | B2 intentionally uses only `context[-1]`; NN-0's intended recurrent path would receive sequential state, while no context-equivalent adapter is defined. |
| NN receiving labels through metadata | **UNKNOWN** | No candidate runner exists; no metadata-stripping boundary is implemented. |
| Evaluation examples in NN memory | **UNKNOWN/FAIL** | No evaluation blacklist or source IDs exist; NN-0 KV entries have no provenance. |
| Evaluation examples in replay | **FAIL** | Replay entries contain only `(x,y,error)` and cannot be proven to exclude probe items. |
| Checkpoint contamination | **FAIL** | Corrupting `model.pt` while leaving `meta.json` unchanged still permits checkpoint load; `params_hash` is not verified. |
| Test-set adaptation | **UNKNOWN** | No frozen evaluator/runner exists to prove that post-probe updates are impossible. |
| Seed cherry-picking | **FAIL** | `MIN_SEEDS=5` is a count, not a frozen seed set; `decision.evaluate()` accepts arbitrary seed tuples and K4 is `>=5`, not exactly the registered set. |
| Hyperparameter tuning on decisive probes | **FAIL** | No immutable protocol or tuning/confirmation split exists. |

## 5. Baseline fairness matrix

| Model | Training information | Evaluation information | Retained state/capacity | Update opportunity | Context/scoring |
|---|---|---|---|---|---|
| Uniform | None | Target vocabulary size | Fixed distribution | None | Receives context but ignores it; shared proper NLL |
| B0 exact lookup | All DEC training `(context,target)` pairs | Full probe context | Unbounded Python dict keyed by full context | Fit once; no probe updates | Full context; Laplace alpha 0.1; proper NLL |
| B1 marginal | All training targets | Full probe context, ignored | One smoothed categorical vector | Fit once | Context ignored; proper NLL |
| B2 order-1 | All training pairs | Full context, uses only last token | `CountModel` row table; alpha 0.5, decay 1 | Fit once; no probe updates | Last token only; proper NLL |
| NN-0 full | Intended scalar sequential experience; KV/replay also receive observed targets | No implemented predictor API | 99,232 weights + 65,536 KV + 65,536 replay | `step()` only; no engine adapter | Scalar input only; no common DEC item scorer |
| NN-0 N1 | Undefined | `MemoryZeroEvaluator` expects `reset()` | Current reset clears hidden state only; KV remains | Undefined | N1 cannot be executed against NN-0 as written |
| Bref | Private transition rows, rule bands, template prior, and optionally private permutation | Full probe context and family-specific relabel flag | Exact generator reference | No learning | Proper NLL, but not an achievable candidate upper bound for OOV abstraction |

The minimum B0/B1/B2/uniform set exists only for DEC. The stronger cheap order-2/3 n-gram and a context-retrieval control are absent. Because the grammar's decisive composition probe shares local transitions with training, the current B2 is not obviously sufficient as the strongest cheap alternative.

## 6. Oracle audit

`RefOracle` copies `grammar._rows`, `grammar._rule_bands`, and, for abstraction, `grammar._perm`. It also places a uniform prior over all 39 templates of length 1-3, not the exact observed training-template prior.

- For composition, the transition rows are in principle inferable from a sufficiently large training stream, so a generator-informed oracle can be a useful reference if it is clearly labelled as an upper/reference model rather than an achievable candidate.
- For abstraction, the probe outputs are symbols `9..17` that never appear in training. The candidate has no observation from which to infer the arbitrary permutation. The oracle receives that permutation directly. This family therefore fails the oracle-achievability requirement and cannot be used to reject NN-0.
- DEC probe families contain stochastic next-token distributions; `Bref` can represent that irreducible entropy. Playgarden composition probes are worse: the same context can have different deterministic labels, so their target is not identifiable.

Observed reference losses for the current DEC harness, calculated only as an oracle audit and not as NN results:

| Family | Seed-0 loss | Range over seeds 1, 7, 42, 99, 1234 |
|---|---:|---:|
| Composition | 0.8810 | 0.7917–1.0808 |
| Abstraction | 1.1602 | 1.0003–1.2538 |

The oracle is not a valid rejection ceiling for the current abstraction family.

## 7. Metric ruling

The current metric is:

~~~text
(baseline_mean_loss - candidate_mean_loss) / baseline_mean_loss
~~~

The formula is mathematically defined for the current smoothed baselines, and the inspected denominator values are positive. It is not, by itself, a scientifically justified 10% effect threshold:

- the denominator changes the absolute effect required by family;
- no confidence interval or variance estimate is computed;
- no seed-level paired contrast is stored;
- K1 and K7 inspect only the first seed;
- K4 accepts any five successful seeds rather than the frozen set;
- K7 only requires B0/B2 to beat uniform, not to be near-perfect;
- the N1 rule pools raw losses even though it is meant to classify a mechanism contribution;
- there is no multiplicity or co-primary-family rule;
- the current A1-A4 report classes do not match the required R0-R5 firewall.

The replacement to freeze after the interface repair is:

1. primary estimand: equal-weight mean per-item NLL difference within each seed and family;
2. paired comparison: candidate and every fixed baseline score the identical frozen items;
3. co-primary families: composition and a repaired, identifiable symbol-transfer family must both pass;
4. uncertainty: seed-clustered 95% paired confidence interval, with an exact sign-permutation check as a small-sample sensitivity analysis;
5. effect reporting: absolute NLL difference and relative reduction, with a pre-declared SESOI chosen before any decisive result; a bare 10% rule is not sufficient;
6. failed/diverged runs remain in the denominator and cause a failed/inconclusive gate; they are never dropped.

No replacement threshold was frozen because the current estimand is invalid. Therefore no protocol hash is issued.

## 8. Statistical protocol and power sensitivity

The existing five-seed list is a replication floor, not a defensible power claim. The minimum protocol I would freeze after the design repair is **10 independent, pre-registered master seeds**, for example:

~~~text
[1, 7, 42, 99, 1234, 2027, 31415, 65537, 100003, 424242]
~~~

All runs must use independent named substreams for generator, trajectory, replay, probe construction, and model initialization. The primary result is the per-seed paired contrast, not a pooled item count that treats correlated items as independent.

Sensitivity of a two-sided paired t approximation at alpha 0.05 is shown below. `d` is the standardized paired effect; it is not an observed result and cannot be inferred without a repaired pilot.

| Seeds | d=0.5 | d=0.75 | d=1.0 | d=1.25 | d=1.5 |
|---:|---:|---:|---:|---:|---:|
| 5 | 0.141 | 0.254 | 0.401 | 0.562 | 0.711 |
| 8 | 0.232 | 0.449 | 0.681 | 0.856 | 0.951 |
| 10 | 0.293 | 0.562 | 0.803 | 0.939 | 0.987 |
| 12 | 0.353 | 0.658 | 0.883 | 0.975 | 0.997 |

This supports 10 as a minimum replication count for a large effect, while making no claim that 10 seeds can detect a small effect. A pilot may estimate variance only if its protocol is explicitly non-decisive and cannot tune the decisive result.

## 9. N1 memory-ablation ruling

The current `>30%` N1 degradation requirement tests a narrower hypothesis:

> the observed holdout margin must depend on external KV memory.

That is not identical to the central hypothesis that a recurrent neural system can acquire reusable structure from sequential experience. A rule may be represented in recurrent weights and remain after KV is removed. Requiring a 30% loss increase would reject that valid weights-only result for the wrong reason.

The current implementation also cannot execute the stated ablation:

- `MemoryZeroEvaluator` calls `reset()` before each item;
- `NN0Trainer` has no `reset()`;
- `reset_state()` clears `last_h` but leaves the KV store unchanged;
- `decision.gate_n1()` compares pooled raw NLL using `NLL_N1 > 1.30 * NLL_full`, with no explicit distinction between KV, recurrent state, and replay.

**Ruling:** make primary generalization and external-memory contribution separate classifications. The primary gate should test reproducible held-out performance against fair controls. N1 should report `memory-dependent`, `memory-independent`, or `inconclusive` using a precisely defined external-KV wipe, while retrieval-consistent outcomes remain R1 under the claim firewall. Do not make a valid generalization result fail solely because KV memory was unnecessary.

## 10. Frozen protocol status

No immutable machine-readable protocol was generated. The necessary protocol-critical fields are not yet simultaneously valid:

- generator identity is disputed by the disconnected Playgarden and DEC implementations;
- token encoder and episode-boundary semantics are absent;
- candidate/baseline output vocabulary is not shared;
- abstraction probes are not achievable by the candidate;
- N1 semantics are undefined for NN-0;
- seed set, uncertainty rule, SESOI, and failed-run policy are not enforced in code;
- no protocol-critical hash refusal exists.

The inspected, non-frozen values are the NN-0 and DEC defaults recorded in Sections 2 and 5. They must not be treated as a launch protocol.

## 11. Guardianship PF-0 through PF-11

| PF | Actual status | Finding |
|---|---|---|
| PF-0 | **PASS** | Host version, CUDA, GPU, and VRAM were directly observed. |
| PF-1 | **FAIL** | HEAD is known, but relevant experiment code is untracked and not present in HEAD; worktree has 39,907 status entries. |
| PF-2 | **PASS for baseline / NOT RUN** | Store hash and absence of LSKE event log recorded; no run was allowed to test post-run equality. |
| PF-3 | **FAIL** | No immutable DEC config/protocol or protocol hash refusal exists. |
| PF-4 | **FAIL** | Components are deterministic individually, but no canonical corpus serializer/fingerprint is bound to a runner. |
| PF-5 | **PARTIAL** | NN-0 and generator focused tests pass; no full runner artifacts exist for byte comparison. |
| PF-6 | **FAIL** | Only narrow first-target checks exist; full sequence/subsequence/n-gram guards are absent. |
| PF-7 | **FAIL** | Disjoint relabel vocabulary is checked, but symbolic-equivalence and within-alphabet leakage are not fully guarded. |
| PF-8 | **FAIL** | DEC baselines share a grammar, but NN-0 is not connected and stronger order-2/3 controls are absent. |
| PF-9 | **FAIL** | No common frozen candidate evaluator or state-hash guard exists; the small harness only asserts it does not call `learn` on a guarded dummy model. |
| PF-10 | **FAIL** | The generic engine has inventory support, but DEC has no runner that emits a sealed run directory. |
| PF-11 | **FAIL** | No executable R0-R5 claim firewall; existing guardianship uses different A1-A4 labels. |

The blocking guardianship set therefore fails.

## 12. Failure-injection results

All mutations below were isolated to temporary objects or synthetic in-memory data. No protected repository surface was mutated.

| Injected defect | Expected detection | Actual result |
|---|---|---|
| Use in-corpus Playgarden anti-memorization probe | Leakage guard rejects | **PASS**: `prove_no_leakage()` returned false |
| Replace candidate with uniform/random loss table | Decision rejects | **PASS**: DEC status was `FAIL` |
| Corrupt protocol hash | Runner refuses | **FAIL**: no protocol/runner/hash guard exists |
| Change one seed | Frozen protocol refuses or records deviation | **FAIL**: corpus changes, but no refusal surface exists |
| Mutate protected Store content in a temporary copy | Content fingerprint changes | **PASS**: `Store.content_hash()` changed; no live before/after runner gate exists |
| Insert a probe into replay | Source blacklist rejects | **FAIL**: replay has no source ID or blacklist |
| Change probe after freeze | Frozen corpus hash rejects | **FAIL**: no frozen corpus/probe hash exists |
| Corrupt checkpoint tensor while leaving metadata | Checkpoint integrity rejects | **FAIL**: `from_checkpoint()` loaded it and did not verify `params_hash` |
| Disable external memory | N1 runs and classifies effect | **FAIL**: NN-0 has no memory-zero adapter; `reset_state()` leaves KV length unchanged |
| Use random candidate predictions | Decision rejects | **PASS**: synthetic random candidate produced `FAIL` |

A safety gate that cannot catch protocol, replay, probe, and checkpoint defects is not launch evidence.

## 13. Reproducibility results

### Component-level deterministic checks

- Focused neural/DEC/Playgarden suite: **58 passed**.
- Two identical synthetic 24-step NN-0/DEC dry runs on CPU, same seed and corpus:

~~~text
run A SHA256: 633f7f80da1eb7567973d9fc7a2f8add3ea4f228278ba2e1fb419bb570c79e89
run B SHA256: 633f7f80da1eb7567973d9fc7a2f8add3ea4f228278ba2e1fb419bb570c79e89
identical: True
~~~

- Existing NN-0 checkpoint/restart tests pass for the tested short continuation.
- Existing Playgarden and DEC tests pass for same-seed generator identity.

### End-to-end reproducibility

**NOT ESTABLISHED.** There is no P1-LN-DEC runner, immutable protocol, corpus artifact, frozen probe artifact, or end-to-end `checkpoint -> restart -> continue` artifact comparison. GPU deterministic flags are set for cuDNN, but CUDA artifact-level reproducibility was not demonstrated for this experiment.

The broader repository suite produced **2,734 passed, 10 skipped, 2 failed**. The two observed current-checkout failures are `p1_os` external-install tests: a plain Python process outside the repository cannot import `p1_os`. They are not used to claim anything about NN-0, but they reinforce that the repository is not a clean launch baseline.

## 14. Repository before/after fingerprints

The protected aggregate manifest was recomputed after all inspection and report-writing activity:

~~~text
BEFORE: a95aae1db3889b4c4ba967c38f69d00c0abe49fb3b8c9236e23f4fb3a217e007
AFTER:  a95aae1db3889b4c4ba967c38f69d00c0abe49fb3b8c9236e23f4fb3a217e007
~~~

The canonical Store content hash remained:

~~~text
e8c1ab3825e7ee0a99eb5cd0db124efd81dd6c0c608db6a3151b684445e08670
~~~

No protected-surface mutation was observed. The report itself is outside the protected surface and was the only requested repository write.

## 15. Operational answer to the central scientific question

The observation that would convince us of a reusable rule is:

> After repairing the benchmark so every probe context has an identifiable target and every novel symbol has an explicitly learnable calibration exposure, the candidate sees rule components and their separate assignments during sequential training but never sees the decisive composition under the held-out assignment. On identical frozen worlds, it must predict the unseen composition and repaired symbol-transfer family with lower per-item NLL than B0, B1, B2/order-3, and the other pre-registered cheap controls; the lower confidence bound of the paired seed-level effect must clear the pre-registered SESOI; the result must replicate across the frozen seed set; and independent leakage, memory, replay, checkpoint, and evaluator-state guards must pass. If the claim is about weights rather than retrieval, wiping only external KV must not erase the result; KV dependence is reported separately.

This is falsifiable. The current Playgarden and DEC probes do not satisfy the identifiable-target and learnable-symbol conditions, so no result from them could answer the question.

## 16. Smallest exact repair transaction

1. Freeze one canonical generator. Prefer a single isolated `Benchmark` whose environment, token encoder, probe families, oracle, and fingerprints are one object. Do not combine the current string Playgarden and integer DEC grammar by convention.
2. Repair Playgarden composition probes so the query contains the information needed to select `b_j` (or use a deterministic one-target-per-context probe); add an ambiguity assertion to the leakage tests.
3. Replace or redesign DEC abstraction so the candidate observes enough calibration to infer the symbol mapping. Do not use the current all-OOV target block as a generalization gate.
4. Add an NN-0 adapter implementing `predict`, `score`, `learn`, `state_dict`, `load_state_dict`, `reset_episode`, and `clear_external_memory`, with explicit vocabulary, target alignment, `START/SEP/EOS`, device, train/eval, and gradient-boundary tests.
5. Add source IDs and blacklist assertions for training, probe, KV, replay, and checkpoints; verify checkpoint hashes; freeze independent substream seeds.
6. Add order-2/3 n-gram and one targeted context-retrieval control, then freeze the paired estimand, SESOI, CI, failure policy, R0-R5 firewall, and machine-readable protocol hash.
7. Re-run this certification. Only if PF-0 through PF-11 and the repaired design pass may an isolated dry-run runner be built and invoked.

No LSKE, ROS, science, schema, governance, Stage-3, or production migration is authorized by this report.

## 17. Exact launch command

**NONE.** No valid launch command exists in the inspected checkout: the DEC protocol, runner, and NN-0 adapter paths are absent, and the current component contract is not admissible. Any command that executes a bespoke training script before the repair transaction would violate the pre-execution stop condition.

## 18. Final classification

**D — NN-0 / PLAYGARDEN INTERFACE DEFECT**

No R0-R5 scientific result was emitted. No capability claim was emitted. The first decisive NN-0 run remains prohibited.
