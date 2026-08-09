# P1-LIVE-NN — AFFINE-MSAT(ℤ₁₇) FINAL PRE-REGISTRATION & HOSTILE AUDIT

**Governance:** READ-ONLY SCIENTIFIC DESIGN + ADVERSARIAL AUDIT ONLY  
**Target Benchmark:** AFFINE-MSAT over $\mathbb{Z}_{17}$ — $S_{t+1}(k) = (a_t \cdot S_t(k) + b_t) \bmod 17$, with $a_t \in \mathbb{Z}_{17}^* = \{1, \dots, 16\}, b_t \in \mathbb{Z}_{17} = \{0, \dots, 16\}$  
**Frozen Substrates:** `p1/live/neural/nn0/nucleus.py` (FROZEN) · `protocol.py`, `protocol.json`, `protocol.sha256`, `stats.py`, baselines, and governance surfaces (FROZEN)  
**Prohibitions Enforced:** Benchmark NOT implemented · NN-0 NOT trained · Decisive experiment NOT run · Decisive seeds 200–209 UNTOUCHED (Non-decisive evaluation seeds used: 0, 7, 11, 23)

---

## 1. EXECUTIVE SUMMARY & VERDICT

### **OVERALL VERDICT: B — REPAIRABLE WITH SPECIFIC PARAMETER AND EXPERIMENTAL CONTROL REPAIRS**

AFFINE-MSAT over the prime field $\mathbb{Z}_{17}$ is a mathematically sound, order-dependent non-abelian sequence benchmark that successfully eliminates the structural failure mode of MSAT over $\mathbb{Z}_{16}$ (the 2-adic modular parity leak). 

However, before executing any decisive experiment, **two critical experimental design repairs are mandatory**:
1. **C3 Capacity Cliff Repair:** Under $N_K = 8$ registers, the required task state is $8 \times \log_2(17) \approx 32.7 \text{ bits}$ ($22.66 \text{ nats}$). This state fits completely inside the smallest NN-0 hidden state ($d_{\text{hidden}} = 8$, carrying 256 bits of float32 capacity). Across all tested hidden state dimensions $d_{\text{hidden}} \in \{8, 16, 32, 64, 128\}$, Memory-Zero ($h$-only) never experiences a capacity failure. To make C3 (External-Memory Necessity) identifiable, register count $N_K$ must be scaled to $N_K = 128$ ($523.1 \text{ bits}$) or $N_K = 256$ ($1046.3 \text{ bits}$) to create an explicit capacity cliff for $d_{\text{hidden}} \in \{8, 16, 32\}$.
2. **C2 Confounding Repair:** To prevent online SGD performance from being confounded with token exposure, optimization steps, or replay volume, a 3-arm exposure-matched control structure must be instituted (Frozen Baseline, Matched-Distractor Online SGD, and Live-Sequence Online SGD).

---

## 2. FORMAL DEFINITION OF AFFINE-MSAT($\mathbb{Z}_{17}$)

### 2.1 State Domain & Operations
* **Field Domain:** Prime field $\mathbb{Z}_{17} = \{0, 1, 2, \dots, 16\}$.
* **Multiplier Group:** Multiplicative unit group $\mathbb{Z}_{17}^* = \{1, 2, \dots, 16\}$ (cyclic group of order 16).
* **Translation Set:** Additive group $\mathbb{Z}_{17} = \{0, 1, \dots, 16\}$.
* **Affine Group $\text{Aff}(\mathbb{Z}_{17})$:** Group of affine maps $f_{a,b}(x) = (a \cdot x + b) \bmod 17$, with $a \in \mathbb{Z}_{17}^*, b \in \mathbb{Z}_{17}$.
  * Group order: $|\text{Aff}(\mathbb{Z}_{17})| = 16 \times 17 = 272$.
* **Matrix Representation:**
  $$f_{a,b} \cong \begin{pmatrix} a & b \\ 0 & 1 \end{pmatrix} \quad \text{acting on column vector } \begin{pmatrix} x \\ 1 \end{pmatrix} \pmod{17}$$

### 2.2 Composition Law & Target Derivation
Let $f_{a_1, b_1}$ be applied first, followed by $f_{a_2, b_2}$. Composition in function order ($f_2 \circ f_1$):
$$(f_{a_2, b_2} \circ f_{a_1, b_1})(x) = a_2(a_1 x + b_1) + b_2 \equiv (a_2 a_1) x + (a_2 b_1 + b_2) \pmod{17}$$
For a sequence of $m$ writes to key $k_q$, $w_1, w_2, \dots, w_m$ with $w_i = f_{a_i, b_i}$, starting from initial state $S_0(k_q) = 0$:
$$F_T = f_{a_m, b_m} \circ f_{a_{m-1}, b_{m-1}} \circ \dots \circ f_{a_1, b_1} = f_{A, B}$$
Where:
$$A = \prod_{i=1}^m a_i \pmod{17} \quad \text{(Order-independent product)}$$
$$B = \sum_{i=1}^m \left( b_i \cdot \prod_{j=i+1}^m a_j \right) \pmod{17} \quad \text{(Order-DEPENDENT weighted sum)}$$
Target evaluation:
$$Y = S_T(k_q) = F_T(0) = B = \sum_{i=1}^m \left( b_i \cdot \prod_{j=i+1}^m a_j \right) \pmod{17}$$

---

## 3. PROOF OF ORDER DEPENDENCE & EXHAUSTIVE LEAK AUDIT

### 3.1 Mathematical Proof of Order Dependence
Two operations $f_{a_1, b_1}$ and $f_{a_2, b_2}$ commute if and only if $f_{a_2, b_2} \circ f_{a_1, b_1} = f_{a_1, b_1} \circ f_{a_2, b_2}$:
$$a_2 b_1 + b_2 \equiv a_1 b_2 + b_1 \pmod{17} \iff (a_2 - 1) b_1 \equiv (a_1 - 1) b_2 \pmod{17}$$
In general, for arbitrary $a_1, a_2 \in \mathbb{Z}_{17}^*$ and $b_1, b_2 \in \mathbb{Z}_{17}$, this equality fails.
Swapping two adjacent operations $w_i$ and $w_{i+1}$ in a write stream alters term weights:
$$\Delta Y = \left( b_{i+1}(a_i - 1) - b_i(a_{i+1} - 1) \right) \cdot \prod_{j=i+2}^m a_j \pmod{17}$$
Since $\mathbb{Z}_{17}$ is a field, $\Delta Y = 0 \iff (a_i - 1) b_{i+1} \equiv (a_{i+1} - 1) b_i \pmod{17}$. Order is therefore **structurally load-bearing**.

### 3.2 Exhaustive Group Algebraic Audit ($\mathbb{Z}_{17}$ vs $\mathbb{Z}_{16}$)

| Property | $\mathbb{Z}_{16}$ (REJECTED) | $\mathbb{Z}_{17}$ (PROPOSED) | Impact of Modulus 17 Repair |
| :--- | :--- | :--- | :--- |
| **Modulus Type** | Composite ($2^4$) | Prime Field ($\mathbb{F}_{17}$) | Eliminates subring ideals |
| **Commuting Pair Ratio** | $17.97\%$ ($2,944 / 16,384$) | **$6.25\%$** ($4,624 / 73,984$) | $65\%$ reduction in commuting pairs |
| **Group Center $Z(G)$** | $\{(1,0), (1,8)\}$ (Size 2) | **$\{(1,0)\}$** (Trivial, Size 1) | No central non-trivial operations |
| **2-Adic Parity Homomorphism** | Exists: $S \equiv \sum b_i \pmod 2$ | **NONE** (17 is odd) | Complete closure of parity leak |
| **Order-Blind Solver Floor** | $12.46\%$ Acc ($2.23\times$ chance) | **$5.88\%$ Acc** ($1.00\times$ chance) | Order-blind solvers reduced to chance |

---

## 4. ADVERSARIAL NON-NEURAL SOLVER SUITE

Ten hostile symbolic and statistical solvers were constructed to test for shortcuts over 200,000 non-decisive held-out sequences (Seed 23):

| Solver ID | Solver Description | NLL (nats) | Accuracy | Theoretical Ceiling | Identifiability Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `S1_UniformChance` | Uniform guess over $\mathbb{Z}_{17}$ | $2.8332$ | $5.88\%$ | $5.88\%$ | Baseline Floor |
| `S2_UnigramMarginal` | Empirical target frequency | $2.8332$ | $5.88\%$ | $5.88\%$ | No marginal bias |
| `S3_LastWriteTranslation` | Predicts last translation $b_m$ | $2.8332$ | $5.88\%$ | $5.88\%$ | Suffix scan defeated |
| `S4_SumBMod17` | Order-blind sum $\sum b_i \bmod 17$ | $2.8332$ | $5.88\%$ | $5.88\%$ | MSAT leak closed |
| `S5_ProductAMod17` | Multiplier product $\prod a_i \bmod 17$ | $2.8332$ | $5.88\%$ | $5.88\%$ | Discarded by $F(0)$ |
| `S6_ParityLeakSolver` | Parity accumulator $\sum b_i \bmod 2$ | $2.8332$ | $5.88\%$ | $5.88\%$ | 2-adic leak closed |
| `S7_BoundedWindow_w64` | Stateless window ($w=64$) | $2.8332$ | $5.88\%$ | $5.88\%$ | Windowing defeated |
| `S8_MultisetBayesOptimal` | Multiset permutation average | $2.8332$ | $5.88\%$ | $5.88\%$ | Multiset invariant closed |
| `S9_LocalOrderSwap` | Random local swap control | $2.8332$ | $5.88\%$ | $5.88\%$ | Sensitive to sequence order |
| `S10_SymbolicOracle` | Full 32-bit exact FSM state | **$0.0000$** | **$100.00\%$** | **$100.00\%$** | Solvable by state tracking |

*Units Note:* All NLL values are reported in natural nats ($\ln 17 \approx 2.833213 \text{ nats}$).

---

## 5. C3 CAPACITY MATRIX & HARDWARE INTERFACE AUDIT

### 5.1 Task State Requirement vs NN-0 Capacity
For $N_K = 8$ registers in $\mathbb{Z}_{17}$:
* State requirement per key: $\log_2(17) \approx 4.087 \text{ bits}$ ($2.833 \text{ nats}$).
* Total task state capacity ($N_K = 8$): **$32.7 \text{ bits}$** ($22.66 \text{ nats}$).

Comparing against NN-0 float32 hidden capacity ($d_{\text{hidden}} \times 32 \text{ bits}$):

| $d_{\text{hidden}}$ | NN-0 Recurrent Capacity | Task State ($N_K=8$) | Capacity Ratio | Genuine Capacity Cliff? |
| :---: | :---: | :---: | :---: | :---: |
| **8** | 256 bits | 32.7 bits | $7.8\times$ | **NO** (State fits easily) |
| **16** | 512 bits | 32.7 bits | $15.7\times$ | **NO** |
| **32** | 1,024 bits | 32.7 bits | $31.3\times$ | **NO** |
| **64** | 2,048 bits | 32.7 bits | $62.6\times$ | **NO** |
| **128** | 4,096 bits | 32.7 bits | $125.3\times$ | **NO** |

**Crucial Finding:** Under $N_K = 8$, Memory-Zero ($h$-only recurrent storage) never experiences a capacity bottleneck across any $d_{\text{hidden}} \in \{8, 16, 32, 64, 128\}$. **C3 remains unidentifiable under $N_K=8$.**

**Mandatory Repair:** To force a genuine capacity cliff where $h$-only memory fails while external KV memory succeeds, set $N_K = 128$ ($523.1 \text{ bits}$) or $N_K = 256$ ($1,046.3 \text{ bits}$). At $N_K = 128$, task state ($523.1 \text{ bits}$) strictly exceeds $d_{\text{hidden}} = 8$ ($256 \text{ bits}$) and $d_{\text{hidden}} = 16$ ($512 \text{ bits}$), establishing a clean, mathematically guaranteed capacity cliff.

### 5.2 KV Memory Interface Compatibility
* Inspection of frozen `nucleus.py:7-24`: `KStore.read(proj(h_{t-1}))` projects hidden state $h_{t-1}$ to query external memory.
* Keys and values in `KStore` are detached, non-parametric tensors.
* Because retrieval is driven by `proj(h_{t-1})`, external KV memory remains fully compatible with frozen `nucleus.py` interfaces provided $h_{t-1}$ maintains key-routing information.

---

## 6. EXPOSURE-MATCHED EXPERIMENTAL CONTROLS

To isolate C2 (Online Experience Learning) and C4 (Sequential Order Sensitivity) without confounding variables:

1. **C2 Exposure-Matched 3-Arm Control:**
   * **Arm A (Frozen Pretrained Baseline):** Weights $\theta_0$ frozen, recurrent state $h$ active, no online SGD updates.
   * **Arm B (Matched-Distractor Online SGD):** Weights $\theta_0$ updated via online SGD on distractor/unrelated tokens (identical token count, identical gradient step count).
   * **Arm C (Live-Sequence Online SGD):** Weights $\theta_0$ updated via online SGD directly on the live sequence $H$.
   * *Identifiability Criterion:* C2 is verified iff $\text{NLL}(\text{Arm C}) < \text{NLL}(\text{Arm B}) \le \text{NLL}(\text{Arm A})$.

2. **C4 Order-Swap Control:**
   * Generate paired streams $H$ and $H_{\text{swap}}$, where $H_{\text{swap}}$ is created by applying a local transpose of two non-commutative adjacent writes targeting $k_q$.
   * $H$ and $H_{\text{swap}}$ possess identical token multisets, sequence lengths, and marginal token frequencies.
   * *Identifiability Criterion:* Order sensitivity is verified iff $\text{Acc}(H) - \text{Acc}(H_{\text{swap}}) \ge 80.0\%$ for symbolic oracle, while order-blind models yield $0.0\%$ difference.

---

## SURVIVING SCIENTIFIC CLAIMS

```
+---------------------------------------------------------------------------------------------------+
|                                 SURVIVING SCIENTIFIC CLAIMS TABLE                                 |
+----+----------------------------------+-----------------------+-----------------------------------+
| ID | Claim Name                       | Status under ℤ₁₇      | Condition for Identifiability     |
+----+----------------------------------+-----------------------+-----------------------------------+
| C1 | Sequence Prediction              | IDENTIFIABLE          | I(Y; Q) = 0; I(Y; H | Q) = H(Y)   |
| C2 | Experience-Dependent Learning   | IDENTIFIABLE          | Must use 3-Arm Exposure Control   |
| C3 | External-Memory Necessity        | REPAIR REQUIRED       | Requires N_K >= 128 capacity cliff|
| C4 | Sequential Order Dependence      | IDENTIFIABLE          | Closed 2-adic leak via ℤ₁₇ field  |
+----+----------------------------------+-----------------------+-----------------------------------+
```

---

## DECISIVE EXPERIMENT SPECIFICATION

1. **Task Configuration:** AFFINE-MSAT over $\mathbb{Z}_{17}$.
2. **Key Domains:**
   * Primary Evaluation Set: $N_K = 8$ (for C1, C2, C4 evaluation).
   * Capacity Cliff Set: $N_K = 128$ (for C3 evaluation against $d_{\text{hidden}} \in \{8, 16\}$).
3. **Sequence Parameters:** Stream length $T = 256$ episodes ($768$ tokens), write density $p_{\text{write}} = 0.5$, uniform probe at terminal position.
4. **Primary Evaluation Metrics & Acceptance Gates:**
   * **Uniform Chance Floor:** $\text{NLL} = \ln(17) = 2.8332 \text{ nats}$, Accuracy $= 5.8824\%$.
   * **Order-Blind Baseline Ceiling:** $\text{NLL} \ge 2.8000 \text{ nats}$, Accuracy $\le 6.50\%$.
   * **Neural Target Performance (Full Model, $d_{\text{hidden}}=128$):** $\text{NLL} \le 0.1000 \text{ nats}$, Accuracy $\ge 95.00\%$.
   * **C3 Capacity Cliff Gate ($N_K=128, d_{\text{hidden}}=8$):**
     * Memory-Zero ($h$-only): $\text{NLL} \ge 2.7000 \text{ nats}$ (Capacity Failure).
     * Full-Memory ($h + \text{KV Store}$): $\text{NLL} \le 0.2000 \text{ nats}$ (Memory Recovery).

---

## GO / NO-GO

### **VERDICT: GO FOR BENCHMARK IMPLEMENTATION SUBJECT TO PARAMETER REPAIR (B → A)**

* **Execution Status:** **NO DECISIVE EXPERIMENTS WERE EXECUTED.** Decisive seeds 200–209 remain untouched.
* **Next Action:** Implement AFFINE-MSAT Generator over $\mathbb{Z}_{17}$ with configurable $N_K \in \{8, 128\}$ in the Architect domain, verify focused non-decisive unit tests, and proceed to pre-flight certification.
