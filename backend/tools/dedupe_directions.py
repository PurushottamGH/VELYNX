#!/usr/bin/env python3
"""
VELYNX Phase 57 — Direction-Canonicalization Migration (Fix C)
==============================================================

Standalone one-shot migration that strips **directionally-inverted duplicate**
edges from the live knowledge graph for asymmetric predicates.

Background
----------
The bidirectional edge-keying artifact: the same underlying assertion was
extracted in two voices and stored as two rows that disagree on direction —

    ("ton roosendaal", "create", "blender")      # active voice
    ("blender",        "create", "ton roosendaal")  # passive voice

— both describing ONE fact (Ton is Blender's creator). The consolidator's
Phase-57 write-path guard (:func:`backend.knowledge.consolidator.\
_canonicalize_asymmetric_direction`) and the reasoner's adjacency dedup
(:meth:`backend.cognition.reasoning_engine.ReasoningEngine._build_graph`)
prevent NEW duplicates. This script removes the LEGACY ones already in the
database so retrieval counts and contradiction detection are no longer
inflated by the doubled edge.

Direction policy (must match the consolidator)
----------------------------------------------
For ``create`` / ``located_in`` the canonical subject is the
**functional-identity endpoint** — the entity for which the relation is
single-valued:

  * ``create``     -> "has exactly one creator"      -> the ARTIFACT
                     ("blender", "create", "ton roosendaal")
  * ``located_in`` -> "is located somewhere"         -> the located entity
                     ("blender foundation", "located_in", "amsterdam")

This is mandated by the belief-revision contract
``pending_singular[(subject, relation)] = obj``, which keys deprecation on
``(subject, relation)`` and assumes the OBJECT is the singular VALUE. Only an
artifact-as-subject ordering makes that collision key flag "two creators of
the same artifact" instead of "one creator made two artifacts".

Selection rule when BOTH directions exist for the same endpoint pair:
    1. Keep the row whose direction already matches the canonical policy
       (artifact / functional-identity endpoint in subject position). This
       preserves a correctly-stored fact and only drops its inverted twin.
    2. If NEITHER row matches the policy (rare: both endpoints are bare proper
       nouns with no role signal, so direction is ambiguous), keep the row
       whose lowercased subject <= lowercased object — the same deterministic
       tiebreak the consolidator applies on the write path, so the migration's
       choice is reproducible and matches what future writes would produce.
    3. Drop every other row that is a duplicate of the kept one under any
       direction, plus exact textual duplicates.

What gets removed
-----------------
For each asymmetric predicate (``create``, ``located_in``, and any surface
synonym the predicate resolver collapses onto them), grouped by the unordered
endpoint pair {a, b}:

    * The inverted twin of a canonical-direction row.
    * Exact textual duplicates of the kept row (same source, relation, target).
    * When no canonical-direction row exists, all-but-one lexicographic winner.

Predicates that are NOT in the asymmetric set (``requires``, ``related_to``,
``produces``, ...) are order-invariant and are left untouched by default. The
``relationships`` table has no UNIQUE constraint on (source, relation, target),
so exact textual duplicates accumulate there as a separate ingestion artifact;
pass ``--include-symmetric-exact-dups`` to collapse them at the same time
(default OFF — the stated scope of this migration is direction inversion only).

Idempotent: running twice is a no-op. The second run finds no inverted pairs
to remove.

Usage
-----
    # default target: the active brain (data/knowledge_graph.db) — DRY RUN
    python backend/tools/dedupe_directions.py

    # apply the deletion
    python backend/tools/dedupe_directions.py --apply

    # also migrate the raw triples store (velynx_data/knowledge_graph/graph.db)
    python backend/tools/dedupe_directions.py --apply --include-raw

    # custom db path
    python backend/tools/dedupe_directions.py --db path/to/graph.db --apply

Exit codes: 0 ok, 1 no relationships table / unreadable db, 2 bad CLI args.
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# ── Canonical-direction policy (single source of truth) ────────────────────────
# MUST stay in sync with backend.knowledge.consolidator._ASYMMETRIC_PREDICATES
# and backend.cognition.reasoning_engine._ASYMMETRIC_PREDICATES. All three hold
# the core predicate forms the predicate resolver collapses surface synonyms
# (create/author/build/found/invent/develop/design, located/lives/resides/...)
# onto, so a single membership test here covers every surface variant.
_ASYMMETRIC_PREDICATES: Set[str] = frozenset({"create", "located_in"})

# Role markers identifying the AGENT endpoint of an asymmetric relation. When
# one endpoint matches ("the creator of blender", "author of krita"), that
# endpoint is the agent and the OTHER is the functional-identity endpoint that
# the canonical policy wants in subject position. Mirrors the consolidator's
# _AGENT_ROLE_RE so the migration's notion of "agent" matches the write path.
_AGENT_ROLE_MARKERS: Tuple[str, ...] = (
    "creator", "author", "founder", "inventor", "developer", "designer",
    "maker", "builder", "writer", "composer", "artist", "director",
    "producer", "architect", "engineer",
)


# ── Data model ────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class Edge:
    """A stored relationship row, frozen for hashing/dedup."""

    id: int
    source: str
    relation: str
    target: str

    @property
    def endpoints(self) -> Tuple[str, str]:
        return self.source, self.target

    def is_agent_role(self, value: str) -> bool:
        """True when ``value`` looks like an agent-role phrase."""
        low = value.lower()
        return any(marker in low for marker in _AGENT_ROLE_MARKERS)


@dataclass
class MigrationReport:
    """Per-db summary of what the migration did."""

    db_path: Path
    scanned: int = 0
    asym_groups: int = 0          # endpoint-pair groups under asymmetric preds
    inverted_removed: int = 0     # inverted twins dropped
    exact_dups_removed: int = 0   # exact textual duplicates dropped
    non_asym_deduped: int = 0     # exact dups on symmetric preds dropped
    kept: int = 0
    sample_removals: List[str] = field(default_factory=list)

    def add_sample(self, edge: Edge, reason: str) -> None:
        if len(self.sample_removals) < 20:
            self.sample_removals.append(
                f"  [{reason}] id={edge.id} "
                f"({edge.source!r} -[{edge.relation}]-> {edge.target!r})"
            )

    def summary(self) -> str:
        lines = [
            f"db: {self.db_path}",
            f"  edges scanned          : {self.scanned}",
            f"  asym endpoint-pairs    : {self.asym_groups}",
            f"  inverted twins removed : {self.inverted_removed}",
            f"  exact dups (asym)      : {self.exact_dups_removed}",
            f"  exact dups (symmetric) : {self.non_asym_deduped}",
            f"  edges kept             : {self.kept}",
        ]
        if self.sample_removals:
            lines.append("  sample removals:")
            lines.extend(self.sample_removals)
        return "\n".join(lines)


# ── Direction logic ───────────────────────────────────────────────────────────
def _is_asymmetric(relation: str) -> bool:
    """True when ``relation`` is in the asymmetric set (core form or synonym).

    Tries the predicate resolver so surface synonyms ("authored", "lives in")
    collapse onto a core form before the membership check. Falls back to a
    literal membership test so the script stays usable even if the resolver
    module is unavailable (e.g. running outside the package import root).
    """
    raw = (relation or "").strip().lower().replace("-", "_").replace(" ", "_")
    if raw in _ASYMMETRIC_PREDICATES:
        return True
    try:
        from backend.knowledge.predicate_resolver import predicate_resolver

        core = predicate_resolver.resolve(relation)
        return core in _ASYMMETRIC_PREDICATES
    except Exception:
        return False


def _canonical_subject(edge: Edge) -> str:
    """Return the endpoint that should be the SUBJECT under the canonical policy.

    For ``create`` the functional-identity endpoint is the ARTIFACT (it holds
    "has one creator"); for ``located_in`` it is the located entity. We detect
    the agent by role-marker matching; the non-agent endpoint wins subject
    position. With no role signal we fall back to the lexicographic-minimum
    endpoint, matching the consolidator's write-path tiebreak.
    """
    s_agent = edge.is_agent_role(edge.source)
    t_agent = edge.is_agent_role(edge.target)
    if s_agent and not t_agent:
        return edge.target
    if t_agent and not s_agent:
        return edge.source
    if edge.source.strip().lower() <= edge.target.strip().lower():
        return edge.source
    return edge.target


def _endpoint_pair_key(edge: Edge) -> Tuple[str, str]:
    """Unordered (sorted) lowercased endpoint pair — the dedup identity."""
    a, b = edge.source.strip().lower(), edge.target.strip().lower()
    return (a, b) if a <= b else (b, a)


# ── DB plumbing ───────────────────────────────────────────────────────────────
def _resolve_db_path(cli_path: Optional[Path]) -> Path:
    if cli_path is not None:
        return cli_path.resolve()
    # Default to the active-brain graph the reasoner walks.
    try:
        from backend.knowledge.knowledge_graph import DB_PATH

        return Path(DB_PATH).resolve()
    except Exception:
        return Path("data/knowledge_graph.db").resolve()


def _load_edges(conn: sqlite3.Connection) -> List[Edge]:
    """Read every relationship row. Returns [] if the table is absent."""
    try:
        cur = conn.execute(
            "SELECT id, source, relation, target FROM relationships"
        )
    except sqlite3.OperationalError:
        return []
    return [
        Edge(id=int(r[0]), source=str(r[1] or ""), relation=str(r[2] or ""),
             target=str(r[3] or ""))
        for r in cur.fetchall()
    ]


def _delete_edges(conn: sqlite3.Connection, ids: List[int]) -> int:
    if not ids:
        return 0
    # Chunked deletion — SQLite has a variable host limit (~999 by default).
    chunk = 500
    deleted = 0
    for i in range(0, len(ids), chunk):
        batch = ids[i:i + chunk]
        placeholders = ",".join("?" * len(batch))
        cur = conn.execute(
            f"DELETE FROM relationships WHERE id IN ({placeholders})",
            batch,
        )
        deleted += cur.rowcount or 0
    return deleted


# ── Core migration ────────────────────────────────────────────────────────────
def plan_migration(
    edges: List[Edge],
    *,
    include_symmetric_exact_dups: bool = False,
) -> Tuple[List[int], MigrationReport, Path]:
    """Decide which edge ids to delete. Pure — touches no database.

    Parameters
    ----------
    edges:
        All relationship rows currently in the table.
    include_symmetric_exact_dups:
        When True, also collapse byte-for-byte duplicate rows on symmetric
        predicates (a separate ingestion artifact). Default False — the
        migration's stated scope is direction inversion only.

    Returns ``(ids_to_delete, report, db_path_placeholder)``. The db_path is
    filled by the caller; this function only produces the plan.
    """
    # We need a throwaway db_path on the report; replaced by caller.
    report = MigrationReport(db_path=Path("<plan>"))
    report.scanned = len(edges)
    drop_ids: List[int] = []

    # Split rows by predicate class.
    asym: List[Edge] = []
    sym: List[Edge] = []
    for e in edges:
        if not e.source or not e.relation or not e.target:
            # Malformed row — leave it for the consolidator's skip logic; the
            # migration's job is direction dedup, not row validation.
            continue
        if _is_asymmetric(e.relation):
            asym.append(e)
        else:
            sym.append(e)

    # ── Asymmetric: collapse by unordered endpoint pair ────────────────────
    groups: Dict[Tuple[str, Tuple[str, str]], List[Edge]] = defaultdict(list)
    for e in asym:
        groups[(e.relation.strip().lower(), _endpoint_pair_key(e))].append(e)

    report.asym_groups = len(groups)

    for (_rel, _pair), members in groups.items():
        if len(members) <= 1:
            continue
        # Choose the keeper. The canonical subject is a property of the
        # ENDPOINT PAIR (the non-agent endpoint, or lex-min with no role
        # signal) — the same for every twin — so it is computed once and every
        # member tested against it. Prefer a twin whose stored direction already
        # matches the policy (preserves a correctly-stored fact); tie-break by
        # lowest id (oldest insertion) so the choice is stable and traceable.
        canonical_source_norm = _canonical_subject(members[0]).strip().lower()
        matching = [
            m for m in members
            if m.source.strip().lower() == canonical_source_norm
        ]
        keeper = min(matching or members, key=lambda m: m.id)

        keep_exact = (keeper.source.strip().lower(),
                      keeper.relation.strip().lower(),
                      keeper.target.strip().lower())
        for m in members:
            if m.id == keeper.id:
                continue
            m_exact = (m.source.strip().lower(), m.relation.strip().lower(),
                       m.target.strip().lower())
            if m_exact == keep_exact:
                drop_ids.append(m.id)
                report.exact_dups_removed += 1
                report.add_sample(m, "exact-dup")
            else:
                drop_ids.append(m.id)
                report.inverted_removed += 1
                report.add_sample(m, "inverted-twin")

    # ── Symmetric: exact-textual-duplicate collapse (opt-in) ───────────────
    # Symmetric predicates are order-invariant; there is no canonical
    # direction to enforce, so by default they are left ENTIRELY alone. When
    # the operator opts in we only drop rows that are byte-for-byte
    # (case-insensitive) duplicates of an earlier row — never on direction
    # grounds.
    if include_symmetric_exact_dups:
        seen_exact: Set[Tuple[str, str, str]] = set()
        for e in sorted(sym, key=lambda m: m.id):
            key = (e.source.strip().lower(), e.relation.strip().lower(),
                   e.target.strip().lower())
            if key in seen_exact:
                drop_ids.append(e.id)
                report.non_asym_deduped += 1
                report.add_sample(e, "sym-exact-dup")
            else:
                seen_exact.add(key)

    report.kept = report.scanned - len(drop_ids)
    # Dedup drop_ids in case an id somehow entered twice (defensive).
    return sorted(set(drop_ids)), report, Path("<plan>")


def migrate_db(
    db_path: Path,
    apply: bool,
    *,
    include_symmetric_exact_dups: bool = False,
) -> MigrationReport:
    """Plan + (optionally) apply the migration on a single database."""
    if not db_path.exists():
        raise FileNotFoundError(f"relationships db not found: {db_path}")

    # Read via the shared WAL-aware connector so concurrent readers (the live
    # pipeline) don't get a "database is locked" during our scan.
    try:
        from backend.memory._sqlite import connect as open_connection
    except Exception:
        open_connection = None  # type: ignore[assignment]

    conn = (open_connection(str(db_path)) if open_connection
            else sqlite3.connect(str(db_path)))
    try:
        edges = _load_edges(conn)
        if not edges:
            report = MigrationReport(db_path=db_path)
            report.kept = 0
            return report

        drop_ids, report, _ = plan_migration(
            edges,
            include_symmetric_exact_dups=include_symmetric_exact_dups,
        )
        report.db_path = db_path

        if apply and drop_ids:
            deleted = _delete_edges(conn, drop_ids)
            conn.commit()
            # Reconcile reported counts with the actual DELETE rowcount in case
            # of concurrent writes between plan and apply.
            if deleted != len(drop_ids):
                print(
                    f"  note: planned {len(drop_ids)} deletions, "
                    f"SQLite removed {deleted} (concurrent writes possible)",
                    file=sys.stderr,
                )
            report.kept = max(0, report.scanned - deleted)
        return report
    finally:
        conn.close()


# ── CLI ───────────────────────────────────────────────────────────────────────
def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Strip directionally-inverted duplicate edges for asymmetric "
            "predicates (create, located_in) from the VELYNX knowledge graph."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        "--db",
        type=Path,
        default=None,
        help="Path to a relationships DB. Default: active brain graph.",
    )
    p.add_argument(
        "--apply",
        action="store_true",
        help="Apply the deletion. Without it the script is a DRY RUN.",
    )
    p.add_argument(
        "--include-raw",
        action="store_true",
        help=(
            "Also migrate the raw triples store "
            "(velynx_data/knowledge_graph/graph.db) in addition to the "
            "active brain."
        ),
    )
    p.add_argument(
        "--include-symmetric-exact-dups",
        action="store_true",
        help=(
            "Also collapse byte-for-byte duplicate rows on symmetric "
            "predicates (a separate ingestion artifact). Default OFF: the "
            "migration's stated scope is direction inversion only."
        ),
    )
    p.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-db summary blocks on success.",
    )
    return p


def _raw_triples_db_path() -> Optional[Path]:
    try:
        from backend.memory.knowledge_graph import _DB_PATH  # type: ignore

        return Path(_DB_PATH).resolve()
    except Exception:
        # Best-effort fallback location used elsewhere in the stack.
        candidate = Path("velynx_data/knowledge_graph/graph.db").resolve()
        return candidate if candidate.exists() else None


def main(argv: Optional[List[str]] = None) -> int:
    args = _build_arg_parser().parse_args(argv)

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"# dedupe_directions — {mode}", file=sys.stderr)

    targets: List[Path] = []
    primary = _resolve_db_path(args.db)
    targets.append(primary)
    if args.include_raw:
        raw = _raw_triples_db_path()
        if raw is None:
            print(
                "# --include-raw requested but raw triples DB not found; "
                "skipping raw target.",
                file=sys.stderr,
            )
        elif raw in targets:
            print(
                f"# raw target {raw} is the same file as the primary; "
                "not migrating twice.",
                file=sys.stderr,
            )
        else:
            targets.append(raw)

    overall_deleted = 0
    for db_path in targets:
        try:
            report = migrate_db(
                db_path,
                apply=args.apply,
                include_symmetric_exact_dups=args.include_symmetric_exact_dups,
            )
        except FileNotFoundError as exc:
            print(f"error: {exc}", file=sys.stderr)
            continue
        overall_deleted += (
            report.inverted_removed
            + report.exact_dups_removed
            + report.non_asym_deduped
        )
        if not args.quiet:
            print(report.summary(), file=sys.stderr)

    action = "removed" if args.apply else "would remove"
    print(
        f"# total edges {action}: {overall_deleted} "
        f"(re-run without --apply to verify it is now a no-op)",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
