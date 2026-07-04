"""
Falsifiable test suite — Phase 64 Temporal Bounds Parser
=========================================================

Proves that :func:`extract_temporal_bounds` translates the supported
natural-language constructs into strict ISO-8601 ``(valid_from, valid_until)``
bounds — and, just as importantly, returns ``(None, None)`` for anything it
cannot resolve unambiguously.

Every assertion in this file can FAIL — there are no tautologies.  The parser
is a pure function (deterministic once ``today`` is pinned), so no clock-mock
shenanigans are required.
"""

from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.nlp.temporal_parser import extract_temporal_bounds

# A pinned reference date so day/month-arithmetic is deterministic.  The parser
# itself ignores it for these constructs, but we pass it explicitly to guarantee
# the tests never depend on the wall clock.
_REF = None  # tests that need a clock pass an explicit date.


# ═══════════════════════════════════════════════════════════════════════════ #
#  Contract examples — the three the task pins verbatim
# ═══════════════════════════════════════════════════════════════════════════ #

class TestContractExamples:
    """The exact strings from the Phase 64 spec — must hold verbatim."""

    def test_closed_range(self):
        assert extract_temporal_bounds(
            "Sam was CEO from 2019 to 2023"
        ) == ("2019-01-01", "2023-12-31")

    def test_open_start_since(self):
        assert extract_temporal_bounds(
            "Sam has been CEO since 2019"
        ) == ("2019-01-01", None)

    def test_ambiguous_yields_none(self):
        assert extract_temporal_bounds(
            "Back when GPT-4 launched..."
        ) == (None, None)


# ═══════════════════════════════════════════════════════════════════════════ #
#  Closed ranges  →  (start, end)
# ═══════════════════════════════════════════════════════════════════════════ #

class TestClosedRanges:
    def test_from_year_to_year(self):
        assert extract_temporal_bounds("from 2019 to 2023") == (
            "2019-01-01",
            "2023-12-31",
        )

    def test_between_and(self):
        assert extract_temporal_bounds("between 2015 and 2018") == (
            "2015-01-01",
            "2018-12-31",
        )

    def test_since_until_combo(self):
        assert extract_temporal_bounds("since 2019 until 2023") == (
            "2019-01-01",
            "2023-12-31",
        )

    def test_numeric_year_range_dash(self):
        assert extract_temporal_bounds("2019-2023") == ("2019-01-01", "2023-12-31")

    def test_numeric_year_range_en_dash(self):
        assert extract_temporal_bounds("2019 \u2013 2023") == (
            "2019-01-01",
            "2023-12-31",
        )

    def test_year_range_with_surrounding_text(self):
        assert extract_temporal_bounds("active 2019 - 2023") == (
            "2019-01-01",
            "2023-12-31",
        )

    def test_month_granularity_range(self):
        assert extract_temporal_bounds("from 2020-03 to 2021-06") == (
            "2020-03-01",
            "2021-06-30",
        )

    def test_named_month_range(self):
        assert extract_temporal_bounds("Jan 2020 to Feb 2020") == (
            "2020-01-01",
            "2020-02-29",  # leap year
        )

    def test_reversed_range_is_rejected(self):
        """A range whose start is AFTER its end must not produce a bound."""
        assert extract_temporal_bounds("from 2023 to 2019") == (None, None)


# ═══════════════════════════════════════════════════════════════════════════ #
#  Open-ended start  →  (start, None)
# ═══════════════════════════════════════════════════════════════════════════ #

class TestOpenStart:
    def test_since_year(self):
        assert extract_temporal_bounds("since 2019") == ("2019-01-01", None)

    def test_since_named_month(self):
        assert extract_temporal_bounds("since Jan 2020") == ("2020-01-01", None)

    def test_from_year_alone(self):
        assert extract_temporal_bounds("from 2018") == ("2018-01-01", None)


# ═══════════════════════════════════════════════════════════════════════════ #
#  Open-ended end  →  (None, end)
# ═══════════════════════════════════════════════════════════════════════════ #

class TestOpenEnd:
    def test_until_year(self):
        assert extract_temporal_bounds("until 2023") == (None, "2023-12-31")

    def test_through_year(self):
        assert extract_temporal_bounds("through 2024") == (None, "2024-12-31")

    def test_till_year(self):
        assert extract_temporal_bounds("till 2022") == (None, "2022-12-31")


# ═══════════════════════════════════════════════════════════════════════════ #
#  Single point anchors  →  (start, end_of_point)   [closed window]
# ═══════════════════════════════════════════════════════════════════════════ #

class TestPointAnchors:
    def test_bare_year(self):
        assert extract_temporal_bounds("in 2021") == ("2021-01-01", "2021-12-31")

    def test_named_month_year(self):
        assert extract_temporal_bounds("Feb 2019") == ("2019-02-01", "2019-02-28")

    def test_named_month_year_leap(self):
        assert extract_temporal_bounds("Feb 2020") == ("2020-02-01", "2020-02-29")

    def test_month_name_first_with_day(self):
        assert extract_temporal_bounds("March 15, 2022") == (
            "2022-03-15",
            "2022-03-15",
        )

    def test_day_first(self):
        assert extract_temporal_bounds("15 March 2022") == (
            "2022-03-15",
            "2022-03-15",
        )

    def test_abbreviated_month_with_dot(self):
        assert extract_temporal_bounds("Apr. 1, 2023") == (
            "2023-04-01",
            "2023-04-01",
        )

    def test_numeric_iso_date(self):
        assert extract_temporal_bounds("2022-07-04") == (
            "2022-07-04",
            "2022-07-04",
        )


# ═══════════════════════════════════════════════════════════════════════════ #
#  Negative cases  →  (None, None)
# ═══════════════════════════════════════════════════════════════════════════ #

class TestNegativeCases:
    """Precision-over-recall: ambiguity must yield (None, None)."""

    @pytest.mark.parametrize(
        "text",
        [
            "",
            "   ",
            "no dates here at all",
            "There are 5 to 10 items",          # bare numerics, no year
            "Order 2024-2025-30 is valid",      # malformed numeric token
            "Back when GPT-4 launched",
            "He is tall and happy",
        ],
    )
    def test_returns_none_none(self, text):
        assert extract_temporal_bounds(text) == (None, None)

    def test_year_alone_inside_longer_number(self):
        """A 4-digit year must not be lifted out of a longer number."""
        assert extract_temporal_bounds("ID 12345678") == (None, None)


# ═══════════════════════════════════════════════════════════════════════════ #
#  Return-type contract
# ═══════════════════════════════════════════════════════════════════════════ #

class TestReturnType:
    def test_always_two_tuple(self):
        out = extract_temporal_bounds("from 2019 to 2023")
        assert isinstance(out, tuple)
        assert len(out) == 2

    def test_elements_are_str_or_none(self):
        out = extract_temporal_bounds("since 2019")
        assert all(x is None or isinstance(x, str) for x in out)

    def test_iso_format_when_present(self):
        """Any non-None element must be a valid ``YYYY-MM-DD`` string."""
        import re
        iso = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        for out in (
            extract_temporal_bounds("from 2019 to 2023"),
            extract_temporal_bounds("since 2019"),
            extract_temporal_bounds("until 2023"),
            extract_temporal_bounds("March 15, 2022"),
        ):
            for el in out:
                if el is not None:
                    assert iso.match(el), f"bad ISO: {el!r}"


# ═══════════════════════════════════════════════════════════════════════════ #
#  Determinism
# ═══════════════════════════════════════════════════════════════════════════ #

class TestDeterminism:
    def test_same_input_same_output(self):
        t = "Sam was CEO from 2019 to 2023"
        first = extract_temporal_bounds(t)
        for _ in range(5):
            assert extract_temporal_bounds(t) == first
