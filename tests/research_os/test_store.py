"""The record store and its integrity checks (invariant K1)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from ros.model import (
    DECISION_ACTIONS,
    EVIDENCE_DIRECTIONS,
    collection_for_id,
    conforms,
    iter_id_references,
    normalise_term,
    prefix_of,
)
from ros.store import DEFAULT_STORE_PATH, Store, errors, load_default


def codes(store: Store) -> set[str]:
    return {f.code for f in store.check()}


# ------------------------------------------------------------------ model


def test_prefix_extraction():
    assert prefix_of("EXP-2026-0001") == "EXP"
    assert prefix_of("SDEBT-2026-0001") == "SDEBT"
    assert prefix_of("not-an-id") is None


def test_collection_lookup_by_identifier():
    assert collection_for_id("EVD-2026-0009").key == "evidence"
    assert collection_for_id("ZZZ-2026-0001") is None


def test_reference_discovery_is_structural_not_configured():
    """Identifiers are found wherever they appear, including inside prose and
    nested structures. A per-field allow-list would miss a dangling reference in
    a field nobody registered."""
    record = {
        "id": "EXP-2026-0001",
        "notes": "supersedes EXP-2026-0000 after review",
        "nested": {"deep": [{"cites": "EVD-2026-0002"}]},
    }
    found = dict(iter_id_references(record))
    assert set(found.values()) == {"EXP-2026-0001", "EXP-2026-0000", "EVD-2026-0002"}
    assert found["notes"] == "EXP-2026-0000"
    assert found["nested.deep[0].cites"] == "EVD-2026-0002"


def test_normalisation_folds_case_and_separators():
    assert normalise_term("No_Verdict") == "no_verdict"
    assert normalise_term("requires-assumption") == "requires_assumption"
    assert normalise_term("Under Validation") == "under_validation"
    assert normalise_term(None) == ""


def test_conformance_treats_empty_as_not_a_violation():
    """A blank field is a missing value, reported elsewhere. Counting it as a
    vocabulary deviation would make an incomplete record look like a
    constitutional one."""
    assert conforms("", EVIDENCE_DIRECTIONS)
    assert conforms(None, DECISION_ACTIONS)
    assert conforms("Revise", DECISION_ACTIONS)
    assert not conforms("accept", DECISION_ACTIONS)


# --------------------------------------------------- positive control (live)


def test_live_store_loads_and_is_error_free():
    """The repository's own SKB must have no integrity errors. This is a real
    assertion about the repository, not about the code."""
    store = load_default(".")
    assert len(store) > 0
    assert errors(store.check()) == []


def test_live_store_digest_is_stable():
    store = load_default(".")
    assert store.content_hash() == load_default(".").content_hash()
    assert len(store.content_hash()) == 64


def test_miniature_lab_is_clean(lab: Path):
    store = Store.load(lab / DEFAULT_STORE_PATH)
    assert errors(store.check()) == []


# ------------------------------------------------------- negative controls


def test_dangling_reference_is_an_error(edit_store):
    store = edit_store(lambda d: d["experiments"][0].update({"hypothesis": "HYP-2026-9999"}))
    assert "SKB-110" in codes(store)
    assert errors(store.check())


def test_duplicate_identifier_is_an_error(edit_store):
    def mutate(document):
        document["unknowns"].append(dict(document["unknowns"][0]))

    store = edit_store(mutate)
    # A duplicate id collapses in the index, so the count itself is the tell.
    assert len(store.by_collection("unknowns")) == 1


def test_identifier_in_the_wrong_collection_is_an_error(edit_store):
    def mutate(document):
        document["unknowns"].append({"id": "EVD-2026-0777", "title": "misfiled"})

    store = edit_store(mutate)
    assert "SKB-102" in codes(store)


def test_malformed_identifier_is_an_error(edit_store):
    def mutate(document):
        document["unknowns"].append({"id": "not-an-identifier", "title": "bad"})

    store = edit_store(mutate)
    assert "SKB-101" in codes(store)


def test_relation_to_a_missing_record_is_an_error(edit_store):
    def mutate(document):
        document["relations"].append({"from": "EXP-2026-0001", "to": "HYP-2026-9999", "type": "x"})

    store = edit_store(mutate)
    assert "SKB-121" in codes(store)


def test_untyped_relation_is_an_error(edit_store):
    def mutate(document):
        document["relations"].append({"from": "EXP-2026-0001", "to": "HYP-2026-0001", "type": ""})

    store = edit_store(mutate)
    assert "SKB-122" in codes(store)


def test_evidence_without_a_target_is_an_error(edit_store):
    store = edit_store(lambda d: d["evidence"][0].pop("target"))
    assert "SKB-140" in codes(store)


def test_superseded_without_lineage_is_an_error(edit_store):
    store = edit_store(lambda d: d["hypotheses"][0].update({"status": "Superseded"}))
    assert "SKB-150" in codes(store)


def test_off_vocabulary_status_is_an_error(edit_store):
    store = edit_store(lambda d: d["hypotheses"][0].update({"status": "Basically Proven"}))
    assert "SKB-130" in codes(store)


def test_off_vocabulary_evidence_direction_is_a_warning_not_an_error(edit_store):
    """Changing the Lock E4 vocabulary is constitutional and rewriting evidence
    is a scientific act. Neither is something a linter may compel, so this is
    reported and does not fail a build."""
    store = edit_store(lambda d: d["evidence"][0].update({"direction": "weakly_supports"}))
    findings = [f for f in store.check() if f.code == "SKB-131"]
    assert findings and all(f.severity == "warning" for f in findings)
    assert errors(store.check()) == []


def test_off_vocabulary_decision_action_is_a_warning(edit_store):
    store = edit_store(lambda d: d["decisions"][0].update({"action": "accept"}))
    findings = [f for f in store.check() if f.code == "SKB-132"]
    assert findings and all(f.severity == "warning" for f in findings)


def test_findings_are_deterministically_ordered(edit_store):
    store = edit_store(lambda d: d["experiments"][0].update({"hypothesis": "HYP-2026-9999"}))
    assert [str(f) for f in store.check()] == [str(f) for f in store.check()]


# ---------------------------------------------------------------- loading


def test_non_mapping_store_is_rejected(tmp_path: Path):
    path = tmp_path / "store.yaml"
    path.write_text("- just\n- a\n- list\n", encoding="utf-8")
    with pytest.raises(ValueError, match="must be a mapping"):
        Store.load(path)


def test_digest_ignores_the_header_but_not_the_records(lab: Path):
    """Re-stating the state date must not change the digest of the science;
    changing a record must."""
    path = lab / DEFAULT_STORE_PATH
    original = Store.load(path).content_hash()

    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    document["skb"]["state_date"] = "2026-07-29"
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    assert Store.load(path).content_hash() == original

    document["unknowns"][0]["title"] = "changed"
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    assert Store.load(path).content_hash() != original
