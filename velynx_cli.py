"""
VELYNX CLI v2 — powered by the Unified Brain
"""
import asyncio
import sys
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown

from backend.brain import VelynxBrain, Intent

console = Console()
brain   = VelynxBrain()


async def main():
    query = " ".join(sys.argv[1:]).strip()
    if not query:
        console.print("[red]Usage: python velynx_cli.py <your query>[/red]")
        sys.exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[cyan]VELYNX thinking...[/cyan]"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("think")
        result = await brain.think(query)

    if result.error:
        console.print(Panel(f"[red]{result.error}[/red]", title="[red]Error[/red]"))
        sys.exit(1)

    # Choose display based on intent
    if result.intent == Intent.SIMULATE:
        # Save HTML and open
        out_path = "velynx_output/simulation.html"
        import os; os.makedirs("velynx_output", exist_ok=True)
        with open(out_path, "w") as f:
            f.write(result.answer)
        console.print(Panel(
            f"[green]Simulation saved to[/green] {out_path}\nOpen in browser.",
            title="[cyan]VELYNX Simulate[/cyan]"
        ))
    else:
        # Show rich markdown answer
        intent_color = {
            Intent.ANSWER:  "cyan",
            Intent.LEARN:   "green",
            Intent.CODE:    "yellow",
            Intent.REFLECT: "magenta",
            Intent.IMPROVE: "blue",
        }.get(result.intent, "white")

        console.print(Panel(
            Markdown(result.answer),
            title=f"[{intent_color}]VELYNX · {result.intent.value.upper()}[/{intent_color}]",
            subtitle=f"[dim]confidence {result.confidence:.0%} · {result.latency_ms:.0f}ms[/dim]",
        ))

        if result.reasoning_chain:
            console.print("\n[dim]Reasoning chain:[/dim]")
            for i, step in enumerate(result.reasoning_chain[:5]):
                console.print(f"  [dim]{i+1}.[/dim] {step}")

        if result.improved:
            console.print("[green]✓ Self-improved during this session[/green]")


if __name__ == "__main__":
    asyncio.run(main())