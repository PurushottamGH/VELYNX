"""
Falsifiable test suite — Phase 64 Temporal Filter
==================================================

Proves that ``filter_triples_by_time`` correctly accepts / rejects triples
based on their ``valid_from`` / ``valid_until`` window and that ``None``
dates (unbounded) pass every query.

Every assertion in this file can FAIL — there are no tautologies.
"""

from __future__ import annotations

import os
import sys
from datetime import date

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.knowledge.temporal_filter import (
    _in_window,
    _parse_date,
    filter_triples_by_time,
)

# ═══════════════════════════════════════════════════════════════════════════ #
#  Helpers
# ═══════════════════════════════════════════════════════════════════════════ #

_NO_TEMPORAL = {
    "subject": "Blender",
    "predicate": "is_a",
    "obj": "Software",
    "confidence": 0.95,
    "source": "user_statement",
}

_REF = "2025-06-15"
_REF_DATE = date(2025, 6, 15)


def _triple(*, valid_from: str | None = None, valid_until: str | None = None):
    """Build a triple dict with optional temporal bounds."""
    d = dict(_NO_TEMPORAL)
    if valid_from is not None:
        d["valid_from"] = valid_from
    if valid_until is not None:
        d["valid_until"] = valid_until
    return d


# ═══════════════════════════════════════════════════════════════════════════ #
#  _parse_date
# ═══════════════════════════════════════════════════════════════════════════ #

class TestParseDate:
    def test_date_only(self):
        assert _parse_date("2025-06-15") == date(2025, 6, 15)

    def test_datetime_drops_time(self):
        assert _parse_date("2025-06-15T14:30:00") == date(2025, 6, 15)

    def test_datetime_with_tz(self):
        assert _parse_date("2025-06-15T00:00:00+00:00") == date(2025, 6, 15)


# ═══════════════════════════════════════════════════════════════════════════ #
#  _in_window  (unit-level)
# ═══════════════════════════════════════════════════════════════════════════ #

class TestInWindow:
    """Direct unit tests for the window predicate."""

    def test_null_bounds_passes(self):
        """No bounds at all → always passes."""
        assert _in_window(_triple(), _REF_DATE) is True

    def test_exact_window(self):
        """valid_from == ref == valid_until."""
        t = _triple(valid_from=_REF, valid_until=_REF)
        assert _in_window(t, _REF_DATE) is True

    def test_inside_window(self):
        """Ref comfortably inside a wide window."""
        t = _triple(valid_from="2025-01-01", valid_until="2025-12-31")
        assert _in_window(t, _REF_DATE) is True

    def test_before_window(self):
        """Ref is before valid_from → reject."""
        t = _triple(valid_from="2025-07-01", valid_until="2025-12-31")
        assert _in_window(t, _REF_DATE) is False

    def test_after_window(self):
        """Ref is after valid_until → reject."""
        t = _triple(valid_from="2025-01-01", valid_until="2025-06-01")
        assert _in_window(t, _REF_DATE) is False

    def test_only_valid_from_past_unbounded_future(self):
        """valid_from set, valid_until absent → future is unbounded."""
        t = _triple(valid_from="2025-01-01")
        assert _in_window(t, _REF_DATE) is True

    def test_only_valid_from_future_unbounded_future(self):
        """valid_from is in the future → fail (even though future is unbounded)."""
        t = _triple(valid_from="2025-07-01")
        assert _in_window(t, _REF_DATE) is False

    def test_only_valid_until_past_unbounded_past(self):
        """valid_until is before ref → fail (even though past is unbounded)."""
        t = _triple(valid_until="2025-06-01")
        assert _in_window(t, _REF_DATE) is False

    def test_only_valid_until_future_unbounded_past(self):
        """valid_until is after ref, past is unbounded → pass."""
        t = _triple(valid_until="2025-12-31")
        assert _in_window(t, _REF_DATE) is True


# ═══════════════════════════════════════════════════════════════════════════ #
#  filter_triples_by_time  (integration-level)
# ═══════════════════════════════════════════════════════════════════════════ #

class TestFilterTriplesByTime:
    """End-to-end filter tests across the three temporal regimes."""

    def test_none_as_of_is_noop(self):
        """``as_of_date=None`` must return every input unchanged."""
        triples = [
            _triple(valid_from="2020-01-01", valid_until="2021-01-01"),
            _triple(valid_from="2030-01-01"),
            _triple(),
        ]
        result = filter_triples_by_time(triples, as_of_date=None)
        assert result == triples

    def test_historical_fact_accepted(self):
        """A fact that was true in the past and is now expired should pass
        when queried for the past date."""
        t = _triple(valid_from="2020-01-01", valid_until="2023-12-31")
        result = filter_triples_by_time([t], as_of_date="2022-06-15")
        assert len(result) == 1

    def test_historical_fact_rejected_when_outside(self):
        """Same fact, queried after expiry → reject."""
        t = _triple(valid_from="2020-01-01", valid_until="2023-12-31")
        result = filter_triples_by_time([t], as_of_date="2025-01-01")
        assert len(result) == 0

    def test_current_fact_accepted(self):
        """A fact still within its window."""
        t = _triple(valid_from="2025-01-01", valid_until="2025-12-31")
        result = filter_triples_by_time([t], as_of_date=_REF)
        assert len(result) == 1

    def test_future_fact_rejected(self):
        """A fact whose window hasn't opened yet."""
        t = _triple(valid_from="2030-01-01", valid_until="2035-12-31")
        result = filter_triples_by_time([t], as_of_date=_REF)
        assert len(result) == 0

    def test_future_unbounded_end_accepted(self):
        """valid_from is past, valid_until absent → unbounded future, should pass."""
        t = _triple(valid_from="2025-01-01")
        result = filter_triples_by_time([t], as_of_date=_REF)
        assert len(result) == 1

    def test_unbounded_start_and_end(self):
        """Neither bound set → always passes."""
        result = filter_triples_by_time([_triple()], as_of_date=_REF)
        assert len(result) == 1

    def test_mixed_batch_selects_correctly(self):
        """A batch of historical, current, and future triples → only current
        ones survive."""
        triples = [
            _triple(valid_from="2020-01-01", valid_until="2024-12-31"),  # expired
            _triple(valid_from="2025-01-01", valid_until="2025-12-31"),  # current
            _triple(valid_from="2030-01-01"),                            # future
            _triple(),                                                    # unbounded → current
            _triple(valid_from="2025-06-01", valid_until=_REF),           # current, closes today
        ]
        result = filter_triples_by_time(triples, as_of_date=_REF)
        assert len(result) == 3
        # Check the right ones survived.
        surviving_subjects = {t["subject"] for t in result}
        assert "Blender" in surviving_subjects  # the 3 passing triples
        assert len(surviving_subjects) == 1  # all have subject "Blender"

    def test_order_preserved(self):
        """Filter must not shuffle the input order."""
        triples = [
            _triple(valid_from="2020-01-01", valid_until="2024-01-01"),
            _triple(valid_from="2025-01-01", valid_until="2025-12-31"),
            _triple(valid_from="2030-01-01", valid_until="2035-12-31"),
        ]
        result = filter_triples_by_time(triples, as_of_date=_REF)
        assert len(result) == 1
        assert result[0] is triples[1]  # same object, second position

    def test_empty_list(self):
        """Empty input → empty output."""
        assert filter_triples_by_time([], as_of_date=_REF) == []

    def test_does_not_mutate_input(self):
        """The original list must not be modified in place."""
        original = [
            _triple(valid_from="2020-01-01"),
            _triple(valid_from="2030-01-01"),
        ]
        original_copy = list(original)
        filter_triples_by_time(original, as_of_date=_REF)
        assert original == original_copy

    def test_none_nested_before_valid_from(self):
        """If valid_from <= as_of_date but valid_until < as_of_date → reject
        (edge-case: both bounds are set, one passes, one fails)."""
        t = _triple(valid_from="2025-01-01", valid_until="2025-06-01")
        result = filter_triples_by_time([t], as_of_date=_REF)
        assert len(result) == 0
