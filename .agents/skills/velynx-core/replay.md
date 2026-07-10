# Replay Engine

The Replay Engine is the backend C8 "pure sandbox simulator" that rehearses a
proposed memory restructuring *before* it is committed to the live cluster
substrate. It lives in the application layer (`backend/`), not in the
canonical `core/`. This document covers replay only; see `prediction.md` for
the canonical scoring rule and `validation.md` for review.

## 1. Where it lives

- `backend/cognition/replay_engine.py` - `ReplayEngine`. The simulator.
- `backend/cognition/decision_policy.py` - `DecisionPolicy`. Reads the
  simulator's `DecisionScore` and decides accept/reject. Performs no
  simulation, mutates no state.
- `backend/cognition/consolidation_tracker.py` - `ConsolidationTracker`.
  Pure-observability recorder for the pipeline.
- `backend/cognition/vector_prediction_core.py` - `VectorPredictionCore` /
  `ClusterEngine`. The live substrate that replay clones.
- `backend/cognition/memory_scheduler.py` - the scheduler that triggers the
  sleep cycle.
- `backend/evaluation/session_replay.py`, `backend/app/routes_ops.py`
  (`/runtime/replay/{correlation_id}`) - operational session replay by
  correlation id (a different, read-only "replay past events" facility,
  not the sandbox simulator).
- `research/` - a side-effect-free study harness that wraps the production
  `ReplayEngine` with a pluggable `ConsolidationPolicy` and a configurable
  replay horizon.

## 2. Responsibilities

The engine's sole job is to **simulate and measure - never to decide**
(`replay_engine.py` docstring). For each proposal it:

1. `deepcopy`s the live clustering substrate into a sandbox.
2. Applies the proposed merge to the clone only.
3. Measures the brain's native cognitive vitals (H, S, A) in both the live
   (pre-merge) and sandbox (post-merge) worlds against a recent-vector
   window, strictly read-only.
4. Returns the two snapshots as a `DecisionScore`.

The accept/reject judgement is made by `DecisionPolicy`, which reads the
`DecisionScore`. Measurement (here) is cleanly separated from policy
(there).

## 3. Invariants

Strict contract from `replay_engine.py`:

- The live `ClusterEngine` is **never** mutated by a simulation. Every
  structural change happens against the sandbox clone.
- Vital measurement is **read-only**: it never calls `assign` or otherwise
  advances engine state (no centroid updates, no surprise tracking, no
  predictor mutation).
- `commit_proposal` is the **only** method that touches the live engine,
  and only the caller may invoke it, and only after a positive policy
  verdict.

`ConsolidationTracker` adds a one-directional observability contract:
nothing in the tracker is ever read back by the cognitive path. Mutating a
counter can never change which proposals are generated, how a replay is
scored, or whether a merge is committed.

## 4. Determinism requirements

The vitals identity test (`test_replay_engine_vitals_r3c.py`) is binding.
Its protocol states: "If any assertion fails, STOP. The protocol demands a
halt on identity failure." The required behaviours:

- **Online equals Replay.** `VectorPredictionCore.ingest` (online) and
  `ReplayEngine.simulate_proposal` (replay) compute the same cognitive
  quantities (S, H_local, H_global, A) for the same observation stream within
  `1e-10`.
- **No-op is a fixed point.** A self-merge proposal (`target_a == target_b`)
  leaves S and A unchanged: `S_after == S_before` and `A_after == A_before`.
- **Replay is pure.** After a replay, the snapshot equals a fresh `deepcopy`
  of the original: cluster count, `last_cluster_id`, and predictor
  transitions are unchanged.
- **Replay is deterministic.** Two replays of the same snapshot produce
  byte-identical S (and by construction the same `DecisionScore`).

Seed every randomized path. The default benchmark seed is 42
(`reproducibility.yaml`).

## 5. Replay workflow

The C8 consolidation pipeline (`consolidation_tracker.py`):

```
scheduler -> propose -> replay -> commit
```

- **scheduler** - `memory_scheduler` reads memory telemetry and signals a
  sleep cycle (`scheduler_triggers`).
- **propose** - the candidate generator produces a merge proposal
  (`target_a`, `target_b`); counted as `proposals_generated`.
- **replay** - `ReplayEngine.simulate_proposal` deepcopies, applies to the
  clone, measures vitals before/after read-only, returns a `DecisionScore`
  (`replay_evaluations`, `queue_replayed`). `DecisionPolicy` then returns
  accept/reject (`replay_accepted` / `replay_rejected`).
- **commit** - on a positive verdict, the caller invokes `commit_proposal`
  against the live engine (`merges_committed`). Post-commit, quarantined
  anomalies are re-checked (`quarantine_replayed`, `anomalies_absorbed` vs
  `anomalies_retired`).

The `research/` harness drives the same loop with a hot-swappable
`ConsolidationPolicy` (Null / Random / FIFOAge / Similarity / Utility /
FreeEnergy / Oracle) and a configurable replay horizon, measuring every
proposal identically so policies stay comparable. It composes the
production components without mutating them.

## 6. The vitals and a canonical caveat

The vitals measured by replay (lower-is-better, matching
`validation.metrics`):

- `S` - `prediction_error`: mean Markov forecast error over the window
  (Euclidean distance between each vector and its predicted centroid).
- `H` - `entropy`: conditional Shannon entropy of the cluster-transition
  chain induced by replaying the window read-only.
- `A` - `active_load`: live clusters plus the spatial volume of the
  anomaly cloud.

`DecisionPolicy` combines these into a Cognitive Energy
`E = lambda*H + mu*S + nu*A` with default coefficients
`(lambda, mu, nu) = (1.0, 2.0, 0.5)`, mirrored from
`validation.metrics.LAMBDA/MU/NU` (kept as mirrors, not imports, so the
cognition module stays standard-library only). Two strategies are
supported: `"free_energy"` (default - accept iff `E_after <= E_before`,
equivalently `delta_energy >= 0`) and `"pareto"` (reject only when strictly
dominated on all four vitals).

**Canonical caveat.** PROGRAM_D_CANONICAL.md Section 5 **permanently
removes** `E = lambda*H + mu*S + nu*A` (and the `lambda/mu/nu` coefficients)
as the scientific substrate, replacing it with the log score
`L = -log P_theta(x_{t+1} | x_<=t)` (see `prediction.md`). The free-energy
proxy therefore remains in `backend/` as the C8 operational policy, but it
is `[REJECTED]` as a load-bearing scientific mechanism. New canonical
science must use `L`, not `E`. Do not reintroduce `E` into `core/`.

## 7. Debugging guidance

- **Identity test failure (online vs replay diverge).** The read-only
  measurement in `simulate_proposal` is likely calling something that
  advances state (`assign`, a centroid update, surprise tracking). Verify
  the sandbox is a `deepcopy` and that measurement never calls `assign`.
- **Live engine mutated by a replay.** Check that `commit_proposal` is
  gated behind a positive policy verdict and that only the caller invokes
  it. A simulation path that touches the live `ClusterEngine` is a
  contract violation.
- **Unexpected accept/reject.** Read the `ConsolidationTracker` traces: each
  replay decision logs `delta_prediction` (dS), `delta_entropy` (dH),
  `delta_load` (dA), `delta_energy` (dE), before/after energy, per-vital
  snapshots, the `decision_strategy` in force, and the structural `reason`.
- **Lock contention during replay.** Replay opens the same SQLite stores
  as the live loop. Connections must go through `backend/memory/_sqlite.py`
  (WAL + busy_timeout) - see `sqlite.md`.
- **Non-determinism across runs.** Confirm the snapshot is a `deepcopy`, the
  recent-vector window is copied (`[v[:] for v in STREAM]` per the vitals
  test), and any RNG uses an explicit seed.
- **Replay efficiency.** `replay_efficiency = replay_accepted /
  replay_evaluations`. A persistent low ratio means the policy is rejecting
  almost all proposals - inspect the trace `reason` field before tuning
  anything (and never tune a scientific constant - see `coding.md`).

## 8. What is not present

- There is no replay engine in `core/`. The canonical science does not
  rehearse merges; it computes `L`, `G`, `M` directly.
- `research/` does not ship its own replay engine; it wraps the backend
  `ReplayEngine`. Do not duplicate the simulator in the study layer.