# Telemetry

Telemetry in VELYNX is the non-blocking observability substrate. It watches
the cognitive and consolidation pipelines without ever participating in them.
All telemetry code lives in the `backend/` application layer; there is no
telemetry in `core/`. This document states the binding invariant and the
per-subsystem sinks.

## 1. The binding invariant

**A telemetry fault must never crash or perturb the system it observes.**

This is stated, in slightly different words, in every telemetry module:

- `backend/simulation/logger.py` (CausalLogger): "the caller is never
  crashed (unless `strict=True`)"; a tombstone record is appended on fault
  so the event is never silently lost.
- `backend/memory/recall_logger.py` (RecallLogger): "Non-blocking
  telemetry... a pure OBSERVER - it never participates in or mutates
  retrieval logic. Every public write is wrapped by the caller in a
  try/except so a telemetry failure can never crash the cognitive loop."
- `backend/cognition/memory_scheduler.py` (MemoryScheduler): "reads
  memory telemetry from a duck-typed source... The scheduler never merges,
  re-clusters, or mutates memory; it only emits a boolean 'consolidate
  now' decision."
- `backend/orchestration/cognitive_loop.py`: the Phase 52.8 recall
  observability hook is wrapped so "retrieval logic itself is untouched.
  A telemetry failure" is logged as a warning, not raised.

Consequences for any new telemetry code:

1. **Non-blocking.** Wrap every write in `try/except`; log and continue.
2. **Pure observer.** Never call into the logic you are observing, never
   mutate its state, never advance an engine.
3. **Structural typing, not imports.** Accept duck-typed sources/sinks.
   CausalLogger "never imports `causal_evaluator`, `reasoning_engine`,
   `simulation_memory_context`, pydantic, or any database driver" so the
   layer is "trivially unit-testable and impossible to entangle with
   pipeline lifecycles".
4. **Never raise out of the telemetry path.** Serializers degrade to
   `repr`; defaults are returned on missing data.
5. **Atomic, concurrent-safe appends** for file-backed ledgers: process
   lock + `O_APPEND` + a single `write()` of `line + "\n"` + `flush` +
   `fsync` (CausalLogger). No torn lines, no interleaving.
6. **Self-healing.** On fault, append a tombstone so the event is not
   silently lost (CausalLogger), unless `strict=True` is explicitly set.

## 2. Where it lives

| Module                                       | Sink                          | Records                                                         |
|----------------------------------------------|-------------------------------|-----------------------------------------------------------------|
| `backend/simulation/logger.py`               | JSON Lines ledger file        | `CausalDelta` (counterfactual evaluation results)               |
| `backend/memory/recall_logger.py`            | `velynx_state.db` tables       | Recall events, trigger concepts, surfaced memories              |
| `backend/cognition/memory_scheduler.py`      | duck-typed `telemetry_source` | Reads `get_memory_summary()` for `active_anomalies_count`        |
| `backend/cognition/lexicon_updater.py`       | `gap_log.jsonl`               | Missed-concept telemetry for auto-healing                       |
| `backend/cognition/consolidation_tracker.py` | in-memory counters + traces   | Replay decisions (observability - see `replay.md`)              |
| `backend/orchestration/cognitive_loop.py`    | recall observability hook     | Recall event logging, non-blocking                               |
| `backend/ops/__init__.py`                     | Prometheus / OpenTelemetry    | Deployment-profile-gated export (`enable_prometheus`, `enable_opentelemetry`) |
| `archive/code/diagnostics/cognitive_telemetry.py` | (archived)              | Legacy C6 meta-level telemetry substrate - do not reuse         |

## 3. Logging

- **CausalLogger** (`backend/simulation/logger.py`) - append-only JSONL
  ledger of counterfactual-evaluation `CausalDelta` records. Record shape:
  `schema: "velynx.causal-delta/v1"`, monotonic `seq`, `ts`, `host`, `pid`,
  `payload` (full CausalDelta), `extra` (caller tags). Sync `log()`, async
  `alog()`, and `iter_records()` for replay/analysis.
- **RecallLogger** (`backend/memory/recall_logger.py`) - SQLite-backed
  recall observability (Phase 52.8). Tables `recall_events`,
  `recall_concepts`, `recall_memories` in `velynx_state.db`. Opened via
  `backend.memory._sqlite.connect` (see `sqlite.md`).
- **Missed-concept telemetry** (`gap_log.jsonl`) - read by
  `lexicon_updater` to drive auto-healing of the lexicon.
- **Standard logging** uses the `logging` module with `velynx.<subsystem>`
  logger names (see `coding.md`).

## 4. Metrics

- **Recall metrics** (RecallLogger): `retrieved_memory_count`,
  `total_recall_energy`, `recall_ratio`, `retrieval_density`,
  `system_error`.
- **Consolidation metrics** (`ConsolidationTracker`): `replay_evaluations`,
  `replay_accepted`, `replay_rejected`, `merges_committed`,
  `queue_replayed`, `quarantine_replayed`, `anomalies_absorbed`,
  `anomalies_retired`, `replay_efficiency`. Pure observability - never
  read back by cognition (see `replay.md`).
- **Health metrics** (`backend/self_model/`): `global_health`,
  `saturation_health`, `diversity_health`, `belief_health`,
  `recall_health`, `health_delta`, `confidence_score`. Application
  observability, not canonical science (see `identity.md`).
- **Resource snapshots** (`backend/ops/ResourceSnapshot`):
  `memory_entries`, `db_pool_checked_out/in`, `redis_connected`,
  `event_queue_depth`, `active_requests`.

## 5. Tracing

- **Distributed tracing** is gated by deployment profile
  (`backend/ops/__init__.py`): `enable_opentelemetry` is `False` for
  development, `False` for staging, `True` for production;
  `enable_prometheus` is `False`/`True`/`True` respectively. Tracing is
  opt-in and never on by default in development.
- **Session replay** (`backend/evaluation/session_replay.py`,
  `backend/app/routes_ops.py` `/runtime/replay/{correlation_id}`,
  `backend/app/routes_eval.py` `/trials/replay/{correlation_id}`)
  reconstructs past cognition/evaluation sessions by `correlation_id` via
  `event_bus.replay`. This is an operational read-only facility, distinct
  from the sandbox ReplayEngine (see `replay.md`).

## 6. Replay diagnostics

Telemetry records are designed to be replayed for analysis without
re-running the cognitive loop:

- `CausalLogger.iter_records()` - iterate the JSONL ledger of causal
  deltas.
- `recall_events` / `recall_concepts` / `recall_memories` - re-derive
  recall behaviour from the SQLite log.
- `ConsolidationTracker.traces` - one structured entry per replay
  decision (deltas, before/after energy, strategy, reason) for
  post-hoc accept/reject diagnosis.
- `event_bus.replay(correlation_id)` - reconstruct a session's event
  stream for debugging.

## 7. Validation expectations for telemetry

- A telemetry unit test must be able to inject a **mutable telemetry
  source** (see `test_c8_control_upgrade.py`: "Mutable telemetry source:
  lets a test dial `active_anomalies_count`"). Telemetry sources are
  duck-typed, so tests substitute fakes.
- A telemetry fault injected during a test must not change the outcome of
  the observed pipeline (the non-blocking invariant is testable).
- File-backed ledgers must remain well-formed under concurrent appends
  (CausalLogger's process lock + `O_APPEND` + single-write contract).
- Telemetry that opens a database must go through
  `backend/memory/_sqlite.py` and must run under `VELYNX_TEST_MODE=1`
  without touching live data (see `sqlite.md`).

## 8. What is not present

- There is no telemetry in `core/`. The canonical science measures `L`,
  `G`, `M` directly (see `prediction.md`); it has no observers.
- There is no always-on tracing in development. OpenTelemetry/Prometheus
  are production-gated.
- The archived `archive/code/diagnostics/cognitive_telemetry.py` is a
  legacy C6 substrate; it is not live telemetry and must not be wired into
  new code.