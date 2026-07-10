# SQLite

SQLite is the persistence layer for the `backend/` application. There is
**no SQLite in `core/`** - the canonical science is stateless machinery that
serializes via `state_dict`/`load_state_dict` (see `prediction.md`). All
SQLite access in `backend/` is centralized through one helper so the
durability and concurrency PRAGMAs are consistent.

## 1. The shared helper - `backend/memory/_sqlite.py`

Every synchronous `sqlite3` connection in the memory stack, the self-model,
the soul graph, the candidate store, concept birth, curiosity, and the
orchestration loop goes through this module. It exports:

- `connect(db_path, row_factory=None, timeout=20.0) -> sqlite3.Connection`
  - the synchronous entry point.
- `apply_async_pragmas(db)` - apply the same PRAGMAs to an `aiosqlite`
  connection.
- `canonical_db_path(relative_path) -> Path` - resolve a logical
  `velynx_data`-relative name to a CWD-independent absolute path.
- `resolve_db_path(db_path)` - redirect a path into the test-isolation dir
  under `VELYNX_TEST_MODE=1`.
- `verify_wal(conn, db_path)` - warn if WAL silently fell back.

PRAGMAs applied on every connection (`_pragma_statements`):

    PRAGMA journal_mode=WAL
    PRAGMA busy_timeout=20000
    PRAGMA synchronous=NORMAL

These are best-effort: each PRAGMA is wrapped in `try/except` so an
unsupported filesystem never blocks a connection. `verify_wal` warns (does
not raise) if the journal mode is not WAL.

Constants:

- `BUSY_TIMEOUT_MS = 20_000` (raised from 5000 in Dec 2025 for the live-fire
  harness: 100 rapid consecutive read/write operations across KGs,
  episodic memory, memory-graph, consolidator, and vector backend).
- `DEFAULT_TIMEOUT_S = 20.0`.
- Logger: `velynx.sqlite`.

## 2. Why the helper exists (the CWD-drift fix)

Many subsystems historically opened `.velynx_data/<file>` as a CWD-relative
string. When the process CWD differed between turns (repo root vs
`backend/`), the same logical store resolved to two different files - the
root cause of the live-fire "ghost memory" / `RETRIEVAL_FAILURE` at
Interaction #2. `canonical_db_path` resolves a logical name to a single
absolute location anchored to the project root, independent of CWD.

Resolution order for `canonical_db_path`:

1. `VELYNX_DATA_DIR` env override, if set -> `<env>/<relative_path>`.
2. Otherwise -> `<project-root>/.velynx_data/<relative_path>`.

The canonical data directory is the dotted `.velynx_data` at the project
root.

## 3. Test isolation

`VELYNX_TEST_MODE=1` redirects every database into
`backend/tests/data/_isolated/<dir>__<file>` so the suite never touches
live user data in `.velynx_data/`. The `<dir>__` prefix keeps same-named
files apart (e.g. `knowledge_graph/graph.db` vs `soul_graph/graph.db`).
The redirect is idempotent; `:memory:` passes through unchanged.

Rationale: the memory stack opens a fresh connection per operation (both
sync `sqlite3` and async `aiosqlite`), and a per-connection in-memory
database would lose its schema between calls. The isolation dir is a real
on-disk location so schema persists across connections within a test run.

## 4. Schema ownership

| Database                | Owner (subsystem)                       | Tables / role                                              |
|-------------------------|-----------------------------------------|------------------------------------------------------------|
| `velynx_state.db`       | memory + cognition (recall observability) | `memory_log`, `concept_states`, `core_beliefs`; `recall_events`, `recall_concepts`, `recall_memories` (Phase 52.8) |
| `velynx_identity.db`    | `backend/self_model/identity_store.py`  | `health_logs`, `audit_logs` (self-model - see `identity.md`) |
| `concept_birth.db`      | `backend/cognition/concept_birth.py`    | Birthed-concept ledger                                      |
| `knowledge_graph.db`   | `backend/knowledge/`                    | Knowledge-graph triples/nodes/edges                         |
| `memory_graph.db`      | `backend/memory/`                       | Memory-graph edges/nodes                                    |
| `soul_graph.db`        | `backend/soul/soul_graph.py`            | Soul-graph store (Program B; `[REJECTED]` as science)       |
| `brain_stem.db`        | cognition substrate                     | Cluster/predictor substrate                                 |
| `predictive.db`        | cognition substrate                     | Predictive-core persistence                                  |
| `test_velynx.db`       | `backend/database/engine.py` (SQLAlchemy) | Async ORM store (`sqlite+aiosqlite`)                       |

`reproducibility.yaml` lists the runtime databases and confirms `*.db`
files are git-ignored and not in VCS.

## 5. Migration rules

There are **two distinct persistence stacks** with different migration
discipline:

1. **`sqlite3` stores** (memory, self-model, soul, knowledge, cognition)
   - opened via `_sqlite.connect`. Schemas are **self-initializing** with
   `CREATE TABLE IF NOT EXISTS` (see `IdentityStore.init_db`,
   `RecallLogger._init_db`). There is no migration framework for these
   stores. Adding a column or changing a type is a code change that must
   handle existing rows defensively (the stores already read with
   `sqlite3.Error` -> default fallbacks).
2. **SQLAlchemy / `aiosqlite` store** (`backend/database/engine.py`,
   `backend/alembic.ini`) - the async ORM store uses **Alembic** for
   migrations. Schema changes here go through Alembic revisions, not
   ad-hoc `CREATE TABLE`.

Rules that apply to both:

- Never commit a database file. `*.db`, `*.db-shm`, `*.db-wal` are
  git-ignored.
- Never open a raw `sqlite3.connect` in `backend/`; route through
  `_sqlite.connect` so PRAGMAs are consistent. (The only deliberate raw
  `sqlite3.connect` calls are in read-only inspection tools
  `backend/diagnose_db.py` and `backend/wipe_db.py`, which open
  `file:<path>?mode=ro` URIs.)
- Anchor every path through `canonical_db_path` so the store is
  CWD-independent.
- Run under `VELYNX_TEST_MODE=1` in tests so the live `.velynx_data/`
  stores are never touched.

## 6. Transaction guidance

- Use a context manager: `with open_connection(db_path) as conn:` so the
  connection is closed even on error.
- Call `conn.commit()` after writes. Reads need no commit.
- WAL allows readers to proceed during a write; do not hold write
  transactions open longer than necessary.
- `busy_timeout=20000` makes a blocked writer wait up to 20 s rather than
  immediately raising `sqlite3.OperationalError: database is locked`. If
  you see that error, the cause is almost always a connection opened
  outside the helper (missing PRAGMAs) or a long-lived write transaction.
- For async code, open with `aiosqlite.connect(path)` and immediately call
  `await apply_async_pragmas(db)`.

## 7. Performance considerations

- **WAL + `synchronous=NORMAL`** is safe with WAL and far faster than
  `FULL`. Do not raise to `FULL` without reason.
- **`busy_timeout=20000`** is tuned for the live-fire 100-consecutive-op
  workload. Lowering it reintroduces `database is locked` under
  concurrency.
- **CWD-independent paths** avoid the ghost-memory failure and the
  double-file problem. Always resolve via `canonical_db_path`.
- **Test isolation** prevents the suite from contending with live data and
  from corrupting user state.
- **Fresh-connection-per-op** is the established pattern in the memory
  stack; connection pooling is not used for the `sqlite3` stores. Do not
  introduce a pool without Architect review.
- **Indexes** should be added where a query's `ORDER BY ... LIMIT` or a
  `FOREIGN KEY` join is hot (e.g. `recall_events` is read by latest
  timestamp; `audit_logs.health_log_id` joins `health_logs.id`).

## 8. Debugging

- `backend/diagnose_db.py` - inspect tables, row counts, and recent rows
  of `velynx_state.db`, `velynx_identity.db`, and the KG, read-only.
- `backend/wipe_db.py` - reset target databases (use only in
  development/test; never against live data).
- `backend/tools/visualize_graph.py`, `backend/tools/dedupe_directions.py`
  - read-only graph inspection and edge dedup.
- If WAL fell back (exotic filesystem), `verify_wal` logs a warning;
  concurrent access may then raise `OperationalError`.

## 9. What is not present

- There is no SQLite in `core/`. Canonical primitives serialize via
  `state_dict`/`load_state_dict` (JSON-compatible dicts), not via a
  database.
- There is no connection pool for the `sqlite3` stores.
- There is no shared ORM across the `sqlite3` stores; each subsystem owns
  its own schema with hand-written SQL. Only the `backend/database`
  SQLAlchemy store uses an ORM and Alembic.