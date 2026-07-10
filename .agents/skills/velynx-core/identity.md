# Identity

The identity subsystem lives in the `backend/self_model/` application layer.
There is **no identity subsystem in `core/`**. This document describes only
repository-supported behaviour and states the canonical status explicitly.

## 1. Canonical status (read first)

PROGRAM_D_CANONICAL.md Section 5 marks **the self-model** `[REJECTED]` as a
load-bearing scientific mechanism (it appears in the canon's "permanently
removed" list). The code in `backend/self_model/` is therefore
**engineering infrastructure for the Program A product, not a canonical
scientific claim**. None of {EXP-0, EXP-1, EXP-2, E0} require it (canon
Section 1, rule 2). Do not sell self-model output as "emergence",
"self-awareness", or any anthropomorphic claim (canon Section 1 prohibits
mind/soul/belief/understanding in live names or claims).

## 2. Two senses of "identity" - do not conflate them

1. **Self-model identity** (`backend/self_model/`) - VELYNX's
   self-representation: cognitive health, audit artifacts, persisted in
   `velynx_identity.db`. This is the subject of this document.
2. **Entity identity** (`backend/simulation/interface.py`,
   `backend/knowledge/`) - structural, identity-bearing fields on a world
   `Entity` (the fields that "define entity identity" and may not be
   modified by overrides). This is part of the world-model ontology, not
   the self-model (see `ontology.md`).

## 3. Where it lives

- `backend/self_model/identity_store.py` - `IdentityStore`. Persists
  health and audit records to `velynx_identity.db`.
- `backend/self_model/baseline_tracker.py` - `BaselineTracker`. Reads live
  cognitive state from `velynx_state.db`; reads long-term trends back from
  `velynx_identity.db`.
- `backend/self_model/health_monitor.py` - `CognitiveHealthMonitor`.
  Computes health scores from tracker aggregates.
- `backend/self_model/self_audit.py` - `CognitiveAuditor`. Produces audit
  artifacts (primary driver, recommended circuit breaker).
- `backend/self_model/self_model.py` - `run_cognitive_cycle()`. Wires the
  four components together.
- `backend/cognition/self_model.py` - the conversational self-representation
  surface (identity/nature/version phrasings; "VELYNX's self-representation:
  identity, epistemic state, and cognitive health").

## 4. Responsibilities (repository-supported)

- Read live cognitive state (memory count, concept saturation/activation,
  prediction friction, energy) from `velynx_state.db`.
- Compute a health report (saturation, diversity, belief, recall, global
  health, confidence, system state) and a velocity warning.
- Produce an audit artifact (primary driver of change, recommended circuit
  breaker).
- Persist each cycle's health report and audit artifact to
  `velynx_identity.db` for trend analysis.
- Expose a conversational self-representation for Program A queries about
  identity, epistemic state, and cognitive health.

## 5. Persistence rules

Two databases, both opened through `backend/memory/_sqlite.py`
(`connect` -> WAL + busy_timeout + synchronous=NORMAL; CWD-independent
`canonical_db_path`; `VELYNX_TEST_MODE` redirects to the isolated test
dir - see `sqlite.md`):

- **`velynx_state.db`** - the **read source** for live cognitive state.
  Tables read by `BaselineTracker`: `memory_log` (memory count, emotional
  energy, prediction error, turn index), `concept_states` (concept,
  activation, evidence count), `core_beliefs` (concept, confidence). The
  self-model does not own this schema; it consumes it read-only.
- **`velynx_identity.db`** - the **write target** owned by `IdentityStore`.
  Tables:
  - `health_logs`: `id`, `timestamp`, `global_health`, `saturation_health`,
    `diversity_health`, `belief_health`, `recall_health`, `health_delta`,
    `confidence_score`, `system_state`, `velocity_warning`.
  - `audit_logs`: `id`, `timestamp`, `health_log_id` (FK -> `health_logs.id`),
    `audit_type`, `primary_driver`, `driver_delta`,
    `recommended_circuit_breaker`, `audit_confidence`.

Schema is created with `CREATE TABLE IF NOT EXISTS` (`init_db`), so the
identity database is self-initializing. `log_health_report` returns the new
`health_log_id`, which `log_audit_artifact` uses as the foreign key - the
audit row is always linked to its health row.

## 6. Invariants

- **Defensive reads.** `BaselineTracker._execute_state_query` catches
  `sqlite3.Error` and returns `[]`; metric getters return defined defaults
  when rows are absent (e.g. `saturation_ratio: 0.0`,
  `recall_energy: "unsupported"`). A missing or unreadable state database
  never crashes the cycle.
- **Clamped scores.** Every health score is clamped to `[0.0, 1.0]` via
  `max(0.0, min(1.0, ...))`. `total_concepts` is `max(1,
  total_ontology_concepts)` to avoid divide-by-zero.
- **State evaluation is monotonic thresholds.** `evaluate_state` maps
  `global_health` to `Excellent` (>= 0.90), `Healthy` (>= 0.70),
  `Unstable` (>= 0.50), else `Pathological`.
- **Audit is linked to health.** `audit_logs.health_log_id` references
  `health_logs.id`; there is no orphan audit row.
- **Latest-by-timestamp access.** `get_latest_health` reads
  `ORDER BY timestamp DESC LIMIT 1`; trend analysis reads the last 30
  `diversity_health` values from `velynx_identity.db`.
- **Test isolation.** Under `VELYNX_TEST_MODE=1` both databases are
  redirected to `backend/tests/data/_isolated/` so the suite never touches
  live identity or state data.

## 7. What is not present

- There is no identity primitive in `core/`. The canonical five primitives
  (`x_t`, `P_theta`, `L`, `G`, `M`) contain no self-model (see
  `prediction.md`).
- The self-model is not validated by any experiment in {EXP-0, EXP-1,
  EXP-2, E0}. Its health scores and audit artifacts are observability for
  the product, not scientific measurements.
- The health-index weights in `CognitiveHealthMonitor` (saturation 0.35,
  belief 0.25, diversity 0.20, recall 0.20) are application heuristics, not
  canonical constants. They are distinct from the `[REJECTED]` CPI
  0.40/0.30/0.20/0.10 weights (canon Section 5) and must not be treated as
  scientific.
- "Velynx identity" in the sense of a persistent personhood or
  developing self is `[REJECTED]` framing. The subsystem stores health and
  audit rows, not a self.