"""The command line, governance registry reading, and self-instrumentation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from ros.cli import EXIT_ERROR, EXIT_FAILED, EXIT_OK, main
from ros.events import EVENT_LOG, Event, emit, read, summarise
from ros.governance import GOVERNING_ARTIFACTS, RegistryState, load_registration
from ros.protocol import freeze_path_for

from .conftest import valid_protocol, write_lab, write_protocol


def run(*argv: str) -> int:
    return main(list(argv))


# --------------------------------------------------------------- governance


def test_live_registry_reports_the_unregistered_governing_artifacts():
    """A measured statement about the repository: the four governing artifacts
    are not registered, so Article L-11 applies."""
    state = RegistryState.load(Path("GOVERNANCE_REGISTRY.yaml"))
    assert set(state.unregistered_governing_artifacts()) == set(GOVERNING_ARTIFACTS)
    assert not state.to_registration().active


def test_missing_registry_means_nothing_registered(tmp_path: Path):
    """Absence of a registry is exactly the state Article L-11 describes, not an
    error to crash on."""
    registration = load_registration(tmp_path)
    assert not registration.active
    assert len(registration.missing()) == 4


def test_registry_with_all_artifacts_and_attestations_is_active(tmp_path: Path):
    write_lab(tmp_path, registration_active=True)
    state = RegistryState.load(tmp_path / "GOVERNANCE_REGISTRY.yaml")
    assert state.unregistered_governing_artifacts() == []
    assert state.to_registration().active


def test_one_missing_governing_artifact_blocks_registration(tmp_path: Path):
    write_lab(tmp_path, registration_active=True)
    path = tmp_path / "GOVERNANCE_REGISTRY.yaml"
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    document["active_domain_standards"].pop()
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    assert not load_registration(tmp_path).active


def test_non_mapping_registry_is_rejected(tmp_path: Path):
    path = tmp_path / "GOVERNANCE_REGISTRY.yaml"
    path.write_text("- not a mapping\n", encoding="utf-8")
    with pytest.raises(ValueError, match="must be a mapping"):
        RegistryState.load(path)


# ---------------------------------------------------------------- cli: exit


def test_check_passes_on_the_live_repository(capsys):
    assert run("check") == EXIT_OK
    assert "0 error(s)" in capsys.readouterr().out


def test_check_fails_on_a_broken_store(lab: Path, edit_store, capsys):
    edit_store(lambda d: d["experiments"][0].update({"hypothesis": "HYP-2026-9999"}))
    assert run("--root", str(lab), "check") == EXIT_FAILED
    assert "SKB-110" in capsys.readouterr().out


def test_gates_command_returns_zero_on_the_live_repository():
    assert run("gates") == EXIT_OK


def test_gates_command_rejects_an_unknown_gate(capsys):
    assert run("gates", "--only", "nope") == EXIT_ERROR
    assert "unknown gate" in capsys.readouterr().err


def test_gates_command_accepts_a_subset():
    assert run("gates", "--only", "store-integrity", "propagation") == EXIT_OK


def test_doctor_runs_and_reports_registration(capsys):
    code = run("doctor")
    out = capsys.readouterr().out
    assert code == EXIT_OK
    assert "registration NOT active" in out
    assert "Article L-11" in out
    assert "== Gates ==" in out
    assert "== Indicators ==" in out


def test_admissibility_command_reports_engineering_only(capsys):
    """The default flags describe a run with nothing attested, and the live
    repository is unregistered, so the honest answer is not admissible."""
    assert run("admissibility", "run-x") == EXIT_FAILED
    assert "engineering-only" in capsys.readouterr().out


def test_admissibility_command_json_shape(capsys):
    run("admissibility", "run-x", "--json")
    payload = json.loads(capsys.readouterr().out)
    assert payload["run_id"] == "run-x"
    assert payload["admissible"] is False
    assert payload["tier"] == "engineering-only"
    assert payload["reasons"]


def test_admissibility_command_on_a_registered_lab(tmp_path: Path, capsys):
    write_lab(tmp_path, registration_active=True)
    code = run(
        "--root",
        str(tmp_path),
        "admissibility",
        "run-y",
        "--protocol-frozen",
        "--protocol-matched",
        "--coverage-disclosed",
        "--json",
    )
    payload = json.loads(capsys.readouterr().out)
    assert code == EXIT_OK
    assert payload["tier"] == "confirmatory-admissible"


def test_admissibility_command_honours_scope(tmp_path: Path, capsys):
    write_lab(tmp_path, registration_active=True)
    code = run(
        "--root",
        str(tmp_path),
        "admissibility",
        "run-z",
        "--determinism",
        "D2",
        "--scope",
        "object",
        "--protocol-frozen",
        "--protocol-matched",
        "--json",
    )
    payload = json.loads(capsys.readouterr().out)
    assert code == EXIT_FAILED
    assert payload["tier"] == "inadmissible"


def test_propagation_command_passes_on_the_live_repository(capsys):
    assert run("propagation") == EXIT_OK
    assert "complete" in capsys.readouterr().out


def test_propagation_command_accepts_one_experiment(capsys):
    assert run("propagation", "EXP-2026-0001") == EXIT_OK


def test_propagation_command_reports_an_unknown_experiment(capsys):
    assert run("propagation", "EXP-9999-9999") == EXIT_ERROR
    assert "not an experiment" in capsys.readouterr().err


def test_propagation_command_fails_when_an_obligation_is_outstanding(lab: Path, edit_store):
    edit_store(lambda d: d["experiments"][0].pop("validity"))
    assert run("--root", str(lab), "propagation") == EXIT_FAILED


def test_kpi_command_json_shape(capsys):
    run("kpi", "--json")
    payload = json.loads(capsys.readouterr().out)
    assert isinstance(payload, list)
    assert {"key", "name", "value", "rendered", "target", "healthy"} <= set(payload[0])


def test_drift_command_passes_on_the_live_repository():
    assert run("drift") == EXIT_OK


def test_render_command_writes_the_projection(lab: Path, capsys):
    assert run("--root", str(lab), "render") == EXIT_OK
    assert (lab / "docs/ros/generated/LABORATORY_STATE.md").exists()
    assert "wrote" in capsys.readouterr().out


def test_protocol_lint_and_freeze_and_verify(tmp_path: Path, capsys):
    path = write_protocol(tmp_path / "p.yaml", valid_protocol())
    assert run("protocol", "lint", str(path)) == EXIT_OK
    assert run("--root", str(tmp_path), "protocol", "freeze", str(path)) == EXIT_OK
    assert freeze_path_for(path).exists()
    assert run("protocol", "verify", str(path)) == EXIT_OK
    assert "matches freeze" in capsys.readouterr().out


def test_protocol_freeze_refuses_an_unlintable_protocol(tmp_path: Path, capsys):
    protocol = valid_protocol()
    protocol["controls"] = [{"name": "unjustified"}]
    path = write_protocol(tmp_path / "p.yaml", protocol)
    assert run("protocol", "lint", str(path)) == EXIT_FAILED
    assert run("protocol", "freeze", str(path)) == EXIT_FAILED
    assert not freeze_path_for(path).exists()


def test_missing_store_reports_an_error_not_a_traceback(tmp_path: Path, capsys):
    assert run("--root", str(tmp_path), "check") == EXIT_ERROR
    assert "ros:" in capsys.readouterr().err


def test_a_command_is_required(capsys):
    with pytest.raises(SystemExit):
        main([])


# --------------------------------------------------------------- events


def test_event_log_is_outside_the_science_tree():
    """Article L-8: engineering telemetry must not be able to reach a scientific
    computation. The path is the enforcement."""
    assert "science" not in EVENT_LOG.parts


def test_emit_and_read_round_trip(tmp_path: Path):
    emit(Event("gate_run", actor="ci", outcome="pass", detail={"gate": "propagation"}), tmp_path)
    emit(Event("gate_run", actor="ci", outcome="fail"), tmp_path)
    records = list(read(tmp_path))
    assert len(records) == 2
    assert records[0]["kind"] == "gate_run"
    assert records[0]["detail"]["gate"] == "propagation"
    assert records[0]["at"]


def test_emit_appends_rather_than_overwrites(tmp_path: Path):
    for index in range(3):
        emit(Event("agent_action", actor=f"agent-{index}", outcome="ok"), tmp_path)
    assert len(list(read(tmp_path))) == 3


def test_unknown_event_kind_is_rejected():
    """A typo'd kind would silently create a category nobody aggregates."""
    with pytest.raises(ValueError, match="unknown event kind"):
        Event("gate_runn", actor="ci", outcome="pass")


def test_reading_a_missing_log_yields_nothing(tmp_path: Path):
    assert list(read(tmp_path)) == []


def test_a_malformed_line_does_not_break_reading(tmp_path: Path):
    """Telemetry must never be able to fail a gate."""
    emit(Event("store_check", actor="ci", outcome="pass"), tmp_path)
    path = tmp_path / EVENT_LOG
    with path.open("a", encoding="utf-8") as handle:
        handle.write("{not json\n\n")
    assert len(list(read(tmp_path))) == 1


def test_summarise_counts_outcomes_per_kind(tmp_path: Path):
    emit(Event("gate_run", actor="ci", outcome="pass"), tmp_path)
    emit(Event("gate_run", actor="ci", outcome="pass"), tmp_path)
    emit(Event("gate_run", actor="ci", outcome="fail"), tmp_path)
    emit(Event("escalation", actor="agent", outcome="raised"), tmp_path)
    assert summarise(tmp_path) == {
        "gate_run": {"pass": 2, "fail": 1},
        "escalation": {"raised": 1},
    }
