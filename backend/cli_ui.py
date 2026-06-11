"""
VELYNX CLI Dashboard — Split-screen cognitive visualizer.
Uses only `rich` (no external deps). Renders the full pipeline
state into a terminal layout: Header | Brain (left) + Voice (right) | Footer.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from typing import Any

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

# Ensure stdout can handle the Tree guide chars and Rich box art.
# Some Windows legacy consoles (cmd.exe, pwsh 5) default to cp1252
# which lacks └├─┼ etc.  Promoting to UTF-8 avoids the error at render time.
if sys.stdout.encoding and "utf" not in sys.stdout.encoding.lower():
    sys.stdout.reconfigure(encoding="utf-8")  # Python 3.7+


# ── Minimal renderable group (Rich 15 removed rich.group.Group) ────────
class _Group:
    """Yield multiple renderables as a single renderable via ``__rich_console__``."""
    def __init__(self, *renderables: object) -> None:
        self._renderables = [r for r in renderables if r is not None]

    def __rich_console__(self, console: Console, options: object) -> object:
        for r in self._renderables:
            yield r

# ── Shared console (no markup in this module, but downstreams may) ──────
console = Console(force_terminal=True, safe_box=True)

# ── Color tokens ─────────────────────────────────────────────────────────
_CYAN = "bold cyan"
_MAGENTA = "bold magenta"
_GREEN = "bold green"
_RED = "bold red"
_YELLOW = "bold yellow"
_WHITE = "bold white"
_DIM = "dim white"
_GREY = "grey58"
_ORANGE = "dark_orange"

CONCEPT_STYLE = {
    "personal": _CYAN,
    "structural": _RED,
    "none": _CYAN,
}
BRIDGE_STYLE = _YELLOW
DOMAIN_STYLE = _ORANGE


def _confidence_style(confidence: float) -> str:
    if confidence >= 0.75:
        return _GREEN
    if confidence >= 0.45:
        return _YELLOW
    return _RED


def _route_style(route: str) -> str:
    return CONCEPT_STYLE.get(route, _DIM)


def _build_header(
    route_type: str,
    elapsed_ms: float,
    query: str,
    confidence: float,
    status: str,
    dissonance: list | None = None,
) -> Panel:
    parts = Text()
    parts.append("VELYNX COGNITIVE CORE", style=_WHITE)
    parts.append("  |  ", style=_DIM)
    parts.append("VRAM: Persistent", style=_GREEN)
    parts.append("  |  ", style=_DIM)
    parts.append(f"Latency: {elapsed_ms:.1f}ms", style=_CYAN)
    parts.append("  |  ", style=_DIM)
    route_label = route_type.upper() if route_type else "NONE"
    parts.append(f"Route: {route_label}", style=_route_style(route_type))
    parts.append("  |  ", style=_DIM)

    confidence_styled = _confidence_style(confidence)
    parts.append(f"Confidence: {confidence:.2f}", style=confidence_styled)
    parts.append("  |  ", style=_DIM)
    status_style = _GREEN if status == "strong" else (_YELLOW if status == "partial" else _RED)
    parts.append(f"Status: {status.title()}", style=status_style)

    # Query on second line
    sub = Text()
    sub.append("Query: ", style=_DIM)
    sub.append(f'"{query}"', style=_WHITE)

    table = Table.grid(padding=0)
    table.add_row(parts)
    table.add_row(sub)

    # Dissonance warning line
    if dissonance:
        for d in (dissonance if isinstance(dissonance, list) else [dissonance]):
            dissonance_line = Text()
            a = d["concept_a"].title()
            b = d["concept_b"].title()
            dissonance_line.append(
                f"[⚠ COGNITIVE DISSONANCE: {a} vs {b}]",
                style="bold red on yellow",
            )
            table.add_row(dissonance_line)

    return Panel(table, style=_DIM, border_style=_DIM)


def _build_soul_tree(soul_result: dict) -> Tree:
    route = soul_result.get("domain_route", "none")
    color = _route_style(route)
    tree = Tree(f"[{color}]>> SOUL PATH[/{color}]")

    if route == "structural":
        tree.add("[dim]Bypassed — structural triage active[/]")
        return tree

    concepts = soul_result.get("concepts", [])
    scores = soul_result.get("scores", {})

    if not concepts:
        tree.add(f"[{_DIM}]No concepts activated[/]")
        return tree

    for c in concepts:
        score = scores.get(c, 0.0)
        branch = tree.add(f"[{_CYAN}]{c}[/{_CYAN}]  [{_DIM}]({score:.2f})[/]")
        _add_score_bars(branch, score)

    return tree


def _add_score_bars(branch, score: float) -> None:
    bar_len = min(int(score * 5), 20)
    if bar_len > 0:
        filled = "#" * bar_len
        empty = "-" * (20 - bar_len)
        branch.add(f"[{_DIM}]{filled}{empty}[/]")


def _build_bridge_tree(bridge_connections: list[dict]) -> Tree:
    tree = Tree(f"[{BRIDGE_STYLE}]>> BRIDGE NODES[/{BRIDGE_STYLE}]")
    if not bridge_connections:
        tree.add(f"[{_DIM}]None — no cross-domain routing[/]")
        return tree

    for bc in bridge_connections:
        soul = bc.get("soul", "?")
        domain = bc.get("domain", "?")
        label = Text()
        label.append(soul.title(), style=_CYAN)
        label.append(" -> ", style=_DIM)
        label.append(domain.title(), style=_ORANGE)
        tree.add(label)
    return tree


def _build_domain_tree(
    domain_concepts: list[str],
    domain_arc: str | None,
    route_type: str,
) -> Tree:
    if not route_type or route_type == "personal":
        tree_label = f"[{DOMAIN_STYLE}]>> DOMAIN PATH[/{DOMAIN_STYLE}]"
    else:
        tree_label = f"[{_RED}]>> DOMAIN PATH (STRUCTURAL)[/{_RED}]"
    tree = Tree(tree_label)

    if not domain_concepts:
        tree.add(f"[{_DIM}]Not traversed — no domain bridge[/]")
        return tree

    for dc in domain_concepts:
        tree.add(f"[{_ORANGE}]{dc}[/{_ORANGE}]")

    if domain_arc:
        arc_node = tree.add(f"[{_DIM}]Arc:[/]")
        for segment in domain_arc.split("; "):
            segment = segment.strip()
            if segment:
                arc_node.add(f"[{_DIM}]{segment}[/]")

    return tree


def _build_voice_panel(speech: str, meta_packet: dict) -> Panel:
    soul_result = meta_packet if "meta" in meta_packet else {}
    meta = soul_result.get("meta", meta_packet.get("meta", {}))
    confidence = meta.get("confidence", 0.0)
    status = meta.get("status", "gap")
    gaps = meta_packet.get("gaps", [])

    content = Text()

    # Confidence badge
    cstyle = _confidence_style(confidence)
    status_icon = {"strong": "+", "partial": "~", "gap": "-"}.get(status, "-")
    content.append(f" {status_icon} Confidence: {confidence:.2f}  Status: {status.title()}\n\n", style=cstyle)

    # The speech output
    if speech:
        content.append(speech, style=_WHITE)
    else:
        content.append("[No speech compiled]", style=_DIM)

    # Gaps warning
    if gaps:
        content.append("\n\n", style=_DIM)
        content.append(" [!] Gaps detected:\n", style=_RED)
        for g in gaps:
            reason = g.get("reason", "")
            term = g.get("concept") or g.get("raw_term", "")
            content.append(f"   • {term}: {reason}\n", style=_YELLOW)

    return Panel(content, title="Compiled Output", border_style=_GREEN, title_align="left")


def _build_temporal_context(
    temporal_context: dict[str, Any] | None,
) -> Tree:
    tree = Tree(f"[{_MAGENTA}]>> TEMPORAL CONTEXT[/{_MAGENTA}]")

    if not temporal_context:
        tree.add(f"[{_DIM}]No prior context[/]")
        return tree

    status = temporal_context.get("status", "")
    route = temporal_context.get("route_type", "none")
    soul = temporal_context.get("primary_soul_concept") or "?"
    domain = temporal_context.get("primary_domain_concept") or "?"
    timestamp = temporal_context.get("timestamp", "")
    confidence = temporal_context.get("confidence_score", 0.0)
    intensity = temporal_context.get("current_intensity", confidence)

    try:
        dt = datetime.fromisoformat(timestamp)
        if dt.tzinfo is not None:
            now = datetime.now(timezone.utc)
        else:
            now = datetime.now()
        delta = now - dt.replace(tzinfo=None) if dt.tzinfo is None else now - dt
        hours_ago = delta.total_seconds() / 3600
        if hours_ago < 1:
            age_str = f"{delta.total_seconds() / 60:.0f}m ago"
        elif hours_ago < 24:
            age_str = f"{hours_ago:.0f}h ago"
        else:
            age_str = f"{hours_ago / 24:.0f}d ago"
    except (ValueError, TypeError):
        age_str = "unknown"

    if status == "healed":
        healed = Text()
        healed.append("System Healed: Previous state has decayed.", style=_GREEN)
        tree.add(healed)
    else:
        label = Text()
        label.append("Previous State: ", style=_DIM)
        label.append(f"[{soul.title()}]", style=_CYAN)
        label.append(" -> ", style=_DIM)
        label.append(f"[{domain.title()}]", style=_ORANGE)
        label.append(f" (Intensity: {intensity:.2f})", style=_DIM)
        tree.add(label)

        detail = Text()
        detail.append(f"Route: {route.upper()}  |  Age: {age_str}", style=_DIM)
        tree.add(detail)

    return tree


def _build_cognitive_routing_panel(
    cognitive_packet: dict,
    temporal_context: dict[str, Any] | None = None,
) -> Panel:
    soul_result = cognitive_packet.get("soul_result", {})
    domain_concepts = cognitive_packet.get("domain_concepts", [])
    domain_arc = cognitive_packet.get("domain_arc", "")
    bridge_connections = cognitive_packet.get("bridge_connections", [])
    route_type = soul_result.get("domain_route", "none")

    soul_tree = _build_soul_tree(soul_result)
    bridge_tree = _build_bridge_tree(bridge_connections)
    domain_tree = _build_domain_tree(domain_concepts, domain_arc, route_type)

    temporal_tree = _build_temporal_context(temporal_context)
    content = _Group(soul_tree, bridge_tree, domain_tree, temporal_tree)

    route_label = route_type.upper() if route_type else "NONE"
    return Panel(content, title=f"Cognitive Routing [{route_label}]", border_style=_route_style(route_type), title_align="left")


def _build_footer(query: str | None = None) -> Panel:
    content = Text()
    content.append("> ", style=_GREEN)
    if query:
        content.append(query, style=_WHITE)
    else:
        content.append("Awaiting input...", style=_DIM)
    return Panel(content, style=_DIM, border_style=_DIM)


class VelynxDashboard:
    """
    Full-screen split terminal visualizer for the VELYNX cognitive pipeline.

    Usage::

        dashboard = VelynxDashboard()
        layout = dashboard.render_response(
            query=query,
            cognitive_packet=cognitive_packet,
            meta_packet=meta_packet,
            execution_time=elapsed_ms,
            compiled_speech=speech,
        )
        console.print(layout)
    """

    def __init__(self) -> None:
        self._last_query: str | None = None

    def render_response(
        self,
        query: str,
        cognitive_packet: dict[str, Any],
        meta_packet: dict[str, Any],
        execution_time: float,
        compiled_speech: str,
        temporal_context: dict[str, Any] | None = None,
    ) -> Layout:
        """
        Populate the full-screen Layout from pipeline outputs and return it.

        Parameters
        ----------
        query:
            The original user query string.
        cognitive_packet:
            Dict from ``cross_query()``. Expected keys:
            ``soul_result``, ``domain_concepts``, ``bridge_connections``,
            ``domain_arc``, ``unified_arc``, ``cross_domain``.
        meta_packet:
            Dict from ``reflect()``. Expected keys:
            ``meta`` (with ``confidence``, ``status``, …), ``gaps``, plus
            all ``soul_result`` fields.
        execution_time:
            Pipeline wall-clock in milliseconds.
        compiled_speech:
            Final NLG string from ``compile_path_to_speech()``.
        temporal_context:
            Most recent memory row from ``MemoryCore.retrieve_recent_state(1)``,
            or None if no prior experiences exist.
        """
        self._last_query = query

        soul_result = cognitive_packet.get("soul_result", {})
        meta = meta_packet.get("meta", {})

        route_type = soul_result.get("domain_route", "none")
        confidence = meta.get("confidence", 0.0)
        status = meta.get("status", "gap")
        dissonance = cognitive_packet.get("dissonance_detected")

        # ── Build layout ──────────────────────────────────────────────────
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=6),
            Layout(name="body"),
            Layout(name="footer", size=3),
        )
        layout["body"].split_row(
            Layout(name="left", ratio=1),
            Layout(name="right", ratio=1),
        )

        layout["header"].update(
            _build_header(route_type, execution_time, query, confidence, status, dissonance)
        )
        layout["left"].update(_build_cognitive_routing_panel(cognitive_packet, temporal_context))
        layout["right"].update(_build_voice_panel(compiled_speech, meta_packet))
        layout["footer"].update(_build_footer(query))

        return layout

    def render_to_string(
        self,
        query: str,
        cognitive_packet: dict[str, Any],
        meta_packet: dict[str, Any],
        execution_time: float,
        compiled_speech: str,
    ) -> str:
        """Same as ``render_response`` but returns the rendered string without
        ANSI codes — useful for logging, embedding, or non-terminal display."""
        import io

        layout = self.render_response(
            query, cognitive_packet, meta_packet, execution_time, compiled_speech, temporal_context=None
        )
        buf = io.StringIO()
        c = Console(file=buf, force_terminal=False, safe_box=True, width=120)
        c.print(layout)
        return buf.getvalue()


if __name__ == "__main__":
    # ── Demo mode: produce a full layout from synthetic data ────────────
    from rich import print as rprint

    dashboard = VelynxDashboard()

    demo_cognitive = {
        "query": "I feel like a failure and I lost faith in myself",
        "soul_result": {
            "query": "I feel like a failure and I lost faith in myself",
            "query_type": "scenario",
            "concepts": ["shame", "identity", "trust", "depression", "loss"],
            "scores": {
                "shame": 3.75,
                "identity": 2.50,
                "trust": 0.42,
                "depression": 0.38,
                "loss": 0.22,
            },
            "arc": "Shame leads through identity and arrives at trust",
            "soul_used": True,
            "confidence_hint": "CERTAIN",
            "triage": {
                "route": "personal",
                "personal_hits": [
                    "i feel like a failure",
                    "i lost faith in myself",
                ],
                "structural_hits": [],
            },
            "domain_route": "personal",
            "domain_hits": {},
        },
        "domain_concepts": ["debugging", "technical debt", "testing"],
        "bridge_connections": [
            {"soul": "shame", "domain": "debugging"},
            {"soul": "identity", "domain": "refactoring"},
        ],
        "domain_arc": "debugging requires testing; debugging produces technical debt",
        "unified_arc": "Shame leads through identity and arrives at trust | Bridges: shame->debugging, identity->refactoring | Domain: debugging requires testing; debugging produces technical debt",
        "cross_domain": True,
    }
    demo_meta: dict[str, Any] = {
        "query": "I feel like a failure and I lost faith in myself",
        "query_type": "scenario",
        "concepts": ["shame", "identity", "trust", "depression", "loss"],
        "scores": {
            "shame": 3.75,
            "identity": 2.50,
            "trust": 0.42,
            "depression": 0.38,
            "loss": 0.22,
        },
        "arc": "Shame leads through identity and arrives at trust",
        "soul_used": True,
        "confidence_hint": "CERTAIN",
        "triage": {
            "route": "personal",
            "personal_hits": [
                "i feel like a failure",
                "i lost faith in myself",
            ],
            "structural_hits": [],
        },
        "domain_route": "personal",
        "domain_hits": {},
        "meta": {"confidence": 0.91, "status": "strong", "weak_concepts": [], "missing_signals": []},
        "gaps": [],
    }
    demo_speech = (
        "Shame leads through identity and arrives at trust. "
        "The experience of Shame maps directly onto debugging in systems. "
        "Debugging requires testing. Debugging produces technical debt."
    )

    rprint("[bold white]\nVELYNX CLI UI — Demo Mode[/]\n")

    layout = dashboard.render_response(
        query=demo_cognitive["query"],
        cognitive_packet=demo_cognitive,
        meta_packet=demo_meta,
        execution_time=35.5,
        compiled_speech=demo_speech,
    )

    console.print(layout)

    # ── Structural demo ─────────────────────────────────────────────────
    demo_cognitive["soul_result"]["domain_route"] = "structural"
    demo_cognitive["soul_result"]["domain_hits"] = {
        "failure": 1.0,
        "bottleneck": 0.9,
        "debugging": 0.5,
    }
    demo_cognitive["soul_result"]["concepts"] = []
    demo_cognitive["soul_result"]["scores"] = {}
    demo_cognitive["soul_result"]["arc"] = ""
    demo_cognitive["soul_result"]["soul_used"] = False
    demo_cognitive["domain_concepts"] = ["failure", "bottleneck", "debugging"]
    demo_cognitive["bridge_connections"] = []
    demo_cognitive["domain_arc"] = "failure requires recovery; bottleneck opposes optimization"
    demo_meta["meta"]["confidence"] = 0.75
    demo_meta["meta"]["status"] = "partial"
    demo_meta["gaps"] = [{"type": "missing_concept", "concept": "recovery", "reason": "no signal match"}]
    demo_speech = "The deployment failure is a bottleneck. Failure requires recovery. Bottleneck opposes optimization."

    print("\n" * 2)
    rprint("[bold white]Structural Route Demo[/]\n")

    layout2 = dashboard.render_response(
        query="the deployment failed and the server is down",
        cognitive_packet=demo_cognitive,
        meta_packet=demo_meta,
        execution_time=42.3,
        compiled_speech=demo_speech,
    )
    console.print(layout2)
