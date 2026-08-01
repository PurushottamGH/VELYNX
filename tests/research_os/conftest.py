"""Shared fixtures for ROS tests.

The central fixture is :func:`lab`, which builds a *complete miniature
laboratory* in a temporary directory: a store, registries that project it, a
governance registry, and a protocol. Tests then break exactly one thing and
assert that exactly one gate notices.

Building a real repository rather than mocking the store is deliberate. A mock
would let the gates pass against a shape the real store never has, which is the
failure mode these gates exist to prevent.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import pytest
import yaml

from ros.store import Store


def _store_document() -> dict[str, Any]:
    """A minimal store that passes every blocking gate."""
    return {
        "skb": {"version": "test-1.0.0", "phase": "test"},
        "hypotheses": [
            {
                "id": "HYP-2026-0001",
                "title": "Test hypothesis",
                "status": "Under Validation",
            }
        ],
        "experiments": [
            {
                "id": "EXP-2026-0001",
                "title": "Test experiment",
                "status": "Closed",
                "hypothesis": "HYP-2026-0001",
                "validity": "Valid",
                "executions": ["run-a"],
                "observations": ["OBS-2026-0001"],
                "evidence": ["EVD-2026-0001"],
                "limitations": "single seed",
            }
        ],
        "observations": [
            {"id": "OBS-2026-0001", "title": "Test observation", "experiment": "EXP-2026-0001"}
        ],
        "evidence": [
            {
                "id": "EVD-2026-0001",
                "title": "Test evidence",
                "direction": "opposes",
                "target": "HYP-2026-0001",
                "source_observations": ["OBS-2026-0001"],
                "rationale": "the measured effect ran against the prediction",
            }
        ],
        "decisions": [
            {
                "id": "DEC-2026-0001",
                "title": "Test decision",
                "action": "revise",
                "cites": ["EVD-2026-0001", "EXP-2026-0001"],
            }
        ],
        "unknowns": [
            {"id": "UNK-2026-0001", "title": "Test unknown", "status": "Open"},
        ],
        "assumptions": [
            {
                "id": "ASM-2026-0001",
                "title": "Test assumption",
                "status": "Open",
                "arising_from": "EXP-2026-0001",
            }
        ],
        "scientific_debt": [
            {"id": "SDEBT-2026-0001", "title": "Test debt", "status": "Open"},
        ],
        "negative_results": [
            {"id": "NEG-2026-0001", "title": "Test negative result", "from": "EXP-2026-0001"}
        ],
        "mechanisms": [],
        "theories": [],
        "relations": [
            {
                "from": "EXP-2026-0001",
                "to": "HYP-2026-0001",
                "type": "tests",
            }
        ],
    }


def _registry_document(active: bool) -> dict[str, Any]:
    from ros.governance import GOVERNING_ARTIFACTS

    if not active:
        return {
            "constitution": {"path": "REPOSITORY_CONSTITUTION.md"},
            "active_domain_standards": [],
            "authority_assignments": {"constitutional_steward": []},
            "activation_requirements": {
                "adopter_attestation": None,
                "independent_reviewer_attestation": None,
            },
        }
    return {
        "constitution": {"path": "REPOSITORY_CONSTITUTION.md"},
        "active_domain_standards": [{"path": path} for path in GOVERNING_ARTIFACTS],
        "authority_assignments": {"constitutional_steward": ["a-human"]},
        "activation_requirements": {
            "adopter_attestation": {"by": "a-human", "at": "2026-01-01"},
            "independent_reviewer_attestation": {"by": "another-human", "at": "2026-01-02"},
        },
    }


def valid_protocol() -> dict[str, Any]:
    """A protocol that lints clean. Tests mutate copies of it."""
    return {
        "id": "PROTO-TEST-0001",
        "hypothesis": "HYP-2026-0001",
        "conditions": ["baseline", "treatment"],
        "controls": [
            {"name": "shuffled labels", "removes": "spurious structure in the target"},
            {"name": "matched compute", "removes": "compute budget as a confound"},
        ],
        "estimand": "difference in mean surprise between conditions",
        "unit_of_inference": "episode",
        "pairing": "paired by seed",
        "sesoi": 0.05,
        "guardrails": ["abort if loss diverges"],
        "seed_generation": "derived from protocol digest",
        "tuning_confirmation_split": {
            "tuning_seeds": [1, 2, 3],
            "confirmation_seeds": [101, 102, 103],
        },
        "stopping_rule": "fixed 30 episodes per condition, no interim looks",
        "exclusion_rule": "exclude runs that raised a FAULT, recorded not deleted",
        "multiplicity_family": "the two primary contrasts, Holm-corrected",
    }


@pytest.fixture
def lab(tmp_path: Path) -> Path:
    """A miniature repository that passes every blocking gate."""
    write_lab(tmp_path, registration_active=False)
    return tmp_path


def write_lab(root: Path, registration_active: bool = False) -> Path:
    """Materialise a miniature laboratory at ``root``."""
    from ros.projections import REGISTRY_FILES
    from ros.store import DEFAULT_STORE_PATH

    document = _store_document()
    store_path = root / DEFAULT_STORE_PATH
    store_path.parent.mkdir(parents=True, exist_ok=True)
    store_path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")

    # Registries project the store: each mentions every identifier it holds.
    for relative, key in REGISTRY_FILES.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        ids = [str(entry["id"]) for entry in document.get(key, [])]
        body = [f"# {key}", ""] + [f"- `{identifier}`" for identifier in ids]
        path.write_text("\n".join(body) + "\n", encoding="utf-8")

    registry = root / "GOVERNANCE_REGISTRY.yaml"
    registry.write_text(
        yaml.safe_dump(_registry_document(registration_active), sort_keys=False),
        encoding="utf-8",
    )
    return root


@pytest.fixture
def edit_store(lab: Path) -> Callable[[Callable[[dict[str, Any]], None]], Store]:
    """Return a helper that mutates the miniature store and reloads it.

    Used to build negative controls: break one thing, reload, assert one gate
    fails.
    """
    from ros.store import DEFAULT_STORE_PATH

    def _edit(mutate: Callable[[dict[str, Any]], None]) -> Store:
        path = lab / DEFAULT_STORE_PATH
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        mutate(document)
        path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
        return Store.load(path)

    return _edit


@pytest.fixture
def protocol_file(tmp_path: Path) -> Path:
    path = tmp_path / "protocol.yaml"
    path.write_text(yaml.safe_dump(valid_protocol(), sort_keys=False), encoding="utf-8")
    return path


def write_protocol(path: Path, protocol: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(protocol, sort_keys=False), encoding="utf-8")
    return path


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
