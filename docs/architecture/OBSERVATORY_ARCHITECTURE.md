# P1 Observatory — Architecture Specification

**Status**: Draft for review. Not yet registered in `GOVERNANCE_REGISTRY.yaml`.
**Scope**: The Observatory subsystem only. This document has no authority over the
scientific process, the engine loop, or any registered normative artifact.
**Version**: 0.1.0 (schema `obs/1`)

---

## 0. Prime directive, and the substrate conflict

### 0.1 Prime directive

> The Observatory observes. It never participates.

Formally, three invariants. Every one is mechanically testable, and the test suite
in §17 exists to keep them true for the life of the project.

| ID | Invariant | Enforcement |
|----|-----------|-------------|
| **I1 — Non-interference** | Attaching, configuring, or crashing the Observatory cannot change any number the engine reports. | Differential run test: identical loss/probe sequences with the Observatory on and off. |
| **I2 — Identity neutrality** | Enabling the Observatory must not change `config_hash` or `run_id`. | Attach only through `logging`, which `RunConfig.identity_dict()` already excludes from the hash. |
| **I3 — Provenance** | Every rendered pixel traces to a real engine event, identified by `(run_id, seq, t)`. No element may exist without such a source. | Renderer consumes only decoded events; no generator may synthesise geometry. Enforced by review + `test_no_synthetic_sources`. |

I3 is why this is an instrument and not a dashboard. A visual element that cannot
name its `(run_id, seq, t)` is a bug, not a decoration.

### 0.2 The substrate conflict — read before designing any renderer

The brief asks for live neurons, neuron creation, neuron deletion, and connection
growth. **The active P1 engine has no neurons and no edges as first-class objects.**
This is a finding from the code, not an opinion:

- `experiments/engine/engine.py::_execute` is the canonical loop. Its entire state is
  `model`, `memory`, `gate`, `replay`, `benchmark`.
- The only registered model family is `p1v0.model.CountModel` — an order-1 categorical
  predictor holding `counts: List[List[float]]` of shape `alphabet × alphabet`, plus
  scalars `alpha`, `decay`, `n_updates`. Default `alphabet` is 8.
- `p1v0.memory.ReplayBuffer` is a reservoir of `(context, target)` pairs.
- There is no growth mechanism, no unit allocation, and no structural plasticity
  anywhere in the active tree. `framework/core/mdl/mdl_growth.py` and the legacy
  `backend/` graph stores (`neural_links.json`, `memory_graph.py`, `concept_birth.py`)
  are Program A/B/C inheritance, outside the active engine.

Two responses were available. Rendering a decorative neural net over a count matrix
violates I3, so it is rejected. The design instead adopts the **honest mapping**:

> The engine's learned state *is already a weighted directed graph.* Observe that graph.

| Requested view | Real state that backs it | Source of truth |
|---|---|---|
| neuron / node | a context state (symbol) of the model | index `i` of `CountModel.counts` |
| edge | a learned transition | `counts[i][j]` |
| node creation | first time a state is ever observed as context or target | first `learn()` touching row/col |
| edge creation | `counts[i][j]` crossing zero | delta stream |
| connection growth | `counts[i][j]` increasing | `learn()` weight |
| edge decay / deletion | row multiplied by `decay` on touch; weight falling below a declared epsilon | `CountModel.learn` decay branch |
| activation propagation | the predictive distribution `predict(context)` | per-step model output |
| attention flow | which row is read, and which cell the loss is charged against | `(obs.context, obs.target, loss)` |
| memory | reservoir contents and its churn | `ReplayBuffer.items`, `n_seen` |
| replay / consolidation | gate decision `k` and the selected batch | `gate.replay_count`, `replay.select` |
| cluster formation | block structure of the transition matrix vs task identity | counts + `obs.task` |

This mapping is faithful today at `alphabet = 8` (8 nodes, ≤64 edges) and — critically —
its *shape* is unchanged when the model later becomes a genuinely growing network with
millions of units. The wire format in §4 is therefore a **generic node/edge delta
stream**, not a count-matrix format. When a growth mechanism lands, it emits the same
event kinds and the Observatory renders it with no protocol change.

**Consequence to accept explicitly**: until a growth mechanism exists, the "millions of
neurons" scale target is exercised by synthetic *load* tests of the transport and
renderer (§17.4), never by synthetic *science*. Load fixtures are labelled
`synthetic=true` in the manifest and are refused by the science-facing UI.

### 0.3 What already exists and is reused

| Need | Existing asset | Verdict |
|---|---|---|
| Observation seam | `core.protocols.Logger` (`event(kind, payload)`, `close()`), fan-out via `logs.MultiLogger` which already swallows sink exceptions | **Reuse.** This is I1 by construction. |
| Identity-neutral config | `RunConfig.identity_dict()` drops `name`, `description`, `logging` | **Reuse** — this is exactly I2. |
| Durable per-step data | `ArtifactWriter` → `steps.csv`, `probes.csv`, `run.log`, `manifest.json`, `status.json`, `inventory` | **Reuse as cold storage.** Already hash-verified. |
| Determinism | `core.seeds.SeedSet` (SHA-256 substreams); engine draws no randomness | **Reuse** — makes deterministic playback trivially achievable. |
| Async event bus | `backend/runtime/event_bus.py` | **Reject as spine.** It silently drops events above queue depth 10 000, times handlers out at 5 s, and fires Redis writes as untracked tasks. Silent loss is disqualifying for an instrument. See §3.5. |
| Web transport | `backend/app/streaming.py` (SSE), FastAPI app | **Reuse the FastAPI host**, replace SSE with the WebSocket protocol in §6. |
| Frontend shell | React 18 + Vite + Zustand + React Query + Recharts | **Reuse.** No WebGL library present; §11 adds one. |
| `Metric` protocol | write-only observers, in `config.metrics` | **Reject as seam.** `metrics` *is* part of `identity_dict()`, so registering the Observatory as a metric would change `config_hash` and violate I2. This is a real trap and is the single most important integration finding in this document. |


---

## 1. Overall architecture

Five stages, one direction. No stage may call upstream.

```
┌─────────────────────────────────────────────────────────────────────────┐
│  P1 ENGINE  (experiments/engine/engine.py — unmodified)                  │
│  environment → model → memory → gate → replay → metrics → artifacts     │
└───────────────┬─────────────────────────────────────────────────────────┘
                │ Logger.event(kind, payload)          ← the only inbound seam
                │ ArtifactWriter → steps.csv / run.log ← durable, already hashed
                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  1. TAP            in-process, synchronous, allocation-bounded           │
│     observatory/tap.py    projects engine state → ObsEvent deltas        │
│     observatory/graph.py  count matrix → node/edge deltas               │
│     observatory/ring.py   bounded ring buffer + explicit drop ledger     │
└───────────────┬─────────────────────────────────────────────────────────┘
                │ ObsEvent stream (schema obs/1)
                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  2. STORE          segmented event log + keyframe snapshots             │
│     observatory/store/    cold: run dir;  warm: segments;  hot: ring     │
└───────────────┬─────────────────────────────────────────────────────────┘
                │ query(run_id, from_seq, to_seq) | snapshot_at(t)
                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  3. SERVER         FastAPI: REST for control, WebSocket for streams      │
│     observatory/server/   session, subscription, decimation, auth        │
└───────────────┬─────────────────────────────────────────────────────────┘
                │ binary frames (§6)
                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  4. CLIENT CORE    transport, decode, reducer → GraphState (typed arrays)│
│     frontend/observatory/core/   framework-agnostic, no React            │
└───────────────┬─────────────────────────────────────────────────────────┘
                │ GraphState buffers (SoA)
                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  5. RENDER + UI    WebGL2 instanced renderer; React only for chrome      │
│     frontend/observatory/render/ , frontend/observatory/ui/              │
└─────────────────────────────────────────────────────────────────────────┘
```

Four load-bearing decisions:

1. **The engine never awaits the Observatory.** The tap's per-event work is O(1)
   amortised and bounded; if the ring is full it drops and *records the drop*. The
   engine cannot block on a socket, a disk, or a browser.
2. **Truth lives in the log, not in the UI.** The client is a pure function of the
   event stream. Any client bug is recoverable by replaying the log; no client state
   is authoritative.
3. **Two ingestion tiers.** *Tier A* (MVP, shipped) reads the artifacts the engine
   already writes — zero engine change, therefore zero interference risk, and it
   already covers replay, time-travel, snapshots, and experiment comparison. *Tier B*
   adds live streaming via an in-process tap and needs one identity-neutral patch
   (§15.4). Tier A must remain fully functional forever, because it is the offline
   scientific path and the audit path.
4. **Deterministic playback is free.** Because the engine draws no randomness of its
   own and all seeds derive from `SeedSet`, re-running a `config_hash` reproduces the
   event stream. Playback fidelity is therefore *verifiable*, not asserted (§8.4).

---

## 2. Module decomposition

Python (`observatory/`) — no dependency on `backend/`, and none on `frontend/`:

| Module | Responsibility | Must not |
|---|---|---|
| `schema.py` | Event kinds, `ObsEvent`, delta records, schema version constant | import anything from the engine |
| `codec.py` | Encode/decode: JSONL (canonical, v1) and binary frames (v2) | lose information; both directions must round-trip |
| `ring.py` | Bounded FIFO, monotonic `seq`, drop ledger | block, allocate per event, or raise |
| `graph.py` | Project model state → node/edge deltas; reconstruct state from deltas | mutate the model |
| `tap.py` | `Logger`-shaped sink; owns ring + projector; swallows all its own errors | propagate an exception to the engine |
| `recorder.py` | Tier A: read a run directory → event stream | assume the run has finished |
| `store/segments.py` | Append-only segment files, index, retention | rewrite history |
| `store/snapshots.py` | Keyframe capture, restore, integrity hash | be the only path to a state (deltas must suffice) |
| `server/app.py` | FastAPI wiring, auth, CORS, lifespan | contain protocol logic |
| `server/ws.py` | WebSocket sessions, subscriptions, backpressure, decimation | drop silently |
| `server/rest.py` | Run discovery, metadata, snapshot, export | stream bulk data |
| `plugins/` | Overlay + probe registry (§12) | reach into engine internals |

TypeScript (`frontend/observatory/`):

| Module | Responsibility |
|---|---|
| `core/transport.ts` | WebSocket lifecycle, resume-from-`seq`, heartbeat |
| `core/decode.ts` | Binary/JSON frame → typed events |
| `core/reducer.ts` | Events → `GraphState` (structure-of-arrays, pre-allocated) |
| `core/timeline.ts` | Playback clock, scrub, seek-to-snapshot + replay-forward |
| `render/scene.ts` | WebGL2 context, passes, resize, pick buffer |
| `render/nodes.ts`, `render/edges.ts` | Instanced draw for nodes and edges |
| `render/layout/` | Layout engines (fixed, force, spectral, GPU force) |
| `overlays/` | Scientific overlays, one file per overlay, registered (§12) |
| `ui/` | React chrome: inspector, timeline, run picker, diff view |

Dependency rule, enforced in CI by an import-lint test: `render` may not import `ui`;
`core` may not import `render` or `ui`; `overlays` may import `core` types only.

---

## 3. Event system

### 3.1 Kinds

Closed set. Adding a kind bumps the schema minor version; changing a payload bumps
major. Kinds mirror the engine's real transitions — nothing is invented.

| Kind | Emitted at | Payload (essential fields) |
|---|---|---|
| `run_start` | engine `run_start` | `run_id`, `config_hash`, `total_steps`, seeds, component names |
| `topology_init` | first state projection | `n_nodes`, `alphabet`, initial nonzero edges |
| `step` | per engine step | `t`, `task`, `loss`, `context`, `target`, `replays`, `gate_fired`, `buffer_size` |
| `node_add` / `node_remove` | node first seen / retired | `id`, `t` |
| `edge_add` | `counts[i][j]` crosses 0 | `src`, `dst`, `w`, `t` |
| `edge_update` | weight changed | `src`, `dst`, `w`, `dw`, `t` |
| `edge_remove` | weight ≤ ε | `src`, `dst`, `t` |
| `activation` | prediction emitted | `context`, `dist` (or top-k), `t` |
| `replay_batch` | gate fired | `k`, `selected`, `shortfall`, `t` |
| `memory_admit` / `memory_evict` | reservoir accept/replace | `slot`, `item`, `t` |
| `probe` | engine `probe` | `block`, `t`, `trained_task`, `losses`, `oracle` |
| `metric_sample` | decimated aggregate | `t`, `name`, `value` |
| `snapshot` | keyframe written | `t`, `snapshot_id`, `hash` |
| `truncated` / `error` / `run_end` | engine lifecycle | as engine emits |
| `stream_meta` | transport bookkeeping | `dropped`, `first_dropped_seq`, `decimation` |

`stream_meta` is not optional. It is how the instrument reports its own measurement
limits — an instrument that hides its dropouts is lying.

### 3.2 Envelope

```
ObsEvent = {
  v:    "obs/1",     # schema version
  seq:  uint64,      # per-run monotonic, gapless unless a drop is reported
  t:    int | null,  # engine step index; null for lifecycle events
  kind: str,
  wall: float,       # monotonic seconds since run_start, for latency only
  p:    {...}        # payload
}
```

`seq` is assigned by the tap, not the clock. Ordering is by `seq`; `wall` is never used
for ordering or for reconstruction, because it is not reproducible.

### 3.3 Delivery guarantees

- **Cold path (Tier A, artifacts)**: lossless. Everything on disk survives.
- **Warm path (segments)**: lossless up to the retention policy in §9.
- **Hot path (live socket)**: lossy *by declaration*. Drops are counted, attributed to a
  `seq` range, and surfaced in the UI as a visible gap marker. Never silent.
- Ordering: total per run, by `seq`.
- Idempotence: replaying a `seq` range is safe; the reducer is a fold over `seq`.

### 3.4 Backpressure

Three levers, applied in this fixed order, each recorded in `stream_meta`:

1. **Decimate** high-frequency kinds (`step`, `activation`, `edge_update`) by stride or
   by aggregate window. Structural kinds (`node_*`, `edge_add`, `edge_remove`, `probe`,
   lifecycle) are **never** decimated — losing a topology change desynchronises the
   client, losing a sample does not.
2. **Coalesce** `edge_update` per `(src,dst)` within a frame window into one absolute
   weight. Safe because updates carry absolute `w`.
3. **Drop** oldest, with the ledger.

### 3.5 Why not `backend/runtime/event_bus.py`

It drops on queue depth without accounting, bounds handlers at 5 s, and dispatches
persistence through `asyncio.create_task` without tracking completion. For an
application event bus those are reasonable; for a scientific instrument each one is an
undetectable data-loss path. The Observatory keeps its own transport and does not
depend on it.


---

## 4. Data model

### 4.1 Server-side (authoritative)

```
Run        run_id, config_hash, name, seeds, status, total_steps,
           component_names, started_at, finished_at, synthetic: bool
Segment    run_id, index, seq_lo, seq_hi, t_lo, t_hi, path, sha256, n_events
Snapshot   run_id, snapshot_id, t, seq, kind: keyframe|manual, sha256, path
GraphNode  id: uint32, born_t, died_t|null, label, kind
GraphEdge  src: uint32, dst: uint32, w: float32, born_t, died_t|null
Series     run_id, name, (t, value)[]           # decimated scalars
```

Node identity is a stable `uint32`, assigned once and never reused within a run.
Reuse would corrupt time-travel: a scrub backwards would resurrect the wrong entity.

### 4.2 Client-side `GraphState` — structure of arrays

Object-per-node dies at 10⁵. The client keeps pre-allocated typed arrays sized to a
capacity, grown by doubling:

```
nodes:  { id: Uint32Array, x/y/z: Float32Array, activation: Float32Array,
          flags: Uint8Array, count: number, capacity: number }
edges:  { src: Uint32Array, dst: Uint32Array, w: Float32Array,
          flags: Uint8Array, count, capacity }
index:  Map<nodeId, slot>          // only structural ops touch this
dirty:  { nodeRanges: [], edgeRanges: [] }   // sub-buffer upload ranges
```

These arrays are the GPU upload source. The reducer writes into them in place; a frame
uploads only dirty ranges. There is no per-frame allocation and no garbage churn.

### 4.3 Invariants

- An `edge_update` for an unknown edge is a **protocol error**, not an implicit insert.
  It means a structural event was lost, and the client must resynchronise from a
  snapshot rather than silently diverge.
- Weights are absolute in every event. Deltas (`dw`) are advisory for animation only.
  This is what makes coalescing and lossy hot paths safe.
- Reconstruction is exact: folding all events from `t=0` to `t=T` yields the model state
  at `T` bit-for-bit. Verified by test (§17.2).

---

## 5. Rendering pipeline

Per frame, fixed order:

```
1. ingest      drain decoded events (budgeted: N events or M ms, whichever first)
2. reduce      apply to GraphState; mark dirty ranges
3. layout      advance layout engine one tick (may be GPU; may be a no-op)
4. upload      glBufferSubData for dirty ranges only
5. draw        edges pass → nodes pass → overlays pass → pick pass (on demand)
6. present     HUD: t, seq, fps, dropped, decimation, provenance of hover target
```

Rules:

- **Ingest is budgeted.** A burst of a million events must not stall the frame; the
  remainder is drained next frame. The HUD shows ingest lag in events and in steps.
- **Layout is separable and declared.** Positions are *not* engine state. Every layout
  engine is named in the HUD and in exported figures, because a force layout is an
  interpretation and must be attributable.
- **No implicit animation.** Interpolation between two real states is allowed only when
  labelled; there is no easing that invents intermediate values by default.
- Visual encodings are declared, unit-bearing, and legended: edge width ↔ weight
  (log scale by default, stated), node size ↔ degree or activation (selectable),
  colour ↔ task attribution or age (categorical palettes are colour-blind safe).

Overlay passes read `GraphState` and may not write it.

---

## 6. WebSocket protocol

`GET /obs/v1/stream` — upgrade. Subprotocol token `obs.v1`.

### 6.1 Handshake

Client sends `hello`, server replies `welcome`, then the client subscribes:

```jsonc
// → hello
{ "op":"hello", "client":"obs-web/0.1.0", "accept":["binary/v2","json/v1"] }
// ← welcome
{ "op":"welcome", "schema":"obs/1", "encoding":"binary/v2",
  "server_time":..., "limits":{"max_subs":8,"max_rate_hz":60} }
// → subscribe
{ "op":"subscribe", "run_id":"...", "from_seq":0,
  "kinds":["step","edge_update","node_add","probe"],
  "mode":"live",                       // live | replay | tail
  "decimation":{"step":10},
  "rate_hz":30, "roi":{"nodes":[...]} }  // roi optional: server-side filter
// ← subscribed
{ "op":"subscribed", "sub_id":1, "resume_seq":0, "snapshot_id":"..." }
```

### 6.2 Frames

Binary frame (`binary/v2`), little-endian:

```
magic  u32  0x4F425331 ("OBS1")
flags  u16  bit0 zstd-compressed payload
kind   u16  event kind id (from the closed registry)
seq    u64
t      i64  (-1 = null)
len    u32
body   len bytes  (packed struct per kind; no field names on the wire)
```

Bulk kinds get array-of-struct bodies so one frame carries many records:
`edge_update` body is `[count:u32][ (src:u32, dst:u32, w:f32) × count ]`. This is the
difference between 60 fps and 6 at 10⁶ edges.

`json/v1` is the same events as JSON objects. It is mandatory to keep: it is what makes
the protocol debuggable, scriptable from Python, and inspectable in DevTools.

### 6.3 Control ops

`subscribe`, `unsubscribe`, `seek {t|seq}`, `set_rate`, `set_decimation`, `pause`,
`resume`, `ping`. Server → client: `subscribed`, `event`, `batch`, `gap`, `error`,
`pong`, `run_end`.

`gap` is explicit: `{ "op":"gap", "sub_id":1, "from_seq":X, "to_seq":Y, "reason":"drop|decimation" }`.
The client renders a visible discontinuity marker. This is a first-class UI element.

### 6.4 Resume

Every client tracks its last applied `seq`. On reconnect it re-subscribes with
`from_seq`. If the server can no longer serve that `seq` (retention), it responds with
the nearest snapshot at or before it, and the client restores then replays forward.
Resume is therefore always possible, at worst from `t=0`.

---

## 7. Snapshot architecture

A snapshot is a **complete, self-describing state at one `(run_id, t, seq)`** — the
keyframe that bounds delta replay cost.

```
Snapshot {
  meta:  { run_id, config_hash, schema, t, seq, created_at, kind, synthetic }
  model: { alphabet, alpha, decay, n_updates, counts }   # from model.state_dict()
  graph: { nodes[], edges[] }                            # derived, redundant, cheap
  memory:{ capacity, n_seen, items[] }                   # reservoir contents
  gate:  { n_fired, n_replays, params }
  metrics_partial: {...}
  sha256: hex                                            # over canonical bytes
}
```

Design points:

- **Derivable, never privileged.** Any snapshot must be reproducible by folding the
  event stream. A snapshot that disagrees with the fold is a bug, and §17.2 tests for
  exactly that. This keeps the delta stream the single source of truth.
- **Read-only capture.** `CountModel.state_dict()` already returns copied rows, so
  capture cannot alias engine state. Capture at a step boundary only.
- **Cadence**: every `snapshot_interval` steps (default: every probe checkpoint, which
  the engine already computes), plus on manual request, plus at `run_end`. Probe
  checkpoints are the natural keyframes because they are the scientifically meaningful
  boundaries.
- **Restoration is an Observatory-side operation.** It rebuilds *the view*. Injecting a
  snapshot back into a live engine is explicitly out of scope: it would make the
  Observatory a participant and break I1. Resuming an engine from a snapshot is an
  engine feature to be designed separately, under the engine's own governance.

---

## 8. Time-travel system

### 8.1 Model

The timeline is indexed by engine step `t`, not wall time. `t` is discrete, totally
ordered, and reproducible — the only sound axis for a scientific instrument.

### 8.2 Seek

`seek(T)` = load nearest snapshot with `t ≤ T`, then fold events `(snapshot.seq, T]`.
Cost is bounded by `snapshot_interval`, not by run length. Backwards seek uses the same
path (restore + fold forward); there is no inverse-delta application, because inverse
application of a decayed float is not exact and would silently diverge.

### 8.3 Modes

| Mode | Behaviour |
|---|---|
| `live` | follow head; drops permitted, reported |
| `tail` | follow head with a fixed lag, so the window is always gap-free |
| `replay` | detached; client drives the clock, arbitrary rate, step/frame stepping |
| `compare` | N runs on one clock, aligned by `t`; per-run panes or overlay diff |

### 8.4 Determinism guarantee

Playback is deterministic in a strong sense: for a given `run_id`, the fold from any
snapshot to any `T` yields identical state, and re-executing the same `config_hash`
regenerates the same stream. Both are asserted by tests. The determinism claim rests on
the engine's own property (documented in `engine.py`: "the engine itself draws no random
numbers"), which the Observatory inherits rather than reinvents.

### 8.5 Comparison

Experiment comparison aligns runs by `t` and by *block index* (blocks come from
`environment.checkpoints()`). Alignment by `t` alone is wrong when two configs have
different `steps_per_task`; the UI must state which alignment is active. Diff surfaces:
per-step loss, probe matrices, edge-weight deltas over the union of node sets, and
gate-firing patterns.


---

## 9. Storage strategy

Three tiers, chosen because their access patterns differ by orders of magnitude:

| Tier | Medium | Holds | Retention |
|---|---|---|---|
| **Hot** | in-process ring (`ring.py`) | last `N` events (default 65 536) | evicted, counted |
| **Warm** | segment files under `artifacts/observatory/<run_id>/` | full event log, chunked | policy below |
| **Cold** | the engine's own run dir (`steps.csv`, `probes.csv`, `run.log`, `manifest.json`) | canonical scientific record | permanent, hash-verified |

Segment layout:

```
artifacts/observatory/<run_id>/
  index.json                 # segments, snapshots, seq/t ranges, hashes
  seg-000000.obs.zst         # append-only event frames
  seg-000001.obs.zst
  snap-000000.json.zst       # keyframes
  manifest.json              # schema version, engine config_hash, provenance
```

Decisions:

- **Append-only, never rewritten.** History is evidence. Compaction produces *new*
  derived files and leaves originals intact.
- **Sealed segments are hashed** and listed in `index.json`, matching the pattern
  `ArtifactWriter.write_inventory` already uses, so `p1 verify`-style integrity checking
  extends naturally to Observatory data.
- **Cold tier is authoritative for science.** The Observatory log is a *derived*
  convenience; deleting it must never destroy a scientific result. This is what makes
  aggressive retention safe.
- Retention default: full fidelity for the most recent K runs; older runs keep
  structural events + snapshots + decimated series, discarding raw `activation`/`step`
  bodies. Policy is declared per run in `manifest.json`, never implicit.
- No database in the MVP. Files plus an index give reproducibility, trivial archiving,
  and content addressing. Postgres/DuckDB is introduced only for cross-run query at the
  scale where scanning indexes stops being adequate (§18, Stage 4).

---

## 10. Performance strategy

Budgets are contractual. Each is a test, not an aspiration (§17.4).

| Boundary | Budget |
|---|---|
| Tap per engine step | ≤ 2 µs typical, allocation-free steady state |
| Tap total run overhead (I1 corollary) | ≤ 2 % wall clock at default decimation |
| Server fan-out | ≤ 5 ms per frame per client at 10⁴ events/frame |
| Client ingest+reduce | ≤ 4 ms/frame |
| Client draw | ≤ 8 ms/frame at 10⁶ edges |
| End-to-end live latency | ≤ 150 ms p95 |

Techniques, in order of leverage:

1. **Decimation at the source.** The engine runs ~10⁴–10⁶ steps; nobody can see 10⁶
   frames. Default `step` stride is chosen so emitted rate ≈ 60 Hz, and the stride is
   reported in `stream_meta` so a reader knows the sampling.
2. **Coalescing.** One absolute weight per `(src,dst)` per frame window.
3. **Batching.** Array-of-struct bodies; one frame per kind per window, not one frame
   per event. Order-of-magnitude effect on socket and decode cost.
4. **Zero-copy client.** Decode straight into the typed arrays that back GPU buffers.
5. **Dirty-range uploads.** Never re-upload a whole buffer for a few changed edges.
6. **Level of detail.** Above a node threshold, render aggregated communities and expand
   on zoom; edges below a weight percentile collapse into a density field. LOD state is
   shown in the HUD — a hidden LOD is a lie about what is on screen.
7. **Off-main-thread.** Decode + reduce in a Worker; `SharedArrayBuffer` where
   available, structured-clone transfer otherwise.

The explicit warning already in `experiments/engine/logs.py` — that routing per-step
records through the logger would dominate runtime — is honoured: the tap writes to a
ring in memory and never formats JSON on the engine thread. Serialisation happens on the
server/flush side.

---

## 11. GPU rendering approach

**WebGL2** is the baseline (universal today); **WebGPU** is an alternate backend behind
the same `Renderer` interface, adopted when compute shaders buy enough to justify the
support matrix.

- **Nodes**: one instanced quad draw. Per-instance `position`, `size`, `colorIndex`,
  `flags`. Signed-distance-field circle in the fragment shader; crisp at any zoom, one
  draw call for the whole graph.
- **Edges**: instanced line quads (not `GL_LINES` — width and antialiasing matter for
  reading weight). Per-instance endpoint *indices*, with positions fetched from a node
  position texture, so a layout tick updates one texture rather than every edge vertex.
- **Layout on GPU**: force-directed integration as a fragment/compute pass over the
  position texture, with a Barnes–Hut or grid-binned approximation for repulsion.
  Positions never round-trip to the CPU except for picking and export.
- **Picking**: separate integer pick pass rendering `nodeId` into a framebuffer; read one
  pixel on click. Exact, and independent of overdraw.
- **Overlays** compose as additional passes with declared blend modes: activation heat,
  attention flux (animated only along real replay/propagation events), task attribution,
  age, weight-percentile contours.
- Determinism note: GPU float order is not bit-reproducible across vendors. Therefore
  **no scientific quantity is ever computed on the GPU.** The GPU draws; it does not
  measure. Any number reported to the user is computed on the CPU from event data.

---

## 12. Plugin system

Follows the pattern already proven in this repository: an explicit registry plus a
single import site (`core/registry.py`, `experiments/engine/plugins.py`). No filesystem
scanning and no entry-point discovery, for the reason the engine already documents — a
run must be explainable from the source tree alone.

Four extension points:

| Point | Contract (essential) | Side |
|---|---|---|
| **Projector** | `project(state) -> Iterable[ObsEvent]` — engine state → events | Python |
| **Overlay** | `{ id, name, requires: kinds[], draw(gl, state, params) }` | TS |
| **Analyzer** | `on_event(e)`, `result() -> dict` — derived series, read-only | Python |
| **Exporter** | `export(run_id, range, opts) -> bytes` | Python |

Rules:

- A plugin **may not** import engine internals, hold a reference to the model, or write
  to `GraphState`. Enforced by review and by an import-lint test.
- Every plugin declares `requires: [kinds]`. If a subscription decimates a required
  kind, the overlay is disabled with a visible reason rather than rendering a
  misleading partial picture.
- Plugins are versioned and recorded in the export manifest, so a figure names the code
  that drew it.

---

## 13. API specification

Base `/obs/v1`. All responses JSON unless noted.

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | liveness, schema version, build |
| `GET` | `/runs` | list runs; filter by `name`, `config_hash`, `status`, `since` |
| `GET` | `/runs/{run_id}` | run metadata, seeds, components, segment/snapshot index |
| `GET` | `/runs/{run_id}/events` | paged event query: `from_seq`, `to_seq`, `kinds`, `limit` |
| `GET` | `/runs/{run_id}/steps` | decimated step series: `from_t`, `to_t`, `stride`, `fields` |
| `GET` | `/runs/{run_id}/probes` | probe matrix |
| `GET` | `/runs/{run_id}/graph?t=` | materialised graph at `t` (snapshot + fold) |
| `GET` | `/runs/{run_id}/snapshots` | list keyframes |
| `POST` | `/runs/{run_id}/snapshots` | request a keyframe (server-side, from the log) |
| `GET` | `/runs/{run_id}/snapshots/{id}` | fetch snapshot (JSON or `.zst`) |
| `POST` | `/compare` | `{run_ids[], align:"t"|"block", fields[]}` → aligned series |
| `GET` | `/runs/{run_id}/export` | `format=csv|jsonl|png|svg`, with provenance manifest |
| `GET` | `/plugins` | registered projectors, overlays, analyzers, versions |
| `WS` | `/stream` | §6 |

Conventions: cursor pagination on `seq`; every payload carries
`{ schema, run_id, generated_at, provenance }`; `ETag` from content hash on immutable
resources. There are no mutating endpoints that touch a run's scientific data — the
Observatory API is read-only with respect to science, and `POST /snapshots` only derives
new views from the existing log.

---

## 14. Frontend architecture

```
frontend/observatory/
  core/      transport, decode, reducer, timeline, selectors   (no React, no WebGL)
  render/    scene, nodes, edges, layout/, picking             (no React)
  overlays/  one module per overlay, registered
  ui/        React: <Observatory/>, Inspector, Timeline, RunPicker, DiffView, HUD
  state/     Zustand store — view state only, never graph data
```

- **Graph data never enters React state.** React re-renders on view state (selection,
  mode, which overlays); the graph lives in typed arrays owned by `core`, mutated in
  place, read by `render`. Putting 10⁶ edges in a store is the standard way this class
  of app dies.
- **The canvas is uncontrolled.** One `<canvas>` with an imperative renderer; React
  manages only its lifecycle and size.
- **Inspector is provenance-first.** Selecting any node, edge, or timeline point shows
  `run_id`, `t`, `seq`, the raw payload that produced the value, and the transform
  applied to render it. This is the primary debugging surface and the direct expression
  of I3.
- **HUD always shows measurement conditions**: `t`, `seq`, fps, ingest lag, dropped
  count, decimation strides, active layout, active LOD. Never hidden, because these are
  the instrument's error bars.
- Reuse: Zustand and React Query are already dependencies. Recharts serves scalar
  panels. Add exactly one rendering dependency (`regl` or raw WebGL2 + a small helper);
  avoid a heavyweight graph framework, since none of them handle 10⁶ edges with
  deterministic provenance.
- Accessibility: full keyboard navigation of the timeline and selection, ARIA-labelled
  controls, colour-blind-safe categorical palettes, a non-colour redundant encoding for
  every categorical channel, and a text/table view of any rendered figure — which also
  makes the instrument scriptable and screen-readable.


---

## 15. Backend architecture

### 15.1 Processes

```
[ engine process ]  p1 run ...            → tap → ring → flusher thread → segments
[ obs server    ]  uvicorn observatory.server.app:app   (separate process)
[ browser       ]  static Vite bundle
```

The server is a **separate process** from the engine. A crashed or wedged server must not
be able to affect a multi-hour scientific run — that is I1 at the process level. The two
communicate only through the filesystem (segments + run dirs) in Tier A/B, with an
optional local socket for lowest-latency live mode later.

### 15.2 Flusher

A single daemon thread drains the ring to the current segment. It is the only component
that serialises or touches disk on the engine's behalf. If it dies, the ring simply fills
and drops with accounting; the engine continues. If the queue is full at process exit,
`close()` performs a bounded final drain and records any shortfall.

### 15.3 Server internals

- `SessionManager` — one object per WebSocket; owns cursor, subscriptions, rate limiter.
- `RunIndex` — watches `artifacts/` for new/updated runs; caches parsed indexes.
- `EventSource` — unified read over hot/warm/cold; a subscription is a cursor over it.
- `SnapshotService` — materialise state at `t` (nearest keyframe + fold), cache by `(run_id, t)`.
- `Decimator` — per-subscription strides and coalescing windows.

### 15.4 The one engine-side patch (Tier B, proposed — not applied)

Live streaming needs the tap attached and fed per-step. Proposed minimal change,
identity-neutral by construction:

1. `LoggingConfig` gains `observatory: bool = False` and `observatory_stride: int = 1`.
   `logging` is already excluded from `identity_dict()`, so `config_hash` is untouched — I2 holds.
2. `_build_logger` appends `ObservatoryTap(...)` to the sink list when enabled.
   `MultiLogger` already isolates sink exceptions — I1 holds for lifecycle events.
3. `_execute` gains two calls guarded by a null-object default:
   `logger.on_step(rec)` after the existing `writer.write_step(rec)`, and
   `logger.on_state(model)` at probe checkpoints only. Default implementation on
   `NullLogger`/`MultiLogger` is `return None`, so the disabled cost is one method call.

This is a change to files under active governance (`experiments/engine/`), so it is
specified here and left **unapplied** pending review. Everything in the MVP below works
without it.

---

## 16. Security model

The Observatory streams the full internal state of a research system and reads from the
artifact tree. Treat it as sensitive by default.

**Current state, stated plainly**: the existing `backend/app/main.py` FastAPI app has no
authentication on any route. The Observatory server must not repeat that. Because the
MVP is local-only, the enforced default is:

- **Bind to `127.0.0.1` only.** Non-loopback binding requires an explicit
  `OBS_ALLOW_REMOTE=1` *and* a configured auth backend; the server refuses to start with
  a remote bind and no auth, rather than starting insecurely.
- **Origin pinning + CSRF** on the WebSocket upgrade (`Origin` allowlist), since
  browsers do not apply same-origin policy to WebSockets.
- Auth ladder as deployment widens: loopback-only → signed local token → OIDC/reverse
  proxy with roles.
- **Roles**: `viewer` (read streams), `analyst` (+ export, snapshots), `admin` (retention,
  config). No role can write engine data — the API has no such capability at all.
- **Path confinement**: run ids are validated against a strict pattern and resolved
  under a configured artifact root; no user-supplied path reaches the filesystem.
  Directory traversal is the obvious attack surface for a run-file server.
- **Resource limits**: max subscriptions, max rate, max query span, decode size caps,
  per-connection memory ceiling — a client must not be able to OOM the server.
- **Secrets**: none in event payloads. Payloads are numeric engine state; the manifest
  carries config, which must not contain credentials. `.env` and key material are never
  read by the Observatory.
- **Untrusted input**: event files are parsed defensively (bounded lengths, checked
  magic, no `pickle`, no `eval`, JSON/struct only). Plugin code is trusted code and
  ships in-repo; there is no dynamic plugin download.
- **Audit**: exports record who exported what range when, for figure provenance.

---

## 17. Testing strategy

The three invariants are the test plan.

### 17.1 Non-interference (I1) — the highest-value tests
- **Differential run**: execute the same config with the Observatory absent, attached,
  and attached-with-a-failing-sink. Assert identical loss sequences, identical probe
  matrices, and identical final `model.state_dict()`.
- **Fault injection**: a tap that raises on every call must not fail the run.
- **Read-only projection**: projecting state must leave `state_dict()` equal.
- **Overhead budget**: measured wall-clock delta within the §10 budget.

### 17.2 Fidelity (I3)
- **Fold equals truth**: folding the event stream from `t=0` reconstructs the model state
  at every step, bit-for-bit.
- **Snapshot agreement**: snapshot at `t` equals the fold to `t`.
- **Codec round-trip**: `decode(encode(e)) == e` for every kind, including boundary
  floats (0, ±inf, NaN, denormals) — property-based via Hypothesis, already a repo
  dependency.
- **Drop accounting**: forced overflow reports an exact dropped count and the correct
  first dropped `seq`.
- **Gap propagation**: a decimated or dropped range surfaces as a `gap` op and a visible
  client marker.

### 17.3 Determinism
- Same `config_hash` re-run ⇒ identical event stream (modulo `wall`).
- Seek to `T` by any snapshot path ⇒ identical state.

### 17.4 Performance / scale
- Synthetic load fixtures at 10⁴ / 10⁵ / 10⁶ nodes and edges, asserting the §10 budgets.
- Fixtures are marked `synthetic=true` and rejected by science-facing views.

### 17.5 Structure
- Import-lint: `core` ⊅ `render`/`ui`; `observatory` ⊅ `backend`; plugins ⊅ engine internals.
- Schema-compat: a stored `obs/1` fixture must still decode after any change.

Client: unit tests on reducer/timeline (Vitest), golden-image tests on the renderer with
tolerance, Playwright for scrub/select/compare flows.

---

## 18. Scalability roadmap

| Stage | Scale | What changes |
|---|---|---|
| **1. Local instrument** | ≤ 10³ nodes, one run, one viewer | files + ring; CPU layout; JSON codec adequate |
| **2. Live lab** | ≤ 10⁵ nodes, concurrent runs, few viewers | binary codec, segments + snapshots, Worker decode, instanced GPU draw, LOD |
| **3. Cluster** | many concurrent runs, remote viewers | server reads a shared artifact store (S3/NFS); auth; per-run shards; server-side ROI filtering |
| **4. Population science** | 10⁶ nodes, 10³ runs, cross-run analytics | GPU layout + compute picking; columnar store (DuckDB/Parquet) for cross-run query; pre-aggregated community graphs; streaming edge-density fields instead of individual edges |
| **5. Longevity** | multi-year | schema migrations with fixtures for every historical version; cold-archive format frozen and documented; the cold tier remains readable with nothing but Python stdlib |

Scale-out order is deliberate: transport and storage before rendering, rendering before
analytics. Rendering 10⁶ edges is a solved problem; reconstructing a lost event is not.

---

## 19. Implementation roadmap

**M0 — Spine (this change set).** `observatory/` package: schema, codec, ring, graph
projection, tap, Tier A recorder. Tests for I1, fold-fidelity, round-trip, drop
accounting. No server, no UI. Deliverable: *provably non-interfering, provably faithful
event stream.*

**M1 — Offline Observatory.** Segment writer + snapshots; FastAPI read-only REST over
existing run dirs; minimal React view: timeline scrub, transition-graph render (Canvas2D
is sufficient at 8–64 edges), inspector with full provenance. Deliverable: *any past run
is fully inspectable.* No engine change needed.

**M2 — Live streaming.** WebSocket protocol, decimation, gap reporting, resume. Requires
the §15.4 patch to be reviewed and approved. Deliverable: *watch a run as it happens,
with honest dropout reporting.*

**M3 — Scientific overlays + comparison.** Overlay and analyzer plugin points; probe
matrix / retention / forgetting views built on `science/metrics/`; multi-run compare with
`t`/block alignment; export with provenance manifest. Deliverable: *the Observatory
becomes the primary analysis surface.*

**M4 — GPU renderer.** WebGL2 instanced nodes/edges, position texture, GPU layout,
pick pass, LOD. Driven by synthetic load fixtures, not by hope. Deliverable: *10⁶ edges
at 60 fps.*

**M5 — Growth-native.** When the engine gains a structural-plasticity mechanism, wire its
real `node_add`/`node_remove`/`edge_add`/`edge_remove` events. The protocol already
carries them; this milestone is mostly deletion of the count-matrix projector's
special-casing. Deliverable: *the neuron-level views the brief asks for, backed by real
neurons.*

**M6 — Hardening.** Auth ladder, retention automation, schema-migration fixtures,
cross-run columnar store.

Sequencing rationale: M0–M1 deliver scientific value with zero risk to the engine. Live
streaming (M2) is deferred behind a governance review because it is the only part that
touches engine files. GPU work (M4) is deferred until there is enough state to justify
it — at `alphabet = 8`, a GPU renderer would be theatre.

---

## 20. Capability coverage

Every capability in the brief, mapped to real state. "Real now" = backed by state that
exists in the active engine today.

| Capability | Real now | Source | Milestone |
|---|---|---|---|
| live neurons | ✅ as states | `counts` row/col index | M2 |
| live edges | ✅ | `counts[i][j]` | M2 |
| neuron creation | ⚠️ first-observation only | first touch of a state | M2 → real in M5 |
| neuron deletion | ❌ no mechanism exists | — | M5 |
| connection growth | ✅ | `learn()` increments | M1 |
| replay visualization | ✅ | `gate.replay_count`, `replay.select` | M2 |
| memory visualization | ✅ | `ReplayBuffer.items`, `n_seen` | M1 |
| attention flow | ✅ as read/charge pattern | `(context, target, loss)` | M2 |
| activation propagation | ✅ | `model.predict` distribution | M2 |
| cluster formation | ✅ | count-matrix block structure vs `task` | M3 |
| experiment comparison | ✅ | multiple run dirs | M3 |
| timeline replay | ✅ | `steps.csv` + segments | M1 |
| snapshot restoration | ✅ view-side | `state_dict()` keyframes | M1 |
| event streaming | ✅ | tap → WS | M2 |
| deterministic playback | ✅ | `SeedSet` + fold | M1 |
| scientific overlays | ✅ | `science/metrics/` | M3 |
| debugging tools | ✅ | inspector + HUD + gap markers | M1 |

Two honest gaps: **neuron deletion has no mechanism to observe**, and **neuron creation is
currently only "first observation of a pre-existing state"**, not allocation of new
capacity. Both are engine features, not Observatory features. The Observatory will not
simulate them.

---

## 21. Open decisions for review

1. Approve or reject the §15.4 engine patch. Everything through M1 proceeds either way;
   M2 is blocked without it.
2. Confirm the substrate mapping in §0.2 is the accepted interpretation of "neurons"
   until a growth mechanism exists.
3. Register this document in `GOVERNANCE_REGISTRY.yaml`, or explicitly declare the
   Observatory non-normative infrastructure outside the registry.
4. Confirm the cold tier (engine run dirs) remains the sole scientific record of truth,
   with Observatory segments classified as derived data.
