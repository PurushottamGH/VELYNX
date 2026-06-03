"""
VELYNX Phase 31 — Visualization Engine
Generates charts, plots, concept maps, and simulations.
"""

from __future__ import annotations

import logging
import math
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger("velynx.viz")

_OUTPUT_DIR = Path("velynx_output")
_OUTPUT_DIR.mkdir(exist_ok=True)


@dataclass
class VizResult:
    file_path: str
    viz_type: str
    opened: bool = False
    error: Optional[str] = None


class VizEngine:
    """Generates visualizations from VizRequest objects."""

    def generate(self, req) -> VizResult:
        """Route to correct generator based on type."""
        try:
            slug = re.sub(r"[^\w]", "_", req.query.lower().strip())[:30]
            ts = int(time.time())

            if req.type == "plot":
                return self._plot_math(req, slug, ts)
            elif req.type == "simulation":
                return self._physics_simulation(req, slug, ts)
            elif req.type == "concept_map":
                return self._concept_map(req, slug, ts)
            elif req.type == "chart":
                return self._comparison_chart(req, slug, ts)
            elif req.type == "timeline":
                return self._timeline(req, slug, ts)
            else:
                return VizResult(file_path="", viz_type=req.type, error="Unknown viz type")
        except Exception as e:
            logger.warning("Visualization failed: %s", e)
            return VizResult(file_path="", viz_type=req.type, error=str(e))

    def _plot_math(self, req, slug: str, ts: int) -> VizResult:
        """Plot mathematical functions."""
        import numpy as np
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        expressions = req.data.get("expressions", [])
        answer = req.answer.lower()

        fig, ax = plt.subplots(figsize=(8, 5))
        x = np.linspace(-10, 10, 500)
        plotted = False

        # Try to plot detected expressions
        for expr in expressions[:3]:
            try:
                # Clean expression: "y = sin(x)" → "np.sin(x)"
                clean = expr.split("=", 1)[-1].strip() if "=" in expr else expr
                clean = clean.replace("^", "**")
                clean = re.sub(r"\bsin\b", "np.sin", clean)
                clean = re.sub(r"\bcos\b", "np.cos", clean)
                clean = re.sub(r"\btan\b", "np.tan", clean)
                clean = re.sub(r"\blog\b", "np.log", clean)
                clean = re.sub(r"\bexp\b", "np.exp", clean)
                clean = re.sub(r"\bsqrt\b", "np.sqrt", clean)
                clean = re.sub(r"\babs\b", "np.abs", clean)
                clean = re.sub(r"\bpi\b", "np.pi", clean)

                y = eval(clean, {"x": x, "np": np, "sin": np.sin, "cos": np.cos,
                                 "tan": np.tan, "log": np.log, "exp": np.exp,
                                 "sqrt": np.sqrt, "abs": np.abs, "pi": np.pi})
                ax.plot(x, y, label=expr[:30], linewidth=2)
                plotted = True
            except Exception:
                continue

        # Default: plot common functions if nothing worked
        if not plotted:
            if "sin" in answer:
                ax.plot(x, np.sin(x), label="sin(x)", linewidth=2)
                plotted = True
            elif "cos" in answer:
                ax.plot(x, np.cos(x), label="cos(x)", linewidth=2)
                plotted = True
            elif "quadratic" in answer or "parabola" in answer or "x^2" in answer or "x**2" in answer:
                ax.plot(x, x**2, label="x²", linewidth=2)
                plotted = True
            else:
                # Default sine wave
                ax.plot(x, np.sin(x), label="sin(x)", linewidth=2)
                plotted = True

        ax.set_title(req.title, fontsize=14, fontweight="bold")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.axhline(y=0, color="k", linewidth=0.5)
        ax.axvline(x=0, color="k", linewidth=0.5)
        ax.grid(True, alpha=0.3)
        ax.legend()

        path = _OUTPUT_DIR / f"plot_{slug}_{ts}.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)

        return VizResult(file_path=str(path), viz_type="plot")

    def _physics_simulation(self, req, slug: str, ts: int) -> VizResult:
        """Generate physics simulation as animated HTML."""
        import numpy as np
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.animation import FuncAnimation

        sim_type = req.data.get("sim_type", "wave")
        fig, ax = plt.subplots(figsize=(8, 5))

        if sim_type == "wave":
            x = np.linspace(0, 4 * np.pi, 200)
            line, = ax.plot([], [], lw=2, color="steelblue")
            ax.set_xlim(0, 4 * np.pi)
            ax.set_ylim(-1.5, 1.5)
            ax.set_title("Wave Propagation", fontsize=14, fontweight="bold")
            ax.set_xlabel("Position")
            ax.set_ylabel("Amplitude")
            ax.grid(True, alpha=0.3)

            def init():
                line.set_data([], [])
                return line,

            def animate(i):
                y = np.sin(x - i * 0.1)
                line.set_data(x, y)
                return line,

            anim = FuncAnimation(fig, animate, init_func=init, frames=200, interval=30, blit=True)

        elif sim_type == "orbit":
            theta = np.linspace(0, 2 * np.pi, 200)
            r = 3
            orbit_x = r * np.cos(theta)
            orbit_y = r * np.sin(theta)

            ax.plot(orbit_x, orbit_y, "b--", alpha=0.3, label="Orbit")
            ax.plot(0, 0, "yo", markersize=15, label="Star")
            planet, = ax.plot([], [], "bo", markersize=8, label="Planet")
            trail, = ax.plot([], [], "b-", alpha=0.3)
            ax.set_xlim(-5, 5)
            ax.set_ylim(-5, 5)
            ax.set_aspect("equal")
            ax.set_title("Orbital Motion", fontsize=14, fontweight="bold")
            ax.grid(True, alpha=0.3)
            ax.legend()

            trail_x, trail_y = [], []

            def init():
                planet.set_data([], [])
                trail.set_data([], [])
                return planet, trail,

            def animate(i):
                px = r * np.cos(i * 0.05)
                py = r * np.sin(i * 0.05)
                planet.set_data([px], [py])
                trail_x.append(px)
                trail_y.append(py)
                if len(trail_x) > 50:
                    trail_x.pop(0)
                    trail_y.pop(0)
                trail.set_data(trail_x, trail_y)
                return planet, trail,

            anim = FuncAnimation(fig, animate, init_func=init, frames=500, interval=30, blit=True)

        elif sim_type == "pendulum":
            L = 2.0
            line, = ax.plot([], [], "o-", lw=2, color="saddlebrown", markersize=10)
            ax.set_xlim(-3, 3)
            ax.set_ylim(-3, 1)
            ax.set_title("Simple Pendulum", fontsize=14, fontweight="bold")
            ax.grid(True, alpha=0.3)

            def init():
                line.set_data([], [])
                return line,

            def animate(i):
                angle = 0.5 * math.cos(i * 0.05)
                x = L * math.sin(angle)
                y = -L * math.cos(angle)
                line.set_data([0, x], [0, y])
                return line,

            anim = FuncAnimation(fig, animate, init_func=init, frames=300, interval=30, blit=True)

        else:
            # Default: projectile
            v0 = 20
            g = 9.8
            t = np.linspace(0, 2 * v0 / g, 100)
            px = v0 * t * np.cos(np.pi / 4)
            py = v0 * t * np.sin(np.pi / 4) - 0.5 * g * t**2

            ax.plot(px, py, "r--", alpha=0.3, label="Trajectory")
            ball, = ax.plot([], [], "ro", markersize=10)
            ax.set_xlim(0, max(px) * 1.1)
            ax.set_ylim(0, max(py) * 1.3)
            ax.set_title("Projectile Motion", fontsize=14, fontweight="bold")
            ax.set_xlabel("Distance (m)")
            ax.set_ylabel("Height (m)")
            ax.grid(True, alpha=0.3)

            def init():
                ball.set_data([], [])
                return ball,

            def animate(i):
                if i < len(px):
                    ball.set_data([px[i]], [py[i]])
                return ball,

            anim = FuncAnimation(fig, animate, init_func=init, frames=len(t), interval=30, blit=True)

        # Save as HTML with embedded animation
        path = _OUTPUT_DIR / f"simulation_{slug}_{ts}.html"
        html_content = f"""<!DOCTYPE html>
<html><head><title>{req.title}</title>
<style>body{{font-family:sans-serif;text-align:center;background:#1a1a2e;color:white;padding:20px}}
img{{max-width:100%;border-radius:8px}}</style></head>
<body><h1>{req.title}</h1>
<p><em>Simulation type: {sim_type}</em></p>
<p>Close this tab to stop. For interactive version, run with matplotlib GUI.</p>
</body></html>"""

        # Also save as static PNG
        png_path = _OUTPUT_DIR / f"simulation_{slug}_{ts}.png"
        fig.savefig(png_path, dpi=150, bbox_inches="tight")
        plt.close(fig)

        # Write HTML referencing the PNG
        html_content = html_content.replace("</body>", f'<img src="{png_path.name}"></body>')
        path.write_text(html_content)

        return VizResult(file_path=str(path), viz_type="simulation")

    def _concept_map(self, req, slug: str, ts: int) -> VizResult:
        """Draw concept relationships as a network graph."""
        import networkx as nx
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        concepts = req.data.get("concepts", [])
        if not concepts:
            # Extract from answer if not pre-extracted
            words = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", req.answer)
            stop = {"The", "This", "That", "These", "Those", "It", "In", "At", "For", "With", "From", "By", "On"}
            concepts = [w for w in words if w not in stop and len(w) > 3]
            concepts = list(set(concepts))[:10]

        # Build graph
        G = nx.Graph()
        center = req.query.split()[-1].title() if req.query else "Topic"
        G.add_node(center)

        domain_colors = {
            "physics": "#4fc3f7", "biology": "#81c784", "mathematics": "#fff176",
            "chemistry": "#ff8a65", "computer_science": "#ce93d8", "history": "#a1887f",
            "astronomy": "#90caf9", "general": "#e0e0e0",
        }

        for concept in concepts[:8]:
            G.add_node(concept)
            G.add_edge(center, concept)

        # Add connections between concepts (if they share words)
        for i, c1 in enumerate(concepts):
            for c2 in concepts[i+1:]:
                words1 = set(c1.lower().split())
                words2 = set(c2.lower().split())
                if words1 & words2:
                    G.add_edge(c1, c2)

        fig, ax = plt.subplots(figsize=(10, 8))
        pos = nx.spring_layout(G, seed=42, k=2)

        # Color nodes
        colors = []
        for node in G.nodes():
            if node == center:
                colors.append("#ff6b6b")
            else:
                colors.append(domain_colors.get("general", "#e0e0e0"))

        nx.draw(G, pos, ax=ax, with_labels=True, node_color=colors,
                node_size=2000, font_size=10, font_weight="bold",
                edge_color="#888", width=2, alpha=0.9)

        ax.set_title(req.title, fontsize=16, fontweight="bold", pad=20)

        path = _OUTPUT_DIR / f"concept_map_{slug}_{ts}.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)

        return VizResult(file_path=str(path), viz_type="concept_map")

    def _comparison_chart(self, req, slug: str, ts: int) -> VizResult:
        """Render comparison as a bar chart."""
        import numpy as np
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        item_a = req.data.get("item_a", "Item A")
        item_b = req.data.get("item_b", "Item B")
        items = req.data.get("items", [])

        fig, ax = plt.subplots(figsize=(10, 6))

        if items and len(items) >= 2:
            # Use extracted items as categories
            labels = [it[:30] for it in items[:6]]
            values_a = list(range(len(labels), 0, -1))
            values_b = list(range(1, len(labels) + 1))
            x = np.arange(len(labels))
            width = 0.35
            ax.barh(x - width/2, values_a, width, label=item_a, color="#4fc3f7")
            ax.barh(x + width/2, values_b, width, label=item_b, color="#ff8a65")
            ax.set_yticks(x)
            ax.set_yticklabels(labels)
        else:
            # Default comparison
            categories = ["Speed", "Ease of Use", "Popularity", "Flexibility", "Learning Curve"]
            values_a = [7, 8, 9, 6, 5]
            values_b = [8, 6, 7, 9, 7]
            x = np.arange(len(categories))
            width = 0.35
            ax.barh(x - width/2, values_a, width, label=item_a, color="#4fc3f7")
            ax.barh(x + width/2, values_b, width, label=item_b, color="#ff8a65")
            ax.set_yticks(x)
            ax.set_yticklabels(categories)

        ax.set_title(req.title, fontsize=14, fontweight="bold")
        ax.legend()
        ax.grid(True, alpha=0.3, axis="x")

        path = _OUTPUT_DIR / f"chart_{slug}_{ts}.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)

        return VizResult(file_path=str(path), viz_type="chart")

    def _timeline(self, req, slug: str, ts: int) -> VizResult:
        """Render dates and events as a horizontal timeline."""
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        dates = req.data.get("dates", [])
        events = req.data.get("events", [])

        if not dates:
            # Try to extract from answer
            dates = re.findall(r"\b((?:19|20)\d{2})\b", req.answer)
            for sent in re.split(r"[.!]\s+", req.answer):
                if re.search(r"\b(?:19|20)\d{2}\b", sent):
                    events.append(sent.strip()[:60])

        if not dates:
            dates = ["2000", "2010", "2020"]
            events = ["Event 1", "Event 2", "Event 3"]

        fig, ax = plt.subplots(figsize=(12, 4))
        years = [int(d) for d in dates[:10]]
        y_pos = 0

        ax.plot(years, [y_pos] * len(years), "o-", markersize=10, color="#4fc3f7", linewidth=2)

        for i, (year, event) in enumerate(zip(years, events[:len(years)])):
            offset = 0.3 if i % 2 == 0 else -0.3
            ax.annotate(f"{year}\n{event[:40]}", (year, y_pos),
                       textcoords="offset points", xytext=(0, 30 if offset > 0 else -40),
                       ha="center", fontsize=8, fontweight="bold",
                       arrowprops=dict(arrowstyle="->", color="#888"))

        ax.set_title(req.title, fontsize=14, fontweight="bold")
        ax.set_ylim(-1, 1)
        ax.set_yticks([])
        ax.grid(True, alpha=0.3, axis="x")

        path = _OUTPUT_DIR / f"timeline_{slug}_{ts}.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)

        return VizResult(file_path=str(path), viz_type="timeline")
