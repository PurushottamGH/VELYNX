#!/usr/bin/env python3
"""
Knowledge Graph Visualizer (Mermaid.js Generator)
=================================================

Reads the live VELYNX knowledge graph from SQLite and emits a Mermaid.js
flowchart (`graph TD`) suitable for pasting into any markdown renderer that
supports mermaid blocks (GitHub, GitLab, VS Code, Obsidian, ...).

Primary data source is the `triples` table (subject / relation / object).
If `triples` is empty, the script falls back to the `edges` table
(source_concept / target_concept), and standalone concepts from `nodes`
are rendered as isolated nodes so silent drops never happen.

Usage
-----
    # full graph (auto-filters to --target neighborhood above 50 nodes)
    python backend/tools/visualize_graph.py

    # force a small view of one entity and its 1-hop neighborhood
    python backend/tools/visualize_graph.py --target "VELYNX" --depth 1

    # write to disk instead of (or in addition to) stdout
    python backend/tools/visualize_graph.py --out debug_graph.md

    # point at a different db (there are several *.db files in this repo)
    python backend/tools/visualize_graph.py --db backend/velynx_data/knowledge_graph/graph.db

Exit codes: 0 ok, 2 empty/inaccessible db.
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

# Matches anything that is NOT [A-Za-z0-9_] (Mermaid node id charset).
# Non-ascii letters etc. must be folded to ascii ids; the original label is
# preserved inside quotes so the visual stays faithful.
_INVALID_ID_CHARS = re.compile(r"[^A-Za-z0-9_]")
# Mermaid node-label quoting follows graphviz-style: escape quotes/backslash.
_LABEL_BAD = re.compile(r'(["\\])')

# Above this many *visible* nodes we refuse to render the whole graph unless a
# --target filter has been supplied. Keeps renderers from choking.
NODE_HARD_LIMIT = 50


# --------------------------------------------------------------------------- #
# Model
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Triple:
    """A single directed edge: subject --(relation)--> object."""

    subject: str
    relation: str
    object: str
    confidence: Optional[float] = None

    @property
    def endpoints(self) -> Tuple[str, str]:
        return self.subject, self.object


@dataclass
class Graph:
    """In-memory view of the knowledge graph after any filtering."""

    triples: List[Triple] = field(default_factory=list)
    isolated_nodes: List[str] = field(default_factory=list)

    @property
    def nodes(self) -> Set[str]:
        out: Set[str] = set()
        for t in self.triples:
            out.add(t.subject)
            out.add(t.object)
        out.update(self.isolated_nodes)
        return out


# --------------------------------------------------------------------------- #
# Persistence / loading
# --------------------------------------------------------------------------- #
def load_graph(db_path: Path) -> Graph:
    """Read triples (then edges, then nodes) from the sqlite db.

    Order is deliberate: `triples` is the live cognitive table; `edges`/
    `nodes` are legacy/structural and only consulted when triples is empty.
    """
    if not db_path.exists():
        raise FileNotFoundError(f"graph db not found: {db_path}")

    # `uri=true` lets us open read-only, so we never risk mutating state during
    # a stress test. immutable=1 would be stronger but can mask live updates.
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        conn.row_factory = sqlite3.Row
        tables = {
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        return _read_graph(conn, tables)
    finally:
        conn.close()


def _read_graph(conn: sqlite3.Connection, tables: Set[str]) -> Graph:
    triples: List[Triple] = []

    if "triples" in tables:
        rows = _safe_fetch(conn, "SELECT subject, relation, object, confidence FROM triples")
        triples = [
            Triple(
                subject=str(r[0]),
                relation=str(r[1]),
                object=str(r[2]),
                confidence=_to_float(r[3]) if len(r) > 3 else None,
            )
            for r in rows
            if r[0] and r[1] and r[2]  # skip null endpoints defensively
        ]

    if not triples and "edges" in tables:
        rows = _safe_fetch(conn, "SELECT source_concept, target_concept FROM edges")
        triples = [
            Triple(subject=str(r[0]), relation="related_to", object=str(r[1]))
            for r in rows
            if r[0] and r[1]
        ]

    isolated: List[str] = []
    if "nodes" in tables:
        covered = {t.subject for t in triples} | {t.object for t in triples}
        rows = _safe_fetch(conn, "SELECT concept FROM nodes")
        isolated = [str(r[0]) for r in rows if r[0] and str(r[0]) not in covered]

    return Graph(triples=triples, isolated_nodes=isolated)


def _safe_fetch(conn: sqlite3.Connection, query: str) -> List[sqlite3.Row]:
    """Run a SELECT; tolerate missing columns by narrowing the query."""
    try:
        return conn.execute(query).fetchall()
    except sqlite3.OperationalError:
        # Column was renamed/absent — retry with the minimum viable projection.
        return []


def _to_float(val: object) -> Optional[float]:
    try:
        return float(val)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


# --------------------------------------------------------------------------- #
# Filtering
# --------------------------------------------------------------------------- #
def filter_to_neighborhood(
    graph: Graph, target: str, depth: int = 1
) -> Graph:
    """BFS over the triple set, keeping nodes within `depth` hops of `target`.

    Edges are kept only if *both* endpoints survive, so the neighborhood is
    internally consistent rather than dangling.
    """
    target_norm = target.strip().lower()
    if not target_norm:
        return graph

    # Build an undirected adjacency index once. Direction of the original edge
    # is preserved on the Triple; this index is just for reachability.
    adjacency: Dict[str, Set[str]] = {}
    for t in graph.triples:
        s, o = t.endpoints
        adjacency.setdefault(s, set()).add(o)
        adjacency.setdefault(o, set()).add(s)

    # Resolve the seed case-insensitively, so the operator doesn't have to
    # remember exact capitalisation ("velynx" vs "VELYNX").
    seed: Optional[str] = next(
        (n for n in adjacency if n.lower() == target_norm), None
    )
    if seed is None:
        # No seed found — surface clearly rather than emitting an empty graph.
        raise SystemExit(
            f"--target '{target}' not found in graph. "
            f"Known nodes are written to stderr; aborting."
        )

    # BFS frontier expansion.
    frontier: Set[str] = {seed}
    kept: Set[str] = set(frontier)
    for _ in range(max(0, depth)):
        nxt: Set[str] = set()
        for node in frontier:
            nxt.update(adjacency.get(node, set()))
        nxt -= kept
        if not nxt:
            break
        kept |= nxt
        frontier = nxt

    kept_triples = [
        t for t in graph.triples if t.subject in kept and t.object in kept
    ]
    kept_isolated: List[str] = []  # isolated nodes are never in a neighborhood
    return Graph(triples=kept_triples, isolated_nodes=kept_isolated)


# --------------------------------------------------------------------------- #
# Mermaid rendering
# --------------------------------------------------------------------------- #
def render_mermaid(graph: Graph, title: str = "VELYNX Knowledge Graph") -> str:
    """Render the graph as a `graph TD` mermaid string.

    Design notes:
      * Node ids are sanitised to [A-Za-z0-9_]; the human-readable label is
        quoted separately so unicode / spaces / punctuation survive intact.
      * Relation text sits on the edge pipe: `A -- "relation" --> B`.
      * Duplicate edges are de-duped (a frequent artefact of re-ingestion).
    """
    lines: List[str] = [f"%% {title}", "graph TD", ""]

    if not graph.nodes:
        lines.append("    empty[/'Graph has no nodes yet'/]")
        return "\n".join(lines) + "\n"

    id_map: Dict[str, str] = {}

    def node_id(label: str, counter: List[int]) -> str:
        if label in id_map:
            return id_map[label]
        counter[0] += 1
        slug = _INVALID_ID_CHARS.sub("_", label).strip("_") or "n"
        # Prefix numeric/empty slugs so mermaid doesn't choke, and disambiguate
        # collisions ("a-b" and "a_b" both fold to "a_b").
        nid = f"N{counter[0]}_{slug}"[:48]
        id_map[label] = nid
        return nid

    counter: List[int] = [0]

    # Declare every node with its label explicitly. Doing it up front keeps the
    # output stable regardless of edge order and makes isolated nodes visible.
    for label in sorted(graph.nodes):
        nid = node_id(label, counter)
        lines.append(f'    {nid}["{_escape_label(label)}"]')

    if graph.triples:
        lines.append("")
        seen_edges: Set[Tuple[str, str, str]] = set()
        for t in sorted(graph.triples, key=lambda x: (x.subject, x.object, x.relation)):
            src = id_map[t.subject]
            dst = id_map[t.object]
            key = (src, dst, t.relation)
            if key in seen_edges:
                continue
            seen_edges.add(key)
            rel = _escape_label(t.relation)
            conf = f" ({t.confidence:.2f})" if t.confidence is not None else ""
            lines.append(f'    {src} -- "{rel}{conf}" --> {dst}')

    return "\n".join(lines) + "\n"


def _escape_label(text: str) -> str:
    """Quote-escape a label for use inside mermaid `["..."]`."""
    return _LABEL_BAD.sub(r"\\\1", text)


def wrap_markdown(mermaid: str, title: str = "VELYNX Knowledge Graph") -> str:
    header = f"# {title}\n\n"
    return f"{header}```mermaid\n{mermaid}```\n"


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _build_arg_parser(default_db: Path) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Render the VELYNX knowledge graph as a Mermaid flowchart.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        "--db",
        type=Path,
        default=default_db,
        help="Path to the SQLite knowledge-graph db.",
    )
    p.add_argument(
        "--target",
        type=str,
        default=None,
        help=(
            "Entity to centre the view on. Required when the graph exceeds "
            f"{NODE_HARD_LIMIT} nodes; otherwise optional."
        ),
    )
    p.add_argument(
        "--depth",
        type=int,
        default=1,
        help="Neighborhood radius (hops) around --target.",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Write a markdown file (mermaid code block) to this path.",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Render the full graph even when it exceeds the node limit.",
    )
    p.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress the mermaid text on stdout (use with --out).",
    )
    return p


def main(argv: Optional[Iterable[str]] = None) -> int:
    repo_root = Path(__file__).resolve().parents[2]
    default_db = repo_root / "velynx_data" / "knowledge_graph" / "graph.db"

    args = _build_arg_parser(default_db).parse_args(argv)

    try:
        graph = load_graph(Path(args.db))
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    total = len(graph.nodes)
    print(f"# loaded {total} nodes, {len(graph.triples)} edges from {args.db}",
          file=sys.stderr)

    if not graph.nodes:
        mermaid = render_mermaid(graph)
        _emit(mermaid, args)
        return 0

    # Large-graph policy: require a target, unless the operator overrides.
    if total > NODE_HARD_LIMIT and not args.target and not args.force:
        print(
            f"error: graph has {total} nodes (> {NODE_HARD_LIMIT}). "
            f"Pass --target <entity> to visualise a neighborhood, "
            f"or --force to render everything.",
            file=sys.stderr,
        )
        return 2

    if args.target:
        try:
            graph = filter_to_neighborhood(graph, args.target, depth=args.depth)
        except SystemExit:
            # Neighborhood miss — list candidates to help the operator recover.
            _print_known_nodes(graph)
            raise
        print(
            f"# filtered to {len(graph.nodes)} nodes around "
            f"'{args.target}' (depth={args.depth})",
            file=sys.stderr,
        )

    mermaid = render_mermaid(graph)
    _emit(mermaid, args)
    return 0


def _emit(mermaid: str, args: argparse.Namespace) -> None:
    if args.out:
        args.out.write_text(
            wrap_markdown(mermaid), encoding="utf-8"
        )
        print(f"# wrote {args.out}", file=sys.stderr)
    if not args.quiet:
        sys.stdout.write(mermaid)
        if not mermaid.endswith("\n"):
            sys.stdout.write("\n")


def _print_known_nodes(graph: Graph) -> None:
    nodes = sorted(graph.nodes)
    print("# known nodes (first 200):", file=sys.stderr)
    for n in nodes[:200]:
        print(f"#   {n}", file=sys.stderr)
    if len(nodes) > 200:
        print(f"#   ...and {len(nodes) - 200} more", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
