"""Observatory invariant tests.

These tests are the reason the Observatory is allowed to exist next to a scientific
engine. Each maps to a numbered invariant in
`docs/architecture/OBSERVATORY_ARCHITECTURE.md`:

    I1  Non-interference    observing cannot change a reported number
    I2  Identity neutrality enabling it cannot change `config_hash` / `run_id`
    I3  Provenance/fidelity the event stream reconstructs real state exactly

The differential tests (I1) are the highest-value tests in the suite: they are what
keeps a future contributor from "just reading the model" inside the tap.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pytest

from observatory import codec
from observatory.graph import GraphProjector, GraphView
from observatory.recorder import RunReader, discover_runs
from observatory.ring import EventRing
from observatory.schema import KINDS, SCHEMA, ObsEvent, SchemaError, events_equal
from observatory.tap import ObservatoryTap

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

ALPHABET = 6


def _build_rig(seed: int):
    """A frozen-rig mechanism set. Rebuilt identically for every differential run."""
    from p1v0.gate import SurpriseGate
    from p1v0.memory import ReplayBuffer
    from p1v0.model import CountModel
    from p1v0.stream import TaskStream

    stream = TaskStream(n_tasks=2, alphabet=ALPHABET, steps_per_task=60, seed=seed)
    model = CountModel(alphabet=ALPHABET, alpha=0.5, decay=0.97)
    memory = ReplayBuffer(capacity=32, seed=seed)
    gate = SurpriseGate(threshold=1.2, k=3)
    return stream, model, memory, gate


def _drive(tap: ObservatoryTap | None, seed: int = 3, state_every: int = 20):
    """Run the frozen rig, optionally observed. Returns (losses, final state)."""
    from p1v0.loop import run as loop_run

    stream, model, memory, gate = _build_rig(seed)
    losses: List[float] = []
    for rec in loop_run(stream, model, memory, gate):
        losses.append(rec.loss)
        if tap is not None:
            tap.on_step(rec)
            if rec.t % state_every == 0:
                tap.on_state(model, t=rec.t)
    return losses, model.state_dict()


class _ExplodingRing(EventRing):
    """A sink that fails on every write. Models a broken Observatory."""

    def append(self, event: ObsEvent) -> None:  # noqa: D102
        raise RuntimeError("instrument failure injected by test")


def _engine_config(name: str, logging: Dict[str, Any] | None = None):
    from experiments.engine.config import RunConfig

    raw: Dict[str, Any] = {
        "config_version": 1,
        "name": name,
        "benchmark": {"name": "markov_retention"},
        "environment": {
            "name": "markov_blocks_v0",
            "params": {"n_tasks": 2, "alphabet": ALPHABET, "steps_per_task": 50},
        },
        "model": {"name": "count_model", "params": {"decay": 0.97}},
        "memory": {"name": "reservoir", "params": {"capacity": 64}},
        "gate": {"name": "surprise"},
        "replay": {"name": "buffer_sample"},
        "metrics": ["online_loss"],
        "seeds": {"master": 7},
        "logging": logging or {"console": False, "step_format": "csv", "plots": False},
    }
    return RunConfig.from_dict(raw)


@pytest.fixture(scope="module")
def engine_run(tmp_path_factory) -> Tuple[Path, Any]:
    """One real engine run, executed unmodified. Shared by the Tier A tests."""
    from experiments.engine.engine import run

    root = tmp_path_factory.mktemp("obs_engine")
    config = _engine_config("obs_engine_run")
    result = run(config, root=root, quiet=True)
    assert result.ok, f"fixture run failed: {result.error}"
    return Path(result.run_dir), config


# --------------------------------------------------------------------------- #
# I1 -- non-interference
# --------------------------------------------------------------------------- #


def test_i1_observed_run_is_numerically_identical():
    """Attaching the tap changes no loss and no final model state."""
    baseline_losses, baseline_state = _drive(None)
    observed_losses, observed_state = _drive(ObservatoryTap(run_id="obs"))

    assert observed_losses == baseline_losses
    assert observed_state["counts"] == baseline_state["counts"]
    assert observed_state["n_updates"] == baseline_state["n_updates"]


def test_i1_failing_instrument_does_not_disturb_or_abort_the_run():
    """A tap that raises on every write must be inert, not fatal."""
    baseline_losses, baseline_state = _drive(None)

    tap = ObservatoryTap(run_id="obs")
    tap.ring = _ExplodingRing(capacity=8)
    observed_losses, observed_state = _drive(tap)

    assert observed_losses == baseline_losses
    assert observed_state["counts"] == baseline_state["counts"]
    assert tap.stats()["faults"] > 0, "failures must be counted, not swallowed silently"


def test_i1_public_methods_never_raise():
    """Every entry point tolerates hostile input rather than propagating."""
    tap = ObservatoryTap(run_id="obs")
    tap.event("totally_unknown_kind", {"weird": object()})
    tap.event("run_start", {"run_id": "x"})
    tap.on_step(object())
    tap.on_state(object())
    tap.on_state(None)
    tap.on_activation(None, [])
    tap.close()
    tap.event("run_end", {})  # after close: ignored, not an error


def test_i1_projection_does_not_mutate_model_state():
    """Projection is read-only with respect to the model."""
    from p1v0.model import CountModel

    model = CountModel(alphabet=ALPHABET, alpha=0.5, decay=0.97)
    for i in range(ALPHABET):
        model.learn(i, (i + 1) % ALPHABET)
    before = [row[:] for row in model.counts]

    projector = GraphProjector()
    projector.project(model.state_dict(), t=0)
    projector.project(model.state_dict(), t=1)

    assert model.counts == before


# --------------------------------------------------------------------------- #
# I2 -- identity neutrality
# --------------------------------------------------------------------------- #


def test_i2_logging_changes_do_not_alter_run_identity():
    """Enabling instrumentation via `logging` cannot change `config_hash`/`run_id`.

    This is the mechanism that lets the Observatory attach to the engine at all:
    `RunConfig.identity_dict()` excludes `logging`, so an observed run and an
    unobserved run remain the same run scientifically.
    """
    plain = _engine_config("identity", {"console": False, "step_format": "csv", "plots": False})
    instrumented = _engine_config(
        "identity", {"console": True, "step_format": "jsonl", "plots": False, "level": "debug"}
    )

    assert plain.config_hash == instrumented.config_hash
    assert plain.run_id == instrumented.run_id
    assert "logging" not in plain.identity_dict()


def test_i2_metrics_are_not_a_valid_attachment_point():
    """Guards the architecture finding: `metrics` IS part of run identity.

    If a future contributor registers the Observatory as a `Metric`, run identity
    changes and observed runs stop being comparable to unobserved ones. This test
    documents and pins that fact.
    """
    from experiments.engine.config import RunConfig

    base = _engine_config("identity").as_dict()
    extra = dict(base)
    extra["metrics"] = list(base["metrics"]) + ["compute"]

    assert RunConfig.from_dict(base).config_hash != RunConfig.from_dict(extra).config_hash


# --------------------------------------------------------------------------- #
# I3 -- fidelity: schema and codec
# --------------------------------------------------------------------------- #


def test_codec_round_trips_every_kind_including_non_finite_floats():
    tricky = {
        "zero": 0.0,
        "neg_zero": -0.0,
        "nan": float("nan"),
        "inf": float("inf"),
        "ninf": float("-inf"),
        "tiny": 5e-324,
        "big": 1.7976931348623157e308,
        "nested": {"list": [1, 2.5, None, True], "s": "unicode: \u03bb \u2713"},
    }
    for kind in KINDS:
        event = ObsEvent(seq=11, kind=kind, t=7, wall=1.25, p=dict(tricky))
        restored = codec.decode_line(codec.encode_line(event))
        assert events_equal(event, restored), f"round-trip failed for {kind}"
        assert restored.v == SCHEMA


def test_codec_encoding_is_canonical_and_stable():
    """Byte-identical encodings, so segments can be content-hashed."""
    a = ObsEvent(seq=1, kind="step", t=0, p={"b": 2, "a": 1})
    b = ObsEvent(seq=1, kind="step", t=0, p={"a": 1, "b": 2})
    assert codec.encode_line(a) == codec.encode_line(b)


def test_codec_rejects_unknown_kind_and_foreign_schema():
    with pytest.raises(SchemaError):
        ObsEvent(seq=0, kind="not_a_real_kind")
    with pytest.raises(SchemaError):
        codec.from_mapping({"v": "obs/999", "seq": 0, "kind": "step"})
    with pytest.raises(SchemaError):
        codec.from_mapping({"v": SCHEMA, "seq": 0})


def test_codec_non_strict_stream_skips_torn_lines():
    good = codec.encode_line(ObsEvent(seq=0, kind="step", t=0, p={"loss": 1.0}))
    text = good + "\n{ this is a torn line\n"
    assert len(list(codec.decode_stream(text, strict=False))) == 1
    with pytest.raises(SchemaError):
        list(codec.decode_stream(text, strict=True))


# --------------------------------------------------------------------------- #
# I3 -- fidelity: ring drop accounting
# --------------------------------------------------------------------------- #


def test_ring_reports_exact_drop_count_and_first_dropped_seq():
    ring = EventRing(capacity=4)
    for seq in range(10):
        ring.append(ObsEvent(seq=seq, kind="step", t=seq, p={}))

    stats = ring.stats()
    assert len(ring) == 4
    assert stats["accepted"] == 10
    assert stats["dropped"] == 6
    assert stats["first_dropped_seq"] == 0
    assert stats["last_dropped_seq"] == 5
    assert stats["dropped_by_kind"] == {"step": 6}
    assert [e.seq for e in ring.peek()] == [6, 7, 8, 9]


def test_ring_protects_structural_events_from_eviction():
    """Losing a topology change desynchronises a client; losing a sample does not."""
    ring = EventRing(capacity=3)
    ring.append(ObsEvent(seq=0, kind="edge_add", t=0, p={"src": 0, "dst": 1, "w": 1.0}))
    for seq in range(1, 8):
        ring.append(ObsEvent(seq=seq, kind="step", t=seq, p={}))

    kinds = [e.kind for e in ring.peek()]
    assert "edge_add" in kinds, "structural event was evicted"
    assert ring.stats()["dropped_by_kind"] == {"step": 5}


def test_ring_peek_since_seq_supports_resume():
    ring = EventRing(capacity=8)
    for seq in range(5):
        ring.append(ObsEvent(seq=seq, kind="step", t=seq, p={}))
    assert [e.seq for e in ring.peek(since_seq=2)] == [3, 4]


# --------------------------------------------------------------------------- #
# I3 -- fidelity: graph projection reconstructs real state exactly
# --------------------------------------------------------------------------- #


def test_graph_fold_reconstructs_model_state_bit_for_bit():
    """The core fidelity claim: folding deltas equals the engine's own matrix.

    Run with decay < 1 so that every `learn` rescales a whole row -- the hard case,
    because a single observation changes many weights at once.
    """
    from p1v0.model import CountModel

    model = CountModel(alphabet=ALPHABET, alpha=0.5, decay=0.9)
    projector = GraphProjector()
    view = GraphView()

    view.apply_all(projector.project(model.state_dict(), t=0))

    prev = 0
    for t in range(1, 300):
        sym = (prev * 3 + t) % ALPHABET
        model.learn(prev, sym)
        prev = sym
        view.apply_all(projector.project(model.state_dict(), t=t))
        assert view.to_matrix() == model.counts, f"divergence at t={t}"

    assert view.stats()["n_edges"] == sum(1 for row in model.counts for w in row if w > 0)


def test_graph_fold_survives_the_codec():
    """Fidelity must hold through serialisation, not only in memory."""
    from p1v0.model import CountModel

    model = CountModel(alphabet=ALPHABET, alpha=0.5, decay=0.95)
    tap = ObservatoryTap(run_id="fidelity")

    tap.on_state(model, t=0)
    prev = 0
    for t in range(1, 120):
        sym = (prev * 5 + 2) % ALPHABET
        model.learn(prev, sym)
        prev = sym
        tap.on_state(model, t=t)

    text = codec.encode_stream(tap.drain())
    view = GraphView()
    for event in codec.decode_stream(text):
        view.apply_event(event)

    assert tap.stats()["faults"] == 0
    assert view.to_matrix() == model.counts


def test_graph_reports_edge_birth_and_decay_death():
    """Node/edge lifecycle events come from real weight transitions."""
    from p1v0.model import CountModel

    model = CountModel(alphabet=3, alpha=0.5, decay=0.5)
    projector = GraphProjector(epsilon=1e-3)

    kinds = [k for k, _ in projector.project(model.state_dict(), t=0)]
    assert kinds == ["topology_init"]

    born = [d for d in projector.project(_after_learn(model, 0, 1), t=1)]
    assert ("edge_add", {"src": 0, "dst": 1, "w": 1.0, "t": 1}) in born
    assert ("node_add", {"id": 0, "t": 1}) in born
    assert ("node_add", {"id": 1, "t": 1}) in born

    # Repeatedly decay row 0 by learning a different target in the same row until the
    # 0->1 weight falls under epsilon. decay=0.5 halves it each time.
    removed = False
    for t in range(2, 40):
        deltas = projector.project(_after_learn(model, 0, 2), t=t)
        if any(k == "edge_remove" and p["dst"] == 1 for k, p in deltas):
            removed = True
            break
    assert removed, "a decayed-to-nothing edge must be reported as removed"


def _after_learn(model, prev: int, sym: int) -> Dict[str, Any]:
    model.learn(prev, sym)
    return model.state_dict()


def test_graph_update_for_unknown_edge_is_an_error():
    """A silent implicit insert would let the view diverge undetected."""
    view = GraphView()
    view.apply("topology_init", {"n_nodes": 2, "nodes": [], "edges": []})
    with pytest.raises(KeyError):
        view.apply("edge_update", {"src": 0, "dst": 1, "w": 1.0})


# --------------------------------------------------------------------------- #
# I3 -- fidelity: tap sampling policy is declared
# --------------------------------------------------------------------------- #


def test_tap_decimation_is_reported_and_keeps_gate_events():
    """Sampling is allowed; hiding the sampling rate is not."""
    tap = ObservatoryTap(run_id="obs", step_stride=10)
    losses, _ = _drive(tap, state_every=10_000)

    events = tap.drain()
    steps = [e for e in events if e.kind == "step"]
    stats = tap.stats()

    assert stats["step_stride"] == 10
    assert stats["steps_seen"] == len(losses)
    assert len(steps) < len(losses), "stride was not applied"
    # Every retained step is either on-stride or a gate firing -- never arbitrary.
    assert all(e.t % 10 == 0 or e.p["gate_fired"] for e in steps)
    assert all(e.p["gate_fired"] for e in events if e.kind == "replay_batch")


def test_tap_seq_is_monotonic_and_gapless_when_nothing_drops():
    tap = ObservatoryTap(run_id="obs", capacity=1_000_000)
    _drive(tap)
    seqs = [e.seq for e in tap.drain()]
    assert seqs == list(range(len(seqs)))


def test_tap_close_emits_the_ledger_and_flushes(tmp_path: Path):
    sink = tmp_path / "obs" / "stream.jsonl"
    tap = ObservatoryTap(run_id="obs", sink_path=sink)
    _drive(tap)
    tap.close()

    assert sink.is_file()
    events = list(codec.decode_stream(sink.read_text(encoding="utf-8")))
    closing = [e for e in events if e.kind == "stream_meta" and e.p.get("closing")]
    assert len(closing) == 1
    assert closing[0].p["dropped"] == 0
    assert closing[0].p["faults"] == 0


def test_tap_records_unmapped_engine_kinds_rather_than_discarding_them():
    tap = ObservatoryTap(run_id="obs")
    tap.event("step_batch", {"n": 5})
    meta = [e for e in tap.drain() if e.kind == "stream_meta"]
    assert meta and meta[0].p["unmapped_kind"] == "step_batch"
    assert tap.stats()["unmapped_kinds"] == {"step_batch": 1}


# --------------------------------------------------------------------------- #
# Tier A -- reading a real, unmodified engine run
# --------------------------------------------------------------------------- #


def test_tier_a_reader_reconstructs_a_gapless_ordered_stream(engine_run):
    run_dir, _config = engine_run
    reader = RunReader(run_dir)
    events = list(reader.events())

    assert events, "no events reconstructed from a completed run"
    assert [e.seq for e in events] == list(range(len(events))), "seq must be gapless"

    assert events[0].kind == "run_start"
    assert events[-1].kind in ("run_end", "truncated", "error")

    step_ts = [e.t for e in events if e.kind == "step"]
    assert step_ts == sorted(step_ts), "steps must be ordered by engine step index"

    n_rows = sum(1 for _ in reader.steps())
    assert len(step_ts) == n_rows
    assert any(e.kind == "probe" for e in events), "probe checkpoints must survive"


def test_tier_a_reader_exposes_engine_provenance(engine_run):
    run_dir, config = engine_run
    reader = RunReader(run_dir)
    manifest = reader.manifest()

    assert reader.run_id == config.run_id
    assert manifest["config_hash"] == config.config_hash
    assert manifest["seeds"]["mode"] == "independent"
    assert reader.metrics()["online_loss"]["steps"] > 0


def test_tier_a_stream_is_encodable_and_decodable(engine_run):
    run_dir, _config = engine_run
    original = list(RunReader(run_dir).events())
    restored = list(codec.decode_stream(codec.encode_stream(original)))
    assert len(restored) == len(original)
    assert all(events_equal(a, b) for a, b in zip(original, restored))


def test_tier_a_discovers_runs_by_marker_not_by_depth(engine_run):
    run_dir, _config = engine_run
    root = run_dir.parent.parent
    assert run_dir in discover_runs(root)


def test_engine_is_reproducible_which_is_what_playback_relies_on(tmp_path: Path):
    """Deterministic playback is inherited from the engine, so pin the property."""
    from experiments.engine.engine import run

    first = run(_engine_config("repro"), root=tmp_path / "a", quiet=True)
    second = run(_engine_config("repro"), root=tmp_path / "b", quiet=True)

    assert first.ok and second.ok
    assert first.config_hash == second.config_hash

    a = (Path(first.run_dir) / "steps.csv").read_text(encoding="utf-8")
    b = (Path(second.run_dir) / "steps.csv").read_text(encoding="utf-8")
    assert a == b, "identical configs must produce identical step records"

    stream_a = [e.p for e in RunReader(first.run_dir).events() if e.kind == "step"]
    stream_b = [e.p for e in RunReader(second.run_dir).events() if e.kind == "step"]
    assert stream_a == stream_b


# --------------------------------------------------------------------------- #
# Structural rules
# --------------------------------------------------------------------------- #


def test_observatory_does_not_depend_on_the_legacy_backend_or_the_engine():
    """Independence is a design requirement, so it is a test.

    `observatory` must be importable by an archival tool with no P1 engine and no
    legacy `backend/` present. Only the test helpers may import engine packages.
    """
    package = Path(__file__).resolve().parents[2] / "observatory"
    offenders: List[str] = []
    for source in sorted(package.glob("*.py")):
        text = source.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if not (stripped.startswith("import ") or stripped.startswith("from ")):
                continue
            if any(mod in stripped for mod in ("backend", "experiments.", "science.", "p1v0")):
                offenders.append(f"{source.name}:{lineno}: {stripped}")
    assert not offenders, "observatory must not import engine or backend modules:\n" + "\n".join(
        offenders
    )


def test_undroppable_kinds_cover_every_structural_and_lifecycle_kind():
    from observatory.schema import LIFECYCLE, STRUCTURAL, UNDROPPABLE

    for kind in LIFECYCLE + STRUCTURAL:
        assert kind in UNDROPPABLE, f"{kind} must never be droppable"
    assert "step" not in UNDROPPABLE
    assert "activation" not in UNDROPPABLE


def test_kind_ids_are_stable_for_the_binary_codec():
    """Renumbering would make archived segments unreadable."""
    from observatory.schema import ID_KINDS, KIND_IDS

    assert len(KIND_IDS) == len(KINDS)
    assert all(ID_KINDS[KIND_IDS[k]] == k for k in KINDS)
    assert KIND_IDS["run_start"] == 1


def test_architecture_document_exists_and_declares_the_invariants():
    """The design record is part of the deliverable, not optional commentary."""
    doc = (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "architecture"
        / "OBSERVATORY_ARCHITECTURE.md"
    )
    text = doc.read_text(encoding="utf-8")
    for needle in ("Non-interference", "Identity neutrality", "Provenance", SCHEMA):
        assert needle in text, f"architecture document is missing {needle!r}"


def test_json_payloads_never_contain_unserialisable_objects():
    """`jsonable` must degrade to repr rather than letting encoding fail."""
    payload = codec.jsonable({"obj": object(), "ok": 1, 2: "int key"})
    json.dumps(payload)
    assert payload["ok"] == 1
    assert "object" in payload["obj"]
    assert "2" in payload


def test_values_equal_handles_nan_and_nesting():
    from observatory.schema import values_equal

    assert values_equal(float("nan"), float("nan"))
    assert values_equal({"a": [1, float("nan")]}, {"a": [1, float("nan")]})
    assert not values_equal({"a": 1}, {"a": 1, "b": 2})
    assert not math.isnan(0.0)
