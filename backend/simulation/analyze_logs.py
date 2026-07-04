#!/usr/bin/env python3
"""
VELYNX Phase 63 — Counterfactual Ledger Analyzer
=================================================

Standalone CLI that reads the JSON Lines ledger written by
:class:`~backend.simulation.logger.CausalLogger` and prints a clean,
aggregated terminal report of the counterfactual experiments it records.

The report shows:

* Total simulations run.
* Percentage of simulations that flipped the answer.
* The Top 3 most frequently modified entities.
* The average ``confidence_delta`` across all runs.

A ``--tail N`` flag restricts the analysis to the last *N* runs — handy for
watching what the most recent batch of counterfactuals did.

Ledger record shape (produced by ``CausalLogger``)::

    {
      "schema": "velynx.causal-delta/v1",
      "seq": 42,
      "ts": "2026-06-24T18:03:11.482341Z",
      "host": "workstation",
      "pid": 12345,
      "payload": {
          "answer_flipped": true,
          "confidence_delta": -0.31,
          "premise": {"Tesla Model 3": {"mobility_type": "hover"}},
          ...
      },
      "extra": {"run_id": "ab12"}
    }

Strict isolation contract
-------------------------
This module imports **only** the Python standard library. It does not import
``backend.simulation.logger`` (or anything else from ``backend.*``); it reads
the ledger file directly by path so it can be run against any ledger copy,
including on machines where the full stack is not installed.

Usage
-----
::

    # Full report over the default ledger:
    python -m backend.simulation.analyze_logs

    # Last 10 runs only:
    python -m backend.simulation.analyze_logs --tail 10

    # Point at a specific ledger file:
    python -m backend.simulation.analyze_logs --ledger path/to/ledger.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

__all__ = [
    "DEFAULT_LEDGER_PATH",
    "LedgerReport",
    "analyze_ledger",
    "load_records",
    "main",
]

# Default ledger location, resolved relative to *this* module so it matches
# CausalLogger's DEFAULT_LEDGER_PATH regardless of the caller's working dir.
DEFAULT_LEDGER_PATH: Path = (
    Path(__file__).resolve().parent / "logs" / "counterfactual_ledger.jsonl"
)

# How many top entities to surface in the report.
TOP_ENTITIES_LIMIT = 3


# ══════════════════════════════════════════════════════════════════════════════
# Reading the ledger
# ══════════════════════════════════════════════════════════════════════════════


def load_records(ledger_path: Path) -> List[Dict[str, Any]]:
    """Parse a JSON Lines ledger into a list of record dicts.

    Lines that are blank, comments, or fail to parse as JSON are skipped
    silently — the same resilient posture the logger's own ``iter_records``
    takes, so a single corrupt line never blocks analysis.

    Tombstone records (written by the logger when a write fails) carry a
    ``"kind": "tombstone"`` marker and no ``payload``; those are dropped here
    because they do not represent a real simulation result.
    """
    records: List[Dict[str, Any]] = []
    if not ledger_path.exists():
        return records

    with open(ledger_path, "r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                # Resilient: skip the bad line, keep the surviving history.
                continue
            if not isinstance(record, dict):
                continue
            # Skip tombstones and any record lacking a usable payload.
            if record.get("kind") == "tombstone":
                continue
            if not isinstance(record.get("payload"), dict):
                continue
            records.append(record)
    return records


def _payload(record: Dict[str, Any]) -> Dict[str, Any]:
    """Return the ``payload`` dict from a ledger record."""
    payload = record.get("payload")
    return payload if isinstance(payload, dict) else {}


def _modified_entities(payload: Dict[str, Any]) -> List[str]:
    """Extract the names of entities modified by a single counterfactual run.

    A ``CausalDelta`` payload stores the premise as
    ``{entity_name: {attr: value, ...}}``. The top-level keys are the modified
    entities. Missing/empty premise → empty list (nothing was modified).
    """
    premise = payload.get("premise")
    if not isinstance(premise, dict):
        return []
    return [str(name) for name in premise.keys() if name]


# ══════════════════════════════════════════════════════════════════════════════
# Aggregation
# ══════════════════════════════════════════════════════════════════════════════


class LedgerReport:
    """Aggregated statistics over a (possibly windowed) slice of the ledger.

    Attributes
    ----------
    total
        Number of valid simulation records analyzed.
    flip_count
        How many of those resulted in ``answer_flipped == True``.
    flip_percent
        ``flip_count / total * 100``, or ``0.0`` when the slice is empty.
    avg_confidence_delta
        Arithmetic mean of ``confidence_delta`` across all records with a
        finite numeric value, or ``0.0`` when none are present.
    top_entities
        List of ``(entity_name, count)`` for the most frequently modified
        entities, most common first.
    """

    def __init__(self) -> None:
        self.total: int = 0
        self.flip_count: int = 0
        self.avg_confidence_delta: float = 0.0
        self.top_entities: List[tuple] = []

    @property
    def flip_percent(self) -> float:
        return (self.flip_count / self.total * 100.0) if self.total else 0.0


def analyze_ledger(records: List[Dict[str, Any]]) -> LedgerReport:
    """Aggregate a list of ledger records into a :class:`LedgerReport`.

    Only records carrying a usable ``payload`` dict should be passed in (the
    reader already filters these out), but every access is defensive so a
    malformed payload degrades gracefully instead of crashing the report.
    """
    report = LedgerReport()
    report.total = len(records)
    if not report.total:
        return report

    flip_count = 0
    delta_sum = 0.0
    delta_n = 0
    entity_counts: Counter = Counter()

    for record in records:
        payload = _payload(record)

        # Answer flip.
        if payload.get("answer_flipped") is True:
            flip_count += 1

        # Confidence delta — only average finite numbers.
        delta = payload.get("confidence_delta")
        if isinstance(delta, (int, float)) and delta == delta:  # filters NaN
            delta_sum += float(delta)
            delta_n += 1

        # Modified entities.
        for name in _modified_entities(payload):
            entity_counts[name] += 1

    report.flip_count = flip_count
    report.avg_confidence_delta = (delta_sum / delta_n) if delta_n else 0.0
    report.top_entities = entity_counts.most_common(TOP_ENTITIES_LIMIT)
    return report


# ══════════════════════════════════════════════════════════════════════════════
# Rendering
# ══════════════════════════════════════════════════════════════════════════════

# Box-drawing characters for the report border.
_BORDER = "═"
_WIDTH = 54


def _box(title: str) -> str:
    """Return a bordered title line for the report header."""
    inner = f"  {title}  "
    pad = max(0, _WIDTH - len(inner))
    return "╔" + _BORDER * _WIDTH + "╗\n" + "║" + inner + " " * pad + "║"


def format_report(
    report: LedgerReport,
    *,
    ledger_path: Path,
    window: Optional[int],
) -> str:
    """Render a :class:`LedgerReport` as a human-readable terminal string.

    Parameters
    ----------
    report
        The aggregated statistics to render.
    ledger_path
        Ledger file the report was built from (shown in the header).
    window
        ``--tail`` value, if any (shown in the header as a scope note).
    """
    lines: List[str] = []
    lines.append(_box("VELYNX — Counterfactual Ledger Report"))
    lines.append("╚" + _BORDER * _WIDTH + "╝")
    lines.append("")
    lines.append(f"  Ledger  : {ledger_path}")
    scope = f"last {window} runs" if window is not None else "all runs"
    lines.append(f"  Scope   : {scope}")
    lines.append("")

    if report.total == 0:
        lines.append("  (no simulation records found)")
        lines.append("")
        return "\n".join(lines)

    # Summary metrics.
    lines.append(f"  Total simulations        : {report.total}")
    lines.append(
        f"  Answer flips             : {report.flip_count} "
        f"({report.flip_percent:.1f}%)"
    )
    lines.append(f"  Avg confidence delta     : {report.avg_confidence_delta:+.4f}")
    lines.append("")

    # Top modified entities.
    lines.append("  Top modified entities:")
    if report.top_entities:
        # Pad entity names to the longest one for a tidy column.
        name_width = min(
            max(len(name) for name, _ in report.top_entities),
            32,
        )
        for rank, (name, count) in enumerate(report.top_entities, start=1):
            label = name if len(name) <= name_width else name[: name_width - 1] + "…"
            pct = count / report.total * 100.0
            lines.append(
                f"    {rank}. {label:<{name_width}}  "
                f"{count:>3} run(s)  ({pct:.1f}% of runs)"
            )
    else:
        lines.append("    (no entity modifications recorded)")
    lines.append("")

    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════════


def _iter_records_tail(path: Path, n: int) -> List[Dict[str, Any]]:
    """Return the last *n* valid records from *path*.

    Reading is already O(file size); slicing in memory keeps the code simple
    and resilient (the skip-on-bad-line policy stays identical to the full
    read). The ledger is append-only and bounded by simulation volume, so the
    whole-file read is acceptable here.

    ``n == 0`` is handled explicitly because ``list[-0:]`` is the *whole*
    list — "last 0 runs" must mean an empty window.
    """
    if n <= 0:
        return []
    return load_records(path)[-n:]


def build_arg_parser() -> argparse.ArgumentParser:
    """Construct the argparse CLI for the analyzer."""
    parser = argparse.ArgumentParser(
        prog="analyze_logs",
        description=(
            "Analyze the VELYNX counterfactual ledger and print an aggregated "
            "terminal report (total runs, answer-flip rate, top modified "
            "entities, average confidence delta)."
        ),
    )
    parser.add_argument(
        "--ledger",
        type=Path,
        default=DEFAULT_LEDGER_PATH,
        help=(
            "Path to the counterfactual_ledger.jsonl file "
            f"(default: {DEFAULT_LEDGER_PATH})."
        ),
    )
    parser.add_argument(
        "--tail",
        type=int,
        default=None,
        metavar="N",
        help="Only analyze the last N simulation runs.",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point. Returns a process exit code."""
    args = build_arg_parser().parse_args(argv)
    ledger_path: Path = args.ledger

    if not ledger_path.exists():
        print(
            f"analyze_logs: ledger not found at {ledger_path}\n"
            "Hint: run some counterfactual simulations first, or pass "
            "--ledger <path>.",
            file=sys.stderr,
        )
        return 1

    if args.tail is not None and args.tail < 0:
        print("analyze_logs: --tail must be a non-negative integer.", file=sys.stderr)
        return 2

    records = (
        _iter_records_tail(ledger_path, args.tail)
        if args.tail is not None
        else load_records(ledger_path)
    )
    report = analyze_ledger(records)
    print(format_report(report, ledger_path=ledger_path, window=args.tail))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
