#!/usr/bin/env python3
"""VELYNX Teach — teach VELYNX human concepts via interactive terminal."""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
import sys

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.prompt import Prompt, Confirm
    console = Console()
except ImportError:
    print("Install rich: pip install rich")
    sys.exit(1)

from backend.app.soul.soul_store import SoulStore

# ── V2 soul auto-linking ──────────────────────────────────────────────────────

SOUL_LEGACY_PATH = Path(__file__).parent / "backend" / "soul" / "concepts.json"


def _sync_to_legacy_soul(name: str, definition: str):
    """Sync a new concept from the modern SoulStore to the legacy soul file
    used by embed_index, soul_graph, and scenario_engine (Layers 1-3)."""
    try:
        soul = {}
        if SOUL_LEGACY_PATH.exists():
            soul = json.loads(SOUL_LEGACY_PATH.read_text(encoding="utf-8"))
        if name not in soul:
            from datetime import datetime
            soul[name] = {
                "taught_by": "Purushottam",
                "core": definition,
                "what_it_is_not": [],
                "real_situations": [],
                "corrections": [],
                "last_updated": datetime.now().isoformat(),
            }
            SOUL_LEGACY_PATH.parent.mkdir(parents=True, exist_ok=True)
            SOUL_LEGACY_PATH.write_text(json.dumps(soul, indent=2, ensure_ascii=False), encoding="utf-8")
            return True
        return False
    except Exception as exc:
        console.print(f"[dim]Legacy soul sync skipped: {exc}[/dim]")
        return False


def _auto_link_concept(new_name: str):
    """Build soul graph edges between the new concept and all existing ones."""
    try:
        from soul.soul_graph import build_pair, load_soul
        soul = load_soul()
        for existing in list(soul.keys()):
            if existing != new_name:
                try:
                    build_pair(new_name, existing)
                except Exception:
                    continue
        console.print(f"[green]  Auto-linked '{new_name}' to all existing concepts.[/green]")
    except ImportError as exc:
        console.print(f"[dim]Auto-linking skipped (soul_graph not available): {exc}[/dim]")
    except Exception as exc:
        console.print(f"[dim]Auto-linking skipped: {exc}[/dim]")


# ------------------------------------------------------------------ #
#  LLM  call  placeholder                                              #
# ------------------------------------------------------------------ #

def call_llm(prompt: str, *, temperature: float = 0.2) -> str:
    """Sync wrapper around the OpenGateway LLM.

    Falls back to a simple echo if no API key is set.
    """
    api_key = os.getenv("OPENGATEWAY_API_KEY", "")
    if not api_key:
        console.print("[yellow]No LLM API key — using local extraction fallback.[/yellow]")
        return _fallback_extraction(prompt)

    async def _run() -> str:
        from backend.models.llm_client import LLMClient, LLMMessage
        client = LLMClient()
        messages = [LLMMessage(role="user", content=prompt)]
        try:
            resp = await client.chat(messages, temperature=temperature, max_tokens=4096)
            return resp.content
        except Exception:
            return _fallback_extraction(prompt)

    return asyncio.run(_run())


def _fallback_extraction(_story: str) -> str:
    return json.dumps({"concepts": [], "relationships": []})


# ------------------------------------------------------------------ #
#  Menus                                                               #
# ------------------------------------------------------------------ #

def show_menu() -> str:
    console.print()
    console.print(Panel.fit(
        "[bold cyan]VELYNX Teach[/bold cyan]\n\n"
        "[1] Teach a Concept\n"
        "[2] Teach a Relationship\n"
        "[3] Teach via Narrative (LLM Extraction)\n"
        "[4] Exit",
        border_style="cyan",
    ))
    return Prompt.ask("[bold cyan]Choose", choices=["1", "2", "3", "4"], default="1")


# ------------------------------------------------------------------ #
#  Mode 1 — Teach a Concept                                           #
# ------------------------------------------------------------------ #

def teach_concept(store: SoulStore) -> None:
    console.print(Panel("[bold]Teach a Concept[/bold]", border_style="green"))
    name = Prompt.ask("Concept name").strip()
    if not name:
        console.print("[red]Name cannot be empty.[/red]")
        return
    definition = Prompt.ask("Definition").strip()
    if not definition:
        console.print("[red]Definition cannot be empty.[/red]")
        return
    origin = Prompt.ask("Origin", choices=["taught", "inferred"], default="taught")
    conf_str = Prompt.ask("Confidence (0.0–1.0)", default="1.0")
    try:
        confidence = float(conf_str)
    except ValueError:
        confidence = 1.0

    store.add_concept(name, definition, origin=origin, confidence=confidence)
    _sync_to_legacy_soul(name, definition)
    _auto_link_concept(name)
    console.print(f"[green]✓ Concept '{name}' saved and linked.[/green]")


# ------------------------------------------------------------------ #
#  Mode 2 — Teach a Relationship                                      #
# ------------------------------------------------------------------ #

def teach_relationship(store: SoulStore) -> None:
    console.print(Panel("[bold]Teach a Relationship[/bold]", border_style="yellow"))
    source = Prompt.ask("Source concept").strip()
    target = Prompt.ask("Target concept").strip()

    if not source or not target:
        console.print("[red]Both source and target are required.[/red]")
        return

    # Validate both concepts exist; offer to create missing ones
    soul = store.load_soul()
    for name in (source, target):
        if name not in soul["nodes"]:
            console.print(f"[yellow]Concept '{name}' does not exist.[/yellow]")
            if Confirm.ask(f"Define '{name}' now?"):
                teach_concept(store)
            else:
                console.print("[red]Aborted.[/red]")
                return

    rel_type = Prompt.ask(
        "Relationship type",
        choices=["requires", "resolves", "opposes", "amplifies", "diminishes", "causes", "relates_to"],
        default="relates_to",
    )
    tension = Confirm.ask("Is there tension between them?", default=False)
    context = Prompt.ask("Context (explain the dynamic)").strip()
    if not context:
        console.print("[red]Context cannot be empty.[/red]")
        return

    weight_str = Prompt.ask("Weight (0.0–1.0)", default="0.8")
    try:
        weight = float(weight_str)
    except ValueError:
        weight = 0.8

    try:
        store.add_relationship(source, target, rel_type, weight=weight, tension=tension, context=context)
        console.print(f"[green]✓ Relationship '{source} → {target}' saved.[/green]")
    except KeyError as exc:
        console.print(f"[red]{exc}[/red]")


# ------------------------------------------------------------------ #
#  Mode 3 — Narrative Extraction                                      #
# ------------------------------------------------------------------ #

EXTRACTION_PROMPT = """You are the Cognitive Extractor for VELYNX, a cognitive mind architecture.

Read the narrative below. Identify ALL human concepts (emotions, mental states, philosophical ideas, values, psychological dynamics) that are present or implied, even if not explicitly named.

Then, identify the RELATIONSHIPS between those concepts — how they interact, oppose, amplify, or depend on each other.

Return ONLY valid JSON — no markdown, no commentary, no trailing commas. The JSON object must have exactly two keys:

{
  "concepts": [
    {
      "name": "string",
      "definition": "a clear, concise definition of the concept",
      "origin": "inferred",
      "confidence": 0.0-1.0
    }
  ],
  "relationships": [
    {
      "source": "concept_name",
      "target": "concept_name",
      "relationship_type": "requires|resolves|opposes|amplifies|diminishes|causes|relates_to",
      "weight": 0.0-1.0,
      "tension": true|false,
      "context": "explain the psychological dynamic between these concepts in this narrative"
    }
  ]
}

Rules:
- Definitions must be self-contained and meaningful.
- Set tension=true when two concepts are in genuine psychological conflict or create internal struggle.
- Set tension=false for complementary, supportive, or neutral relationships.
- weight should reflect the strength/intensity of the relationship (higher = stronger).
- Skip concepts that are too vague to define meaningfully.
- Every relationship's source and target must match a concept name in the concepts array.
- Extract at least 2 concepts and 1 relationship. If the narrative is rich, extract more.
- Confidence reflects how clearly the concept/relationship is evidenced in the text.

Narrative:
---
{story}
---
"""


def teach_narrative(store: SoulStore) -> None:
    console.print(Panel(
        "[bold]Teach via Narrative[/bold]\n[dim]Paste a story, scenario, or life experience. Blank line to finish.[/dim]",
        border_style="magenta",
    ))

    lines: list[str] = []
    while True:
        line = console.input()
        if line.strip() == "" and lines:
            break
        if line.strip():
            lines.append(line)

    story = "\n".join(lines).strip()
    if not story:
        console.print("[red]No narrative provided.[/red]")
        return

    console.print("[dim]Extracting concepts and relationships via LLM...[/dim]")
    prompt = EXTRACTION_PROMPT.format(story=story)

    try:
        raw = call_llm(prompt, temperature=0.2)
    except Exception as exc:
        console.print(f"[red]LLM call failed: {exc}[/red]")
        return

    # Parse JSON — strip markdown fences, whitespace, and extract
    import re

    cleaned = raw.strip()
    # Remove markdown code fences
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"```\s*$", "", cleaned, flags=re.MULTILINE)
    cleaned = cleaned.strip()

    data: dict | None = None
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        # Try extracting just the outermost { } block
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end > start:
            try:
                data = json.loads(cleaned[start:end + 1])
            except json.JSONDecodeError:
                pass

    # LLM might have returned the concepts array directly without wrapper
    if data is None:
        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, list):
                data = {"concepts": parsed, "relationships": []}
        except json.JSONDecodeError:
            pass

    if data is None:
        console.print("[red]Could not parse LLM response as JSON.[/red]")
        console.print("[dim]Raw LLM response:[/dim]")
        console.print(raw[:2000])
        return

    concepts = data.get("concepts", [])
    relationships = data.get("relationships", [])

    if not concepts and not relationships:
        console.print("[yellow]No concepts or relationships extracted from the narrative.[/yellow]")
        return

    console.print(f"\n[bold]Extracted: {len(concepts)} concept(s), {len(relationships)} relationship(s)[/bold]\n")

    # Display and confirm concepts
    for c in concepts:
        name = c.get("name", "").strip()
        definition = c.get("definition", "").strip()
        origin = c.get("origin", "inferred")
        conf = float(c.get("confidence", 0.5))
        if not name or not definition:
            continue
        console.print(f"  [cyan]Concept:[/cyan] {name}")
        console.print(f"    [dim]{definition}[/dim]")
        console.print(f"    origin={origin}, confidence={conf}")

    # Display relationships
    for r in relationships:
        src = r.get("source", "")
        tgt = r.get("target", "")
        rtype = r.get("relationship_type", "relates_to")
        tension = r.get("tension", False)
        ctx = r.get("context", "")
        console.print(f"  [yellow]Edge:[/yellow] {src} → {tgt} ({rtype})")
        if tension:
            console.print("    [magenta]⚡ TENSION[/magenta]")
        console.print(f"    [dim]{ctx}[/dim]")

    if not Confirm.ask("\nSave all extracted concepts and relationships?", default=True):
        console.print("[dim]Discarded.[/dim]")
        return

    # Save concepts first (so relationships can reference them)
    saved_concepts = 0
    for c in concepts:
        name = c.get("name", "").strip()
        definition = c.get("definition", "").strip()
        if not name or not definition:
            continue
        origin = c.get("origin", "inferred")
        conf = float(c.get("confidence", 0.5))
        try:
            store.add_concept(name, definition, origin=origin, confidence=conf)
            _sync_to_legacy_soul(name, definition)
            saved_concepts += 1
        except Exception as exc:
            console.print(f"[red]Failed to add concept '{name}': {exc}[/red]")

    # Auto-link all saved concepts
    for c in concepts:
        name = c.get("name", "").strip()
        definition = c.get("definition", "").strip()
        if name and definition:
            _auto_link_concept(name)

    saved_edges = 0
    for r in relationships:
        src = r.get("source", "")
        tgt = r.get("target", "")
        if not src or not tgt:
            continue
        try:
            store.add_relationship(
                source=src,
                target=tgt,
                relationship_type=r.get("relationship_type", "relates_to"),
                weight=float(r.get("weight", 0.8)),
                tension=bool(r.get("tension", False)),
                context=r.get("context", ""),
            )
            saved_edges += 1
        except KeyError as exc:
            console.print(f"[red]Skipping edge {src}→{tgt}: {exc}[/red]")

    console.print(f"[green]✓ Saved {saved_concepts} concept(s) and {saved_edges} relationship(s).[/green]")


# ------------------------------------------------------------------ #
#  Main loop                                                           #
# ------------------------------------------------------------------ #

def main() -> None:
    console.print(Panel.fit(
        "[bold cyan]VELYNX Teach v2[/bold cyan]\n[dim]Relational Soul Graph Interface[/dim]",
        border_style="cyan",
    ))

    store = SoulStore()
    store.load_soul()  # run migration if needed

    while True:
        try:
            choice = show_menu()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Goodbye.[/dim]")
            break

        if choice == "1":
            try:
                teach_concept(store)
            except Exception as exc:
                console.print(f"[red]Error: {exc}[/red]")
        elif choice == "2":
            try:
                teach_relationship(store)
            except Exception as exc:
                console.print(f"[red]Error: {exc}[/red]")
        elif choice == "3":
            try:
                teach_narrative(store)
            except Exception as exc:
                console.print(f"[red]Error: {exc}[/red]")
        elif choice == "4":
            console.print("[dim]Goodbye.[/dim]")
            break


if __name__ == "__main__":
    main()
