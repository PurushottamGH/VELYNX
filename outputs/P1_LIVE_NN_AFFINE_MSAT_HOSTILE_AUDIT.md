# P1-LIVE-NN — AFFINE-MSAT Hostile Mathematical & Information-Theoretic Audit

**Role:** Independent hostile scientific reviewer (adversarial design gate)
**Target:** AFFINE-MSAT — `S_{t+1} = (a_t · S_t + b_t) mod 16`, `a_t` odd — proposed as successor to the rejected MSAT
**Predecessor findings:** `outputs/P1_LIVE_NN_MSAT_HOSTILE_AUDIT.md` (verdict C), `outputs/P1_LIVE_NN_NEXT_BENCHMARK_DESIGN.md`
**Transaction type:** DESIGN VALIDATION ONLY

**Prohibitions honoured:**
AFFINE-MSAT **NOT IMPLEMENTED** as a benchmark · benchmark generators **NOT MODIFIED** · `nucleus.py` **NOT MODIFIED** · NN-0 **NOT TRAINED** · decisive experiment **NOT RUN** · seeds 200–209 **NOT CONSUMED** (seeds used: 0, 7, 11, 23) · nothing sealed, nothing committed.

---

## 0. EVIDENCE POSTURE — READ BEFORE ANY FINDING

**This audit's evidence posture differs from the MSAT audit's, deliberately, and the difference must be stated plainly.**

The MSAT audit measured nothing and said so. This audit **executed group-theoretic enumerations** over `Aff(ℤ_n)` in throwaway interpreter sessions. No file was created, no generator was written, no network was trained, no reserved seed was touched. The distinction that makes this permissible:

> Enumerating the multiplication table of a 128-element group is **not an experiment on the benchmark**. It is the evaluation of a closed-form algebraic property. It has no seeds in the scientific sense, no sample-size dependence, and no possible outcome other than the one the group axioms already determine.

Findings are labelled:

- **THEOREM** — algebraic identity, proved by argument. Enumeration is confirmatory only.
- **ENUMERATED** — exhaustive computation over a finite structure. Not a sample; the whole space.
- **MONTE CARLO** — sampled estimate with a stated N and seed. Carries sampling error. **Used only for solver accuracies, never for a structural claim.**
- **CODE** — line-cited property of `p1/live/neural/nn0/nucleus.py`.
- **SPEC** — internal inconsistency in a design document.

Every quantitative claim below carries its N and its seed. This is the standard the MSAT design's §7 solver matrix failed (finding M-07/R-8 of the prior audit), and it would be indefensible to charge that defect and then repeat it.

**One methodological correction applied mid-audit, recorded for the record:** the first solver run reported `last2 = 0.28`, `prefix_half = 0.67`, `suffix_half = 0.82` on ℤ₁₆. Those numbers are **memorization artifacts** — the feature tables held ~63k–80k cells against 100k samples, so nearly every cell contained one example and the "solver" was reciting its own training set. All solver numbers in §5 are re-derived on a **disjoint 200k held-out split**. The inflated numbers are reported here only to document the correction; they appear nowhere in the findings.

---

## 1. EXECUTIVE VERDICT

### **B — REPAIRABLE**

AFFINE-MSAT is the right structural answer to the defect that killed MSAT, and it genuinely works: **the affine group over ℤ_n is non-abelian, order becomes load-bearing, and the order-blind accumulator that solved MSAT at 100% collapses.** That is a real repair and it should be credited without hedging. C4 — the claim the prior audit ruled INVALID — becomes identifiable for the first time in this program's history.

But the specific modulus proposed, **16**, reintroduces the exact defect it was designed to remove, in one bit.

### The finding that decides this audit

**Over ℤ_{2^k}, every unit `a` is odd, hence `a ≡ 1 (mod 2)`. Therefore:**

```
S_{t+1} ≡ a_t·S_t + b_t  ≡  S_t + b_t   (mod 2)
⟹  Y ≡ Σ_i b_i  (mod 2)                              [THEOREM]
```

The map `(a,b) ↦ b mod 2` is a **group homomorphism from Aff(ℤ_{2^k}) onto the abelian group (ℤ₂,+)**. The low bit of the target is therefore a *commutative, permutation-invariant sum of the translation coefficients* — MSAT's defect, surviving intact in one bit of the answer.

**ENUMERATED:** 60,001 compositions each at n = 8, 16, 32 — **zero violations**.

**Consequences, all measured on a disjoint held-out split (N=200k train / 200k eval, seed 23):**

| Order-blind statistic | ℤ₁₆ held-out acc | ratio to chance | ℤ₁₇ held-out acc | ratio |
|---|---|---|---|---|
| `Σb mod n` | **0.1394** | **2.23×** | 0.0595 | 1.01× |
| `Σb mod 2` (parity alone) | **0.1246** | **1.99×** | 0.0593 | 1.01× |
| multiset of all `(a,b)` | 0.0665 | 1.06× | 0.0586 | 1.00× |

The parity solver lands on **0.1246 ≈ 2/16 = 0.125**, precisely the floor the theorem predicts. A one-line permutation-invariant statistic beats chance by a factor of two on the proposed modulus, and the Bayes-optimal order-blind solver reaches **0.1621 at m=8** (MONTE CARLO, N=300 multisets × ≤400 permutations, seed 11) — it does **not** converge to chance as depth grows, because the leaked bit is depth-independent.

### The repair is one character

**Use an odd modulus.** `n = 17`. Every leak closes simultaneously: the 2-adic homomorphism does not exist for odd `n`, the centre of `Aff(ℤ₁₇)` is trivial `{(1,0)}` (versus `{(1,0),(1,8)}` for ℤ₁₆ — ENUMERATED), the commuting-pair fraction drops from **17.97%** to **6.25%** (ENUMERATED over all 16,384 and 73,984 ordered pairs respectively), and **all ten held-out local solvers sit at chance, ratio 0.98×–1.01×.**

### The second finding — the affine repair does nothing for C3

The sufficient statistic for AFFINE-MSAT is the running register `S(k)` itself: **4 bits per key, 32 bits total** — *identical to MSAT*. The affine repair changes the *function* computed, not the *state required to compute it*. So the 128× capacity margin against NN-0's 4096-bit GRU hidden state (`d_hidden=128`, `nucleus.py:59`) is **completely unchanged**. Every word of the prior audit's M-02 stands. **C4 is repaired; C3 is not touched.**

### The third finding — algorithmic solvability is not learning necessity

The mandate's §12 rule is the correct frame, and AFFINE-MSAT falls on the wrong side of it as currently motivated. The task is exactly executed by:

```
for (k, a, b) in writes:  S[k] = (a*S[k] + b) % n        # 32-bit FSM, 2 lines
```

This is a **fixed-size, fixed-program finite-state machine**. A benchmark solved by executing a two-line known algorithm tests *whether the architecture can execute a known recurrence*, not *whether it learns from experience*. That is a legitimate and worthwhile claim — but it is **C-exec**, not C2, and the design must say so.

### Claim survival

| Claim | Status (ℤ₁₆ as proposed) | Status (after R-1: odd modulus) | Blocking |
|---|---|---|---|
| **C1** History necessity | IDENTIFIABLE | IDENTIFIABLE | — |
| **C2** Online experience learning | **NOT IDENTIFIABLE** | **NOT IDENTIFIABLE** | exposure unmatched; algorithmic-vs-learning conflation |
| **C3** Persistent external memory | **NOT IDENTIFIABLE** | **NOT IDENTIFIABLE** | 128× capacity margin unchanged; `project_key(0)==0` |
| **C4** Sequential order dependence | **NOT IDENTIFIABLE** (2-adic leak) | **IDENTIFIABLE** | closes on R-1 alone |
| **C5** OOD generalization | **NOT IDENTIFIABLE** | IDENTIFIABLE on 2 of 5 axes | 3 axes are relabelings |

### Why B and not C

The prior audit ruled C because MSAT's **transition function** was wrong and no parameter change could fix an abelian group. Here the transition function is **correct**. The defect is a *parameter* — the modulus — and the fix is `16 → 17`. Everything downstream (vocabulary, episode format, stream length, GTX-1070 feasibility) is unchanged. That is the definition of REPAIRABLE.

### Why not A

Three blocking items remain: the modulus (R-1), the unchanged C3 capacity margin (R-2, inherited unrepaired from the prior audit), and the algorithmic-solvability/learning-necessity conflation (R-3). **A design cannot be certified ready while its own headline claim C3 is unidentifiable for a reason its author has now been told twice.**

---

## 2. FORMAL AFFINE SYSTEM

### 2.1 Definitions

```
n              modulus                    (proposed 16; this audit recommends odd)
Zn = {0..n-1}  state domain
Un = (Z/nZ)*   unit group,  a ∈ Un ⟺ gcd(a,n)=1
K  = {k_1..k_NK}                          key / register domain
```

**State.** One register per key, `S_t(k) ∈ Zn`, with `S_0(k) = 0` for all `k`. (INIT is deleted — §2.5.)

**Operation alphabet.** The affine group of the line over `Zn`:

```
Aff(Zn) = { f_{a,b} : x ↦ (a·x + b) mod n | a ∈ Un, b ∈ Zn }
|Aff(Zn)| = |Un| · n
|Aff(Z16)| = 8 · 16 = 128        |Aff(Z17)| = 16 · 17 = 272
```

**Matrix representation** (used throughout §4):

```
f_{a,b}  ≅  [ a  b ]        acting on column (x, 1)ᵀ
            [ 0  1 ]
```

**Composition law.** Writing `f∘g` for "apply `g` first, then `f`":

```
f_{a1,b1} ∘ f_{a2,b2} = f_{ a1·a2 ,  a1·b2 + b1 }          [THEOREM]
```

**Observation stream.** `T` episodes of 3 tokens, one opcode class only:

```
WRITE(k, c)  ->  [WRITE_TOK, k, OP_c]        c indexes a pre-registered (a,b) table
QUERY(k_q)   ->  [QUERY_TOK, k_q]            terminal episode
```

**Query.** `Q = (QUERY_TOK, k_q)`, `k_q ~ U(K)`.

**Target.** `Y = S_T(k_q)`.

### 2.2 The composite map and the exact target

Let `w_1, …, w_m` be the writes to `k_q` **in stream order**, `w_i = f_{a_i, b_i}`. The composite is

```
F_T = f_m ∘ f_{m-1} ∘ ⋯ ∘ f_1 = f_{A, B}
```

with, by induction on the composition law,

```
A = Π_{i=1}^{m} a_i                                        (order-independent)
B = Σ_{i=1}^{m} ( b_i · Π_{j=i+1}^{m} a_j )                (order-DEPENDENT)
```

Since `S_0(k_q) = 0`:

```
Y = F_T(0) = B = Σ_{i=1}^{m} b_i · Π_{j>i} a_j             [THEOREM]
```

**This single identity is the whole audit.** Read it carefully:

- `Y` depends on `b_i` **weighted by the product of every multiplier that comes after it**. Position enters through the weight. This is exactly why order is load-bearing — and exactly what MSAT lacked, where every weight was 1.
- `Y` does **not** depend on `A = Πa_i` at all. The `a`-product is a genuine channel of the composite map that the target discards. (Confirmed: `max P(Y | Πa) = 0.0667` vs chance 0.0625 on ℤ₁₆; `0.0662` vs `0.0588` on ℤ₁₇ — MONTE CARLO, N=200k, seed 7.)
- Writes to keys other than `k_q` do not enter. `I(Y; Q) = 0` holds by the same uniformity argument as MSAT, preserved because every `a_i` is a unit, so each `f_{a,b}` is a **bijection** on `Zn` and uniformity of the composite is exact.

### 2.3 Quantities the target depends on — exhaustive list

| Quantity | Enters `Y`? | Note |
|---|---|---|
| multiset of `(a_i,b_i)` for `k_q` | insufficient alone | the defect MSAT had; here insufficient — *except in the low bit when `n` is even* (§3.3) |
| **ordered sequence** of `(a_i,b_i)` for `k_q` | **YES — fully determines** | |
| `Πa_i` | NO | discarded by `F_T(0)` |
| `Σb_i` | NO for odd `n`; **partially YES for even `n`** | §3.3 |
| `m` (write count) | only through the above | `max P(Y|m) = 0.0659` (ℤ₁₆), `0.0622` (ℤ₁₇) |
| writes to `k ≠ k_q` | NO | |
| `k_q` identity | NO | `I(Y;Q)=0` |
| absolute positions | NO | only relative order within `WRITES(k_q)` |

### 2.4 State-space accounting — and why it does not help C3

Per key the register is `⌈log₂ n⌉` bits. For `n=16, N_K=8`: **32 bits**. For `n=17, N_K=8`: `8·log₂17 = 32.7` bits.

**This is identical to MSAT.** The prior audit's M-02 is therefore inherited in full: 32 bits of task state against `d_hidden=128` float32 = 4096 bits of recurrent capacity, a **128× margin**, and 4× below the threshold the design's own §9 derives. The affine repair is orthogonal to C3. Any claim that AFFINE-MSAT strengthens the memory argument is false.

### 2.5 Why INIT must be deleted (and one defect that dies with it)

Under `S_0 = 0`, the first write `f_{a,b}` yields `b` — an arbitrary element of `Zn`. A separate INIT opcode is therefore redundant. Deleting it removes constraint C-a, removes the INIT/UPDATE distinction entirely, and **eliminates the prior audit's M-03 zero-argument leak** (`0 ∈ V` but `0 ∉ Δ` made a zero argument uniquely identify the init). One deletion closes one HIGH finding. This was recommended in the prior audit §13 and is retained.

---

## 3. NON-COMMUTATIVITY PROOF

### 3.1 The commutation condition

```
f_{a1,b1} ∘ f_{a2,b2} = f_{a1a2, a1b2+b1}
f_{a2,b2} ∘ f_{a1,b1} = f_{a2a1, a2b1+b2}
```

Multiplier parts agree (`Un` is abelian). The maps commute **iff**

```
a1·b2 + b1 ≡ a2·b1 + b2   (mod n)
⟺  b2(a1 − 1) ≡ b1(a2 − 1)   (mod n)              [THEOREM]
```

So `f_i, f_j` commute iff `b_j(a_i−1) ≡ b_i(a_j−1)`. **Not all pairs commute** — the group is non-abelian for every `n ≥ 3`. This is the property MSAT lacked and it is genuinely present.

### 3.2 How much of the group commutes — ENUMERATED

Exhaustive over all ordered pairs:

| `n` | `\|Aff(Zn)\|` | commuting ordered pairs | fraction | centre `Z(Aff)` |
|---|---|---|---|---|
| 8 | 32 | 352 / 1,024 | 0.3438 | `{(1,0), (1,4)}` |
| **16** | **128** | **2,944 / 16,384** | **0.1797** | **`{(1,0), (1,8)}`** |
| 11 | 110 | 1,210 / 12,100 | 0.1000 | `{(1,0)}` |
| **17** | **272** | **4,624 / 73,984** | **0.0625** | **`{(1,0)}`** |

**Two structural facts adverse to the proposed `n=16`:**

1. **~18% of ordered operation pairs commute.** If the generator samples operations uniformly, roughly one in six adjacent transpositions is a **null swap** — `Y` is unchanged. A Local Swap control that samples the swapped pair uniformly is therefore a no-op on ~18% of sessions. This does not invalidate the control, but it **must be conditioned**: the swap must be drawn from the *non-commuting* pairs, and the generator must assert `Y_swapped ≠ Y_original` per session. On ℤ₁₇ the same problem exists at 6.25%. **The assertion is mandatory either way.**

2. **`Aff(ℤ₁₆)` has a non-trivial centre.** `f_{1,8}` (i.e. `x ↦ x+8`) commutes with everything: for `a` odd, `a·8 ≡ 8 (mod 16)`. So the operation "add half the modulus" is *globally order-blind*. `Aff(ℤ₁₇)` has trivial centre — no operation is order-blind.

### 3.3 **A-01 — The 2-adic leak: `Y mod 2` is an order-blind commutative sum**

| Field | Content |
|---|---|
| **ID** | **A-01** |
| **Severity** | **CRITICAL** |
| **Kind** | **THEOREM** (ENUMERATED confirmation; MONTE CARLO quantification) |
| **Attack** | Compute `Σb mod 2` over all writes to `k_q`, ignoring order entirely and ignoring every `a`. Predict `Y` uniformly among the 8 residues of that parity. |
| **Proof** | `n = 2^k ⟹ gcd(a,n)=1 ⟹ a odd ⟹ a ≡ 1 (mod 2)`. Hence `S_{t+1} = a_t S_t + b_t ≡ S_t + b_t (mod 2)`. Induction from `S_0 = 0` gives `Y ≡ Σ_i b_i (mod 2)`. Equivalently: `(a,b) ↦ b mod 2` is a surjective group homomorphism `Aff(ℤ_{2^k}) → (ℤ₂,+)`, and the image is **abelian** — so the composite's parity cannot depend on order. |
| **Evidence** | **ENUMERATED:** 60,001 compositions at each of `n = 8, 16, 32`, depths `m ∈ {2,3,4}` — **0 violations**. **MONTE CARLO** (N=200k train / 200k held-out eval, seed 23): parity solver **0.1246** on ℤ₁₆ = **1.99× chance**, versus **0.0593 = 1.01×** on ℤ₁₇. The full `Σb mod 16` statistic does better still: **0.1394 = 2.23× chance**. |
| **Why it matters** | The prior audit killed MSAT because a permutation-invariant statistic solved it at 100%. On ℤ₁₆ a permutation-invariant statistic solves **one full bit** of it — the order-blind Bayes floor is `2/n = 0.125`, and the measured Bayes-optimal order-blind solver reaches **0.1621 at m=8** and **does not decay with depth** (0.3606 → 0.2657 → 0.1948 → 0.1729 → 0.1621 for m=3,4,5,6,8; MONTE CARLO N=300, seed 11). Contrast ℤ₁₇: 0.2661 → 0.1567 → 0.1032 → 0.0832 → **0.0815**, converging toward chance 0.0588. **The even modulus installs a permanent floor; the odd modulus does not.** |
| **Claim compromised** | **C4** — an order-blind model retains a 2× advantage, so any pre-registered C4 threshold at or below 0.125 is unreachable by an honest order-blind baseline and any threshold above it is passed by one. Also **C1**, weakly: `H(Y | multiset) = ln 8`, not `ln 16`. |
| **Required repair** | **Use an odd modulus.** `n = 17` is the minimal prime ≥ 16 and preserves ~4-bit registers (`log₂17 = 4.09`), chance `1/17 = 0.0588`, `NLL_chance = ln 17 = 2.833` nats. Any odd `n` removes the homomorphism (the leak requires *all units ≡ 1 mod p* for some `p | n`, which holds only for `p = 2`). Prime additionally gives a trivial centre. |
| **Verification test** | **Analytic pre-execution gate, no training:** assert `gcd(n, 2) == 1`. Then assert, over 10k generated sessions, that the held-out accuracy of the `Σb mod n` solver and the `Σb mod 2` solver both lie in `[chance − 0.01, chance + 0.01]`. On the proposed `n=16` this **fails immediately** at 0.1394 and 0.1246. |

### 3.4 The H1/H2 construction — the test MSAT could not pass

The mandate requires the smallest pair with identical token multiset and length but `Y(H1) ≠ Y(H2)`. Under MSAT this was **provably impossible**. Under AFFINE-MSAT it is a two-episode construction.

Take `n = 17`, `k_q = k_1`, and the two operations `f_{2,1}` and `f_{3,0}`:

```
H1 = [WRITE, k1, (2,1)] , [WRITE, k1, (3,0)] , [QUERY, k1]
     S: 0 → (2·0+1) = 1 → (3·1+0) = 3                  Y(H1) = 3

H2 = [WRITE, k1, (3,0)] , [WRITE, k1, (2,1)] , [QUERY, k1]
     S: 0 → (3·0+0) = 0 → (2·0+1) = 1                  Y(H2) = 1
```

Identical token multiset, identical counts, identical length, identical key and operation frequencies. **`Y(H1) = 3 ≠ 1 = Y(H2)`.** Verified against the commutation condition: `b_2(a_1−1) = 0·1 = 0`, `b_1(a_2−1) = 1·2 = 2`, and `0 ≢ 2 (mod 17)` ⟹ non-commuting. ∎

**`m = 2` is the minimum**, since `m = 1` composites are trivially order-free. **The design is not rejected on §2's criterion — it passes.**

**But note what the same construction yields on ℤ₁₆ with the parity check applied:** `Σb = 1 + 0 = 1` in both orderings, so both targets are odd — `Y(H1)` and `Y(H2)` differ, but an order-blind parity solver still narrows each to 8 candidates. The pair exists; the leak coexists with it. **A-01 is not refuted by the existence of H1/H2, and the two findings must not be confused.**

---

## 4. CLOSED-FORM SHORTCUT AUDIT

The mandate's warning is the right one: **"requires sequence order" ≠ "requires learning."** This section finds the minimum sufficient statistic and asks what algorithm realizes it.

### 4.1 The nine attacks

| # | Attack | Result | Basis |
|---|---|---|---|
| 1 | **Direct affine composition** | **SOLVES EXACTLY.** Maintain `(A,B)`, update `(A,B) ← (a·A, a·B + b)`, answer `B`. | THEOREM |
| 2 | **Product of `a` coefficients** | **FAILS.** `Y = F_T(0)` discards `A`. `max P(Y \| Πa) = 0.0667` vs 0.0625 (ℤ₁₆), `0.0662` vs 0.0588 (ℤ₁₇). | MONTE CARLO N=200k, seed 7 |
| 3 | **Weighted sum of `b`** | **SOLVES EXACTLY** — but the weights `Π_{j>i} a_j` are *position-dependent*, so this is not a shortcut; it is the task restated. Held-out `Σb` (unweighted): **0.1394 (ℤ₁₆) / 0.0595 (ℤ₁₇)**. | THEOREM + MONTE CARLO |
| 4 | **Parity** | **1 BIT LEAKS on even `n`** — A-01. 0.1246 vs chance 0.0625. Zero leak on odd `n`. | THEOREM, ENUMERATED |
| 5 | **Modular arithmetic (`Σb mod n`)** | **2.23× chance on ℤ₁₆**; 1.01× on ℤ₁₇. | MONTE CARLO held-out |
| 6 | **Polynomial features** | `Y` is a degree-`m` multilinear polynomial in `(a,b)`. Requires all `m` variables *in order*; no fixed-degree truncation helps. No shortcut. | THEOREM |
| 7 | **Matrix-product representation** | Equivalent to attack 1 via the `[[a,b],[0,1]]` embedding. Exact, and again just the task. | THEOREM |
| 8 | **Symbolic expression reduction** | The expression `Σ b_i Π_{j>i} a_j` admits no order-free normal form for non-abelian `Aff`. | THEOREM |
| 9 | **Sufficient-statistic compression** | The running register `S(k)` is minimal sufficient — see §4.2. | THEOREM |

### 4.2 The minimum sufficient statistic

**`S(k_q) ∈ Zn` — a single register, `⌈log₂ n⌉` bits.**

*Minimality proof.* Sufficiency: the recurrence `S ← aS + b` depends on history only through `S`, so `S_t` is a sufficient statistic for all future evolution. Minimality: `Aff(Zn)` acts **transitively** on `Zn` (given `x,y` pick `a=1, b=y−x`), so for any two distinct states there exists a continuation distinguishing them. Hence no coarser partition of `Zn` is sufficient — any lossy compression of `S` loses recoverable information. ∎

Across all keys: **`N_K · ⌈log₂ n⌉` bits = 32 bits** at `N_K=8, n=16`. At `n=17`, `8 · log₂17 = 32.7` bits.

### 4.3 **A-02 — A 32-bit fixed-width register solves the entire benchmark**

| Field | Content |
|---|---|
| **ID** | **A-02** |
| **Severity** | **HIGH** (scientific framing, not a leak) |
| **Kind** | THEOREM |
| **Attack** | The complete solver, for any `n`, any `N_K`, any `T`: |
| | ```python\nS = [0]*N_K\nfor (k, a, b) in writes:  S[k] = (a*S[k] + b) % n\nanswer = S[k_q]\n``` |
| **Result** | **100% accuracy, exactly, always.** Two lines, 32 bits of state, no learning, no memory beyond the register file. |
| **Interpretation** | This is *not* a defect in the sense A-01 is. It is **order-dependent** — it must process the stream sequentially and cannot be permuted. It defeats none of C1 or C4. But it establishes decisively that AFFINE-MSAT is **algorithmically trivial**: the benchmark measures whether an architecture can *execute a two-line known recurrence over a 32-bit register file*. |
| **Claim compromised** | **C2 as currently worded.** A task whose optimal solver is a fixed-program FSM with no learned parameters cannot, by itself, evidence "learning from experience" — because the thing to be learned is a constant. See §7.1. |
| **Required repair** | Restate the claim the benchmark supports. AFFINE-MSAT supports **C-exec**: *"this architecture can acquire and execute a fixed non-commutative state recurrence over `N_K` registers, and the acquisition requires online exposure."* That is a real, defensible, publishable claim. It is not "learns from experience" in the open-ended sense, and the design must stop implying it is. |
| **Verification test** | Report the FSM solver as a **mandatory baseline (B4)** with its exact 100% score and its 32-bit state size stated alongside `d_hidden`. Any reader must see both numbers together. |

### 4.4 The scientific rule, applied (mandate §12)

**Algorithmic solvability:** AFFINE-MSAT is solvable by a 32-bit FSM at 100%. **CONFIRMED.**

**Does that invalidate the benchmark? No** — and the mandate is right to insist on the distinction. Compare the two rejected/accepted cases:

| | MSAT (rejected) | AFFINE-MSAT (this audit) |
|---|---|---|
| Cheap solver | order-**blind** accumulator, 100% | order-**dependent** FSM, 100% |
| Does the solver need sequence? | **No** — multiset suffices | **Yes** — multiset is insufficient (odd `n`) |
| Does it refute C4? | **Yes, fatally** | **No** |
| What it does refute | C1, C4 | the *open-ended* reading of C2 |

**The rule that separates them:** a cheap solver invalidates a claim when the solver *lacks the property the claim asserts is necessary*. The order-blind accumulator lacked order, so it killed C4. The FSM has order, so C4 survives; but the FSM has **no learned parameters**, so it constrains C2.

**Conclusion:** AFFINE-MSAT tests *execution of a learned algorithm*, not *acquisition of open-ended experience*. Both are legitimate. Only one is what the design claims.

---

## 5. LOCAL SHORTCUT AUDIT

### 5.1 Method — and the correction that had to be made

Fifteen hostile solvers, each fitted as a lookup table from feature → most-frequent target on **200,000 training sessions**, then evaluated on a **disjoint 200,000-session held-out split**. Unseen features at eval time are scored by uniform random guess. `m ~ U[3,8]`, operations drawn uniformly from `Aff(Zn)`, seed 23.

**Why held-out is non-negotiable here.** The first pass fitted and evaluated on the same 100k sessions and produced `last2 = 0.2824`, `prefix_half = 0.6737`, `suffix_half = 0.8238` on ℤ₁₆ — numbers that would have read as catastrophic shortcuts. They are artifacts: those features have 16k–80k distinct cells against 100k samples, so each cell held ~1 example and the table was reciting its training set. **Held-out evaluation collapses all three to chance.** Reporting the in-sample numbers would have repeated precisely the defect this program charged against the MSAT §7 matrix.

### 5.2 Results — held-out, N=200k eval

| # | Solver | ℤ₁₆ acc | ratio | ℤ₁₇ acc | ratio | unseen cells |
|---|---|---|---|---|---|---|
| 1 | last operation | 0.0628 | 1.00× | 0.0587 | 1.00× | 0.0% |
| 2 | first operation | 0.0624 | 1.00× | 0.0584 | 0.99× | 0.0% |
| 3 | last 2 operations | 0.0613 | 0.98× | 0.0581 | 0.99× | 0.0 / 6.8% |
| 4 | last 3 operations (n-gram) | 0.0657 | 1.05× | 0.0595 | 1.01× | 90.9 / 99.0% |
| 5 | bounded window (suffix half) | 0.0639 | 1.02× | 0.0576 | 0.98× | 66.3 / 80.0% |
| 6 | suffix scan | ≡ #5 | 1.02× | ≡ #5 | 0.98× | — |
| 7 | prefix scan | ≡ #2 family | 1.00× | — | 0.99× | — |
| 8 | opcode frequency (multiset) | 0.0665 | 1.06× | 0.0586 | 1.00× | 98.5 / 99.8% |
| 9 | position classifier | ≡ #10 | 1.00× | — | 0.99× | — |
| 10 | operation-count classifier | 0.0625 | 1.00× | 0.0585 | 0.99× | 0.0% |
| 11 | **coefficient-product (`Πa`)** | 0.0631 | 1.01× | 0.0588 | 1.00× | 0.0% |
| 12 | **`b`-sum heuristic (`Σb mod n`)** | **0.1394** | **2.23×** | 0.0595 | 1.01× | 0.0% |
| 12b | **`b`-parity (`Σb mod 2`)** | **0.1246** | **1.99×** | 0.0593 | 1.01× | 0.0% |
| 13 | finite-state machine (full `S`) | 1.0000 | 16× | 1.0000 | 17× | — (A-02) |
| 14 | static transition lookup | 0.0625 | 1.00× | 0.0588 | 1.00× | — |
| 15 | compressed symbolic state (<4 bits) | ≤ 0.0625 | ≤1.00× | ≤0.0588 | ≤1.00× | §4.2 minimality |

### 5.3 Verdict on local shortcuts

**Against a pre-registered threshold of 0.10 (the program's standing shortcut gate):**

- **ℤ₁₆ FAILS** on solvers 12 and 12b — `Σb mod n` at **0.1394** and parity alone at **0.1246**, both above 0.10. These are the A-01 leak, and nothing else.
- **ℤ₁₇ PASSES on every one of the fifteen.** Maximum ratio across the entire battery is **1.01×**. Not one local statistic beats chance.
- Solver 13 is exempt by §4.4 — it is order-dependent and constrains C2, not C4.

**This is the cleanest result in the program's history and it should be stated as such.** On an odd modulus, AFFINE-MSAT defeats the entire local-shortcut battery that destroyed both DOSAM and MSAT. The single remaining defect is the modulus itself.

---

## 6. C3 MEMORY-CAUSALITY AUDIT

Per mandate: **state-space size is not admitted as evidence.** The prior audit's M-02, M-10 and M-22 are inherited and re-verified against the affine design.

### 6.1 The intervention, stated exactly

```
Condition M1:  θ frozen (parameter_hash verified)
               h = 0
               replay = ∅
               context = ∅
               optimizer state = ∅
               M = M1        (register file for k_q encodes S(k_q) = y1)
               query Q = (QUERY_TOK, k_q)

Condition M2:  identical in every listed respect
               M = M2        (encodes S(k_q) = y2 ≠ y1)

Required:      P(Ŷ | M1) ≠ P(Ŷ | M2),  and specifically Ŷ tracks y1 vs y2
```

### 6.2 Alternative causal paths — does any survive?

| Path | Can it carry `Y` under M1/M2? | Closed? |
|---|---|---|
| **hidden state `h`** | **YES — 4096 bits vs 32 bits needed.** Zeroed *in the intervention*, but the intervention is not the task: in the unablated system `h` is live and sufficient. | **NO — A-03** |
| **weights `θ`** | Frozen and hash-verified; cannot vary between M1/M2 by construction | YES |
| **replay** | `clear_replay()` exists (`nucleus.py:583`) | YES, if called |
| **optimizer** | **No `reset_optimizer` exists** — reset surface is exhausted by `reset_state`/`reset_episode`/`clear_external_memory`/`clear_replay` (`nucleus.py:571,575,579,583`). AdamW moments persist. | **NO — inherited M-22** |
| **cache** | `KVMemory._stack_cache` invalidated on write (`:279`), on `load_state_dict` (`:320`), on `clear()` (`:330`); numerically inert | YES (benign) |
| **RNG** | saved/restored incl. CUDA in the checkpoint bundle | YES |
| **Python-side state** | `step_count`, `history{loss,err}`, `source_blacklist` survive `reset_episode` | benign, unaudited |
| **context** | **`context = ∅` is not expressible** — `predict_context` raises `ValueError("context must not be empty")` (`nucleus.py:623–624`) | **NO — inherited M-14** |

**Three paths remain open: `h`, optimizer state, and context.** The mandate's rule applies: *"If any alternative causal path survives, C3 is not identified."*

### 6.3 **A-03 — The affine repair leaves C3 exactly where MSAT left it**

| Field | Content |
|---|---|
| **ID** | **A-03** |
| **Severity** | **CRITICAL** |
| **Kind** | THEOREM + CODE |
| **Attack** | Ask what the affine change did to the *state requirement*. Answer: nothing. §4.2 proves the minimal sufficient statistic is one register per key — `32 bits` at `N_K=8`, identical to MSAT. `d_hidden = 128` float32 = **4096 bits** (`nucleus.py:59`). Margin: **128×**, unchanged. |
| **Evidence** | §2.4 and §4.2 of this audit; `nucleus.py:59` `d_hidden: int = 128`. The design's own capacity rule requires `C_task > 128` bits; AFFINE-MSAT at `N_K=8` supplies 32. |
| **Why it survives** | `h` and `M` are **parallel sufficient causes** in this architecture. The A4-style intervention is proof-by-elimination: it shows that *when every other channel is severed*, output depends on `M`. That is a **read-path patency test**, not a necessity proof. The affine operator changed the *function*, not the *graph*. |
| **Claim compromised** | **C3 — NOT IDENTIFIABLE**, for the third consecutive design. |
| **Required repair** | Make capacity the **independent variable**: sweep `d_hidden ∈ {128, 64, 32, 16, 8}` and locate the crossover where a converged recurrent-only model (`M=∅`, full context, **best-of-3 seeds, maximum not mean**) falls below 0.10. `d_hidden` is already a config field — **this requires no code change**. C3 then becomes the honest conditional: *"below capacity `d*`, external memory is necessary."* Alternatively raise `N_K` to 64 (`256 bits`), but that contradicts the minimum-surviving-task goal. |
| **Verification test** | **Blocking pre-execution gate.** Converged recurrent-only, `M=∅`, best-of-3, must score ≤ 0.10 at the reported `d_hidden`. At `d_hidden=128, C_task=32 bits` the expected outcome is **far above 0.10 ⟹ REFUSE**. This gate has now been recommended in three consecutive audits and appears in no gate list. |

### 6.4 **A-04 — `project_key(0) == 0` makes the M1/M2 read key-blind (inherited, unrepaired)**

| Field | Content |
|---|---|
| **ID** | **A-04** |
| **Severity** | **CRITICAL** |
| **Kind** | CODE |
| **Attack** | The intervention requires querying `M` at `context = ∅`, `h = 0`. NN-0 addresses memory by `project_key(h)` — frozen, detached random projection (`nucleus.py:199–215`), whose docstring states the consequence outright: **`project_key(0) == key_head.bias == 0`**. |
| **Evidence** | `nucleus.py:212` `h = h.detach()`; `:207–210` documents the zero-query consequence and warns queries must follow ≥1 token; `:294–298` normalizes the query then takes cosine top-k — a zero query gives a degenerate selection independent of `k_q`. |
| **Why fatal for AFFINE-MSAT specifically** | AFFINE-MSAT has `N_K` **distinct registers**. The whole point of the query is *which register*. A `k_q`-blind read cannot express the question. `Ŷ(M1) ≠ Ŷ(M2)` would then be satisfied by any difference in memory contents whatsoever — certifying a channel that is not retrieval. |
| **Claim compromised** | C3 entirely; the M1/M2 gate as literally written. |
| **Required repair** | Report only (mandate). Either address memory by the query key symbol (`key = embed(k_q)`), or pre-register `context` width 1 and state that `h` is evolved by exactly one token — but then the "`h` contributes nothing" premise is false and needs its own matched control. |
| **Verification test** | Write `N_K` rows `(k_i, S(k_i))`; issue the M1/M2 query for each `k_i`; assert recovery ≥ 0.98. Expected: **identical read for all keys ⟹ recovery ≈ 1/N_K ⟹ REFUSE.** Prior measured exact-key recovery was **0.8824** against a ≥0.98 requirement — already failing before the zero-query issue. |

---

## 7. C2 EXPERIENCE-LEARNING AUDIT

### 7.1 The three-way separation the mandate requires

| | What it is | Is it learnable? | Where it lives |
|---|---|---|---|
| **A. the affine algebra** | `(a,b)` composition, mod-`n` arithmetic, operation semantics | **Yes, once — then constant.** A fixed program (§4.3). | `θ` |
| **B. session-specific state** | the current `S(k)` for this session's stream | **Not learnable — it is *stored*.** Different every session. | `h` or `M` |
| **C. learning from sequential experience** | improving *while* the session runs | the actual C2 claim | update rule |

**This separation is the crux of the whole audit.** AFFINE-MSAT requires A (learn the algebra once) and B (hold the state). It does **not** require C. A system that learned the algebra during pretraining and thereafter only *stored state* would score 100% with **zero online learning**.

**Therefore:** high accuracy on AFFINE-MSAT is evidence for A + B. It is **not** evidence for C. The design's C2 claim conflates them, and §4.3's two-line FSM is the proof — it has A hardcoded, B in a register, and C absent, and it scores 100%.

### 7.2 The four-arm protocol and what it actually identifies

| Arm | Protocol | Isolates | Statistic |
|---|---|---|---|
| **frozen** | θ0, no updates, memory writes permitted | B alone (storage + retrieval) | `NLL_frozen` — the **baseline** |
| **online** | θ0 + per-episode SGD in stream order | A+B+C | `ΔNLL_online = NLL_frozen − NLL_online` |
| **shuffled** | identical episodes, presentation order permuted to the *optimizer*, identical exposure | order-dependence of the **learning trajectory** | `ΔNLL_order = NLL_shuffled − NLL_online` |
| **batch** | same episodes, offline i.i.d. batches, **matched gradient-step count** | C vs mere gradient volume | `ΔNLL_onlineness = NLL_batch − NLL_online` |

**C2 is identifiable only if `ΔNLL_online > 0` AND `ΔNLL_onlineness > 0`.** The first alone shows only that SGD works. **The design specifies no gradient-step-matched batch arm**, so it cannot separate "learned online" from "received more gradient steps" — inherited defect, unrepaired.

Note: the **shuffled** arm here permutes *presentation order to the optimizer*, which is a different operation from permuting writes inside one history. It is unaffected by A-01 and remains valid.

### 7.3 **A-05 — Exposure is not equalized and no exposure unit is defined (inherited)**

| Field | Content |
|---|---|
| **ID** | **A-05** |
| **Severity** | **HIGH** |
| **Kind** | CODE + SPEC |
| **Attack** | Count what each arm consumes. |
| **Evidence** | `replay_every = 1`, `replay_batch_size = 64` mean an online arm runs a replay batch **every step** — many times the gradient exposure of an arm "matched" by episode count. `bptt_window = 1` is *enforced* (`NN0Config.__post_init__` raises otherwise), so credit assignment spans exactly one transition. |
| **Why it bites AFFINE-MSAT harder than MSAT** | The affine recurrence is a **composition**. With `bptt_window=1`, gradients never flow across two writes to the same key, so the model can learn the single-step map `S ← aS+b` but the *composition over `m ∈ [3,8]` steps is never differentiated end to end*. For a commutative sum that mattered little; for a non-commutative composition it is the entire structure. |
| **Claim compromised** | **C2 — NOT IDENTIFIABLE.** Any `ΔNLL` is confounded with exposure volume, and the compositional structure is not in the gradient signal at all. |
| **Required repair** | Define the exposure unit as the **triple (gradient steps, replay exposures, tokens seen)** and equalize all three across arms, or report all three and treat imbalance as a covariate. Additionally: either raise `bptt_window` to span a key's write group, or restate C2 as the single-transition claim. |
| **Verification test** | Instrument `step_count` and a replay-exposure counter per arm; assert pairwise equality within 1% before comparing NLL. Separately: train at `T` and evaluate at `3T` with no updates — a learned recurrence transfers, a memorized distribution does not. |

---

## 8. FORMAT-PRETRAINING AUDIT

### 8.1 What `θ0` is permitted to know

**PERMITTED (FORMAT):** the token inventory; that episodes are fixed-width 3-token; that slot 1 is an opcode, slot 2 a key, slot 3 an operation code; that `QUERY` terminates the stream; that the answer alphabet is `Zn`; the unconditional output entropy `ln n`.

**FORBIDDEN (TASK):** any conditional `P(Y | f(H))`; **the values of `a` and `b` behind any `OP_c` code**; modulo-`n` arithmetic as an operation; affine composition; the commutation condition; which operations commute; `S_0 = 0`.

### 8.2 **A-06 — If `θ0` knows the affine algebra, the online experiment tests state adaptation only**

| Field | Content |
|---|---|
| **ID** | **A-06** |
| **Severity** | **HIGH** (framing, and it is decidable in advance) |
| **Kind** | SPEC |
| **Attack** | Ask the mandate's question directly: what if `θ0` already knows `a`, `b`, modular arithmetic, affine composition, and operation semantics? |
| **Answer** | Then `θ0` possesses **A** (§7.1) in full, and the online phase can only be acquiring **B** — this session's register values. The experiment measures **state adaptation**, not algebra acquisition. |
| **Is that acceptable?** | **Yes — and it is arguably the cleaner experiment**, provided the claim is restated to match. State adaptation with frozen algebra is exactly the regime where "does the state live in `h` or in `M`?" is a sharp question, because the confound of concurrent weight learning is removed. **But it supports C-exec + C3-conditional, not open-ended C2.** |
| **Which claim it supports** | *"Given an architecture that has already acquired a non-commutative state recurrence, session-specific register state is maintained in [`h` \| `M`], and below recurrent capacity `d*` it must be `M`."* That is defensible and worth running. |
| **Required repair** | The design must **choose and pre-register** one of two regimes and state the claim each licenses: **(i) algebra-naive `θ0`** — operation codes are arbitrary symbols with no pretrained semantics; online phase must acquire A **and** B; supports the stronger C2 but confounds A with C. **(ii) algebra-competent `θ0`** — pretrained on the algebra with scrambled targets; online phase acquires B only; supports the sharper C3 conditional. **Recommend (ii)**, honestly labeled. |
| **Verification test** | Blocking gate, either regime: `Acc(θ0) ∈ [chance − 0.01, chance + 0.01]` on in-distribution **and every OOD set** before any online update. Under (ii) additionally assert `θ0` predicts single-step `S ← aS+b` at ≥ 0.95 given an explicit `(S,a,b)` probe — that is the *definition* of algebra-competent and must be measured, not assumed. |

### 8.3 **A-07 — Pretraining on the same generator leaks task structure through the input distribution**

| Field | Content |
|---|---|
| **ID** | **A-07** |
| **Severity** | **MEDIUM** |
| **Kind** | SPEC |
| **Attack** | If `θ0` is pretrained on format sequences drawn from the AFFINE-MSAT generator with scrambled targets, the *inputs* retain the generator's statistics: the anchor constraint, the `m` distribution, the operation-code frequencies, the write-count-per-key profile. |
| **Claim compromised** | C2's clean baseline; the interpretation of every `ΔNLL`. |
| **Required repair** | Pretrain on a **structurally uniform** corpus: opcodes, keys, operation codes i.i.d. uniform, no anchor constraint, episode count independent of `m`. |
| **Verification test** | The §8.2 chance gate, applied per OOD axis. Deviation ⟹ corpus leaked ⟹ regenerate. |

---

## 9. OOD AUDIT

Five axes, each with train support, test support, overlap, and the claim it licenses. **An axis is rejected if the test condition is reachable by the training-time solver with no structural change** — i.e. if it is a relabeling or mere IID novelty.

| Axis | TRAIN SUPPORT | TEST SUPPORT | OVERLAP | GENERALIZATION CLAIM | Verdict |
|---|---|---|---|---|---|
| **1. Held-out coefficients** | `a ∈ {1,3,5,7}`, `b ∈ {0..7}` | `a ∈ {9,11,13,15}`, `b ∈ {8..15}` | ∅ in symbols; **full overlap in the group generated** | "extends the learned algebra to unseen coefficient values" | **ACCEPT (strongest axis)** |
| **2. Held-out operations** | a subset `Ω_train ⊂ Aff(Zn)` that **generates** the group | `Aff(Zn) \ Ω_train` | ∅ in symbols | "composes unseen elements of a learned group" | **ACCEPT** — must assert `⟨Ω_train⟩ = Aff(Zn)` |
| **3. Held-out composition lengths (depth)** | `m ∈ [3,8]` | `m ∈ [12,24]` | ∅ | "applies the recurrence beyond trained depth" | **ACCEPT — the most scientifically valuable axis** (§7.3) |
| **4. Held-out initial states** | `S_0 = 0` (fixed) | `S_0 = s ≠ 0` | ∅ | — | **REJECT — see A-08** |
| **5. Held-out modulo bases** | `n = 17` | `n = 19` | ∅ | "transfers to a different ring" | **REJECT — see A-09** |

### 9.1 **A-08 — The held-out-initial-state axis is a relabeling**

| Field | Content |
|---|---|
| **ID** | **A-08** |
| **Severity** | MEDIUM |
| **Kind** | THEOREM |
| **Attack** | Start the register at `s ≠ 0` instead of 0. |
| **Proof it is vacuous** | Prepending the single operation `f_{1,s}` to any stream converts `S_0 = 0` into `S_0 = s`. The axis is therefore **inside the training distribution up to one extra write** — it is the depth axis with `m+1`, relabeled. `Aff(Zn)` acts transitively on `Zn`, so no initial state is structurally distinguished. |
| **Claim compromised** | C5 axis 4 — no discriminative power. |
| **Required repair** | Delete the axis. If nonzero initial states are wanted for realism, sample `S_0 ~ U(Zn)` in **both** train and test and stop calling it OOD. |
| **Verification test** | Assert the axis is absent from the pre-registered OOD set, or that `S_0` support is identical across train and test. |

### 9.2 **A-09 — The held-out-modulo-base axis is untestable without changing the output head**

| Field | Content |
|---|---|
| **ID** | **A-09** |
| **Severity** | MEDIUM |
| **Kind** | THEOREM + CODE |
| **Attack** | Train on `n = 17`, test on `n = 19`. |
| **Why it fails** | Changing `n` changes the **output alphabet size**, hence the readout dimension, hence chance level (`1/17` → `1/19`), hence the NLL scale. `Aff(ℤ₁₇)` and `Aff(ℤ₁₉)` are non-isomorphic groups of different order. This is not a generalization test; it is a **different task with a different label space**, and no fixed readout can express it. Additionally the unit groups differ (`|U₁₇|=16`, `|U₁₉|=18`), so operation codes do not transfer. |
| **Claim compromised** | C5 axis 5 — not merely weak, **incoherent**. |
| **Required repair** | Delete. If cross-ring transfer is genuinely wanted, it needs a shared vocabulary spanning both rings from the start and a readout sized to `max(n)`, which is a different benchmark and should be scoped separately. |
| **Verification test** | Assert `n` is constant across every arm and axis of a single run. |

### 9.3 Surviving OOD design

Three axes survive: **coefficients, operations, depth.** All three test whether the *algebra* was learned rather than a distribution memorized, and depth doubles as the C2 discriminator from §7.3. That is sufficient — the prior audit found MSAT's depth axis *arithmetically impossible* (`T` fixed while `m` varied); here that is fixed by making `T` derived:

```
T = Σ_k m_k              ⟹ T is a random variable, reported as a distribution
OOD axes specified in m, NEVER in T
```

**A-10 (MEDIUM, SPEC):** the design must state this explicitly, or it inherits the prior audit's M-13 verbatim. Verification: `assert T == sum(m_k)` per session.

---

## 10. BASELINE FAIRNESS

### 10.1 The exposure unit

**A fair unit of exposure is the quadruple, and all four must be equalized or reported per arm:**

```
(gradient steps, replay exposures, tokens seen, information-bearing events)
```

where an **information-bearing event** is one write to the *queried* key — the only episodes that enter `Y` (§2.3). This last unit matters because AFFINE-MSAT streams contain writes to `N_K − 1` non-queried keys plus any noise; two arms can match on tokens while differing 2× on information-bearing events if `m` distributions differ. **No prior design in this program has defined this unit.**

### 10.2 The eleven baselines

| # | Baseline | ℤ₁₆ expected | ℤ₁₇ expected | Purpose |
|---|---|---|---|---|
| **B0** | uniform random | 0.0625 | 0.0588 | floor |
| **B1** | marginal / majority class | 0.0625 | 0.0588 | vacuous vs uniform generator; keep as sanity check |
| **B2** | n-gram (last 3 ops) | 0.0657 | 0.0595 | held-out; confirms no local structure |
| **B3** | finite-window / suffix | 0.0639 | 0.0576 | confirms window shortcuts dead |
| **B4** | **symbolic affine-composer (FSM)** | **1.0000** | **1.0000** | **A-02.** Must be reported with its 32-bit state size beside `d_hidden`. |
| **B5** | **finite-state accumulator, order-blind (`Σb`)** | **0.1394** | **0.0595** | **The A-01 detector. The single most important baseline.** |
| **B5b** | order-blind parity (`Σb mod 2`) | 0.1246 | 0.0593 | isolates the leaked bit |
| **B6** | frozen NN (θ0, no updates) | chance required | chance required | enforces §8 format boundary |
| **B7** | batch learner, **matched gradient steps** | — | — | separates onlineness from gradient volume (§7.2). **Absent from all prior designs.** |
| **B8** | shuffled learner | — | — | order-dependence of the learning trajectory |
| **B9** | **memory-zero (`M=∅`, full context, converged, best-of-3)** | **expected ≫ 0.10** | **expected ≫ 0.10** | **The C3 capacity gate (A-03). Blocking.** |
| **B10** | KV-only (`h=0`, frozen θ) | undefined — key-blind (A-04) | same | isolates retrieval |

### 10.3 The strongest baseline

**B5 — the order-blind accumulator — on ℤ₁₆, at 2.23× chance.** It is the direct descendant of the solver that killed MSAT, and on the proposed even modulus it is still alive. On ℤ₁₇ it dies (1.01×), and then the strongest legitimate baseline becomes **B9, the memory-zero recurrent model**, which is expected to pass and thereby **refuse C3**.

**That ordering is the audit's practical conclusion:** fix the modulus and the benchmark's own strongest baseline stops being a shortcut and starts being the C3 capacity gate — which is exactly where the scientific difficulty actually lies.

**A-11 (MEDIUM, SPEC):** no baseline in any prior design states its gradient-step budget or convergence criterion. B9 in particular must be **best-of-N over N≥3 seeds, reported as maximum not mean** — a capacity gate must be adversarial toward the claim it protects. Verification: assert every baseline row reports budget, criterion, and seeds.

---

## 11. MINIMUM SURVIVING TASK

Searching for the smallest configuration that survives every attack in §3–§5. **The goal is causal identifiability, not size.**

### 11.1 Minimal parameters

| Parameter | Minimum surviving value | Why not smaller |
|---|---|---|
| **modulus `n`** | **17** (any odd `n ≥ 5`; prime preferred) | Even `n` ⟹ A-01 2-adic leak. `n=9` gives `\|Aff\|=54`, commuting fraction 11.1%, trivial centre — viable but chance 11.1% is coarse and 3-adic structure invites an analogous mod-3 probe. **17 is the minimal prime ≥ 16 preserving 4-bit registers and a 6.25% commuting fraction.** |
| **operations `\|Ω\|`** | **16 pre-registered `(a,b)` codes**, chosen so ≥50% of ordered pairs do not commute and `⟨Ω⟩ = Aff(ℤ₁₇)` | Fewer than ~8 risks an abelian or near-abelian subgroup. The generation requirement is what makes OOD axis 2 meaningful. |
| **composition length `m`** | **`m ≥ 2` for H1/H2 existence; `m ~ U[3,8]` for the benchmark** | `m=1` is order-free. `m≥3` keeps the order-blind Bayes solver near chance (0.2661 at m=3 → 0.0815 at m=8 on ℤ₁₇). |
| **state variables `N_K`** | **8 for C1/C4; `N_K` must be a swept variable for C3** | C4 needs only 1 key. **C3 cannot be fixed at any value** — see §11.3. |
| **stream length `T`** | **derived, `T = Σ_k m_k ∈ [24,64]`** ⟹ 72–192 tokens | Fixing `T` independently caused the prior audit's M-13. |

**Vocabulary:** 8 keys + 16 op-codes + `WRITE_TOK` + `QUERY_TOK` = **26 tokens** — smaller than MSAT's 36 and smaller than the 28 proposed in the prior audit (no `NOISE` needed; non-queried keys are the distractors).

### 11.2 Minimum task for C1 + C4 alone

**One key, `n = 17`, `m = 2`, 16 op-codes, `T = 2`.** Seven tokens total. The H1/H2 pair of §3.4 lives here. This configuration is *sufficient* to establish order dependence and history necessity, and it costs nothing to run.

### 11.3 The irreducible obstruction

**No fixed `N_K` makes C3 identifiable**, because C3's difficulty is the *ratio* of task state to recurrent capacity, and that ratio has two free ends. The minimum surviving design therefore **cannot be a single configuration** — it must be a sweep:

```
d_hidden ∈ {128, 64, 32, 16, 8}     ×     N_K ∈ {8, 16, 32, 64}
```

and C3's claim becomes the crossover surface where recurrent-only accuracy falls below 0.10. `d_hidden` and `N_K` are both existing configuration fields, so **the sweep needs no code change** — only the decision to treat capacity as the variable it is.

### 11.4 Cost on a GTX-1070

`T ≤ 64` episodes ⟹ ≤ 192 tokens; `d_embed=32`, `d_hidden ≤ 128`; 400 eval sessions × 5 capacity settings × ~8 arms. Minutes to low hours, **cheaper at small `d_hidden` than the rejected MSAT**. The repair costs specification effort, not compute.

---

## 12. CLAIM MATRIX

Status vocabulary is exactly as mandated: **IDENTIFIABLE / NOT IDENTIFIABLE / INVALID / UNTESTED**. `PROVEN` is not used, including for design-only arguments — a correction to this audit's own predecessor, which used "PROVEN BY DESIGN" for C1. C1 is **IDENTIFIABLE**; whether it holds is established by the generator's construction, but the word "proven" is withheld per mandate.

### C1 — History Necessity

| | |
|---|---|
| **Identifying intervention** | Compare `Ŷ` given `Q` alone versus `Q` with full `H`. Analytically: `I(Y;Q) = 0` because every `f_{a,b}` with `a ∈ Un` is a bijection on `Zn`, so `Y` is exactly uniform for every `k_q`. |
| **Control** | B0 uniform (0.0588), B1 marginal (0.0588) — both must sit at chance |
| **Alternative explanation** | Key-conditional bias if operation sampling correlated with `k_q`; excluded by i.i.d. uniform sampling |
| **Required evidence** | Held-out `max P(Y \| k_q) ≤ chance + 0.01`; `max P(Y \| m) ≤ chance + 0.01` (measured 0.0622 at chance 0.0588) |
| **Kill criterion** | **K-1:** any query-only or count-only statistic exceeds chance + 0.01 |
| **Status** | **IDENTIFIABLE** (both moduli) |

### C2 — Online Experience Learning

| | |
|---|---|
| **Identifying intervention** | Four-arm paired comparison (§7.2): frozen / online / shuffled / **gradient-step-matched batch** |
| **Control** | B6 frozen θ0 at chance; B7 matched-batch; B8 shuffled |
| **Alternative explanation** | **(i)** more gradient steps, not onlineness (A-05); **(ii)** the algebra was pretrained and only state is being stored (A-06, §7.1); **(iii)** the two-line FSM shows a 100% solver needs **no** learning at all (A-02) |
| **Required evidence** | `ΔNLL_online > 0` **and** `ΔNLL_onlineness > 0`, with all four exposure units equalized within 1% |
| **Kill criterion** | **K-2:** any arm's exposure quadruple differs > 1% from its comparator. **K-3:** `θ0` outside `[chance ± 0.01]` before updates |
| **Status** | **NOT IDENTIFIABLE** (both moduli) — no matched-batch arm exists; exposure undefined; `bptt_window=1` excludes the compositional structure from the gradient |

### C3 — Persistent External Memory

| | |
|---|---|
| **Identifying intervention** | `do(M=M1)` vs `do(M=M2)` with θ frozen+hashed, `h=0`, replay ∅, context ∅, optimizer ∅ (§6.1) |
| **Control** | **B9 memory-zero**, converged, best-of-3, maximum reported; B10 KV-only |
| **Alternative explanation** | **`h` is sufficient** — 32 bits of task state against 4096 bits of hidden state, a **128× margin unchanged by the affine repair** (A-03). Plus two open channels: optimizer state (no `reset_optimizer`) and context (`predict_context` raises on empty). Plus the read is `k_q`-blind at the intervention point (A-04). |
| **Required evidence** | B9 ≤ 0.10 at the reported `d_hidden`; exact-key recovery ≥ 0.98; all three open channels closed |
| **Kill criterion** | **K-4:** B9 > 0.10. **K-5:** exact-key recovery < 0.98 (last measured **0.8824**). **K-6:** the intervention read is identical across distinct `k_q`. |
| **Status** | **NOT IDENTIFIABLE** (both moduli) — third consecutive design |

### C4 — Sequential Order Dependence

| | |
|---|---|
| **Identifying intervention** | Local swap of two adjacent **non-commuting** writes to `k_q`, with per-session assertion `Y_swapped ≠ Y_original` |
| **Control** | **B5 order-blind accumulator** (`Σb mod n`) and **B5b** parity |
| **Alternative explanation** | **On ℤ₁₆: the 2-adic leak.** `Y ≡ Σb (mod 2)` is order-blind and permutation-invariant (A-01), giving B5 **0.1394 = 2.23× chance** and B5b **0.1246 = 1.99×**. On ℤ₁₇ both collapse to 1.01× and no alternative survives. |
| **Required evidence** | B5 and B5b within 0.01 of chance; H1/H2 pair exhibited (§3.4 — it exists, `m=2`); ≥50% of the operation table's ordered pairs non-commuting |
| **Kill criterion** | **K-7:** any order-blind statistic > 0.10. **K-8:** `Y_swapped == Y_original` for a session drawn as a swap arm. **K-9:** `gcd(n,2) == 0`. |
| **Status** | **NOT IDENTIFIABLE** as proposed (`n=16`) → **IDENTIFIABLE** on odd `n`. **Closes on R-1 alone.** |

### C5 — OOD Generalization

| | |
|---|---|
| **Identifying intervention** | Three surviving axes: held-out coefficients, held-out operations (with `⟨Ω_train⟩ = Aff`), held-out depth `m` |
| **Control** | B6 at chance on **every** OOD set; B4 FSM at 100% on every axis (a correct algorithm is axis-invariant — this is the reference ceiling) |
| **Alternative explanation** | Axis 4 (initial states) is a relabeling — one prepended `f_{1,s}` (A-08). Axis 5 (modulo bases) is a different label space (A-09). Depth confounded with stream length unless `T` is derived (A-10). |
| **Required evidence** | Per axis: disjoint support asserted; `θ0` at chance; accuracy reported against B4's 100% ceiling |
| **Kill criterion** | **K-10:** any axis has non-empty train/test support overlap, or is reachable by prepending ≤1 operation. **K-11:** `T` specified independently of `Σ m_k`. |
| **Status** | **NOT IDENTIFIABLE** as proposed (5 axes, 2 invalid, `T` inconsistent) → **IDENTIFIABLE on 3 of 5 axes** after repair |

### 12.1 Summary

| Claim | As proposed (`n=16`) | After R-1 (odd `n`) | After R-1…R-5 |
|---|---|---|---|
| C1 | IDENTIFIABLE | IDENTIFIABLE | IDENTIFIABLE |
| C2 | NOT IDENTIFIABLE | NOT IDENTIFIABLE | IDENTIFIABLE |
| C3 | NOT IDENTIFIABLE | NOT IDENTIFIABLE | IDENTIFIABLE (conditional on `d_hidden`) |
| C4 | **NOT IDENTIFIABLE** | **IDENTIFIABLE** | IDENTIFIABLE |
| C5 | NOT IDENTIFIABLE | NOT IDENTIFIABLE | IDENTIFIABLE (3 of 5 axes) |

**Nothing is INVALID.** That is the substantive difference from the MSAT audit, where C4 was INVALID — refuted by the generator's own algebra with no parameter able to fix it. Here every claim is either identifiable or repairable by stated means.

### 12.2 Full vulnerability register

| ID | Sev | Title | Claim | § |
|---|---|---|---|---|
| **A-01** | **CRITICAL** | 2-adic leak: `Y mod 2 = Σb mod 2` is order-blind on even `n` | C4, C1 | 3.3 |
| **A-03** | **CRITICAL** | Affine repair leaves the 128× capacity margin untouched | C3 | 6.3 |
| **A-04** | **CRITICAL** | `project_key(0)==0` ⟹ key-blind read at the intervention point | C3 | 6.4 |
| **A-02** | HIGH | 32-bit FSM solves at 100% ⟹ tests execution, not learning | C2 | 4.3 |
| **A-05** | HIGH | Exposure unequalized; `bptt_window=1` excludes composition | C2 | 7.3 |
| **A-06** | HIGH | Pretraining regime undecided ⟹ claim undetermined | C2 | 8.2 |
| **A-07** | MEDIUM | Pretraining corpus leaks input-distribution structure | C2 | 8.3 |
| **A-08** | MEDIUM | Held-out-initial-state axis is a relabeling | C5 | 9.1 |
| **A-09** | MEDIUM | Held-out-modulo-base axis has an incoherent label space | C5 | 9.2 |
| **A-10** | MEDIUM | `T` must be derived from `Σ m_k` | C5 | 9.3 |
| **A-11** | MEDIUM | Baselines lack step budgets; B9 must be best-of-N maximum | C3 | 10.3 |
| **A-12** | LOW | `Aff(ℤ₁₆)` centre `{(1,0),(1,8)}` ⟹ `x↦x+8` is globally order-blind | C4 | 3.2 |
| **A-13** | LOW | ~18% of ℤ₁₆ ordered pairs commute (6.25% on ℤ₁₇) ⟹ swap must be conditioned | C4 | 3.2 |

**3 CRITICAL, 3 HIGH, 5 MEDIUM, 2 LOW.** Every CRITICAL except A-01 is inherited unrepaired from the MSAT audit.

---

## 13. REQUIRED REPAIRS

**R-1 through R-3 are blocking.** No decisive run may proceed until all three are closed and independently verified.

### Blocking

**R-1 — Change the modulus to an odd value.** (closes A-01, A-12; **closes C4 outright**)
`n = 17`. Chance `1/17 = 0.0588`, `NLL_chance = ln 17 = 2.833` nats. Registers remain ~4 bits. The 2-adic homomorphism `Aff(ℤ_{2^k}) → (ℤ₂,+)` does not exist for odd `n`; the centre becomes trivial; the commuting-pair fraction drops 17.97% → 6.25%; **all fifteen held-out local solvers fall to ratio ≤ 1.01×.** Analytic gate: `assert gcd(n,2) == 1`. Empirical gate: B5 and B5b within 0.01 of chance. **This is a one-parameter change and it is the highest-value edit available anywhere in the design.**

**R-2 — Make recurrent capacity the independent variable.** (closes A-03; converts C3 to a measurable conditional)
Sweep `d_hidden ∈ {128,64,32,16,8}` × `N_K ∈ {8,16,32,64}`. Add as **blocking**: converged recurrent-only (`M=∅`, full context, **best-of-3 seeds, maximum**) must score ≤ 0.10 at the reported capacity, else C3 is unidentifiable at those parameters and the run **refuses**. Both fields already exist in `NN0Config` — **no code change required.** *This gate has now been recommended in three consecutive audits and appears in no gate list. Its continued absence is the single largest governance defect in the program.*

**R-3 — Pre-register which claim the benchmark supports.** (closes A-02, A-06)
Choose regime (i) algebra-naive `θ0` or (ii) algebra-competent `θ0` (§8.2), and state the licensed claim verbatim. **Recommend (ii)** with the claim: *"an architecture that has acquired a non-commutative state recurrence maintains session-specific register state in [`h` | `M`]; below recurrent capacity `d*` it must be `M`."* Report the two-line FSM (B4, 100%, 32 bits) beside `d_hidden` in every results table, so no reader can mistake algorithmic solvability for learning necessity.

### Required before publication

**R-4 — Fix the shared C2/C3 operating point.** (closes A-04, and the two open channels)
Pre-register `context` width 1, not ∅, and state that `h` is evolved by exactly one token; add a matched `M=∅` single-token control. Address memory by the query key symbol rather than `project_key(h)`, **or** delete C3 from the claim set rather than certify a `k_q`-blind read. Mandate full model reconstruction between arms and assert optimizer-state emptiness via `state_digest()` (no `reset_optimizer` exists).

**R-5 — Define exposure and add the missing arm.** (closes A-05, A-11)
Exposure unit = **(gradient steps, replay exposures, tokens seen, information-bearing events)**; equalize within 1% or report as covariates. Add **B7**, the gradient-step-matched offline batch arm — absent from every prior design and without which C2 cannot be separated from gradient volume. Either raise `bptt_window` to span a key's write group or restate C2 as the single-transition claim. Every baseline states its step budget, convergence criterion, and seeds; B9 reports the **maximum** over ≥3 seeds.

**R-6 — Repair the OOD axis set.** (closes A-08, A-09, A-10)
Delete the initial-state axis (relabeling) and the modulo-base axis (incoherent label space). Retain coefficients, operations, depth. Assert `⟨Ω_train⟩ = Aff(Zn)` for the operation axis. Make `T = Σ_k m_k` derived; specify OOD depth in `m`, never in `T`; report stream length as a distribution.

**R-7 — Condition the swap arm.** (closes A-13)
Draw the Local Swap from **non-commuting** pairs only and assert `Y_swapped ≠ Y_original` per session. ~18% of ℤ₁₆ pairs and 6.25% of ℤ₁₇ pairs commute, so an unconditioned swap is a silent no-op on that fraction. State **exactly one** swap threshold — the prior design carried three mutually contradictory ones.

**R-8 — Regenerate the pretraining corpus structurally uniform** (A-07), with the chance gate applied to in-distribution **and every OOD set**.

---

## 14. KILL CRITERIA

Pre-registered, blocking, and **not waivable by the party that authored the design.** Any single criterion firing halts the transaction.

| # | Criterion | Fires when | Against `n=16` as proposed |
|---|---|---|---|
| **K-1** | Query/count leakage | any query-only or count-only statistic > chance + 0.01 | PASSES (0.0659, 0.0625) |
| **K-2** | Exposure imbalance | any arm's exposure quadruple differs > 1% from its comparator | **FIRES** — undefined |
| **K-3** | Pretraining leak | `Acc(θ0)` outside `[chance ± 0.01]` on any eval set | UNTESTED |
| **K-4** | **Recurrent sufficiency** | converged `M=∅`, best-of-3, scores > 0.10 | **FIRES** — 32 bits vs 4096 |
| **K-5** | Retrieval fidelity | exact-key value recovery < 0.98 | **FIRES** — measured 0.8824 |
| **K-6** | Key-blind read | intervention read identical across distinct `k_q` | **FIRES** — `project_key(0)==0` |
| **K-7** | **Order-blindness** | any order-blind statistic > 0.10 | **FIRES** — 0.1394 / 0.1246 |
| **K-8** | Swap invariance | `Y_swapped == Y_original` in a swap-arm session | **FIRES** — on ~18% of sessions |
| **K-9** | **Even modulus** | `gcd(n, 2) ≠ 1` | **FIRES** — `n = 16` |
| **K-10** | OOD overlap | any axis has overlapping support, or is reachable by prepending ≤1 operation | **FIRES** — axes 4 and 5 |
| **K-11** | Generator inconsistency | `T` specified independently of `Σ m_k` | **FIRES** if inherited |
| **K-12** | Unreproducible number | any quantitative claim lacks a probe, N, and seed | — (this audit states all three) |
| **K-13** | Self-certification | a design's own verdict used as evidence of readiness | **FIRES** on the predecessor's §20 |

**Nine of thirteen fire against the design as proposed. K-9 is a one-line check that subsumes K-7 and K-8 and can be run before any GPU is powered on.**

---

## 15. FINAL GO / NO-GO

### VERDICT: **B — REPAIRABLE**

**NO-GO as specified. GO conditional on R-1, R-2, R-3.**

### 15.1 The determination

AFFINE-MSAT is the correct structural answer to the defect that killed MSAT, and the mathematics confirms it works. `Aff(Zn)` is genuinely non-abelian: the composite target is `Y = Σ_i b_i · Π_{j>i} a_j`, in which each translation coefficient is weighted by the product of every multiplier that follows it, so position enters the answer through the weight. The H1/H2 falsification pair — **provably impossible under MSAT** — exists here at `m = 2` and is exhibited in §3.4. Fifteen hostile local solvers, evaluated on a disjoint 200k held-out split, sit at ratio 0.98×–1.06× on an odd modulus. **C4 becomes identifiable for the first time in this program.** That is a genuine advance and the design deserves credit for it.

But the specific modulus proposed reintroduces the defect it was built to remove. Because every unit of ℤ_{2^k} is odd, `a ≡ 1 (mod 2)`, so `(a,b) ↦ b mod 2` is a homomorphism onto an **abelian** group and `Y ≡ Σ b_i (mod 2)` identically — zero violations across 60,001 enumerated compositions at each of `n = 8, 16, 32`. One full bit of the target is an order-blind commutative sum: MSAT's defect, intact, in the low bit. Measured consequence on ℤ₁₆: `Σb mod n` reaches **0.1394 (2.23× chance)** and parity alone **0.1246 (1.99×)**, both above the 0.10 shortcut gate, and the Bayes-optimal order-blind solver plateaus at **0.1621** rather than decaying with depth. On ℤ₁₇ the same statistics read **0.0595** and **0.0593** against chance 0.0588 — dead.

Separately, and independently of the modulus: the affine repair does **nothing** for C3. The minimal sufficient statistic is still one register per key — **32 bits at `N_K=8`, identical to MSAT** — against 4096 bits of GRU hidden state. The 128× margin is unchanged, `h` remains a parallel sufficient cause, and the capacity gate recommended in three consecutive audits still appears in no gate list. And the two-line 32-bit FSM that solves the task at 100% establishes that AFFINE-MSAT measures *execution of a fixed recurrence*, not open-ended experience learning — a legitimate claim, but not the one the design makes.

### 15.2 Why B and not C

C would require that no parameter choice repairs the design. **The transition function here is correct**; the defect is the modulus, and `16 → 17` closes A-01, A-12 and C4 in a single character, with vocabulary, episode format, stream length and GTX-1070 feasibility all unchanged. That is the definition of REPAIRABLE. The contrast with the predecessor is exact: MSAT was C because *no* parameter can make an abelian group non-abelian.

### 15.3 Why not A

Three blocking items. **R-1** — the modulus is even and nine of thirteen kill criteria fire. **R-2** — C3 is unidentifiable for the third consecutive design, for a reason now reported three times. **R-3** — the design has not decided whether `θ0` knows the affine algebra, and until it does, the claim the experiment supports is undetermined. A design cannot be certified ready while its headline claim is unidentifiable on grounds already communicated twice.

### 15.4 Standing governance objection, restated

The predecessor certified itself **"A — SCIENTIFICALLY READY"** while naming its own blocking defect in §4.21 and omitting the fix from §12. This audit records that **no design document may supply its own readiness verdict**, and that the recurrent-only capacity gate — recommended in the DOSAM audit, the MSAT audit, and again here as R-2 — must be entered into the gate list as blocking before any further design iteration is reviewed. Three identical recommendations that produce no specification change is a process failure, not a technical one.

### 15.5 Conditions for reopening

R-1, R-2, R-3 closed and independently verified. K-1…K-13 pre-registered as blocking. B5/B5b within 0.01 of chance on the repaired generator. B9 reported as best-of-3 maximum with its step budget. The H1/H2 pair exhibited from the actual generator. `⟨Ω_train⟩ = Aff(Zn)` asserted. `T = Σ_k m_k` asserted per session. On satisfaction of those, this audit's verdict moves to **A** without further redesign — the mathematics is sound and the remaining work is specification discipline.

### 15.6 Transaction compliance

AFFINE-MSAT **not implemented** as a benchmark. No benchmark file created or modified. `nucleus.py` **read only**. NN-0 **not trained**. Decisive experiment **not run**. Seeds 200–209 **not consumed** (seeds used: 0, 7, 11, 23). Nothing sealed, nothing committed.

Group-theoretic enumerations were executed in throwaway interpreter sessions and are declared in §0. Every quantitative claim carries its kind (**THEOREM / ENUMERATED / MONTE CARLO / CODE / SPEC**), its N, and its seed. The one in-sample measurement error made during this audit — inflated `last2`/`prefix_half`/`suffix_half` figures from fitting and evaluating on the same 100k sessions — was detected, corrected on a disjoint held-out split, and is documented in §0 and §5.1 rather than quietly dropped.

**DECISIVE EXPERIMENT: NOT RUN — PROHIBITED AND HONOURED.**

---

*End of audit.*
