"""Tests for backend.knowledge.fact_extractor subject-boundary extraction.

Regression coverage for the auxiliary-verb leak: the subject of a passive
sentence such as "supermegasoftware was created" must come back as the bare
entity "supermegasoftware", never "supermegasoftware was".

Note on the bare sentence "supermegasoftware was created": it has no object or
agent, so it yields no S-V-O triple at all. The subject-boundary correctness for
that exact sentence is therefore asserted directly against the subject extractor
(``_resolve_subject_phrase``), while the end-to-end leak is exercised with a
sentence that actually produces a triple ("... created by a developer").
"""
import os
import sys

import pytest

# Make `backend.` imports resolve from the repo root, matching the other tests.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Skip the whole module cleanly if the spaCy model isn't installed, rather than
# erroring — extraction is hard-dependent on en_core_web_sm.
pytest.importorskip("spacy")

from backend.knowledge import fact_extractor
from backend.knowledge.fact_extractor import _resolve_subject_phrase, extract_triples

try:
    _NLP = fact_extractor._get_nlp()
except RuntimeError as exc:  # model not downloaded
    pytest.skip(str(exc), allow_module_level=True)


def _subjects(text):
    """Return just the subject strings extracted from ``text``."""
    return [subj for (subj, _rel, _obj) in extract_triples(text)]


def _subject_token(text):
    """Return the (passive) subject token of ``text``'s root clause."""
    doc = _NLP(text)
    root = next(t for t in doc.sents).root
    return next(c for c in root.children if c.dep_ in ("nsubj", "nsubjpass"))


# ── The headline case: exact sentence from the bug report ────────────────────
def test_supermegasoftware_was_created_subject_boundary():
    """"supermegasoftware was created" -> subject "supermegasoftware" (not "... was").

    Asserted at the subject-boundary level because this agentless passive yields
    no object, hence no full triple.
    """
    subj = _subject_token("supermegasoftware was created")
    phrase = _resolve_subject_phrase(list(subj.subtree))

    assert phrase == "supermegasoftware"
    assert "was" not in phrase.lower().split()


def test_resolve_subject_phrase_filters_auxiliary_tokens():
    """Directly feeding an AUX token to the resolver drops it from the subject."""
    doc = _NLP("supermegasoftware was created")
    # tokens = ["supermegasoftware" (NOUN), "was" (AUX)]
    phrase = _resolve_subject_phrase([doc[0], doc[1]])

    assert doc[1].pos_ == "AUX"  # guard: we really are feeding an auxiliary
    assert phrase == "supermegasoftware"


# ── End-to-end leak: a passive sentence that does produce a triple ───────────
def test_passive_sentence_with_agent_has_clean_subject():
    """"supermegasoftware was created by a developer" -> subject "supermegasoftware"."""
    subjects = _subjects("supermegasoftware was created by a developer")

    assert subjects, "expected a triple from the passive-with-agent sentence"
    assert subjects[0] == "supermegasoftware"
    assert "was" not in subjects[0].lower().split()


@pytest.mark.parametrize(
    "sentence, expected_subject",
    [
        ("the framework was developed by engineers", "the framework"),
        ("velynx is built", "velynx"),
    ],
)
def test_other_passive_subjects_stay_clean(sentence, expected_subject):
    """Auxiliaries ("was", "is") never appear in extracted subjects."""
    subjects = _subjects(sentence)
    assert subjects, f"expected a triple from {sentence!r}"
    for aux in ("was", "is", "been", "were"):
        assert aux not in subjects[0].lower().split()
    assert subjects[0] == expected_subject
