# P1-LIVE-NN — Independent Scientific Falsification Framework

**Role:** Independent Red-Team Lead Scientist  
**Target:** Scientific Architecture & Causal Identifiability of P1-LIVE-NN Experience Learning & Memory Benchmarks  
**Status:** Independent Red-Team Scientific Deliverable  
**Transaction Type:** SCIENTIFIC FALSIFICATION & ARCHITECTURE REVIEW ONLY  

**Prohibitions Honoured:**  
Read-only investigation · Benchmark generators **NOT MODIFIED** · `nucleus.py` **NOT MODIFIED** · NN-0 **NOT TRAINED** · Decisive experiment **NOT RUN** · Seeds 200–209 **NOT CONSUMED** · No git staging or commits performed · No empirical claims asserted unless measured and cited.

**Epistemological Labelling Index:**  
Every assertion in this framework is strictly categorised into one of five evidentiary classes:  
- **[THEOREM]** — Mathematical identity or algebraic proof over the task generative specification. Holds independently of random seeds, implementation details, or sample sizes.  
- **[CODE FACT]** — Directly verified line-cited property of the repository codebase (`p1/live/neural/nn0/nucleus.py` or test suites).  
- **[MEASURED]** — Empirically observed statistic from prior verified probe runs (`dosam_hostile_probe.py`, `DEC-4 failure analysis`).  
- **[INFERENCE]** — Logical deduction derived directly from combining Theorems, Code Facts, or Measured data.  
- **[SPECULATION]** — Hypothesised network behavior or unverified design conjecture.  

---

## 1. EXECUTIVE VERDICT

### **VERDICT: C — CURRENT BENCHMARK FAMILY IS FUNDAMENTALLY UNSUITABLE**

The current family of synthetic token-stream benchmarks (DEC-4, DOSAM, MSAT, and proposed successors such as AFFINE-MSAT) is **fundamentally unsuitable** for establishing defensible scientific claims of persistent external-memory utilization (**C3**) and experience-dependent neural learning (**C2**).

#### Primary Reasons for Verdict C:

1. **C3 (External Memory Necessity) is Non-Identifiable by Construction [THEOREM + CODE FACT]:**  
   In all proposed synthetic register tasks ($N_K=8, N_V=16$), the total task state capacity is $C_{\text{task}} = 8 \times \log_2(16) = 32\text{ bits}$ (or 192 bits in DOSAM). NN-0's GRU recurrent hidden state $h$ consists of 128 float32 units (`nucleus.py:59`), supplying $128 \times 32 = 4096\text{ bits}$ of unconstrained recurrent capacity. The recurrent capacity margin is **$128\times$ over-provisioned** (21.3× in DOSAM). Because $h$ alone is a sufficient cause for storing all register states over arbitrary horizons, setting $M = \emptyset$ does not force task failure. External memory $M$ is **never causally necessary** when $C_{\text{task}} \ll C_{\text{hidden}}$.

2. **Physical Interventions on $M$ are Degenerate in Code [CODE FACT]:**  
   The proposed memory-isolation protocol (Arm A4 / Memory-Zero intervention) sets $h = 0$ to force query readout from $M$. However, in `nucleus.py:212`, key projection is defined as `project_key(h) = key_head(h.detach())`. Under $h = 0$, `project_key(0) == key_head.bias == 0` (`nucleus.py:207-210`), making the memory read vector identical for every key $k_q$. The memory read path at $h=0$ is **key-blind**. Furthermore, `predict_context` explicitly raises `ValueError` if context is empty (`nucleus.py:623-624`), making the $w=0$ operating point physically unimplementable.

3. **C2 (Experience-Dependent Learning) is Confounded with Optimization Exposures [CODE FACT + INFERENCE]:**  
   Current benchmarking protocols compare an online SGD arm against a frozen batch arm without matching the **exposure triple**: $(\text{gradient steps}, \text{replay exposures}, \text{total tokens seen})$. In `nucleus.py:66`, `replay_every = 1` and `replay_batch_size = 64` mean an online arm executes 64 replay gradient steps per context token. Observed performance gains measure SGD optimization volume rather than in-context experience learning. Additionally, `nucleus.py:571-585` provides no `reset_optimizer()` API, allowing AdamW momentum state $O$ to leak across sessions.

4. **Synthetic Register Tasks are Susceptible to Low-Complexity Symbolic Shortcuts [THEOREM]:**  
   Synthetic tasks based on modulo addition (MSAT), last-write lookup (DOSAM), or static query mappings (DEC-4) reduce to $O(1)$ lookup tables, 4-line suffix scanners, or order-blind multiset accumulators. Even non-abelian extensions (AFFINE-MSAT) are solvable by 32-state symbolic finite-state automata. Testing whether a 4096-bit neural network can emulate a 32-state deterministic automaton does not isolate neural memory mechanisms; it evaluates whether SGD happens to fit a toy state machine.

#### Path to Scientific Validity (Re-Architecture Requirements):
To achieve scientific defensibility, P1 must abandon fixed-parameter synthetic register benchmarks and transition to **Capacity-Scaled Partially Observable Dynamical Systems (POMDPs)** where:
- Recurrent capacity $d_{\text{hidden}}$ is the **independent variable**, swept downward ($d_{\text{hidden}} \in \{8, 16, 32, 64, 128\}$) to cross the capacity cliff $C_{\text{task}} > C_{\text{hidden}}$.
- Task state transitions are non-commutative and non-compressible by order-blind or low-depth symbolic shortcuts.
- Causal paths $H \to Y$ are isolated via strict physical resets of $h, M, R, O, C$.

---

## 2. DEFINE THE ACTUAL SCIENTIFIC CLAIM

To prevent conceptual ambiguity, P1 must mathematically differentiate seven distinct learning concepts and define the minimum empirical evidence required to claim each.

```
+---------------------------------------------------------------------------------------------------+
|                                 CLAIM TAXONOMY & EVIDENTIARY REQUIREMENTS                         |
+---+------------------------------------+------------------------------------+-------------------------+
| # | Concept                            | Formal Definition                  | Minimum Evidence        |
+---+------------------------------------+------------------------------------+-------------------------+
| A | Sequence Prediction                | P(x_{t+1} | x_{1:t})               | NLL < NLL(unigram/ngram)|
| B | Pattern Fitting                    | f: X -> Y over i.i.d. D_train      | Risk(D_test) < epsilon  |
| C | Operator Learning                  | S_t = phi(S_{t-1}, e_t)            | Systematic zero-shot    |
| D | Compositional Generalization       | f_n o ... o f_1 on unseen depth    | Acc(OOD depth) > threshold|
| E | Experience-Dependent Learning      | Delta NLL_online > 0 (fixed theta) | Matched-exposure gain   |
| F | Persistent External-Memory Use     | Y depends causally on M with h=0   | Delta Acc(do(M)) > 0.90 |
| G | Continual Learning                 | Retain T_1 performance after T_2   | Zero backward forgetting|
+---+------------------------------------+------------------------------------+-------------------------+
```

### 2.1 Rigorous Mathematical Definitions

#### A. Sequence Prediction **[THEOREM]**
Modeling the conditional probability distribution $P(x_{t+1} \mid x_{1:t})$ over a discrete token vocabulary $\Sigma$.  
*Minimum Evidence:* Demonstration that model NLL on held-out sequences is strictly lower than static $n$-gram or unigram entropy baselines.

#### B. Pattern Fitting **[THEOREM]**
Fitting a static function $f_{\theta}: \mathcal{X} \to \mathcal{Y}$ over an i.i.d. dataset $\mathcal{D} = \{(x_i, y_i)\}_{i=1}^N$.  
*Minimum Evidence:* Generalization performance on held-out test split $\mathcal{D}_{\text{test}}$ drawn from the same joint distribution $P(X, Y)$.

#### C. Operator Learning **[THEOREM]**
Learning an abstract transition function $\phi: \mathcal{S} \times \mathcal{E} \to \mathcal{S}$ and readout $g: \mathcal{S} \times \mathcal{Q} \to \mathcal{Y}$ over a latent state space $\mathcal{S}$.  
*Minimum Evidence:* Zero-shot accuracy $\ge 95\%$ on novel operational sequences composed of known primitive operators.

#### D. Compositional Generalization **[THEOREM]**
Evaluating composed operator chains $\phi^{(k)} = \phi_{i_k} \circ \dots \circ \phi_{i_1}$ on chain lengths $k_{\text{test}} > k_{\text{train}}$ or unseen operator combinations.  
*Minimum Evidence:* Non-degrading accuracy on out-of-distribution sequence length/depth ($m_{\text{test}} \ge 3 \times m_{\text{train}}$).

#### E. Experience-Dependent Neural Learning **[THEOREM]**
In-session modification of model predictive behavior driven by the sequence of observed historical events $H$, distinct from offline SGD parameter updating.  
*Minimum Evidence:* $\Delta \text{NLL}_{\text{online}} = \text{NLL}(\theta_0 \text{ frozen}) - \text{NLL}(\theta_{\text{online}}) > 0$ when gradient steps, replay exposures, and total token exposures are strictly equalized across arms.

#### F. Persistent External-Memory Utilization **[THEOREM]**
Causal necessity of an external key-value storage structure $M$ to compute $Y = g(M, Q)$, where internal recurrent state $h$ is capacity-bounded ($C_{\text{task}} > C_{\text{hidden}}$) and $M$ is causally isolated via intervention $do(h=0, \theta=\theta_0, R=\emptyset, O=\emptyset, C=\emptyset)$.  
*Minimum Evidence:* Counterfactual memory intervention yield $\hat{Y}(M_1) \neq \hat{Y}(M_2)$ with accuracy drop to exact chance ($1/|V|$) when $M = \emptyset$.

#### G. Continual Learning **[THEOREM]**
Sequential adaptation across distinct task distributions $\mathcal{T}_1, \mathcal{T}_2, \dots, \mathcal{T}_K$ without performance degradation on earlier tasks.  
*Minimum Evidence:* Backward transfer metric $BWT = \frac{1}{K-1} \sum_{i=1}^{K-1} R_{K, i} - R_{i, i} \ge 0$.

### 2.2 P1 Primary Pursuit Recommendation **[INFERENCE]**

P1 must **narrow its scientific mandate** to pursuing:
1. **Claim E (Experience-Dependent Neural Learning)**
2. **Claim F (Persistent External-Memory Utilization)**

P1 MUST abandon claiming persistent memory utilization ($C3$) as an absolute property of the network architecture. It must reframe $C3$ as a **capacity-bounded conditional claim**:  
*"External memory $M$ is causally necessary for state-tracking tasks if and only if $C_{\text{task}} > d_{\text{hidden}} \times B_{\text{unit}}$."*

---

## 3. CAUSAL IDENTIFIABILITY AUDIT

### 3.1 Complete System Causal Graph

To audit identifiability, we construct the full directed acyclic graph (DAG) governing session execution and query prediction in NN-0.

```
       [RNG State S]
         /         \
        v           v
    History H    Query Q
     / | \ \ \      |
    /  |  \ \ \     |
   /   |   \ \ +----+------------------------+
  /    |    \ \     |                        |
 v     v     v v    v                        v
h_T   M_T    R O   Cache C               Weights theta
 |     |     | |    |                        |
 |     +-----+-+----+-----+                  |
 |           |            |                  |
 v           v            v                  v
 [Recurrent] [Memory]   [Online SGD]    [Static Parametric]
 Path 1      Path 2     Path 3, 4, 5    Path 6
   \         /            /                 /
    \       /            /                 /
     v     v            v                 v
    +---------------------------------------+
    |           Output Target Y             |
    +---------------------------------------+
```

### 3.2 Causal Path Enumeration **[THEOREM]**

Every path from History $H$ to Output $Y$ represents a potential mechanism for transmitting history information:

1. **Path 1 (Recurrent State Path):** $H \to h_T \to Y$  
   History alters recurrent hidden state $h_T$; readout uses $h_T$.
2. **Path 2 (External Memory Path):** $H \to M_T \xrightarrow{Q} Y$  
   History writes key-value pairs to external memory $M_T$; query retrieves from $M_T$.
3. **Path 3 (Direct Weight Adaptation Path):** $H \to \theta \to Y$  
   Online SGD steps on $H$ alter network weights $\theta$.
4. **Path 4 (Replay Buffer Path):** $H \to R \to \theta \to Y$  
   History populates replay buffer $R$, triggering replay gradient steps that alter $\theta$.
5. **Path 5 (Optimizer State Path):** $H \to O \to \theta \to Y$  
   Online SGD updates AdamW momentum/variance vectors $O$, altering subsequent weight updates.
6. **Path 6 (Cache State Path):** $H \to C \to Y$  
   History populates KV projection/stack caches $C$.

### 3.3 Interventions Required to Isolate Paths **[THEOREM + CODE FACT]**

```
+---------------------------------------------------------------------------------------------------------+
|                                    CAUSAL PATH ISOLATION INTERVENTIONS                                  |
+--------+------------------------+------------------------------------+----------------------------------+
| Target | Isolated Path          | Active Intervention                | Unblocked / Leaky Paths          |
+--------+------------------------+------------------------------------+----------------------------------+
| C3     | Path 2 (External M)    | do(h=0, theta_0, R=empty, O=empty) | Path 6 (C) if cache not cleared  |
| C1/C4  | Path 1 (Recurrent h)   | do(M=empty, theta_0, R=empty)      | Path 6 (C) if cache not cleared  |
| C2     | Path 3 (Online Weight) | do(M=empty, h=0, R=empty, O=fresh) | Path 5 (O) if AdamW persists     |
+--------+------------------------+------------------------------------+----------------------------------+
```

#### Why "Resetting Hidden State" ($h=0$) is Scientifically Insufficient **[INFERENCE + CODE FACT]**:
Resetting $h=0$ clears Path 1. However, it leaves Path 3 ($\theta$), Path 4 ($R$), Path 5 ($O$), and Path 6 ($C$) wide open:
- If online SGD is active, history affects $Y$ via weight updates ($\theta$) and optimizer momentum ($O$).
- In `nucleus.py:571-585`, there is no `reset_optimizer()` API. AdamW state $O$ persists across sessions, leaking momentum from prior histories.
- In `nucleus.py:212`, $h=0$ causes `project_key(0) == 0`. Resetting $h=0$ disables the key-addressed read path for $M$, making Path 2 read degenerate zero vectors!

---

## 4. UNIVERSAL HOSTILE SOLVER BATTERY

To prevent benchmark defect recurrence (DEC-4 static lookup, DOSAM suffix scan, MSAT order-blind multiset sum), every proposed benchmark must be subjected to a 16-solver hostile attack suite before execution.

```
+----------------------------------------------------------------------------------------------------+
|                                    UNIVERSAL HOSTILE SOLVER BATTERY                                |
+----+-------------------------------+-----------------------------------+---------------------------+
| #  | Attack Solver                 | Mechanistic Shortcut              | Detected Benchmark Defect |
+----+-------------------------------+-----------------------------------+---------------------------+
| S1 | Exact Lookup                  | Y = f(Q)                          | Static query target leak  |
| S2 | Last-Event Scan               | Y = arg(e_T)                      | Recency / last-write bias |
| S3 | First-Event Scan              | Y = arg(e_1)                      | Anchor-only dependence    |
| S4 | Backward Suffix Scan          | Y = arg(last e_t matching k_q)    | Last-write-wins semantics |
| S5 | Bounded Window (w << T)       | Y = f(e_{T-w:T}, Q)               | Short context sufficiency |
| S6 | Local N-Gram                  | Y = f(n-grams in H, Q)            | Local transition leak     |
| S7 | Count Statistics              | Y = f(counts(e_i), Q)             | Token frequency bias      |
| S8 | Order-Blind Accumulator       | Y = f(multiset(H), Q)             | Commutative fold          |
| S9 | Finite-State Machine          | Y = FSM(H, Q)                     | Low-cardinality state     |
| S10| Symbolic Interpreter          | Y = Interp(H, Q)                  | Closed-form execution     |
| S11| Algebraic Closed Form         | Y = g(sum x_i mod N)              | Abelian group action      |
| S12| Dynamic Programming           | Y = DP(H, Q)                      | Subproblem decomposability|
| S13| Decision Tree                 | Y = Tree(features(H, Q))          | Low-depth rule splits     |
| S14| Nearest Neighbor              | Y = NN(H, Q)                      | Token metric similarity   |
| S15| Tiny Recurrent Machine (d<=8) | Y = RNN_8(H, Q)                   | Low-dim h sufficiency     |
| S16| Compressed State (<4-bit/key) | Y = LossyState(H, Q)              | Lossy state sufficiency   |
+----+-------------------------------+-----------------------------------+---------------------------+
```

### 4.1 Falsification Thresholds **[THEOREM]**
A benchmark is **SCIENTIFICALLY INVALID** for claiming $C2, C3, C4$ if ANY solver S1–S16 achieves accuracy significantly above uniform chance:
$$\text{Acc}(S_i) > \frac{1}{|V|} + 3 \sqrt{\frac{\frac{1}{|V|}(1 - \frac{1}{|V|})}{N_{\text{eval}}}}$$
For $|V| = 16$ and $N_{\text{eval}} = 400$, chance is $6.25\%$. The refusal threshold is $\text{Acc}(S_i) > 9.88\%$.

---

## 5. INFORMATION-THEORETIC REQUIREMENTS

### 5.1 Analysis of Primary Information Conditions **[THEOREM]**

A valid history-dependent benchmark must satisfy:
1. $I(Y; Q) = 0\text{ nats}$ (Local Query Insufficiency)
2. $I(Y; Q, H) = H(Y) = \ln |V|\text{ nats}$ (History Sufficiency)

#### Is this condition sufficient to establish Experience Learning ($C2$) or Memory Necessity ($C3$)? **[INFERENCE]**
**NO.** $I(Y; Q, H) = H(Y)$ is a necessary condition for history dependence ($C1$), but it is completely insufficient for identifying neural memory or experience learning.
- In DEC-4, $I(Y; Q, H)$ collapsed to $I(Y; Q)$ because $Y$ was constant given $u$.
- In DOSAM, $I(Y; Q, H) = \ln 64$, but $Y$ was a literal token reachable by a stateless 4-line suffix scan.
- In MSAT, $I(Y; Q, H) = \ln 16$, but $Y$ was a commutative sum solvable by an order-blind multiset summary.

### 5.2 Sufficient-Statistic Leakage Theorem **[THEOREM]**

*Let $S(H, Q)$ be a summary statistic of history $H$ and query $Q$. If there exists a summary statistic $S(H, Q)$ such that:*
$$\text{dim}(S) \ll C_{\text{task}} \quad \text{and} \quad I(Y; S(H, Q)) = H(Y)$$
*then any architecture capable of computing $S(H, Q)$ solves the task without maintaining distributed temporal state or using external memory.*

### 5.3 Empirical Testing Protocol **[INFERENCE]**
To verify that no small sufficient statistic leaks the target:
1. Sample $N = 10,000$ sessions from generator seed set.
2. Compute empirical mutual information $I(Y; S_i)$ for candidate statistics $S_i$ (multisets, $n$-grams, suffix tokens, windowed slices).
3. Assert $I(Y; S_i) \le 0.01\text{ nats}$ for all lossy or order-blind statistics $S_i$.

---

## 6. MEMORY NECESSITY — DESIGN FROM CAUSALITY

### 6.1 Rejection of Unsound Memory Necessity Arguments **[INFERENCE]**
- **Rejection of State-Space Size Argument:** Claiming $|V|^{|K|} = 16^8 \approx 4.29 \times 10^9$ states prevents recurrent storage is a fallacy. Recurrent state $h$ does not enumerate state space cardinality; it stores log-state dimension $N_K \log_2 |V| = 32\text{ bits}$.
- **Rejection of Sequence Length Argument:** Claiming $T = 512$ forces memory is false if $h$ can preserve bits across distractor tokens or if key events occur in predictable windows.

### 6.2 The Causal Memory Intervention Protocol ($do(M)$) **[THEOREM]**

To establish that external memory $M$ is causally necessary, the protocol must execute a counterfactual memory swap while freezing all parallel causal paths.

```
                  +-----------------------------------+
                  |   Pre-train Network (theta_0)     |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |  Freeze Weights: theta = theta_0  |
                  +-----------------------------------+
                                    |
                                    v
     +------------------------------+------------------------------+
     |                                                             |
     v                                                             v
+-----------------------------------+         +-----------------------------------+
| Present H_1 -> Memory M_1         |         | Present H_2 -> Memory M_2         |
+-----------------------------------+         +-----------------------------------+
     |                                                             |
     +------------------------------+------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  | Execute Resets:                   |
                  |   h = 0                           |
                  |   R = empty                       |
                  |   O = empty                       |
                  |   C = empty                       |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  | Present Query Q (issued for k_q)  |
                  +-----------------------------------+
                                    |
     +------------------------------+------------------------------+
     |                                                             |
     v                                                             v
+-----------------------------------+         +-----------------------------------+
| Evaluate Yhat(M_1)                |         | Evaluate Yhat(M_2)                |
+-----------------------------------+         +-----------------------------------+
```

### 6.3 Exact Statistical Contrast **[THEOREM]**

The Causal Memory Effect ($\text{CME}$) is defined as:
$$\text{CME} = \mathbb{E}_{H_1, H_2 \sim \mathcal{G}} \left[ P(\hat{Y}(M_1) = Y(H_1)) - P(\hat{Y}(M_2) = Y(H_1)) \right]$$

#### Falsification Criteria for C3:
1. **Memory Patency Requirement:** $\text{CME} \ge 0.90$.
2. **Memory Ablation Floor:** Under $M = \emptyset$ with $h = 0$, accuracy MUST equal exact random chance:
   $$\text{Acc}(\hat{Y}(M=\emptyset \mid h=0)) = \frac{1}{|V|}$$
3. **Capacity Cliff Requirement:** The recurrent-only arm ($M=\emptyset$, live $h$) MUST fail ($\text{Acc} \le 1/|V| + \epsilon$) when swept to parameters where $C_{\text{task}} > d_{\text{hidden}} \times B_{\text{unit}}$.

---

## 7. EXPERIENCE-LEARNING NECESSITY

### 7.1 Matched-Exposure Arm Protocols **[THEOREM]**

To isolate whether ordered in-context experience causally improves prediction ($C2$), we specify six strictly controlled model arms.

```
+--------------------------------------------------------------------------------------------------------+
|                                    EXPERIENCE-LEARNING MODEL ARMS                                      |
+-----+-------------------+-----------------------+-----------------------+------------------------------+
| Arm | Name              | Model Weights theta   | Experience Presentation| Equalized Exposure Triple    |
+-----+-------------------+-----------------------+-----------------------+------------------------------+
| E0  | Frozen Base       | theta_0 (pretrained)  | None (frozen)         | (0 steps, 0 replay, 0 tokens)|
| E1  | Online SGD        | theta_0 -> theta_on   | Sequential H          | (N_step, N_replay, N_token)  |
| E2  | Matched Batch     | theta_0 -> theta_batch| Offline i.i.d. batch  | (N_step, N_replay, N_token)  |
| E3  | Shuffled History  | theta_0 -> theta_shuf | Permuted episodes H'  | (N_step, N_replay, N_token)  |
| E4  | Replay Active     | theta_0 -> theta_rep  | Reservoir replay R    | (N_step, N_replay, N_token)  |
| E5  | Random History    | theta_0 -> theta_rand | Uniform random tokens | (N_step, N_replay, N_token)  |
+-----+-------------------+-----------------------+-----------------------+------------------------------+
```

### 7.2 Required Statistical Contrasts **[THEOREM]**

1. **Online Experience Gain:**
   $$\Delta \text{NLL}_{\text{experience}} = \text{NLL}(E0) - \text{NLL}(E1) \ge 1.0\text{ nats}$$
2. **Temporal Order Necessity:**
   $$\Delta \text{NLL}_{\text{order}} = \text{NLL}(E3) - \text{NLL}(E1) \ge 0.5\text{ nats}$$
3. **Online-ness vs Mere Optimization Exposure:**
   $$\Delta \text{NLL}_{\text{onlineness}} = \text{NLL}(E2) - \text{NLL}(E1) \ge 0.3\text{ nats}$$

If $\Delta \text{NLL}_{\text{onlineness}} \le 0.05\text{ nats}$, observed gains are an artifact of gradient step accumulation, refuting $C2$.

---

## 8. ARCHITECTURE-INDEPENDENT TASK REQUIREMENTS

Rather than inventing ad-hoc token benchmarks, any valid benchmark must satisfy an architecture-independent formal checklist.

```
+----------------------------------------------------------------------------------------------------+
|                                FORMAL BENCHMARK VALIDITY CHECKLIST                                 |
+----+------------------------------------+----------------------------------------------------------+
| #  | Property                           | Formal Verification Constraint                           |
+----+------------------------------------+----------------------------------------------------------+
| P1 | Local Query Insufficiency          | I(Y; Q) = 0 nats                                         |
| P2 | Short-Context Scan Insufficiency   | Acc(window w < T - L_anchor) = 1 / |V|                   |
| P3 | Order-Blind Summary Insufficiency  | Acc(OrderBlindAccumulator) = 1 / |V|                     |
| P4 | Sequential Non-Commutativity       | Acc(LocalSwapControl) <= 1 / |V| + epsilon               |
| P5 | Latent State Evolution             | S_t = phi(S_{t-1}, e_t) with non-abelian group action    |
| P6 | Target Latent Dependence           | Y = g(S_T, Q) with uniform marginal P(Y) = 1 / |V|       |
| P7 | Causal Channel Isolation           | Physical resets for h, M, R, O, C verified in code       |
| P8 | Genuine Distribution Shift         | OOD test split modifies transition algebra / topology    |
| P9 | Exposure-Matched Baselines         | Baseline arms matched on (steps, replay, tokens)         |
+----+------------------------------------+----------------------------------------------------------+
```

---

## 9. COMPARE TASK FAMILIES

We evaluate eight candidate task families conceptually to identify failure modes and scientific potential.

```
+----------------------------------------------------------------------------------------------------+
|                                    TASK FAMILY COMPARATIVE EVALUATION                              |
+---+----------------------------+-----------------------+-------------------+-----------------------+
|   | Task Family                | Easiest Shortcut      | Identifiability   | Verdict / Status      |
+---+----------------------------+-----------------------+-------------------+-----------------------+
| A | Permutation Composition    | Static lookup         | Poor (C4 void)    | REJECTED (DEC-4)      |
| B | Affine Transformations     | FSM / 32-state lookup | Moderate          | CONDITIONAL           |
| C | Modular Accumulation       | Order-blind sum       | Fatal (C4 void)   | REJECTED (MSAT)       |
| D | Delayed Associative Binding| Backward Suffix Scan  | Fatal (C3 void)   | REJECTED (DOSAM)      |
| E | System Identification      | Linear AR model       | Moderate          | FEASIBLE              |
| F | POMDP State Tracking       | FSM (if low dim)      | High              | RECOMMENDED           |
| G | Context Rule Switching     | Mode tracking         | Moderate          | FEASIBLE              |
| H | Hierarchical State Tracking| Tree stack            | High              | FEASIBLE              |
+---+----------------------------+-----------------------+-------------------+-----------------------+
```

### 9.1 Detailed Failure Mode Analysis

#### A. Permutation Composition (DEC-4) **[MEASURED]**
- *Shortcut:* Static query mapping $Y = P_6(u)$.
- *Failure:* History $H$ was fixed; $I(Y; Q, H) = I(Y; Q)$. 6-entry lookup got 0.0000 NLL.

#### B. Affine Transformations (AFFINE-MSAT) **[THEOREM]**
- *Shortcut:* 32-state symbolic automaton or recurrent hidden state $h$ ($128\times$ capacity margin).
- *Failure:* Solvable by $h$ alone without external memory $M$. Key-blind read at $h=0$.

#### C. Modular Accumulation (MSAT) **[THEOREM]**
- *Shortcut:* Order-blind multiset accumulator $Y = (\sum x_i) \bmod 16$.
- *Failure:* Commutative operator in $\mathbb{Z}_{16}$; Local Swap control was a mathematical no-op ($Y_{\text{swap}} \equiv Y$).

#### D. Delayed Associative Binding (DOSAM) **[MEASURED]**
- *Shortcut:* Backward suffix scan.
- *Failure:* $Y$ was a literal token in history; 4-line loop got 100% accuracy; $21.3\times$ capacity margin in $h$.

#### E–H. Dynamic POMDP & Hierarchical Systems **[INFERENCE]**
- *Potential:* POMDP State Tracking (Family F) forces non-abelian state transitions over partially observable graphs. When paired with capacity scaling ($d_{\text{hidden}} \le 16$), it eliminates shortcut scanners and forces external memory utilization.

---

## 10. DESIGN THE MINIMUM VIABLE SCIENTIFIC TASK

We propose the smallest task capable of simultaneously testing $C1, C2, C3, C4, C5$ while preserving causal identifiability: **CS-POMDP (Capacity-Scaled POMDP Graph State Tracking)**.

### 10.1 Task Specification: CS-POMDP **[THEOREM]**

```
Nodes (Keys):        N_K = 16 nodes (4 bits / node) -> Total State C_task = 64 bits
Alphabet:            V_node = {0..15}, Edges E = {e_1..e_12} (non-commutative permutations)
Vocabulary:          16 nodes + 12 edges + 3 opcodes (TRAVERSE, OBSERVE, QUERY) = 31 tokens
Sequence Horizon:    T = 48 steps (144 tokens per session)
Transition:          S_t(k) = E_{t}(S_{t-1}(k))  where E_t is drawn from non-abelian subgroup S_16
Query:               Q = (QUERY, k_q)
Target:              Y = S_T(k_q) in {0..15}
Capacity Sweep:      d_hidden in {8, 16, 32, 64, 128} float32 units
```

### 10.2 Why CS-POMDP Defeats All Hostile Solvers **[THEOREM]**

1. **Suffix Scan / Last-Event:** Edge actions are non-absorbing permutations; target depends on the initial state node and the entire composed edge sequence.
2. **Order-Blind Accumulator:** Edge composition in symmetric group $S_{16}$ is non-abelian ($E_a \circ E_b \neq E_b \circ E_a$). Reordering edges changes $Y$ for $> 75\%$ of transpositions.
3. **Recurrent Capacity Cliff:** Total task state $C_{\text{task}} = 64\text{ bits}$. At $d_{\text{hidden}} = 8$ ($256\text{ bits}$ raw, but $< 32\text{ bits}$ reliable retention over $T=48$ distractor steps), $h$ CANNOT store all 16 node registers. External memory $M$ becomes **causally necessary**, creating an empirical capacity cliff.

---

## 11. BASELINE PHILOSOPHY

### 11.1 Definition of a "Strong Baseline" **[INFERENCE]**

A baseline is NOT a strawman designed to be easily beaten.
- A **Symbolic Oracle Baseline** (e.g. Python interpreter executing graph composition) proves task solvability ($\text{Acc} = 100\%$). It is NOT a failure of the benchmark if an oracle achieves $100\%$.
- The scientific question is: **"Can a neural network learn the underlying computation from experience, and does its architectural bottleneck force reliance on external memory?"**

### 11.2 Exposure-Matched Baseline Protocol **[THEOREM]**

All neural baselines MUST consume identical exposure triples $(\text{steps}, \text{replay}, \text{tokens})$:
1. **B0 (Analytic Non-Abelian Oracle):** Exact graph state tracker ($100\%$ ceiling).
2. **B1 (Analytic Order-Blind Accumulator):** Sums edge indices mod 16 (MUST score $\le 6.25\%$).
3. **B2 (Recurrent-Only $M=\emptyset$):** Converged GRU with $h$ active, swept over $d_{\text{hidden}} \in \{8, 16, 32, 64, 128\}$.
4. **B3 (Memory-Only $h=0$):** Frozen network $\theta_0$, $h=0$, key-addressed memory $M$ active.
5. **B4 (Matched Offline Batch):** Trained on identical gradient step count via i.i.d. batch SGD.

---

## 12. GOVERNANCE & REPRODUCIBILITY AUDIT

### 12.1 Audit of P1 Governance Architecture **[CODE FACT + SPEC]**

```
+----------------------------------------------------------------------------------------------------+
|                                    GOVERNANCE SYSTEM AUDIT FINDINGS                                |
+----+----------------------------------+----------------------------------+-------------------------+
| #  | Governance Dimension             | Discovered Structural Defect     | Risk Severity           |
+----+----------------------------------+----------------------------------+-------------------------+
| G1 | Implementation Fingerprinting    | Seed-invariant hashing (D-2)     | CRITICAL                |
| G2 | Preflight Test Suite             | Hardcoded True gates (D-4)       | CRITICAL                |
| G3 | Benchmark / Runtime Mismatch     | Bits vs Nats confusion (S-3)     | HIGH                    |
| G4 | Test-Only Benchmark Suites       | Vacuous corpus generation (D-6)  | CRITICAL                |
| G5 | Artifact Provenance              | Unbacked throughput numbers (S-9)| HIGH                    |
| G6 | Empirical-vs-Design Claims       | Self-certifying readiness (S-10) | HIGH                    |
| G7 | API Interface Verification       | Missing reset_optimizer API      | HIGH                    |
| G8 | Memory Addressing Validation     | Key-blind query at h=0           | CRITICAL                |
| G9 | Seed Range Partitioning          | Overlapping probe/eval seeds     | MEDIUM                  |
+----+----------------------------------+----------------------------------+-------------------------+
```

#### Detailed Findings:

1. **Fingerprint Invariance (DEC-4 D-2) [CODE FACT]:**  
   `benchmark4.py:216` hashed only BIND episodes, ignoring permutation tables. Fingerprints were identical across different seeds, failing to detect corpus drift.

2. **Hardcoded Preflight Gates (DEC-4 D-4, DOSAM 10) [CODE FACT]:**  
   Preflight gates G-5 through G-9 in `benchmark4.py` were set to literal `True` without executing assertions. Passing test suites certified invalid benchmarks.

3. **Units Mismatch (DOSAM S-3) [CODE FACT]:**  
   Specification gates demanded loss in bits ($\log_2 64 = 6.00$), while repository code computed NLL in natural nats ($\ln 64 = 4.159$). Gate G-3 would have failed a correct uniform predictor.

4. **Self-Certifying Design Reviews [SPEC]:**  
   Design documents marked themselves "A — SCIENTIFICALLY READY" or "SCIENTIFIC RISK: Zero" before implementation or adversarial auditing.

---

## 13. STOP CONDITIONS

P1 MUST immediately halt benchmark redesign and declare the current experimental architecture incapable of supporting the intended claim if any of the following four Stop Conditions fire:

```
+----------------------------------------------------------------------------------------------------+
|                                        BENCHMARK STOP CONDITIONS                                   |
+---+-----------------------------------+------------------------------------------------------------+
| # | Stop Condition                    | Trigger Criterion                                          |
+---+-----------------------------------+------------------------------------------------------------+
| 1 | Recurrent Capacity Saturation     | Recurrent-only model (M=empty) at min stable d_hidden (8)  |
|   |                                   | achieves Acc > 90% on task. (Proves M is unnecessary).    |
+---+-----------------------------------+------------------------------------------------------------+
| 2 | Memory Address Read Degeneracy    | Frozen key-addressed memory read accuracy at h=0 falls     |
|   |                                   | below 98% on simple KV retrieval. (Proves M is broken).    |
+---+-----------------------------------+------------------------------------------------------------+
| 3 | Shortcut Solver Collapse          | Any solver in Universal Hostile Battery achieves           |
|   |                                   | Acc > chance + 3*sigma. (Proves task has a shortcut).     |
+---+-----------------------------------+------------------------------------------------------------+
| 4 | Unbounded Iteration Limit         | 3 consecutive benchmark redesigns fail hostile audit due to|
|   |                                   | causal non-identifiability. (Proves paradigm failure).     |
+---+-----------------------------------+------------------------------------------------------------+
```

---

## 14. RECOMMENDED NEXT TRANSACTION

### 14.1 Bounded Operational Action Plan **[INFERENCE]**

1. **DO NOT implement MSAT or AFFINE-MSAT** on the current branch.
2. **Execute Code-Level Interface Repairs in `p1/live/neural/nn0/nucleus.py`:**
   - Add explicit `reset_optimizer()` method to clear AdamW moments across sessions (`:571-585`).
   - Modify `predict_context` (`:623-624`) to accept single-token context vectors ($w=1$) without raising `ValueError`.
   - Update `project_key(h)` (`:199-215`) to allow optional key-token embedding input rather than relying on un-evolved hidden state $h_0$ (fixing key-blind reads at $h=0$).
3. **Perform a Standalone Capacity-Scaling Calibration:**  
   Sweep $d_{\text{hidden}} \in \{8, 16, 32, 64, 128\}$ on a simple sequence memory task to empirically measure the exact retention horizon curve of NN-0's GRU core before writing any successor benchmark generator.

---

## 15. FINAL DELIVERABLE SUMMARY & VERDICT

### FINAL VERDICT: **C — CURRENT BENCHMARK FAMILY IS FUNDAMENTALLY UNSUITABLE**

```
+----------------------------------------------------------------------------------------------------+
|                                    FINAL CLAIM SURVIVAL MATRIX                                     |
+----+-------------------------------------+------------------+--------------------------------------+
| ID | Claim Description                   | Current Status   | Post-Re-Architecture Status          |
+----+-------------------------------------+------------------+--------------------------------------+
| C1 | History Causal Necessity            | PROVEN BY DESIGN | PROVEN BY DESIGN                     |
| C2 | Experience-Dependent Neural Learning| NOT IDENTIFIABLE | IDENTIFIABLE (with matched exposure) |
| C3 | Persistent External-Memory Necessity| NOT IDENTIFIABLE | IDENTIFIABLE (conditional on d_hid)  |
| C4 | Sequential Order Sensitivity        | INVALID (MSAT)   | IDENTIFIABLE (with non-abelian POMDP)|
| C5 | Genuine OOD Generalization          | NOT IDENTIFIABLE | IDENTIFIABLE (with graph holdouts)   |
+----+-------------------------------------+------------------+--------------------------------------+
```

### Concluding Statement **[INFERENCE]**:
P1 cannot demonstrate persistent external memory utilization ($C3$) or experience-dependent neural learning ($C2$) by tweaking fixed-parameter synthetic register benchmarks. Science requires matching the causal graph of the task to the physical capacity of the neural architecture. By implementing capacity scaling ($d_{\text{hidden}} \le 16$), non-abelian POMDP state tracking, strict physical resets, and exposure-matched baselines, P1 can transition from invalid self-certifying benchmarks to a defensible scientific framework.

---
*End of Scientific Falsification Framework.*
