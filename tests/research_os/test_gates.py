"""Quality gates, projections and indicators."""

from __future__ import annotations

from pathlib import Path

import pytest

from ros.gates import GATE_BY_NAME, GATES, run_gates
from ros.governance import load_registration
from ros.kpi import compute, failing
from ros.projections import drift, render_laboratory_state
from ros.store import DEFAULT_STORE_PATH, Store, load_default

from .conftest import valid_protocol, write_lab, write_protocol


def gate(run, name):
    return next(r for r in run.results if r.name == name)


def load(lab: Path) -> Store:
    return Store.load(lab / DEFAULT_STORE_PATH)


# ------------------------------------------------------------ gate registry


def test_gate_names_are_unique():
    assert len(GATE_BY_NAME) == len(GATES)


def test_every_gate_has_a_description():
    assert all(g.description for g in GATES)


def test_registration_and_vocabulary_gates_are_advisory():
    """Both are advisory by design. Registration cannot be fixed by an engineer,
    and closing the vocabulary gap requires a constitutional change request or a
    Scientific Decision. A blocking gate on either would halt legitimate work to
    protest a state CI may not compel, and would be switched off."""
    assert not GATE_BY_NAME["registration"].blocking
    assert not GATE_BY_NAME["lock-vocabulary"].blocking


def test_store_propagation_and_drift_gates_block():
    for name in ("store-integrity", "projection-drift", "propagation", "protocols"):
        assert GATE_BY_NAME[name].blocking


# ------------------------------------------------------ positive control


def test_all_blocking_gates_pass_on_the_live_repository():
    run = run_gates(load_default("."), ".")
    assert run.blocked == [], run.render()
    assert run.exit_code == 0


def test_all_blocking_gates_pass_on_the_miniature_lab(lab: Path):
    run = run_gates(load(lab), lab)
    assert run.blocked == [], run.render()


def test_advisory_failure_does_not_block(lab: Path):
    """The miniature lab is unregistered, so the advisory gate fails while the
    build still passes — the distinction the gate design turns on."""
    run = run_gates(load(lab), lab)
    assert not gate(run, "registration").passed
    assert run.exit_code == 0
    assert "advisory" in run.render()


def test_registration_gate_passes_when_registration_is_active(tmp_path: Path):
    write_lab(tmp_path, registration_active=True)
    run = run_gates(load(tmp_path), tmp_path)
    assert gate(run, "registration").passed
    assert load_registration(tmp_path).active


# ------------------------------------------------------ negative controls


def test_store_integrity_gate_fails_on_a_dangling_reference(edit_store, lab: Path):
    edit_store(lambda d: d["experiments"][0].update({"hypothesis": "HYP-2026-9999"}))
    run = run_gates(load(lab), lab)
    assert not gate(run, "store-integrity").passed
    assert run.exit_code == 1


def test_propagation_gate_fails_on_an_undischarged_obligation(edit_store, lab: Path):
    edit_store(lambda d: d["experiments"][0].pop("validity"))
    run = run_gates(load(lab), lab)
    result = gate(run, "propagation")
    assert not result.passed
    assert "execution_validity" in result.render()
    assert run.exit_code == 1


def test_protocol_gate_fails_on_an_unlintable_protocol(lab: Path):
    protocol = valid_protocol()
    protocol["controls"] = [{"name": "unjustified"}]
    write_protocol(lab / "configs/protocols/p.yaml", protocol)
    run = run_gates(load(lab), lab)
    assert not gate(run, "protocols").passed


def test_protocol_gate_fails_when_a_frozen_protocol_was_edited(lab: Path):
    from ros.protocol import freeze

    path = write_protocol(lab / "configs/protocols/p.yaml", valid_protocol())
    freeze(path)
    edited = valid_protocol()
    edited["stopping_rule"] = "stop when it looks significant"
    write_protocol(path, edited)
    run = run_gates(load(lab), lab)
    result = gate(run, "protocols")
    assert not result.passed
    assert "changed since it was frozen" in result.render()


def test_protocol_gate_passes_a_clean_frozen_protocol(lab: Path):
    from ros.protocol import freeze

    path = write_protocol(lab / "configs/protocols/p.yaml", valid_protocol())
    freeze(path)
    assert gate(run_gates(load(lab), lab), "protocols").passed


def test_a_gate_that_raises_counts_as_failing(lab: Path, monkeypatch):
    """A crashing gate must not be read as a pass."""

    def boom(store, root):
        raise RuntimeError("instrument broken")

    monkeypatch.setattr(GATE_BY_NAME["propagation"], "run", boom)
    run = run_gates(load(lab), lab, ["propagation"])
    result = gate(run, "propagation")
    assert not result.passed
    assert "RuntimeError" in result.summary
    assert run.exit_code == 1


def test_unknown_gate_name_raises(lab: Path):
    with pytest.raises(KeyError):
        run_gates(load(lab), lab, ["no-such-gate"])


# ------------------------------------------------------------- projections


def test_no_drift_on_the_live_repository():
    """A real assertion: the nine hand-maintained registries agree with the
    store on which records exist."""
    report = drift(load_default("."), ".")
    assert report.clean, report.render()


def test_drift_detects_a_record_missing_from_its_registry(lab: Path, edit_store):
    edit_store(lambda d: d["unknowns"].append({"id": "UNK-2026-0002", "title": "new"}))
    report = drift(load(lab), lab)
    assert not report.clean
    assert any(f.code == "PROJ-310" for f in report.findings)


def test_drift_detects_a_registry_citing_a_record_that_does_not_exist(lab: Path):
    path = lab / "science/skb/05_UNKNOWN_REGISTRY.md"
    path.write_text(path.read_text(encoding="utf-8") + "\n- `UNK-2026-0404`\n", encoding="utf-8")
    report = drift(load(lab), lab)
    assert not report.clean
    assert any(f.code == "PROJ-311" for f in report.findings)


def test_missing_registry_is_a_warning_not_an_error(lab: Path):
    """A registry that has not been written yet is not a contradiction."""
    (lab / "science/skb/05_UNKNOWN_REGISTRY.md").unlink()
    report = drift(load(lab), lab)
    assert report.clean
    assert any(f.code == "PROJ-301" for f in report.findings)


def test_render_writes_a_generated_projection(lab: Path):
    target = render_laboratory_state(load(lab), lab)
    text = target.read_text(encoding="utf-8")
    assert target.exists()
    assert "GENERATED BY" in text.splitlines()[0]
    assert "Article L-11" in text
    assert "UNK-2026-0001" in text


def test_render_is_deterministic(lab: Path):
    first = render_laboratory_state(load(lab), lab).read_text(encoding="utf-8")
    second = render_laboratory_state(load(lab), lab).read_text(encoding="utf-8")
    assert first == second


def test_render_states_registration_when_active(tmp_path: Path):
    write_lab(tmp_path, registration_active=True)
    text = render_laboratory_state(load(tmp_path), tmp_path).read_text(encoding="utf-8")
    assert "Registration is **active**" in text


# ---------------------------------------------------------------- metrics


def test_metrics_are_computed_from_the_store_only(lab: Path):
    metrics = compute(load(lab), load_registration(lab))
    assert {m.key for m in metrics} >= {
        "admissible_capacity",
        "uncertainty_resolution",
        "falsifier_coverage",
        "propagation_completeness",
        "negative_result_preservation",
        "decision_density",
        "vocabulary_conformance",
        "store_integrity",
    }
    assert all(m.interpretation for m in metrics), "a metric without an interpretation is a number"


def test_admissible_capacity_is_zero_without_registration(lab: Path):
    """A flawless run in this repository today still bears no evidence. The
    metric must say so, because it means confirmatory compute is wasted."""
    metrics = {m.key: m for m in compute(load(lab), load_registration(lab))}
    assert metrics["admissible_capacity"].value == 0.0
    assert metrics["admissible_capacity"].healthy is False


def test_admissible_capacity_is_one_when_registered(tmp_path: Path):
    write_lab(tmp_path, registration_active=True)
    metrics = {m.key: m for m in compute(load(tmp_path), load_registration(tmp_path))}
    assert metrics["admissible_capacity"].value == 1.0


def test_falsifier_coverage_falls_when_a_hypothesis_has_no_experiment(edit_store, lab: Path):
    edit_store(lambda d: d["hypotheses"].append({"id": "HYP-2026-0002", "status": "Proposed"}))
    metrics = {m.key: m for m in compute(load(lab), load_registration(lab))}
    assert metrics["falsifier_coverage"].value == 0.5
    assert metrics["falsifier_coverage"].healthy is False


def test_vocabulary_conformance_matches_the_store_check(edit_store, lab: Path):
    """The store check and the metric must agree on what conformance means.
    Two components normalising differently would report different figures for
    identical data."""
    store = edit_store(lambda d: d["decisions"][0].update({"action": "accept"}))
    warnings = [f for f in store.check() if f.code in {"SKB-131", "SKB-132"}]
    metrics = {m.key: m for m in compute(store, load_registration(lab))}
    conformance = metrics["vocabulary_conformance"]
    total = len(store.by_collection("evidence")) + len(store.by_collection("decisions"))
    assert conformance.value == pytest.approx((total - len(warnings)) / total)


def test_failing_lists_only_metrics_with_unmet_targets(lab: Path):
    metrics = compute(load(lab), load_registration(lab))
    assert all(m.healthy is False for m in failing(metrics))


def test_live_metrics_compute_without_error():
    metrics = compute(load_default("."), load_registration("."))
    assert len(metrics) == 10
