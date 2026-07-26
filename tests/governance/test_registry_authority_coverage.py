"""Authority-graph guard for the RS-1 activation target.

AF-8 was closed on the strength of a statement that the steward's
`permitted_transitions` cover "every RS-1 transition", while the target
implemented 19 of 21. Four separate artifacts asserted the stronger claim. This
test makes the claim mechanical: it joins RS-1 §1's owned transitions against
the target Registry's granted transitions and fails on any asymmetry in either
direction.

Validation artifact, not a governance check: no `A-xx` identifier, no
conformance verdict, no authority (Constitution §4 ¶4).
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RS1 = REPO / "governance" / "activation" / "RS-1_RESEARCH_STANDARD.draft.md"
TARGET = REPO / "governance" / "activation" / "GOVERNANCE_REGISTRY.target.yaml"

TUPLE = re.compile(
    r"\{\s*(?:standard:\s*(?P<std>[\w.-]+)\s*,\s*)?"
    r"type:\s*(?P<type>\w+)\s*,\s*from:\s*(?P<frm>\w+)\s*,\s*to:\s*(?P<to>\w+)\s*\}"
)

CONSTITUTIONAL = {
    "amend_constitution",
    "supersede_constitution",
    "withdraw_constitution",
    "activate_domain_standard",
}


def _tuples(block: str, want_standard: bool) -> set[tuple[str, str, str]]:
    out = set()
    for m in TUPLE.finditer(block):
        if want_standard and m.group("std") is None:
            continue
        if not want_standard and m.group("std") is not None:
            continue
        out.add((m.group("type"), m.group("frm"), m.group("to")))
    return out


def _rs1_owned() -> set[tuple[str, str, str]]:
    text = RS1.read_text(encoding="utf-8")
    start = text.index("owned_transitions:")
    end = text.index("scope:", start)
    return _tuples(text[start:end], want_standard=False)


def _target_blocks() -> tuple[str, str]:
    text = TARGET.read_text(encoding="utf-8")
    e = text.index("e_target:")
    grants_start = text.index("permitted_transitions:", e)
    grants_end = text.index("successor:", grants_start)
    owned_start = text.index("owned_transitions:", e)
    owned_end = text.index("not_owned:", owned_start)
    return text[grants_start:grants_end], text[owned_start:owned_end]


def test_rs1_declares_twenty_one_owned_transitions():
    assert len(_rs1_owned()) == 21


def test_target_jurisdiction_matches_rs1_section_1_exactly():
    grants, owned = _target_blocks()
    assert _tuples(owned, want_standard=False) == _rs1_owned()


def test_every_owned_transition_has_a_registry_granted_authority():
    """§4 ¶1: an authority whose permitted transitions are absent or
    inconsistent has no authority. §4 ¶5: a transition needs a Registry-listed
    authority. Every one of the 21 must therefore be granted."""
    grants, _ = _target_blocks()
    granted = _tuples(grants, want_standard=True)
    missing = sorted(_rs1_owned() - granted)
    assert not missing, f"owned but not granted: {missing}"


def test_no_grant_exceeds_rs1_jurisdiction():
    """A grant for a tuple RS-1 does not own would be the Registry enlarging
    jurisdiction (§4 ¶3)."""
    grants, _ = _target_blocks()
    extra = sorted(_tuples(grants, want_standard=True) - _rs1_owned())
    assert not extra, f"granted but not owned: {extra}"


def test_constitutional_transitions_are_still_granted():
    grants, _ = _target_blocks()
    for name in CONSTITUTIONAL:
        assert re.search(
            rf"^\s*-\s*{name}\s*$", grants, re.MULTILINE
        ), f"{name} missing from permitted_transitions"


def test_decision_lifecycle_tuples_are_granted_not_omitted():
    """The specific AF-8 residual: {decision, none -> proposed} and
    {decision, proposed -> withdrawn}."""
    grants, _ = _target_blocks()
    granted = _tuples(grants, want_standard=True)
    assert ("decision", "none", "proposed") in granted
    assert ("decision", "proposed", "withdrawn") in granted


def test_no_artifact_claims_a_partial_grant():
    """Route A is the repository's single Decision authority model. No artifact
    may state that a subset of RS-1's transitions is granted, or that any tuple
    is 'absent by design'."""
    stale = [
        "absent by design",
        "19 mapping",
        "covering all but",
    ]
    for path in sorted((REPO / "governance").rglob("*.md")) + [TARGET]:
        text = path.read_text(encoding="utf-8", errors="replace")
        # The resolution dossier and this test describe the superseded model on
        # purpose; governance artifacts must not assert it.
        for phrase in stale:
            assert phrase not in text, f"{path.name} still asserts the 19-grant model: {phrase!r}"
