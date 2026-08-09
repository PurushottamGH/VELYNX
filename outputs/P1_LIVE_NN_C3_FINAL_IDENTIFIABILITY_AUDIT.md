# P1-LIVE-NN — Final C3 Identifiability Challenge & Architectural Audit

**Role:** Independent Red-Team Lead Scientist  
**Target:** Scientific Identifiability of Persistent External-Memory Utilization (C3) & Experience Learning (C2)  
**Status:** Final Hostile Red-Team Audit & Scientific Adjudication  
**Transaction Type:** SCIENTIFIC AUDIT & IDENTIFIABILITY DETERMINATION ONLY  

**Prohibitions Honoured:**  
Read-only codebase inspection · Benchmark generators **NOT MODIFIED** · `nucleus.py` **NOT MODIFIED** · NN-0 **NOT TRAINED** · Decisive experiment **NOT RUN** · Seeds 200–209 **NOT CONSUMED** · No git staging or commits performed.

**Epistemological Labelling Index:**  
- **[THEOREM]** — Mathematical identity, information-theoretic bound, or formal proof.  
- **[CODE FACT]** — Direct, line-cited property of `p1/live/neural/nn0/nucleus.py` or active repository code.  
- **[MEASURED]** — Quantitative empirical result from prior verified audits (`outputs/P1_LIVE_NN_AFFINE_MSAT_HOSTILE_AUDIT.md`).  
- **[INFERENCE]** — Logical deduction derived from combining Theorems, Code Facts, or Measured data.  
- **[SPECULATION]** — Unverified hypothesis or design conjecture.  

---

## 1. EXECUTIVE VERDICT

### **VERDICT: C3 IS UNIDENTIFIABLE AS AN UNCONDITIONAL ARCHITECTURAL CLAIM; IDENTIFIABLE ONLY UNDER A CAPACITY-BOUNDED REGIME ($d_{\text{hidden}} \le d_{\text{critical}}$)**

Current testing protocols cannot scientifically establish **C3 (Persistent External Memory Utilization)** as an intrinsic property of the NN-0 architecture on synthetic register benchmarks.

#### Primary Reasons for Unidentifiability in Current Substrate **[INFERENCE]**:

1. **Massive Capacity Over-Provisioning [THEOREM + CODE FACT]:**  
   For default task dimensions ($N_K=8, V=16$ or $n=17$), the exact task state capacity is $C_{\text{task}} = 8 \times \log_2(17) \approx 32.77\text{ bits}$ **[THEOREM]**. NN-0's GRU hidden state $h$ contains $d_{\text{hidden}} = 128$ float32 units ([`nucleus.py:59`](file:///C:/Users/Purushottam/Documents/P1/p1/live/neural/nn0/nucleus.py#L59)), yielding up to $128 \times 32 = 4096\text{ bits}$ of unconstrained continuous recurrent capacity **[CODE FACT]**. Because $C_{\text{hidden}} \gg C_{\text{task}}$ ($125\times$ margin), the recurrent hidden state $h$ is a mathematically sufficient cause for storing all register states over arbitrary horizons. Disabling external memory ($M = \emptyset$) does not force task failure.

2. **Degenerate Key Projection under Zero-State Intervention [CODE FACT]:**  
   The proposed causal intervention $do(h=0)$ to isolate memory readout is physically broken in code. `project_key(h)` executes `key_head(h.detach())` ([`nucleus.py:212`](file:///C:/Users/Purushottam/Documents/P1/p1/live/neural/nn0/nucleus.py#L212)). When $h = 0$, `project_key(0) == key_head.bias == 0` ([`nucleus.py:208-210`](file:///C:/Users/Purushottam/Documents/P1/p1/live/neural/nn0/nucleus.py#L208-L210)). Setting $h=0$ renders memory reads key-blind and uniform across all queries, confusing structural memory failure with intervention-induced projection collapse.

3. **Conflation of Sequence Length with Memory Necessity [THEOREM]:**  
   Increasing token sequence length $T$ does **not** increase task state capacity $C_{\text{task}}$ for fixed register count $N_K$. The sufficient statistic remains 32.77 bits regardless of whether $T=50$ or $T=10,000$. A recurrent network with sufficient capacity ($d_{\text{hidden}}=128$) emulates a 32-bit Finite-State Machine (FSM) boundedly over infinite sequence lengths without requiring external KV storage.

4. **Optimizer State & Replay Leakage [CODE FACT]:**  
   NN-0 lacks a `reset_optimizer()` API ([`nucleus.py:571-585`](file:///C:/Users/Purushottam/Documents/P1/p1/live/neural/nn0/nucleus.py#L571-L574)). AdamW momentum vectors $O$ and un-cleared replay buffers $R$ leak historical information across evaluation boundaries, creating alternate causal paths from history $H$ to prediction $Y$.

#### Path to Scientific Validity **[INFERENCE]**:
To make C3 identifiable, P1 must abandon claiming external memory as an absolute architectural requirement for synthetic benchmarks, and re-frame C3 as a **capacity-bounded conditional claim**:  
$$\Delta \text{Acc}(do(M)) > 0 \iff d_{\text{hidden}} \le d_{\text{critical}} \approx \left\lceil \frac{C_{\text{task}}}{B_{\text{unit}}} \right\rceil$$
where $d_{\text{hidden}}$ is swept as an independent variable across $\{8, 16, 32, 64, 128\}$.

---

## 2. CAPACITY-CLIFF ADJUDICATION

We rigorously test the hypothesis: *"Is $C_{\text{task}} > C_{\text{hidden}}$ strictly necessary to prove external-memory necessity?"*

```
+---------------------------------------------------------------------------------------------------------+
|                                  8-DIMENSIONAL CAPACITY CLIFF EVALUATION                                |
+---+----------------------------+------------------------------------------------------------------------+
| # | Dimension                  | Scientific Finding & Impact on Identifiability                         |
+---+----------------------------+------------------------------------------------------------------------+
| 1 | Continuous Hidden States   | [THEOREM] h in R^d has infinite theoretical measure-theoretic capacity,|
|   |                            | but float32 precision and noise collapse effective discrete capacity.  |
| 2 | Numerical Stability        | [INFERENCE] GRU state drift over long horizons (T > 200) degrades      |
|   |                            | bit-packing, reducing usable bits below d_hidden * 32.                 |
| 3 | Recurrent Computation      | [THEOREM] Storing N_K keys in h requires non-linear update operations  |
|   |                            | that avoid cross-talk; effective capacity is bounded by packing packing|
| 4 | Temporal Compression       | [INFERENCE] Un-gated recurrent updates cause exponential decay unless  |
|   |                            | exact identity maps exist in GRU weight space.                         |
| 5 | Sufficient Statistics      | [THEOREM] Task state S_t in Aff(Z_17)^8 requires exactly 32.77 bits.    |
|   |                            | S_t is minimal sufficient statistic for predicting Y.                  |
| 6 | Task-Conditioned Encoding  | [INFERENCE] Supervised SGD fits a 32-bit FSM directly into h if        |
|   |                            | d_hidden >= 16 float32 dimensions.                                     |
| 7 | Randomized Interventions   | [INFERENCE] Swapping distant histories tests whether h retains state,  |
|   |                            | but does not force M usage if h capacity is unconstrained.             |
| 8 | Adversarial Histories      | [THEOREM] For fixed N_K, state space size |S| is constant over T.     |
|   |                            | Adversarial history depth does NOT expand state space size.            |
+---+----------------------------+------------------------------------------------------------------------+
```

### 2.1 Mathematical Deconstruction of the Capacity Cliff **[THEOREM]**

Let $\mathcal{S}$ be the task state space. For $N_K$ registers over $\mathbb{Z}_{n}$, $|\mathcal{S}| = n^{N_K}$.  
The minimal state entropy is:
$$H(S) = N_K \log_2(n) \quad \text{bits}$$
For $N_K=8, n=17$: $H(S) = 8 \log_2(17) \approx 32.77\text{ bits}$.

Let $h_t \in \mathbb{R}^{d_{\text{hidden}}}$ be the GRU hidden state vector.  
Under IEEE 754 float32, each dimension uses 32 bits (1 sign, 8 exponent, 23 mantissa).  
Theoretical maximum bit capacity:
$$C_{\text{theoretical}}(h) = 32 \times d_{\text{hidden}} \quad \text{bits}$$
For $d_{\text{hidden}}=128$: $C_{\text{theoretical}}(h) = 4096\text{ bits}$.

Due to GRU non-linearities ($\tanh, \sigma$), floating-point noise, and gradient update dynamics, the *robust discrete capacity* $C_{\text{robust}}(h)$ under SGD training is empirically bounded by $B_{\text{unit}} \approx 1\text{ to }2\text{ bits per dimension}$:
$$C_{\text{robust}}(h) \approx (1.0 \sim 2.0) \times d_{\text{hidden}} \quad \text{bits}$$
Even under conservative robust bounds ($B_{\text{unit}} = 1.0$), a GRU with $d_{\text{hidden}}=128$ provides $\approx 128\text{ bits}$ of robust discrete memory, which is **$3.9\times$ greater** than the required 32.77 bits **[INFERENCE]**.

### 2.2 Is $C_{\text{task}} > C_{\text{hidden}}$ Necessary? **[INFERENCE]**

- **For Absolute Memory Necessity ($M=\emptyset \implies \text{Accuracy} = \text{Chance}$):** **YES.**  
  If $C_{\text{hidden}} > C_{\text{task}}$, there exists a parameter set $\theta^*$ such that $h_t$ forms an exact isomorphic embedding of the task FSM $\mathcal{S}$. External memory $M$ is mathematically redundant.
- **For Inductive Memory Advantage ($\text{Sample Efficiency / Generalization}$):** **NO.**  
  External memory $M$ allows the network to store raw observations $e_t$ without compressing them into $h_t$, providing faster convergence and longer horizon retention even when $C_{\text{hidden}} > C_{\text{task}}$.

**Conclusion:** $C_{\text{task}} > C_{\text{hidden}}$ is **strictly necessary** to claim *architectural memory necessity*, but **unnecessary** to claim *inductive memory advantage*.

---

## 3. CAUSAL DAG & PATH ISOLATION

### 3.1 Complete System Causal Graph **[THEOREM + CODE FACT]**

To audit identifiability, we map the exact structural causal model governing query evaluation in NN-0:

```
                  [RNG Seed S]
                    /       \
                   v         v
               History H   Query Q
                / | \ \ \     |
               /  |  \ \ \    |
              /   |   \ \ \   |
             v    v    v v v  v
            h_T  M_T   R O C theta
             |    |    | | |   |
             |    |    | | |   |
             |    +----+-+-+---+-----+
             |         |   |         |
             v         v   v         v
            Path 1   Path 2 Path 3,4,5 Path 6
            (Recurr) (ExtM) (SGD/Opt)  (Params)
             \         |     /        /
              \        |    /        /
               v       v   v        v
              +-----------------------+
              |    Prediction Y       |
              +-----------------------+
```

### 3.2 Path Enumeration & Mechanisms **[THEOREM]**

1. **Path 1 (Recurrent Hidden State):** $H \to h_T \xrightarrow{Q} Y$  
   History $H$ accumulates in GRU state $h_T$. Readout maps $(h_T, Q) \to Y$.
2. **Path 2 (External Memory Retrieval):** $H \to M_T \xrightarrow{Q, project\_key(h)} Y$  
   History writes key-value pairs to $M_T$. Query retrieves via key matching.
3. **Path 3 (Direct Online Weight Adaptation):** $H \to \theta \xrightarrow{Q} Y$  
   Online SGD updates weights $\theta$ during stream processing ([`nucleus.py:760-805`](file:///C:/Users/Purushottam/Documents/P1/p1/live/neural/nn0/nucleus.py#L760-L805)).
4. **Path 4 (Replay Buffer Adaptation):** $H \to R \to \theta \xrightarrow{Q} Y$  
   Replay reservoir $R$ triggers offline gradient steps, mutating $\theta$ ([`nucleus.py:656-680`](file:///C:/Users/Purushottam/Documents/P1/p1/live/neural/nn0/nucleus.py#L656-L680)).
5. **Path 5 (Optimizer State Persistence):** $H \to O \to \Delta \theta \to Y$  
   AdamW momentum/variance vectors $O$ persist across evaluation steps, altering future weight updates ([`nucleus.py:534-566`](file:///C:/Users/Purushottam/Documents/P1/p1/live/neural/nn0/nucleus.py#L534-L566)).
6. **Path 6 (Cache State Persistence):** $H \to C \to Y$  
   Internal stack cache `_stack_cache` ([`nucleus.py:240`](file:///C:/Users/Purushottam/Documents/P1/p1/live/neural/nn0/nucleus.py#L240)) retains key/value tensors across calls until invalidated.

### 3.3 Isolation Intervention Derivation **[THEOREM + CODE FACT]**

To isolate **Path 2 ($M_T \to Y$)**, all confounding paths must be blocked simultaneously:

$$\text{Target Isolated Path:} \quad P(Y \mid do(M), Q)$$

Required Intervention Set $\mathcal{I}_{\text{memory}}$:
1. Block Path 1 ($h_T$): Set $h_T = \tilde{h}_{\text{null}}$, where $\tilde{h}_{\text{null}}$ is a non-zero parameter-aligned null query state (resolving `project_key(0) == 0` defect).
2. Block Path 3 & 4 ($\theta, R$): Set training mode to frozen evaluation (`model.eval()`, `torch.no_grad()`, `clear_replay()`).
3. Block Path 5 ($O$): Execute `reset_optimizer()` to zero AdamW momentum buffers.
4. Block Path 6 ($C$): Execute `clear_external_memory()` cache validation.

```
+-------------------------------------------------------------------------------------------------------+
|                                   CAUSAL PATH ISOLATION INTERVENTIONS                                 |
+--------+-----------------------+----------------------------------+-----------------------------------+
| Target | Isolated Path         | Active Intervention Set          | Unblocked / Leaky Paths           |
+--------+-----------------------+----------------------------------+-----------------------------------+
| C3     | Path 2 (External M)   | do(h=h_null, theta=theta_0,      | Path 1 if h_null leaks task state |
|        |                       |    R=empty, O=fresh, C=empty)   |                                   |
| C1/C4  | Path 1 (Recurrent h)  | do(M=empty, theta=theta_0,       | Path 5 if AdamW momentum persists |
|        |                       |    R=empty, O=fresh)              |                                   |
| C2     | Path 3 (Online SGD)   | do(M=empty, h=0, R=empty,        | Path 4 if replay steps run        |
|        |                       |    O=fresh, theta_matched)       | un-matched                        |
+--------+-----------------------+----------------------------------+-----------------------------------+
```

---

## 4. FORMAL C3 DEFINITION

### 4.1 Rigorous Mathematical Formulation **[THEOREM]**

We define **Persistent External-Memory Utilization (C3)** not as an absolute binary property of an unconstrained network, but as a **Causal Information Advantage over Bounded Recurrence**:

$$\text{C3 Statement:} \quad \Delta I(Y; M_T \mid Q, do(\mathcal{I}_{\text{freeze}})) = I(Y; M_T \mid Q, do(h = \tilde{h}_{\text{null}})) - I(Y; h_T \mid Q, do(M = \emptyset)) > 0$$

Under capacity constraint $d_{\text{hidden}} \le d_{\text{critical}}$:
$$C3 \iff \lim_{T \to \infty} \left[ \text{Acc}(M_{\text{full}}, d_{\text{hidden}}) - \text{Acc}(M_{0}, d_{\text{hidden}}) \right] \ge \delta_{\text{SESOI}}$$
where $\delta_{\text{SESOI}} = 0.15$ is the Smallest Effect Size of Interest.

### 4.2 Architectural Formulation Selection **[INFERENCE]**

We evaluate the 5 candidate formulations proposed in the challenge:

- **A. Memory is theoretically necessary:** **REJECTED.** False for finite task state spaces; an unconstrained RNN is a universal FSM approximator.
- **B. Memory is empirically necessary under a specified capacity budget:** **ACCEPTED (PRIMARY).** Scientifically defensible; forcing $d_{\text{hidden}} < \lceil C_{\text{task}} / B_{\text{unit}} \rceil$ creates an empirical capacity cliff.
- **C. Memory provides a measurable advantage under fixed architecture constraints:** **ACCEPTED (SECONDARY).** Measures sample efficiency and convergence speed benefits of $M$.
- **D. Memory is causally necessary for this implementation:** **REJECTED.** False for current $d_{\text{hidden}}=128$ baseline.
- **E. Memory is a useful inductive bias:** **ACCEPTED (DESCRIPTIVE).** Accurately describes external KV storage as a structural prior.

**Defensible Scientific Framing:**  
> *"P1 defines C3 as the empirical necessity of external key-value memory for state tracking under a strictly bounded recurrent capacity budget ($d_{\text{hidden}} \le 16$), demonstrated by counterfactual memory zeroing under matched parametric exposure."*

---

## 5. HIDDEN-STATE CHEATING ANALYSIS

### 5.1 Mechanisms of Recurrent "Cheating" **[INFERENCE]**

A GRU network can maintain task history without external memory via three distinct mechanisms:

1. **Orthogonal Subspace Packing:**  
   In a 128-dimensional continuous space, 8 independent 4-bit registers can be mapped to 8 orthogonal 16-dimensional linear subspaces. Linear operations $\text{Aff}(\mathbb{Z}_{17})$ act independently within each subspace without cross-talk.
2. **Fixed-Point Attractor Networks:**  
   SGD can condition the GRU weight matrices $W_{hh}, W_{ih}$ to form $17^8$ discrete fixed-point attractors, making the recurrent dynamics stable against floating-point drift over arbitrary sequence lengths.
3. **Order-Blind Multiset Accumulation:**  
   In defective commutative benchmarks (MSAT over $\mathbb{Z}_{16}$), the hidden state merely accumulates scalar sums, requiring only 4 bits of total state.

### 5.2 Does Increasing Sequence Length $T$ Defeat Hidden-State Storage? **[THEOREM]**

**NO.** This is a fundamental mathematical misconception.

Let the task generator be an FSM $\mathcal{M} = (\Sigma, \mathcal{S}, s_0, \delta, g)$.  
- Vocabulary size $|\Sigma| = 3 N_K V$.
- State space size $|\mathcal{S}| = n^{N_K} = 17^8 \approx 6.97 \times 10^9$.
- State transition: $S_{t+1} = \delta(S_t, x_t)$.

The cardinality of the sufficient statistic $S_t$ is **strictly constant** with respect to sequence length $T$:
$$\text{dim}(\text{Sufficient Statistic}) = \log_2 |\mathcal{S}| = 32.77\text{ bits} \quad \forall T \in \mathbb{N}$$

Whether $T = 50$ or $T = 10,000$, the network only needs to store $S_t$ at step $t$. It does **not** need to store the raw history sequence $x_{1:t}$. Therefore, extending $T$ to 10,000 tokens does **not** force the network to use external memory if $d_{\text{hidden}} = 128$ is already sufficient to store $S_t$ **[THEOREM]**.

### 5.3 Adversarial Probe Design for Hidden-State Cheating **[INFERENCE]**

To test whether $h$ alone encodes history without $M$:

```
Stream H1: WRITE(k1, f1) -> WRITE(k2, f2) -> ... -> [1000 filler ops] -> QUERY(k1)
Stream H2: WRITE(k1, f3) -> WRITE(k2, f2) -> ... -> [1000 filler ops] -> QUERY(k1)
```
- Both streams end in identical 50-token recent contexts $C_{\text{recent}}$ and identical query token $Q = \text{QUERY}(k1)$.
- Target $Y_1 \neq Y_2$.
- **Probe Rule:** Evaluate model with $do(M = \emptyset)$. If $\hat{Y}_1 = Y_1$ and $\hat{Y}_2 = Y_2$ with $>95\%$ accuracy, the recurrent hidden state $h_T$ has successfully encoded distant history $H_1 \neq H_2$ through 1000 filler ops without external memory.

---

## 6. CAPACITY-SCALING PROTOCOL

To scientifically establish C3, P1 must execute a controlled capacity-scaling study.

### 6.1 Experimental Protocol Design **[INFERENCE]**

```
Independent Variables:
  1. Recurrent Hidden Dimension:  d_hidden in {8, 16, 32, 64, 128}
  2. Memory Configuration:       M in {0 (Disabled), 1 (Single-Slot), Full (65536 Slots)}
  3. Modulus:                    n = 17 (AFFINE-MSAT repaired)
Fixed Controls:
  - Vocabulary Size: V = 128
  - Key Count: N_K = 8
  - Sequence Length: T = 200
  - Random Seeds: 10 seeds per cell (Seeds 300-309)
```

```
+----------------------------------------------------------------------------------------------------+
|                                CAPACITY-SCALING PROTOCOL SPECIFICATION                             |
+-----------------------+----------------------------------------------------------------------------+
| Dimension             | Exact Protocol Rule                                                        |
+-----------------------+----------------------------------------------------------------------------+
| Training Exposure     | Strictly 50,000 stream tokens per cell; 1 gradient step per token.         |
| Parameter Accounting  | Total trainable parameters P(d_hidden, M) reported for every cell.          |
| Optimization Budget   | AdamW (lr=1e-3, weight_decay=5e-4); fixed 5000 optimization steps.         |
| Inference Context     | Evaluated on 1,000 held-out probe sequences (T=50, 200, 500).              |
| Memory Intervention   | Evaluation run under both standard pass and counterfactual do(M=empty).    |
| Stopping Rule         | Fixed token budget reached (no early stopping on eval loss).              |
| Statistical Contrast  | Two-sided Wilcoxon signed-rank test across seeds (p < 0.01, SESOI = 0.15). |
+-----------------------+----------------------------------------------------------------------------+
```

### 6.2 Decision Matrix & Falsification Criteria **[INFERENCE]**

```
                     ACCURACY MATRIX ACROSS RECURRENT CAPACITY (d_hidden)

  Accuracy
  1.0 +-------------------------------------------------------------------------+
      |                                                      M=Full / M=1       |
  0.8 |                                                 +-----------------------+
      |                                                /
  0.6 |                                               /
      |                                              /   M=0 (No Memory)
  0.4 |                                             /
      |  Chance = 0.0588                           /
  0.0 +-------------------------------------------+-----------------------------+
      d_hidden = 8          d_hidden = 16         d_hidden = 32     d_hidden = 128
      (C_hidden < 32b)      (C_hidden ~ 32b)      (C_hidden > 32b)  (C_hidden >> 32b)
      <--- CAPACITY CLIFF REGIME --->             <--- RECURRENT OVERPOWERED --->
```

- **Pattern Establishing C3:**  
  At $d_{\text{hidden}} \in \{8, 16\}$, $M=0$ accuracy drops to chance ($\approx 5.88\%$), while $M=\text{Full}$ maintains $>90\%$ accuracy. This establishes a **Capacity Cliff** where external memory is causally necessary for task success.
- **Pattern Falsifying C3:**  
  If $M=0$ achieves $>90\%$ accuracy even at $d_{\text{hidden}} = 8$ or $16$, or if $M=\text{Full}$ fails to outperform $M=0$ at low $d_{\text{hidden}}$, the external memory mechanism hypothesis is **FALSIFIED** **[INFERENCE]**.

---

## 7. C2 EXPOSURE-CONTROL PROTOCOL

### 7.1 Audit of C2 in AFFINE-MSAT **[INFERENCE]**

**Claim C2:** *"In-session ordered experience causes neural learning."*

Current protocols compare an online SGD arm against a frozen batch arm without matching the **exposure triple**:
$$\text{Exposure Triple:} \quad \mathcal{E} = (N_g: \text{gradient steps}, \; N_r: \text{replay steps}, \; N_t: \text{tokens seen})$$

In [`nucleus.py:65-66`](file:///C:/Users/Purushottam/Documents/P1/p1/live/neural/nn0/nucleus.py#L65-L66), `replay_every = 1` and `replay_batch_size = 64`. An online arm processing a 200-token stream executes $200 \times 64 = 12,800$ replay gradient steps. A static batch arm sees only 200 tokens. The performance gap measures **optimization volume**, not experience-dependent learning **[CODE FACT + INFERENCE]**.

### 7.2 Strict 5-Arm Causal Exposure Contrast **[INFERENCE]**

To isolate C2, all arms must evaluate on identical parameter initializations $\theta_0$ over a target session $H$:

```
+--------------------------------------------------------------------------------------------------------+
|                                    5-ARM C2 EXPOSURE CONTROL MATRIX                                    |
+-----+-----------------------+--------------------------------+--------------------+--------------------+
| Arm | Name                  | Stream Order                   | SGD Steps (N_g)    | Tokens Seen (N_t)  |
+-----+-----------------------+--------------------------------+--------------------+--------------------+
| A1  | Online Sequential SGD | Exact temporal order H         | N_stream           | N_stream           |
| A2  | Frozen In-Context     | Sequential H (eval mode)       | 0                  | N_stream           |
| A3  | Shuffled Batch SGD    | Random permutation perm(H)     | N_stream (matched) | N_stream (matched) |
| A4  | Replay-Only Control   | Uniform draw from past buffers | N_stream (matched) | N_stream (matched) |
| A5  | No-Update Baseline    | None                           | 0                  | 0                  |
+-----+-----------------------+--------------------------------+--------------------+--------------------+
```

### 7.3 C2 Identifiability Condition **[THEOREM]**

$$\text{C2 Identifiable} \iff \text{Acc}(\text{Arm A1}) - \text{Acc}(\text{Arm A3}) \ge \delta_{\text{SESOI}} \quad \text{under } \mathcal{E}_{\text{A1}} \equiv \mathcal{E}_{\text{A3}}$$

If Arm A1 (sequential stream) does not outperform Arm A3 (shuffled stream with matched gradient steps and token exposures), the claim that *stream ordering causes learning* is **FALSIFIED** **[INFERENCE]**.

---

## 8. AFFINE-MSAT ADJUDICATION

### **VERDICT: B — AFFINE-MSAT IS SCIENTIFICALLY SUFFICIENT FOR C2/C4 AFTER MODULUS REPAIR ($16 \to 17$), BUT UNSUITABLE FOR UNCONSTRAINED C3**

```
+-----------------------------------------------------------------------------------------------------+
|                                    AFFINE-MSAT CLAIM SURVIVAL MATRIX                                |
+-------+-------------------------+------------------------------------+------------------------------+
| Claim | Status (n=16 as proposed)| Status (n=17 repaired)             | Primary Blocking Reason      |
+-------+-------------------------+------------------------------------+------------------------------+
| C1    | IDENTIFIABLE            | IDENTIFIABLE                       | None                         |
| C2    | NOT IDENTIFIABLE        | IDENTIFIABLE (under 5-Arm Control) | Exposure matching required   |
| C3    | NOT IDENTIFIABLE        | IDENTIFIABLE (under d_hidden <= 16)| Capacity over-provisioning   |
| C4    | NOT IDENTIFIABLE (2-adic)| IDENTIFIABLE                      | Fixed by modulus 17          |
| C5    | NOT IDENTIFIABLE        | IDENTIFIABLE (2 of 5 axes)         | Relabeled vocabulary axes    |
+-------+-------------------------+------------------------------------+------------------------------+
```

#### Narrowest Defensible Justification **[INFERENCE]**:
1. **Modulus 17 fully repairs C4:** Changing $n=16 \to 17$ removes the 2-adic homomorphism $Y \equiv \sum b_i \pmod 2$, collapsing the order-blind solver from $2.23\times$ chance down to exact chance ($1.01\times$) **[MEASURED]**.
2. **C3 requires capacity scaling:** Modulus 17 does not change task state size ($32.77\text{ bits}$). AFFINE-MSAT($\mathbb{Z}_{17}$) can only establish C3 if coupled with the Capacity-Scaling Protocol ($d_{\text{hidden}} \le 16$).

---

## 9. NN-0 REQUIRED CHANGES

We evaluate candidate modifications to `nucleus.py` and rank them strictly by scientific identifiability necessity.

```
+-------------------------------------------------------------------------------------------------------+
|                                    NN-0 ARCHITECTURAL REPAIR RANKING                                  |
+--------------------------------+-----------+----------------------------------------------------------+
| Modification Candidate         | Rank      | Scientific Rationale                                    |
+--------------------------------+-----------+----------------------------------------------------------+
| Configurable hidden dimension  | REQUIRED  | Essential for Capacity-Scaling Protocol (d_hidden <= 16) |
| Optimizer reset API            | REQUIRED  | Prevents AdamW momentum leakage across sessions (Path 5) |
| Decoupled key projection / null| REQUIRED  | Fixes project_key(0) == 0 degenerate read bug            |
| Parameter freeze API           | REQUIRED  | Enables strict torch.no_grad() eval arms                 |
| Recurrent state reset API      | REQUIRED  | Already present (reset_state()), must be retained        |
| Replay clear API               | REQUIRED  | Already present (clear_replay()), must be retained       |
| BPTT >= sequence length        | OPTIONAL  | Improves gradient flow over T=200; not a causal gate     |
| Explicit key-token addressing  | OPTIONAL  | Architecture refinement; cosine top-k works              |
| KV overwrite mechanism         | OPTIONAL  | Prevents memory bloat; top-k read handles append-only    |
| Memory temperature scaling     | OPTIONAL  | Hyperparameter tuning                                    |
| Causal state snapshots         | OPTIONAL  | Diagnostic logging convenience                           |
+--------------------------------+-----------+----------------------------------------------------------+
```

---

## 10. FALSIFICATION CRITERIA

The scientific integrity of P1 relies on clear, pre-registered falsification criteria.

```
+------------------------------------------------------------------------------------------------------+
|                                    EXPLICIT FALSIFICATION CRITERIA                                   |
+---+----------------------------+---------------------------------------------------------------------+
| # | Targeted Hypothesis        | Exact Falsification Condition                                       |
+---+----------------------------+---------------------------------------------------------------------+
| 1 | C3 External Memory         | M=0 (disabled) achieves >= 90% accuracy on AFFINE-MSAT(Z_17) at     |
|   | Necessity Hypothesis       | d_hidden <= 16 float32 dimensions.                                  |
| 2 | C3 Memory Retrieval        | Counterfactual do(M=empty) intervention causes < 0.15 accuracy drop  |
|   | Functional Impact          | across all d_hidden configurations.                                 |
| 3 | C2 Experience Learning     | Arm A1 (Online Sequential SGD) shows no statistically significant    |
|   | Hypothesis                 | gain over Arm A3 (Shuffled Batch SGD) under matched exposures.      |
| 4 | C4 Sequential Order        | An order-blind multiset solver achieves > 1/17 (5.88%) accuracy on  |
|   | Dependence Hypothesis      | held-out AFFINE-MSAT(Z_17) test streams.                            |
+---+----------------------------+---------------------------------------------------------------------+
```

---

## 11. SINGLE NEXT TRANSACTION

**DO NOT DESIGN ANOTHER BENCHMARK.**  
**DO NOT WRITE NUCLEUS CODE.**  

### **RECOMMENDED SINGLE NEXT TRANSACTION:**

> **Issue the formal specification for "NN-0 Nucleus Identifiability Patch & AFFINE-MSAT($\mathbb{Z}_{17}$) Capacity-Scaling Protocol".**

#### Scope of Transaction **[INFERENCE]**:
1. Specify the exact interface additions for `nucleus.py`:
   - `reset_optimizer()` method.
   - `d_hidden` parameter exposure in `NN0Config`.
   - `project_key_null()` non-zero bias decoupling.
2. Specify the experimental matrix for the Capacity-Scaling study ($d_{\text{hidden}} \in \{8, 16, 32, 64, 128\} \times M \in \{0, 1, \text{Full}\}$ over $\mathbb{Z}_{17}$).
3. This transaction maximizes scientific information gained, fixes all identifiability blockers, and requires minimal code churn.
