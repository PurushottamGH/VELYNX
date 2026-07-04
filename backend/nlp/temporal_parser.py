"""
VELYNX Phase 64 — Temporal Bounds Parser
=========================================

Translates natural-language time references into **strict ISO-8601 date bounds**
that can be written directly into a knowledge triple's ``valid_from`` /
``valid_until`` columns.

Given free-form text, :func:`extract_temporal_bounds` returns a 2-tuple

    ``(start_iso, end_iso)``

where each element is either an ISO-8601 ``YYYY-MM-DD`` string or ``None``.

Design philosophy
-----------------
* **Precision over recall.** When a construct is ambiguous we return
  ``(None, None)`` rather than fabricate a bound. A missing temporal bound is
  cheap; a *wrong* one silently corrupts the knowledge graph.
* **Stdlib only.** Uses just :mod:`re` and :mod:`datetime` — no external NLP
  dependency, no model download, no circular import risk.
* **Leaf utility.** No imports from any other VELYNX module. Safe to call from
  anywhere in the pipeline.
* **Reference-clock agnostic.** All inferences are relative to the explicit
  ``today`` argument (defaulting to :func:`datetime.date.today`), which makes the
  output fully deterministic and unit-testable.

Supported surface forms
-----------------------
A. **Explicit ranges** — "from 2019 to 2023", "between 2015 and 2018",
   "2010–2020", "2010-2020".
B. **Open-ended start** — "since 2019", "since Jan 2020", "from 2018".
C. **Open-ended end** — "until 2023", "through 2024", "ending in 2019".
D. **Bare year / month / day anchors** — "in 2021", "Jan 2020",
   "March 15, 2022". These describe a *point*, not a window; the parser widens
   them to the smallest bracket that contains the point (full year / month /
   day). A lone point yields a **closed** window ``[start, start_end]``.

Anything that does not match a recognised construct returns ``(None, None)``.
"""

from __future__ import annotations

import re
from calendar import monthrange
from datetime import date


# ════════════════════════════════════════════════════════════════════════════ #
#  Month name tables
# ════════════════════════════════════════════════════════════════════════════ #

_MONTH_NAMES: dict[str, int] = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "jun": 6, "jul": 7, "aug": 8, "sep": 9,
    "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}


# ════════════════════════════════════════════════════════════════════════════ #
#  Regex catalog
# ════════════════════════════════════════════════════════════════════════════ #
# Every expression is anchored with word boundaries / whitespace so a phrase
# like "from 2019 to 2023" is not accidentally matched inside "mid-2019".

_RE_YEAR = r"(\d{4})"
_RE_MONTH_NUM = r"(0?[1-9]|1[0-2])"
_RE_DAY = r"(0?[1-9]|[12]\d|3[01])"
_RE_MONTH_NAME = r"(" + "|".join(_MONTH_NAMES) + r")\.?"

# A single "anchor" — the smallest addressable point in time we support.
# Captures, in order:  (year) (month_name|month_num)? (day)?
_RE_ANCHOR = (
    rf"(?:{_RE_MONTH_NAME}\s+)?{_RE_YEAR}(?:\s*[/\-]\s*{_RE_MONTH_NUM})?"
    rf"(?:\s*[/\-]\s*{_RE_DAY})?"
    rf"|{_RE_DAY}\s+{_RE_MONTH_NAME}\s+{_RE_YEAR}"
    rf"|{_RE_MONTH_NAME}\.?\s+{_RE_DAY},?\s+{_RE_YEAR}"
)
_RE_ANCHOR_C = re.compile(_RE_ANCHOR, re.IGNORECASE)

# Range connectors — "from X to/through Y", "between X and Y",
# "since X until Y", and bare "X to Y" / "X - Y".  The leading keyword is
# *optional* so connector-only forms ("Jan 2020 to Feb 2020") still bind; this
# is safe because ``_RE_ANCHOR`` requires a 4-digit year, which rules out
# spurious numeric spans like "5 to 10".
_RE_RANGE = re.compile(
    rf"""
    (?:from|between|since\s)?\s*                       # optional opener
    (?P<a>{_RE_ANCHOR})                                # opening anchor
    \s+(?:to|until|through|and|[\u2013\-])\s+
    (?P<b>{_RE_ANCHOR})                                # closing anchor
    """,
    re.IGNORECASE | re.VERBOSE,
)

# Bare numeric range "2019-2023" / "2019 – 2023".  Anchored so we only fire on
# two adjacent years separated by a dash — never inside a longer token.  The
# trailing lookahead also rejects a following ``-\d`` / ``/\d`` so that a
# malformed date or numeric ID like "2024-2025-30" is not mistaken for a range.
_RE_YEARRANGE = re.compile(r"(?<!\d)(\d{4})\s*[\u2013\-]\s*(\d{4})(?!\d|[-/]\s*\d)")

# Open-ended START ("since", "from")  →  (start, None)
_RE_SINCE = re.compile(
    rf"(?:since|from|starting(?:\s+in)?\s+)\s*(?P<a>{_RE_ANCHOR})",
    re.IGNORECASE,
)

# Open-ended END ("until", "through", "ending in")  →  (None, end).
# A single trailing ``\s+`` separates the keyword from the anchor for *every*
# branch (the previous form dropped the gap on the bare ``until``/``through``
# branches, so "until 2023" failed to match).
_RE_UNTIL = re.compile(
    rf"(?:"
    rf"until\s+the\s+end\s+of"      # longest first — beats plain "until"
    rf"|until|till|through"
    rf"|ending\s+(?:in|on)"
    rf"|ends?\s+(?:in|on)"
    rf")\s+(?P<a>{_RE_ANCHOR})",
    re.IGNORECASE,
)

# ── Anchor sub-patterns (named groups, used by _parse_anchor) ────────────────
# These are matched with ``fullmatch`` against a single normalised anchor
# substring, so each one pins the exact granularity we can resolve.

_RE_DAY_FIRST = re.compile(                       # "15 March 2022"
    rf"(?P<d>{_RE_DAY})\s+(?P<mon>{_RE_MONTH_NAME})\s+(?P<y>{_RE_YEAR})",
    re.IGNORECASE,
)
_RE_MON_DAY = re.compile(                         # "March 15, 2022"
    rf"(?P<mon>{_RE_MONTH_NAME})\.?\s+(?P<d>{_RE_DAY}),?\s+(?P<y>{_RE_YEAR})",
    re.IGNORECASE,
)
_RE_MON_YEAR = re.compile(                        # "March 2022"
    rf"(?P<mon>{_RE_MONTH_NAME})\.?\s+(?P<y>{_RE_YEAR})",
    re.IGNORECASE,
)
_RE_YMD = re.compile(                             # "2022" / "2022-03" / "2022-03-15"
    rf"(?P<y>{_RE_YEAR})"
    rf"(?:\s*[/\-]\s*(?P<mon>{_RE_MONTH_NUM}))?"
    rf"(?:\s*[/\-]\s*(?P<d>{_RE_DAY}))?",
)


# ════════════════════════════════════════════════════════════════════════════ #
#  Public API
# ════════════════════════════════════════════════════════════════════════════ #

def extract_temporal_bounds(
    text: str,
    *,
    today: date | None = None,
) -> tuple[str | None, str | None]:
    """Extract ``valid_from`` / ``valid_until`` ISO-8601 bounds from free text.

    Parameters
    ----------
    text:
        The raw natural-language string to inspect.
    today:
        Optional reference date (defaults to :func:`datetime.date.today`).
        Injected purely so tests can pin the clock; production callers leave
        this unset.

    Returns
    -------
    ``(start_iso, end_iso)`` — each is a ``YYYY-MM-DD`` string or ``None``.
    Returns ``(None, None)`` when no unambiguous temporal construct is found.

    Precedence (first match wins)
    -----------------------------
    1. Explicit range      → ``(start, end)``
    2. Open-ended start    → ``(start, None)``
    3. Open-ended end      → ``(None, end)``
    4. Bare numeric range  → ``(start, end)``
    5. Single point anchor → ``(start, end_of_point)``  (closed window)
    6. Otherwise           → ``(None, None)``
    """
    if not text or not text.strip():
        return (None, None)

    ref = today or date.today()

    # 1. Explicit range — "from 2019 to 2023".  If the user *did* write a range
    # but the endpoints are contradictory (start after end), we do NOT fall
    # through to the looser open-ended matchers — a detected-but-invalid range
    # is ambiguous, and ambiguity must yield ``(None, None)``.
    m = _RE_RANGE.search(text)
    if m:
        a = _parse_anchor(m.group("a"), ref)
        b = _parse_anchor(m.group("b"), ref)
        if a and b:
            start = _start_of(a)
            end = _end_of(b)
            if start <= end:
                return (_iso(start), _iso(end))
            # Endpoints don't form a valid window → stop, don't salvage.
            return (None, None)

    # 2. Open-ended start — "since 2019" / "from 2018".
    m = _RE_SINCE.search(text)
    if m:
        a = _parse_anchor(m.group("a"), ref)
        if a:
            return (_iso(_start_of(a)), None)

    # 3. Open-ended end — "until 2023".
    m = _RE_UNTIL.search(text)
    if m:
        a = _parse_anchor(m.group("a"), ref)
        if a:
            return (None, _iso(_end_of(a)))

    # 4. Bare year-range — "2019-2023".
    m = _RE_YEARRANGE.search(text)
    if m:
        y1, y2 = int(m.group(1)), int(m.group(2))
        if y1 <= y2:
            return (f"{y1:04d}-01-01", f"{y2:04d}-12-31")

    # 5. Single point anchor — "in 2021", "Jan 2020".  A bare numeric anchor
    # must be a *standalone* token: a run like "2024-2025-30" (a malformed
    # date / ID) is rejected so we don't silently truncate it to "Feb 2024".
    for m in _RE_ANCHOR_C.finditer(text):
        if not _is_standalone_token(text, m.start(), m.end()):
            continue
        a = _parse_anchor(m.group(0), ref)
        if a:
            return (_iso(_start_of(a)), _iso(_end_of(a)))

    return (None, None)


# ════════════════════════════════════════════════════════════════════════════ #
#  Internal helpers
# ════════════════════════════════════════════════════════════════════════════ #
# An "anchor" is the coarsest granularity we can resolve from the text:
#   * day    → exact date
#   * month  → month of a year
#   * year   → a whole year
# We never produce sub-day resolution; the parser deliberately rounds outward.

class _Anchor:
    __slots__ = ("year", "month", "day")

    def __init__(self, year: int, month: int | None, day: int | None) -> None:
        self.year = year
        self.month = month
        self.day = day


def _is_standalone_token(text: str, start: int, end: int) -> bool:
    """True when the span ``text[start:end]`` is not embedded in a longer
    alphanumeric/dash run.

    Used to reject bare-numeric anchors that are really fragments of a longer
    identifier (e.g. ``2024-2025-30``), where the regex would otherwise
    truncate the match to ``2024-2``.  A leading/trailing word character or a
    contiguous ``-``/``/`` digit means the token continues beyond the match.
    """
    if start > 0:
        prev = text[start - 1]
        if prev.isalnum() or prev in "-/._":
            return False
    if end < len(text):
        nxt = text[end]
        if nxt.isalnum() or nxt in "-/._":
            return False
    return True


def _parse_anchor(raw: str, ref: date) -> _Anchor | None:
    """Reduce a raw anchor string to a :class:`_Anchor`.

    Returns ``None`` on any malformed token rather than raising — callers
    treat that as "no bound found".
    """
    if not raw:
        return None
    s = raw.strip().lower().rstrip(".,;:")
    if not s:
        return None

    year: int | None = None
    month: int | None = None
    day: int | None = None

    # Each branch uses *named* groups so capture indices are unambiguous.
    if m := _RE_DAY_FIRST.fullmatch(s):           # "15 March 2022"
        day = int(m.group("d"))
        month = _month(m.group("mon"))
        year = int(m.group("y"))
    elif m := _RE_MON_DAY.fullmatch(s):            # "March 15, 2022"
        month = _month(m.group("mon"))
        day = int(m.group("d"))
        year = int(m.group("y"))
    elif m := _RE_MON_YEAR.fullmatch(s):           # "March 2022"
        month = _month(m.group("mon"))
        year = int(m.group("y"))
    elif m := _RE_YMD.fullmatch(s):                # "2022", "2022-03", "2022-03-15"
        year = int(m.group("y"))
        if m.group("mon"):
            month = int(m.group("mon"))
        if m.group("d"):
            day = int(m.group("d"))

    if year is None or not (1 <= year <= 9999):
        return None
    if month is not None and not (1 <= month <= 12):
        return None
    if day is not None and month is not None:
        max_day = monthrange(year, month)[1]
        if not (1 <= day <= max_day):
            return None
    elif day is not None and month is None:
        return None  # a bare day without month is meaningless

    return _Anchor(year, month, day)


def _month(token: str) -> int:
    """Map a (lower-cased) month token to its ordinal 1–12."""
    return _MONTH_NAMES[token.lower().rstrip(".")]


def _start_of(a: _Anchor) -> date:
    """Inclusive lower edge of the anchor's bracket."""
    return date(a.year, a.month or 1, a.day or 1)


def _end_of(a: _Anchor) -> date:
    """Inclusive upper edge of the anchor's bracket."""
    month = a.month or 12
    last_day = a.day or monthrange(a.year, month)[1]
    return date(a.year, month, last_day)


def _iso(d: date) -> str:
    return d.isoformat()
