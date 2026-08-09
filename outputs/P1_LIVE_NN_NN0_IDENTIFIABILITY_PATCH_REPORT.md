# P1-LIVE-NN — NN-0 Nucleus Identifiability Patch Report

**Transaction:** NN-0 architectural/interface repair for C3 capacity-scaling identifiability
**Date:** 2026-08-09
**Scope:** Interface/architecture repair only — no AFFINE-MSAT, no new benchmark, no decisive run

## FINAL STATUS: PARTIAL

All six patches are implemented and all fourteen acceptance criteria have a passing
test **except** T4 (CPU/CUDA parity), which **cannot be executed on this host** — CUDA
is unavailable, so its five cases skip rather than pass. T14 additionally records a
**known, expected, unavoidable** consequence: 8 protocol-sealed tests now fail because
the sealed hash covers `nucleus.py` byte-for-byte and re-sealing was prohibited.

Status is PARTIAL rather than COMPLETE solely because of those two items. Both are
listed explicitly under *Unresolved / Blockers*. Nothing is claimed as verified that
was not actually executed.

**C3 is not proven, tested, or evidenced by this transaction.** These patches only make
the future capacity-scaling experiment *identifiable* — they produce no result about
whether external memory carries predictive information.

---

## 1. PROHIBITIONS HONOURED

| Prohibition | Status |
|---|---|
| Do NOT implement AFFINE-MSAT | Honoured — not touched |
| Do NOT implement a new benchmark | Honoured — no generator modified |
| Do NOT run decisive experiments | Honoured — only unit-scale training inside tests |
| Do NOT consume seeds 200–209 | Honoured — tests use seeds 0–22 only |
| Do NOT modify canonical governance surfaces | Honoured — `protocol.py`/`protocol.json` unmodified |
| Do NOT stage or commit | Honoured — nothing staged; both files remain untracked |
| Do NOT seal a protocol / modify protocol hashes | Honoured — no re-seal performed |

**Git incident (disclosed):** during verification I ran `git stash push` on `nucleus.py`,
which failed because the file is untracked; the paired `git stash pop` then partially
applied a **pre-existing unrelated stash** (`WIP on main: Phase 62.1`) into the working
tree, creating conflicts in `backend/`. On the operator's instruction the tracked tree
was restored with `git reset --hard HEAD` (back to `d5ae8f29`). `stash@{0}` was **not**
dropped and still holds all Phase 62.1 content. No commit, no staging, and no loss of
patch work occurred (all patch files are untracked). This is disclosed because it
touched repository state outside the requested scope.

---

## 2. IMPLEMENTATION PLAN (WRITTEN BEFORE CODE)

| # | Current defect | Exact code surface | Minimal patch | Invariant added | Acceptance test |
|---|---|---|---|---|---|
| 1 | `d_hidden` never audited across capacities; no capacity recorded in checkpoint metadata | `NN0Config.d_hidden`, `TinyGRUCore.__init__`, `save_checkpoint`, `from_checkpoint` | Record `d_hidden` in `meta.json`; refuse a reload whose recorded capacity disagrees | A checkpoint cannot be silently reinterpreted at another capacity | T1, T3, T3b |
| 2 | `project_key(0) == key_head.bias == 0` → `do(h=0)` yields a key-blind, constant memory read | `TinyGRUCore.project_key` | Add `project_key_token(x)`: address from the key-token embedding via a frozen, seeded, non-persistent buffer | The memory address stays query-dependent when `h=0` | T9, T9b |
| 3 | No `reset_optimizer()`; AdamW moments **and** per-parameter `step` leak history across an evaluation boundary | `NN0Trainer.optim` | Rebuild the optimizer and drop `.grad` | Optimizer state clears without touching θ | T5, T5b |
| 4 | No strict freeze; `eval()` does not block updates and `requires_grad=False` alone still permits a stale-`.grad` `optim.step()` | `NN0Trainer._assert_trainable_source` | `freeze_parameters()`/`unfreeze_parameters()` + `_frozen` latch at the single shared choke point | θ is immutable while frozen, and updates refuse loudly | T6, T12 |
| 5 | `state_dict()` **aliases** live KV/replay lists — a "snapshot" mutates as the trainer runs, so "A and B differ only in M" is inexpressible | `NN0Trainer` | Add deep `snapshot()`/`restore()` incl. RNG, freeze flag, `d_hidden` | Snapshot is immutable and restore is bit-exact | T10, T11, T11b–d |
| 6 | Over-repair risk | — | BPTT, replay, KV temperature, architecture beyond addressing, generators, statistics, schedule all untouched | Identifiability repair kept separate from performance work | T14 |

---

## 3. FILES CHANGED

| File | Change |
|---|---|
| `p1/live/neural/nn0/nucleus.py` | Patches 1–5 (both files remain **untracked**, as instructed) |
| `p1/tests/live/test_nn0_identifiability.py` | **New** — 21 test functions → 55 cases after parametrisation |

Added public surface: `project_key_token`, `reset_optimizer`, `optimizer_state_is_empty`,
`freeze_parameters`, `unfreeze_parameters`, `parameters_frozen`, `parameter_hash`,
`snapshot`, `restore`.

---

## 4. WHAT DETERMINES K_write AND K_query (PATCH 2)

Two addressing modes now exist. The pre-existing one is unchanged; the new one is additive.

**Mode A — hidden-conditioned (pre-existing, still the default training/eval path):**

```
K_write = key_head(h_{t-1}.detach())     # written at step t
K_query = key_head(h_{t-1}.detach())     # queried at step t
```
Determined by: the incoming hidden state `h_{t-1}` and the frozen `key_head` weights.
`key_head` never receives gradient (the `.detach()` severs it), so it stays at its
seeded initialisation. **Defect retained by design:** at `h=0`, `key_head(0)` is
`key_head.bias`, initialised to zeros — every query collapses to one constant vector.
T9 asserts this collapse explicitly so the defect can never be silently reintroduced
as a "fix".

**Mode B — token-conditioned (new, for the `do(h=0)` intervention):**

```
K_write = E[x_key] @ key_token_proj
K_query = E[x_key] @ key_token_proj
```
Determined by: **the key token identity alone** — its embedding row `E[x_key]` and
`key_token_proj`, a frozen `(d_embed, d_read)` random matrix.

Properties, each asserted by test:
- **Deterministic** — drawn from a dedicated `torch.Generator` seeded by `cfg.seed`, so it
  is identical at every `d_hidden` and cannot perturb the global RNG stream that
  parameter init consumes (T2).
- **Independent of stale hidden state** — `h` is not an input, so `do(h=0)` leaves the
  address intact (T9).
- **Query identity survives h=0** — distinct key tokens produce distinct addresses and
  distinct reads; the same token always addresses the same slot (T9, T9b).
- **Auditable / non-parametric** — `persistent=False` keeps it out of `state_dict`, it
  adds **0** trainable parameters, and `.detach()` keeps the store gradient-free.
- **Snapshot-compatible** — re-derived identically from `cfg.seed`, so exact snapshots
  round-trip (T3, T11).
- **Differentiable where appropriate** — deliberately **not** differentiable, matching the
  existing non-parametric-store contract; the read still reaches the loss, the address does not.

*Note:* `project_key_token` is now **available** but is not yet wired into the training
or evaluation path — the future protocol selects it at the intervention site. This is
deliberate: switching the default addressing mode would change learning dynamics, which
Patch 6 forbids without a test demonstrating necessity.

---

## 5. TESTS RUN — EXACT COUNTS

Command:
```bash
python -m pytest p1/tests/live/test_nn0_identifiability.py p1/tests/live/test_nn0_nucleus.py tests/live/test_ln_dec_interface.py tests/live/test_ln_dec_repair1.py -q
```

**Result: 116 passed, 6 skipped, 3 failed, 5 errors (106s)**

New suite alone: **49 passed, 6 skipped** (`test_nn0_identifiability.py`).
Pre-existing nucleus suite alone: **all passed** (`test_nn0_nucleus.py`, unmodified).

| ID | Criterion | Cases | Result |
|---|---|---|---|
| T1 | `d_hidden ∈ {8,16,32,64,128}` | 5 + 1 monotonicity | **PASS** |
| T2 | Deterministic init at every `d_hidden` | 5 | **PASS** |
| T3 | Checkpoint/reload equivalence at every `d_hidden` | 5 + 1 refusal | **PASS** |
| T4 | CPU/CUDA parity | 5 | **SKIPPED — CUDA unavailable on host** |
| T5 | `reset_optimizer` clears AdamW state | 2 | **PASS** |
| T6 | `freeze_parameters` prevents mutation | 1 | **PASS** |
| T7 | Hidden reset gives exact `h=0` | 1 | **PASS** |
| T8 | Memory reset gives exact empty `M` | 1 | **PASS** |
| T9 | Addressing stays query-dependent at `h=0` | 2 | **PASS** |
| T10 | Two states differing only in `M` identical elsewhere | 1 | **PASS** |
| T11 | Snapshot/restore round-trip equality | 4 | **PASS** |
| T12 | θ checksum unchanged across frozen prediction | 1 | **PASS** |
| T13 | No stale cache survives memory mutation/reset | 2 | **PASS** |
| T14 | Default existing NN-0 tests remain green | — | **PASS for NN-0; 8 protocol-seal failures — see §7** |

The 6 skips are all CUDA-gated: 5 from T4, 1 pre-existing (`test_cuda_cpu_execution`).

T5b is worth noting for method: my first version conflated surfaces — `step()` also
draws a replay sample and appends to KV, so restoring θ alone left replay RNG and memory
drifting and the "identical update" check failed. Corrected to restore a full snapshot,
isolating the optimizer as the only manipulated variable. It also now asserts the
positive control: with moments left in place, the same update from the same θ lands
**elsewhere**, proving the optimizer state was causally active rather than inert.

---

## 6. PARAMETER COUNTS FOR ALL d_hidden

Protocol configuration (`vocab=128, d_embed=32, d_read=32`):

| `d_hidden` | Parameters | Δ |
|---|---|---|
| 8 | 6,024 | — |
| 16 | 8,592 | +2,568 |
| 32 | 15,264 | +6,672 |
| 64 | 34,368 | +19,104 |
| **128** | **100,224** | +65,856 |

**Backward-compatibility check:** `d_hidden=128` gives **100,224**, which matches the
sealed protocol's recorded `parameter_count` exactly. The default architecture is
unchanged in parameter terms; `project_key_token` adds no trainable parameters at any capacity.

Counts are cross-checked in-test against an independently derived closed form
(`expected_params`), not against the model's own `parameter_count()` — so a wiring
mistake cannot make the assertion vacuously true. Test-suite config
(`vocab=32, d_embed=16, d_read=16`): 1,592 / 2,752 / 5,504 / 12,928 / 34,688.

---

## 7. BEHAVIOUR INTENTIONALLY CHANGED

1. **`meta.json` gains a `d_hidden` field, and reload refuses a mismatch.** A checkpoint
   whose recorded capacity disagrees with its config is rejected instead of loaded.
   Reload of pre-patch checkpoints is preserved via `meta.get("d_hidden", cfg.d_hidden)`.
2. **`probe()` no longer forces `model.train()` on exit.** It previously called
   `self.model.train()` unconditionally, so probing a frozen/eval model silently flipped
   it back to train mode — which would corrupt a frozen evaluation arm. It now restores
   the prior mode, matching `predict_context`'s existing pattern. This is a genuine
   behavioural change and the one place I judged the existing code unsafe for the
   protocol; it is required for T12.
3. **`step`/`step_sequence` raise `AssertionError` when frozen** rather than silently
   updating. Enforced once at the shared `_assert_trainable_source` choke point, so both
   paths and any future caller are covered by construction.
4. **8 protocol-sealed tests now fail** — see below.

### The 8 sealed-test failures (expected and unavoidable)

All 8 abort at the *same* line, `protocol.py:510`, with
`ProtocolRefusal: canonical implementation hash drifted`:

```
tests/live/test_ln_dec_interface.py::test_protocol_hash_seed_store_and_seoi_detectors
tests/live/test_ln_dec_interface.py::test_dry_run_is_reproducible_without_decisive_execution
tests/live/test_ln_dec_repair1.py::test_r10_decisive_gate_cannot_be_bypassed_by_omitting_root
tests/live/test_ln_dec_repair1.py::test_r5_exposure_unit_is_recorded_in_the_protocol       (ERROR)
tests/live/test_ln_dec_repair1.py::test_r7_decisive_and_diagnostic_families_are_separated  (ERROR)
tests/live/test_ln_dec_repair1.py::test_r10_protocol_hash_is_stable                        (ERROR)
tests/live/test_ln_dec_repair1.py::test_r10_decisive_execution_is_still_refused            (ERROR)
tests/live/test_ln_dec_repair1.py::test_r10_sesoi_is_closed_with_a_derivation_and_a_consumed_seed_range (ERROR)
```

`nucleus.py` is in `IMPLEMENTATION_FILES` (`protocol.py:41`) and the gate is a plain
SHA-256 over the whole file, so **any** byte change trips it:

- sealed: `241ad5c96379c4ec3dbd07ee84b50cdc005561d51dc066a5c631a9042fda718b`
- current: differs (patched)

**These are not behavioural regressions.** The gate runs inside
`load_and_verify_protocol` *before* any nucleus code executes, so no NN-0 behaviour is
under test in any of the 8. Clearing them requires re-sealing the protocol, which this
transaction is explicitly forbidden from doing. This is the correct governance outcome:
the seal detected an unsealed change to a protected surface, exactly as designed.

---

## 8. UNRESOLVED / BLOCKERS

1. **T4 (CPU/CUDA parity) is UNVERIFIED.** CUDA is unavailable on this host; all 5 cases
   skip. The test is written and will execute on CUDA hardware, but **no parity claim
   should be treated as evidenced until it has actually run there.** This must be
   discharged before the capacity-scaling experiment runs on GPU.
2. **The protocol seal must be re-sealed by the operator** before any decisive run — an
   authorisation deliberately outside this transaction.
3. **`project_key_token` is available but not wired in.** The future protocol must select
   it at the `do(h=0)` intervention site. Until then the default path retains the
   `project_key(0) == 0` collapse.
4. **`d_critical` remains unmeasured.** The audit's `B_unit ≈ 1–2 bits/dimension` is an
   estimate, not a measurement; which of {8, 16} actually sits below the cliff is an
   empirical question this transaction does not touch.
5. **`optimizer_state_is_empty()` is a state assertion, not a leakage proof.** It confirms
   AdamW moments and step counters are cleared; it cannot prove no other stateful surface
   leaks history.
6. **Restore mutates global RNG.** `restore()` sets the process-wide torch/random/numpy
   state, consistent with the existing checkpoint contract. Two trainers cannot be
   restored independently in one process without the second overwriting the first's RNG.
7. **Scope note:** `d_hidden` was already a functioning `NN0Config` field, so Patch 1
   reduced to capacity provenance plus test coverage rather than new plumbing.

---

## 9. SCIENTIFIC STATEMENT

This transaction repaired **interfaces**, not evidence. It makes four things possible
that were previously impossible or unsound:

1. Sweeping `d_hidden ∈ {8,16,32,64,128}` with recorded, verified capacity provenance.
2. A `do(h=0)` intervention that does not silently destroy the memory address (Path 1
   blocked without confounding Path 2).
3. Blocking the optimizer-momentum path (Path 5) independently of θ.
4. Constructing `State A ≡ State B except for M` from an immutable deep snapshot.

**No claim about C3 is made, supported, or weakened by this work.** Whether external KV
memory provides predictive information unavailable to the recurrent state remains
entirely open, and the capacity-scaling experiment that could address it has not been
designed, sealed, or run here.
