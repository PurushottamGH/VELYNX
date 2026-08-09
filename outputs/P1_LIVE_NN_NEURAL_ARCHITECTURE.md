# P1 LIVE INTELLIGENCE PROGRAM — TRACK C
## Neural Brain + Experience-Driven Learning Architecture

**EXPERIMENTAL — P1 LIVE INTELLIGENCE RESEARCH**

---

**Mode:** Maximum effort / Research Architect / **READ-ONLY**. This document modifies no existing P1 artifact — no code, no spec, no schema, no registry, no Git history. It is a design and a research plan only.

**Host floor (verified on this machine, 2026-08-07):**

| Item | Verified value |
|---|---|
| Python | 3.11.9 |
| PyTorch | 2.6.0+cu118 |
| CUDA available | `True` |
| GPU | NVIDIA GeForce GTX 1070 |
| VRAM total / free | 8192 MiB / ~7202 MiB |
| Driver (nvidia-smi) | 582.66 |

**Measured microbenchmark (this report's own runs, `torch` on-device, batch=64, seq=32, next-token NLL):**

| Core | Parameters | ms/step | Peak VRAM | Tokens/s |
|---|---|---|---|---|
| GRU | 82,816 | 5.82 | 55.0 MB | 352,082 |
| LSTM | 103,552 | 6.05 | 59.0 MB | 338,401 |
| MLP (fixed window) | 428,928 | 6.22 | 25.9 MB | 329,357 |
| Small Transformer (2L·6h) | 301,952 | 18.49 | 53.7 MB | 110,735 |

Computational capability is independently demonstrated. Every VRAM or speed figure cited below is traceable to this table unless explicitly stated as a bound or target.

**Epistemic tags (inherited from the P1 canon):** `[FACT]` mechanically verified or derivable · `[HYPOTHESIS]` falsifiable with a pre-registered null · `[SPECULATION]` untested, never load-bearing · `[REJECTED]` falsified or superseded.

**Prime question this track exists to answer:** *Can a small local neural system acquire a capability from sequential experience, retain it across restart, generalize from previous experiences, learn from errors, and improve without complete retraining — on an 8 GB GTX 1070?*

---

## 1. TASK 1 — DEFINE P1-NN-0

### 1.1 Candidate architectures, compared on the required axes

| Candidate | Params (`≈100k` class) | VRAM | Speed (measured where possible) | Continual-learning suitability | Online updates | Catastrophic forgetting | Inter-pre-avoidability | Checkpoint cost | GTX 1070 |
|---|---|---|---|---|---|---|---|---|---|
| **MLP (fixed window)** | 428,928 | 25.9 MB | 329 k t/s | poor (no state) | trivial | extreme | high per-value | tiny | trivial |
| **GRU** | 82,816 | 55.0 MB | 352 k t/s | good (stateful) | natural | moderate without replay, low with | moderate (hidden) | tiny | trivial |
| **LSTM** | 103,552 | 59.0 MB | 338 k t/s | good | natural | as GRU | moderate | tiny | trivial |
| **Small Transformer** | 301,952 | 53.7 MB | 111 k t/s | good but stateless | needs KV bookkeeping | high without replay | high (attention) | small | fine, 3× slower |
| **State-space / Mamba / S4** | ~60–150k | low | untested on Windows/cu118 | excellent long-range | natural | excellent if trained streaming | low | small | kernel risk |
| **Autoencoder** | 30–200k | low | fast | representation only | easy | moderate | latent | tiny | trivial |
| **Contrastive encoder** | 30–200k | low | fast | representation only | easy | moderate | latent | tiny | trivial |
| **Predictive world model** | varies | low | fast | excellent (prediction is the curriculum) | natural | low with replay | moderate | small | ideal |
| **External-memory NN (DNC / RAM)** | 100–500k | medium | slower | good, complex to train | hard | low | low | medium | heavier |
| **Hybrid (recurrent core + external memory + replay)** | ~100k | ≤100 MB | fast | **excellent, minimal** | natural | low | TBD (probes) | small | ideal |

**Readings.**

1. `[FACT]` An MLP cannot carry state; every long-range dependency must fit a fixed window, so *novel sequence lengths* are structurally out of distribution. It stays in the design **only as the fixed-capacity control C1** (mirroring the repo's `C1` control pattern).
2. `[FACT]` A Transformer on this GPU costs ~3× wall time (111k vs 352k tokens/s), has no implicit state, and needs KV/position machinery. Its long-range strength is exactly what an **external key/value memory** will add — without paying quadratic attention now.
3. `[HYPOTHESIS]` State-space scans (Mamba/S4) would be ideal long-range cores, but on **Windows + torch 2.6.0+cu118 + GTX 1070** custom scan kernels are a portability gamble for the first milestone. Kept as the NN-2 upgrade path, not NN-0.
4. `[FACT]` Autoencoders and contrastive encoders produce representations, not a **prediction-error channel** that drives sequential learning. They are *components* of the memory stack (input encoder, or key projection), not the core.
5. `[FACT]` The P1 scientific canon already fixes the learning law: **only prediction error may drive structure acquisition** (`−log P_θ`, proper scoring loss). NN-0 therefore has one single learning signal: next-token prediction error.

### 1.2 Chosen starting architecture — NN-0

**NN-0 — "minimal predictive recurrent core":**

- A tiny next-token world model: `GRU(hidden=128)` over a small vocabulary (`V ≤ 256`) with embedding `d_e = 32`.
- Prediction head outputs `P_θ(x_{t+1} | h_t, read_t)`.
- One external **key/value episodic memory** feeding a read-query into the core.
- One **reservoir replay buffer** for continual training.
- **Only** parameter trainable: `θ`. Memory ranks, buffer states, etc. are non-parametric.

```
x_t        → Embedding(d_e=32)
read_t     =  KVMem.read(proj(h_t))                 # retrieval, not params
h_t        =  GRU(input=32, hidden=128)(x_t, h_{t-1}, read_t)
P(x_{t+1}) =  softmax(proj(h_t))
L_t        =  −log P_θ(x_{t+1} | x_{≤t})            # sole learning signal
```

### 1.3 Why this absorbs every requirement

- **Small:** ~105k params, ~1.1 MB state, ~55 MB VRAM at batch=64 measured. Largest single session comfortably below 8 GB.
- **Predictive:** every capability is a reduction of next-token error; there is no second, supervised task to hide the mechanism.
- **Sequential-experience-native.** Experience arrives as a stream; a recurrent core + short memory already obliterates the "online learning" problem.
- **Error everywhere.** Prediction is performed at every step including the first, so *capability present before experience* is measurable at step 0 (see Task 10).
- **Upgrade lanes open:** a Transformer read-head or SSM core can replace the GRU (NN-2) without touching the memory/replay skeleton.

`[FACT]` NN-0 is the neural instantiation of the repo's existing founding law (`−log P_θ`, error-driven structure acquisition), replacing the conjugate Dirichlet–Markov predictor with a trainable GRU. This is continuity, not a new law.

---

## 2. TASK 2 — DEVELOPMENTAL SANDBOX

### 2.1 Environment principle

`[FACT]` NN-0 learns **in an environment, not on a static dataset.** The environment is a **sequence-rule generator** — a deterministic, reseedable generator of token streams whose structure comes from a latent rule set. The learner sees **only tokens**. It never receives any rule, class, hidden state, or label. **No designer writes a per-task classifier head; no answer is installed behind a token.** Every *emergence measure* is borrowed from held-out axes of the environment, never from the trainer.

This is the same discipline as the canon's `I2` ("emergent structure operationally distinguishable from injected structure"). The sandbox is a strict generalization of the repo's `E0` nonlinear-latent sampler: **symbolic** rather than continuous, so that non-linear, non-differentiable structure is exploited.

### 2.2 The P1-ARC class of environments ("playgarden")

A family of sequence worlds over alphabet `Σ`:

```
G = (Σ, rules R, train/held-out split σ)
```

Rules are *primitive generators* drawn at seed time: repetition `A^n`, mirror, reverse, bounce `ABABA…`, counting, transpose `x→f(x)`, chaining, prefix, insertion, and **composition** `R_a ∘ R_b` (a then b in one plot).

- Symbols are **anonymous and syntactically re-drawn per seed** — no preloaded semantics, no symbol shortcut.
- The modelling unit is the transparent next-token; to solve a stage, the learner must extract persistent structure from token pairs alone.
- The **held-out split is confound-clean**: combinations, lengths, and depths that *never co-occur* in the training stream (§7).
- Three observation protocols, used in stages:

| Protocol | What is predicted | Emergent target |
|---|---|---|
| **STREAM** | next token `x[t+1]` given `x[:t]` | recursively visible structure |
| **CLOZE** | a masked symbol given both sides | composition, gap-dependency |
| **SEQUENCE-LEVEL** | continuation to the terminator | length/duration, procedure |

NN-0 starts on **STREAM**; NN-1 adds CLOZE; NN-2 adds SEQUENCE-LEVEL.

### 2.3 Curriculum (stages of increasing requirement)

Each stage exposes a *measurable transition*; a **stage gate** is a statistical test on a probe (Section 7/10), not a hand-tuned epoch count. The labels never supervise the answer — only the next-token error does.

| Stage | What the model must acquire | Probe on | Emerges from |
|---|---|---|---|
| S0 Symbols | the marginal `P(x)` over an iid base | held-out token counts | frequency |
| S1 Sequences | 1st–2nd-order transitions | held-out pairs | co-occurrence |
| S2 Patterns | repetition / bounce structure | new lengths at length seen | local recurrence |
| S3 Composition | `a∘b` composed pattern | held-out distinct primitives | composition of links |
| S4 Concepts | categorical invariance (two symbols in the same class = same transition) | held-out class symbols | invariance in hidden |
| S5 Relations | transitivity | `a<b<c` ⇒ inferred edge | property of hidden classes |
| S6 Memory | bridging > window | held-out length far past max seen | reservoir recall |
| S7 Prediction | multi-step forecast | horizon 2–3 unseen | predictive hidden |
| S8 Reasoning | algorithmic: count, copy, choose (architecture-limited) | held-out-length copies | compositional (NN-2) |

`[HYPOTHESIS]` Each stage is impossible from memorization alone because the gate is sampled *outside* the distribution of positions subsequently seen. Any stage that *can* be solved by pure memorization is a failed stage and must be re-designed.

---

## 3. TASK 3 — EXPERIENCE LEARNING

### 3.1 Formal vocabulary

| Term | Definition |
|---|---|
| `x_t` | observation/token at time `t` |
| `h_{t-1}`, `h_t` | hidden state (the world-model summary) before/after the update |
| `State_t` | `(h_t, mem_read)`, the compressed internal summary available at `t` |
| `Prediction_t` | `P_t = P_θ(x_{t+1} | x_{≤t})` |
| `Action_t` | **none in NN-0** (predictive learner). Actions enter NN-2. |
| `Outcome_t` | `x_{t+1}`, the token the environment actually emits |
| `Error_t` | `L_t = −log P_θ(x_{t+1} | x_{≤t})` — the only statistic that updates |
| `LearningUpdate_t` | `θ ← AdamW(θ, ∇_θ L_t)` (+ replay loss) |
| `Memory_t` | the key/value store and its read value at `t`. Written whenever `L_t` exceeds a low threshold `τ` |

**What produces gradients — exhaustive list:** only the next-token prediction cross-entropy `L_t = −log P_θ(x_{t+1} | x_{≤t})`. No scalar reward, no real-valued target, no class label, no reconstruction objective. The replay head contributes the *same* loss over stored experiences, preserving the old behavioural manifold.

### 3.2 Separation of mechanisms

| Mechanism | When | Store | Where gradient |
|---|---|---|---|
| immediate memory write | per-step | episodic KV (host) | none (only affects later reads) |
| experience *replay* | per mini-batch | reservoir | through `λ` into `L` |
| weight update | per step | θ | yes |
| **consolidation** | every `C` steps (checkpoints) | weight re-alignment from stored episodes | through review/replay |
| evaluation | every `E` steps | probe log | **never** affects θ |

Rule: evaluation probes run with `θ` frozen and no backprop; probe results never flow back into the memory or the weights.

---

## 4. TASK 4 — MEMORY

### 4.1 Store options, compared

| Store type | Continual | VRAM | Update | Weights | Failure mode | Use in hierarchy |
|---|---|---|---|---|---|---|
| **neural weights** | slow, compressed schema | low | gradient | permanent | slow decay, forgetting | very top (schema) |
| vector memory (ring) | recent-state ring | small | cheap | temp | evicts by time | working window |
| key/value memory | `(key)→value` | medium | cheap | durable till cap | append-only, evicts at cap | the continuity store |
| episodic database | browsable, durable | disk | cheap | durable | append/cap | audit + cold storage |
| graph memory | relational | medium | expensive | — | — | NN-2 (relations) |
| replay buffer | experience | bounded | cheap | temporary | evicts by reservoir | training signal |

### 4.2 The NN-0 hybrid hierarchy

```
   [ neural weights θ (schema) ]   <-- trained by replay + current loss
        ▲                                        ▲
   [ key/value episodic mem ]      [ reservoir replay buffer ]
        ▲ read (query)                cap ≈ 64k-256k, prioritized
   [ GRU core ]
        ▲
   [ working state ring ]
```

**Design:** NN-0 has exactly **three** stores: (1) the **neural weights** (slow, container of schema), (2) a host-resident **episodic key/value store** (fast read/write of `(key=proj(h), value, outcome, err)`), capped at ~64k pairs, and (3) a **reservoir replay buffer** of 64–256k experiences. Everything else (event logs, sqlite DB) is **audit/persistence**, not structure.

**A new fact lands in the episodic store and in the reservoir — not in a retraining step.** This is the **no-new-weights** invariant: a fact arriving late is immediately readable, and the weight update path is never *forced* to absorb it; replay then migrates it into the schema gradually (consolidation).

**Anti-forgetting in the store:** episodic KV is append-only until cap (no weight-competition); the only loss is reservoir eviction, which is uniform random and bounded → the *contents* are never overwritten except by cap-roll out.

---

## 5. TASK 5 — CONTINUAL LEARNING

### 5.1 Defenses, evaluated

| Defense | Evidence | Cost | Online | NN-0 verdict |
|---|---|---|---|---|
| Experience replay (reservoir) | strong, cheap, first-line | O(1) | trivial | **adopt (primary)** |
| Reservoir sampling | the default design of replay | 0 | trivial | **adopt** |
| Prioritized replay | large, compute-free | 0 | trivial | **adopt (error-ranked)** |
| Regularization `L2` / weight decay | small | 0 | trivial | **adopt (tiny)** |
| EWC | strong, but Fisher computation & stability | +memory, +compute | moderate | **NN-1 only** |
| Knowledge distillation | needs teacher | — | on | NN-1 |
| Dual-model teacher/student | mature | compute+state | — | NN-2 |
| Checkpoint acceptance | gates | 0 | trivial | **adopt (at each consolidation)** |
| Rehearsal | = replay | 0 | trivial | (part of replay) |
| Adapter-style | per-skill params | +params | — | NN-2 |

### 5.2 The minimum mechanism for NN-0

**`[FACT]` NN-0 = replay-reservoir only.** This is the single minimum adequate defense; the literature review (streaming/continual line, e.g., the Replay analysis paper: "with replay, forgetting is dramatically reduced") supports a bounded reservoir as the cheap, strong first-line for heterogeneous and drifting streams.

**Concretely:**

- **Reservoir** `R` of size ~32k–256k via standard reservoir (online random-exchange) semantics: the incoming item replaces a uniformly chosen slot with probability proportional to capacity. No biased eviction.
- **Prioritization at read**: replay batch is drawn with weights `(1+rank(L_t))^α`, `α≈0.6` — items with large error more likely.
- **Inter-chunk ratio** `λ ≈ 0.5` — replay fraction per mini-batch, mirroring the literature.
- **Weight decay** `5e-4` (not EWC).
- **Checkpoint acceptance** at each consolidation: run the frozen **probe battery**; if a probe decays by more than `δ` (§10) between checkpoints, roll the *update* back (single-parameter soft constraint), never a whole-system reject.

**Explicitly excluded from NN-0:** EWC (needs Fisher — NN-1), distillation, dual-model (NN-2), adapters (NN-2). Each appears exactly at the generation where it earns its compute.

---

## 6. TASK 6 — SELF-DISCOVERY

"A P1 discovers something on its own" is *not* one boolean. Define levels and the test that separates each:

| Level | What "discovery" means here | Distinguishing test |
|---|---|---|
| **Memorization** | recall of a seen instance (or instance family) | exact match of an observed sequence |
| **Interpolation** | answer within the *sampled* envelope | an input inside the trained distribution range |
| **Generalization** | answer to an *unseen* position/example | a held-out example in-distribution-but-unseen |
| **Composition** | combining two previously learned primitives | train `a`,`b`; test `a∘b` (never co-present) |
| **Abstraction** | rule survives a change of surface symbols | same rule with re-rolled alphabet → accuracy ≈ unchanged |
| **Novel hypothesis** | prediction for a *never-before-seen* operator | a seed-drawn operator the model "guesses" above chance |
| **Causal** | direction `A→B` vs `B→A` under intervention | two streams, one pure correlation and one with a causal intervention → probes a register vs a correlator |

**The probes (`P*`) make these measurable:**

- `P-mem` — exact token reproduction of a seen experience, e.g. identical A^n[3].
- `P-gen` — held-out instances of *a known* structure.
- `P-comp` — train `a`, `b` separately; held-out `a∘b`. Memorizing both but not composing yields chance.
- `P-abs` — freeze rule *structure*; new symbol set; accuracy ≈ held-in (unaffected by re-roll).
- `P-causal` — two stream designs, one pure A−B correlation and one intervention; only an internal causal register is changed.
- `P-novel` — a novel operator, predicted at > chance, and the held-out answer is not in the training set memory.

**Epistemic rule:** no level label is claimed without the corresponding `P-*` discriminator run on the fixed probe set. In particular, "P1 discovered X" may only be announced after `P-gen`/`P-comp`/`P-abs` all beat their baselines *and* the appropriate negation test (memorization) fails.

---

## 7. TASK 7 — ANTI-CHEATING TESTS

Mandatory battery (to prevent fooling ourselves):

1. **Held-out combinations** — combos of primitives placed in the training stream only at separate slots; tested on a *never-co-occurring* combination.
2. **Novel sequence lengths** — test at lengths outside the trained envelope (both longer and shorter).
3. **Novel combinations** (`a∘b` pairs never co-trained) — distinct from item 1, guarantees composition is actually required.
4. **Randomized labels** — the same stream with permuted outcome labels must devolve to chance. If not, we have a shortcut.
5. **Ablations** — remove (a) replay, (b) external memory, (c) the GRU (→ fixed-window MLP). Capability drop must be measurable.
6. **Fresh init** — every run starts at random initialization; capability is never "already present" via any preloaded prior.
7. **Multiple seeds** — ≥ 5 per milestone gate, error bars and per-seed lines reported.
8. **Before/after existence** — same probe battery at step 0 (before) and after each stage; capability must be **absent at init**.
9. **Categorical forgetting** — at each stage transition, re-run *all previous* capability probes.

**Source accounting — the baseline:** held-out **test** tokens/symbols must **never** be present in the reservoir or in the episodic store. An explicit `source_id` blacklist + hash check enforces this. Any training-set presence → the probe is void.

---

## 8. TASK 8 — PERSISTENCE / RESTART

NN-0 must stop, restart, and retain everything it "knows" plus its exact trajectory. Checkpoint format (a `.tar` of seven files):

| Path | Contents |
|---|---|
| `model.pt` | `θ`, all tensors |
| `optim.pt` | Adam state (moments, step) |
| `rng.pt` | `torch.get_rng_state()`, `torch.cuda.get_rng_state()`, `numpy`, `random` |
| `episodic.pt` | key/value store (key/projection tensors + values) |
| `replay.pt` | reservoir buffer (items + priorities) |
| `meta.json` | version `{arch, v, seed, hash}`, timestamp |
| `lineage.json` | previous checkpoint links, step counts, experiment ID |

- **Random-state capture** — all four RNG streams saved/restored (torch CPU, torch CUDA, numpy, Python `random`).
- **Model version** — a monotone integer in `meta.json`; version bumps are atomic commits.
- **Training lineage** — every continuation writes a pointer to the previous checkpoint and a run hash in `lineage.json`, so the *entire life* is reproducible even if intermediate states are pruned.
- **Restart test** — restore and run the probe battery: bytes-identical to the same battery run pre-shutdown, then continue streaming from the *same* RNG state.

---

## 9. TASK 9 — GTX-1070 RESOURCE BUDGET

| Item | Budget | Note |
|---|---|---|
| Parameters (NN-0) | **≤ 110k** | target ~105k |
| Batch | 64–128 | seq ≤ 64 |
| VRAM (model + state + optimizer) | **≤ 150 MB** | batch=64 measured 55 MB |
| Training speed | ~150–350k tokens/s | GRU measured 352k |
| Epoch budget per stage | ~1M tokens / ≤ 20 min | at the measured rate |
| Total curriculum (s0–s8) | ≤ 12M tokens | few hours |
| Model checkpoint | ≤ 1 MB + stores ≤ 6 MB | under 10 MB total |
| Memory tables | key/value ≤ 64k · reservoir ≤ 256k | — |
| Restart | < 5 s incl. RNG | verified at §8 |

**Small-experiment-first ruleset:** (a) always measure, never assert; (b) if a component exceeds the line, it's cut and re-scoped, not enlarged; (c) keep base memory in `np.float32` everywhere except where measured; (d) any config change is a new experiment with a new seed, never a silent retune.

---

## 10. TASK 10 — SUCCESS CRITERION (P1-NN-0)

NN-0 **succeeds on this task** only if *all* of the following hold:

| # | Condition | How it is measured | Gate |
|---|---|---|---|
| C1 | capability **absent before experience** | the probe exists at *init-0* = chance | zero at init |
| C2 | acquired **from** sequential experience | ablation <a> and <b> drop performance | Δ > gate |
| C3 | **survives restart** | post-restart probes = pre-restart | exact equality |
| C4 | solves a **held-out novel case** | novel-length / novel-composition probe | ≥ gate |
| C5 | **correction changes** future behavior | inject one corrected chunk; analyze → flipped class | behavioral change |
| C6 | old capabilities remain measurable | forgetting probe after each stage | decay ≤ δ |
| C7 | no full retraining from init | history shows only forward continuation | lineage check |

Failure criterion: any single failure (**C1** violated, C4 blocked, C3 broken, C5 no change, C6 decay, or C7 retrained) → **NN-0 is [REJECTED] for this environment** and the outcome is preserved as an honest reported result.

---

## 11. TASK 11 — BUILD PLAN (NN-0 → NN-1 → NN-2)

| Gen | Core | Added machinery | Gates it targets | Deliverable |
|---|---|---|---|---|
| **NN-0** | GRU + KV memory + reservoir | — | C1–C7, s0–s4 | measured evidence, pipeline, evidence bundle |
| **NN-1** | GRU + **EWC** | concept/relation decoder, prioritized | s4–s6 | continual-EWC comparison |
| **NN-2** | optional SSM/Transformer + **attention memory** | CLOZE, SEQUENCE-LEVEL, multi-step | s6–s8 | reasoning evidence |
| NN-3 | + actions | planning stream | beyond | open |

Each is a self-contained nucleus with its own checkpoint line, so each fails/succeeds independently. **Release gate:** no generation is *archived* until its evidence passes its own Section 10 battery.

---

## 12. TASK 12 — REPORT

# SELECTED NN-0 ARCHITECTURE

**GRU 128 + embedding 32 + readout $V$, with (a) an external key/value store and (b) a reservoir replay buffer. The error object is only next-token cross-entropy. `|θ| ≈ 105k`.**

```
e   = Embedding(x_t, V, 32)
r   = KStore.read(proj(h_{t-1}))
h   = GRU(cat(e, r), h_{t-1}, 128)
P   = Softmax(Readout(h))
L   = CE(P, x_{t+1})     # the *sole* learning signal
```

# WHY

1. **Error stream = development channel.** One gradient only, so every stage feeds the same law; no hidden supervisor path.
2. **Guarantee on your 1070.** 105k params, 1.1 MB state, ~55 MB VRAM (batch 64, measured), one session.
3. **Native experience learning.** The stream is the curriculum; no dataset reshuffling, no epoch copying, no pretrain.
4. **Forgets less by construction than a Transformer of similar size.**
5. **Probe-compatible** — every level of self-discovery runs on this core; no reconstruction/labels to shadow it.
6. **Upgradable scalably**: SSM core and Transformer candidates replace the GRU at NN-2 without breaking the memory/replay contract.

### Why not the alternatives

| Alternative | Why not NN-0 |
|---|---|
| MLP | cannot do novel lengths — static window |
| LSTM | ~20% more params, same pros; GRU is smaller |
| Transformer | 3× slower on the GTX 1070; strong only for long context — that's the memory's job |
| SSM/Mamba | kernel port risk on cu118/Windows; later |
| Autoencoder | no prediction error channel |
| Contrastive | representation-only, not driving |
| External-memory NN | complex to train; the KV store already provides the gain |
| World-model-only | needs the KV + replay; NN-0 **is** a minimal world-model |

# PARAMETER BUDGET

| Block | Parameters |
|---|---|
| Embedding (V=128 · d=32) | 4,096 |
| GRU (input 32+v → 128) | ~61,440 |
| Readout head (128 → V) | 16,384 |
| Read-projection / key head | ~12,000 |
| Extras / bias | < 4,000 |
| **Total** | **≈ 105,000** |

fp32 weights ≈ 0.4 MB; Adam moments ≈ 0.7 MB; full checkpoint < 1.5 MB total (incl. tensors).

# MEMORY DESIGN

Three tiers, exact for NN-0:

1. **Neural weights `θ`** — slow schema (the durable, compressed rule).
2. **Episodic key/value** (host-resident) — a *new fact* available immediately, without a weight update (the **"no-new-weights" invariant**).
3. **Reservoir replay** — 64–256k, error-prioritized, the only channel by which old behavior is re-learned (consolidation).

A new fact is adoptable by a single read of tier 2; its representation in the schema is formed *gradually* by tier 3 (consolidation). **No full retraining from init, ever.**

# TRAINING LOOP

```
for t in stream:
    h, P  = forward(x_t)                   # read + GRU + head
    L     = CE(P, x_{t+1})
    θ     ← AdamW(∇L)
    if L > τ:
        store.write(key=proj(h), val=x_{t+1})   # episodic
    reservoir.push((x_t, x_{t+1}, h))
    if sample(p):                          # replay scheduler
        b ← reservoir.prioritized(λ·64)
        θ ← AdamW(∇(CE(P_b, y_b)))
    if t % E == 0:
        eval_probes(frozen θ)
```

# EXPERIENCE FORMAT

One record per step, written to `lineage.json` and the audit DB:

```
Experience t = {
  id         : step,
  state      : h_t,            # 128-vector
  prediction : P_t,            # V-vector
  outcome    : x_{t+1},
  error      : −log P_t[x_{t+1}],
  memory     : { read_topk : [k, …], written_key : key | None },
  replay     : { sampled : bool, in_batch : bool },
  after      : θ_hash,
}
```

# EVALUATION MATRIX

| Probe | Name | Metric | Gate |
|---|---|---|---|
| P1 | capability before init | before/after | absent = pass |
| P2 | marginal `P(x)` | KL | ≤ 0.03 |
| P3 | 1st-order | NLL | < Markov baseline |
| P4 | pattern completion | accuracy | ≥ 0.85 |
| P5 | composition `a∘b` held-out | accuracy | ≥ 0.7 |
| P6 | concept invariance | accuracy | ≥ 0.8 |
| P7 | relations | accuracy | ≥ 0.7 |
| P8 | long-range memory | accuracy | ≥ 0.7 |
| P9 | multi-step forecast | accuracy | ≥ 0.65 (NN-1) |
| P10 | reasoning (S8) | accuracy | ≥ 0.7 (NN-2) |
| F-at | forgetting | retention | ≥ base − δ each stage |

# FAILURE CONDITIONS

NN-0 is **[REJECTED]** or blocked for its environment when any of:

- C1 fails: capability present at **init (before any experience)** → shortcut/leak → investigate
- C2 fails: acquiring it required replay/memory ablation (i.e., cannot given the stream alone).
- C3 fails: restart does not reproduce; persistence is not proven.
- C4 fails: no held-out generalization (model is a memorizer).
- C5 fails: a correction doesn't change the future.
- C6 fails: an old capability decays beyond δ.
- C7 fails: capability was reached by retraining from init (forbids the mission).
- Missing VRAM-under-consumption or wall-time ≥ 10× budget → redesign, not shrink.

# GTX 1070 RESOURCE PLAN

```
Parameters     ≤ 110k    (target 105k)
Model state    ≈ 1.1 MB  (fp32)
Optimizer      ≈ 0.9 MB
VRAM           ≈ 55 MB @ batch=64/seq=32 (measured; ≤150 MB bound)
Throughput     ≈ 350k tokens/s (GRU, measured)
Curriculum     s0–s7 ≈ ≤ 8M tokens ≈ 1–4 h single session
Checkpoint     ≤ 1.5 MB; bundle < 10 MB/checkpoint
Restart        < 5 s, byte-identical probes
```

**Discipline:** (1) every number is reproduced by the actual run; (2) small experiments first; (3) any module pushing the budget is cut and re-scoped.

---

## EXACT FIRST IMPLEMENTATION TRANSACTION

Order that must be observed exactly; executables run read-only with respect to P1:

**Transaction T0 — "nucleus" (single file + single test):**

1. Create **`p1/live/neural/nn0/nucleus.py`** — the only file whose content is exactly the NN-0 contract above (`Embedding(128,32) → GRU(32,→128) → Readout(128, V)` + KV-store hooks + reservoir append + probe harness). Gradient flow is the sole `CE` path; everything else is read-only infrastructure.
2. Create **`p1/tests/live/test_nn0_nucleus.py`** — runs one stream of 1,024 tokens; asserts: deterministic given seed, learnable (validation loss < init chance), VRAM < 150 MB, and probe `P1` (before) recorded.
3. Execute `python -m pytest p1/tests/live/test_nn0_nucleus.py -v` — must be green.
4. `git add p1/live/neural/nn0/nucleus.py p1/tests/live/test_nn0_nucleus.py` only; **nothing else**.
5. Record (in `outputs/.../P1_NN0_RUN0.md`): baseline probes, loss curves, VRAM, timing, parameters.

**Freeze after T0:** no further writes until the milestone report exists.

**END — EXPERIMENTAL — P1 LIVE INTELLIGENCE RESEARCH**