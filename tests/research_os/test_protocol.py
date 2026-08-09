"""The protocol compiler: lint, freeze, verify (invariant K3)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from ros.protocol import (
    REQUIRED_FIELDS,
    canonical_bytes,
    digest,
    freeze,
    freeze_path_for,
    lint,
    load,
    verify,
)

from .conftest import valid_protocol, write_protocol


def codes(protocol: dict) -> set[str]:
    return {f.code for f in lint(protocol)}


# ------------------------------------------------------------ Lock E1 fields


def test_lock_e1_requires_fourteen_fields():
    assert len(REQUIRED_FIELDS) == 14


def test_valid_protocol_lints_clean():
    assert lint(valid_protocol()) == []


@pytest.mark.parametrize("field_name", REQUIRED_FIELDS)
def test_every_required_field_is_load_bearing(field_name):
    """One negative control per Lock E1 field. A field that can be removed
    without a finding is not required in practice."""
    protocol = valid_protocol()
    protocol.pop(field_name)
    assert "PROTO-201" in codes(protocol)


@pytest.mark.parametrize("field_name", REQUIRED_FIELDS)
def test_every_required_field_rejects_an_empty_value(field_name):
    protocol = valid_protocol()
    protocol[field_name] = "" if not isinstance(protocol[field_name], list) else []
    assert {"PROTO-202", "PROTO-203"} & codes(protocol)


# --------------------------------------------------------------- E1 semantics


def test_control_without_a_confound_is_rejected():
    """Lock E1 names 'controls declared without stating which confound they
    remove' as a failure mode, so presence alone is not enough."""
    protocol = valid_protocol()
    protocol["controls"] = [{"name": "shuffled labels"}]
    assert "PROTO-212" in codes(protocol)


def test_control_without_a_name_is_rejected():
    protocol = valid_protocol()
    protocol["controls"] = [{"removes": "something"}]
    assert "PROTO-211" in codes(protocol)


def test_control_that_is_not_a_mapping_is_rejected():
    protocol = valid_protocol()
    protocol["controls"] = ["shuffled labels"]
    assert "PROTO-210" in codes(protocol)


def test_overlapping_tuning_and_confirmation_seeds_are_rejected():
    """Reusing a tuning seed for confirmation is how a stopping rule gets
    altered after inspection."""
    protocol = valid_protocol()
    protocol["tuning_confirmation_split"] = {
        "tuning_seeds": [1, 2, 3],
        "confirmation_seeds": [3, 4, 5],
    }
    assert "PROTO-221" in codes(protocol)


def test_split_must_name_both_halves():
    protocol = valid_protocol()
    protocol["tuning_confirmation_split"] = {"tuning_seeds": [1]}
    assert "PROTO-220" in codes(protocol)


def test_non_positive_sesoi_is_rejected():
    protocol = valid_protocol()
    protocol["sesoi"] = 0
    assert {"PROTO-202", "PROTO-230"} & codes(protocol)


def test_list_field_given_a_scalar_is_rejected():
    protocol = valid_protocol()
    protocol["conditions"] = "baseline and treatment"
    assert "PROTO-203" in codes(protocol)


# ------------------------------------------------------------ content address


def test_digest_is_stable_and_key_order_independent():
    """Reordering a protocol must not look like changing it."""
    protocol = valid_protocol()
    reordered = dict(reversed(list(protocol.items())))
    assert digest(protocol) == digest(reordered)


def test_digest_changes_when_a_value_changes():
    protocol = valid_protocol()
    changed = valid_protocol()
    changed["sesoi"] = 0.10
    assert digest(protocol) != digest(changed)


def test_underscore_prefixed_keys_are_not_part_of_identity():
    """Annotations and editor metadata must not invalidate a freeze."""
    protocol = valid_protocol()
    annotated = valid_protocol()
    annotated["_note"] = "added while reading"
    assert digest(protocol) == digest(annotated)


def test_canonical_bytes_are_compact_and_sorted():
    raw = canonical_bytes({"b": 1, "a": 2}).decode()
    assert raw == '{"a":2,"b":1}'


# ------------------------------------------------------------ freeze / verify


def test_freeze_writes_a_sidecar_and_verifies(protocol_file: Path):
    record = freeze(protocol_file, commit="abc123")
    sidecar = freeze_path_for(protocol_file)
    assert sidecar.exists()
    payload = json.loads(sidecar.read_text(encoding="utf-8"))
    assert payload["digest"] == record.digest
    assert payload["frozen_at_commit"] == "abc123"
    assert payload["algorithm"] == "blake2b-256-canonical-json"
    matched, _ = verify(protocol_file)
    assert matched


def test_freeze_refuses_a_protocol_that_does_not_lint(tmp_path: Path):
    """The gate is before the first tick, not after the last."""
    protocol = valid_protocol()
    protocol["controls"] = [{"name": "unjustified"}]
    path = write_protocol(tmp_path / "bad.yaml", protocol)
    with pytest.raises(ValueError, match="does not lint clean"):
        freeze(path)
    assert not freeze_path_for(path).exists()


def test_verify_detects_a_post_freeze_edit(protocol_file: Path):
    freeze(protocol_file)
    protocol = load(protocol_file)
    protocol["sesoi"] = 0.5
    write_protocol(protocol_file, protocol)
    matched, message = verify(protocol_file)
    assert not matched
    assert "has changed since it was frozen" in message


def test_verify_reports_an_unfrozen_protocol(protocol_file: Path):
    matched, message = verify(protocol_file)
    assert not matched
    assert "never frozen" in message


def test_reformatting_does_not_break_a_freeze(protocol_file: Path):
    """A freeze must survive a reformat, or engineers will avoid touching
    protocols for the wrong reason."""
    freeze(protocol_file)
    protocol = load(protocol_file)
    protocol_file.write_text(
        yaml.safe_dump(protocol, sort_keys=True, default_flow_style=False, width=40),
        encoding="utf-8",
    )
    matched, _ = verify(protocol_file)
    assert matched


def test_loading_a_non_mapping_protocol_raises(tmp_path: Path):
    path = tmp_path / "list.yaml"
    path.write_text("- a\n- b\n", encoding="utf-8")
    with pytest.raises(ValueError, match="must be a mapping"):
        load(path)
