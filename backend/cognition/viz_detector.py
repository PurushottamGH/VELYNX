"""
VELYNX Phase 31 — Visualization Detector
Detects if a query needs a visualization and what type.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class VizRequest:
    type: str       # "plot", "simulation", "concept_map", "chart", "timeline"
    query: str
    answer: str
    data: dict      # extracted data for visualization
    title: str


class VizDetector:
    """Detects if a query would benefit from visualization."""

    _TRIGGER_WORDS = {
        "plot", "graph", "show", "simulate", "visualize", "draw",
        "animate", "diagram", "map", "chart", "display", "render",
    }

    def detect(self, query: str, answer: str) -> Optional[VizRequest]:
        """Returns VizRequest if visualization would help, else None."""
        q = query.lower().strip()
        a = answer.lower()

        # Always visualize if trigger word present
        has_trigger = any(w in q for w in self._TRIGGER_WORDS)

        # Auto-detect type based on content
        viz_type = self._detect_type(q, a, has_trigger)
        if not viz_type:
            return None

        # Extract data for visualization
        data = self._extract_data(viz_type, query, answer)

        # Generate title
        title = self._make_title(query, viz_type)

        return VizRequest(
            type=viz_type,
            query=query,
            answer=answer,
            data=data,
            title=title,
        )

    def _detect_type(self, q: str, a: str, has_trigger: bool) -> Optional[str]:
        """Detect what type of visualization is needed."""

        # Concept map: "concept map", "map of", "relationships"
        if any(w in q for w in ["concept map", "map of", "relationships", "connections"]):
            return "concept_map"

        # Comparison: "compare", "vs", "versus", "difference between"
        if any(w in q for w in ["compare", "vs", "versus", "difference between"]):
            return "chart"

        # Timeline: "over time", "history of", "timeline", "evolution of"
        if any(w in q for w in ["over time", "history of", "timeline", "evolution of", "throughout"]):
            return "timeline"

        # Plot: math expressions, "plot", "graph of", equations (check before simulation)
        if any(w in q for w in ["plot", "graph of", "draw"]):
            return "plot"

        # Simulation: physics with motion/force/wave
        if any(w in q for w in ["simulate", "simulation", "orbit", "pendulum", "projectile"]):
            return "simulation"

        # Auto-detect from answer content
        if has_trigger:
            # Math equation in answer → plot
            if re.search(r"[yf]\s*=\s*.+x", a) or re.search(r"\b(sin|cos|tan|log|exp)\b", a):
                return "plot"
            # Physics with numbers → simulation
            if re.search(r"\b(velocity|acceleration|force|gravity|orbit)\b", a) and re.search(r"\d+", a):
                return "simulation"
            # Default to concept map for knowledge queries
            return "concept_map"

        return None

    def _extract_data(self, viz_type: str, query: str, answer: str) -> dict:
        """Extract relevant data for the visualization type."""
        data = {"query": query, "answer": answer}

        if viz_type == "plot":
            # Extract math expressions
            expressions = re.findall(r"([yf]\s*=\s*[^\n.]+)", answer)
            data["expressions"] = expressions[:3]
            # Extract any numbers for range hints
            numbers = re.findall(r"\b(\d+(?:\.\d+)?)\b", answer)
            data["numbers"] = [float(n) for n in numbers[:10]]

        elif viz_type == "chart":
            # Extract comparison items
            comp = re.search(r"compare\s+(.+?)\s+(?:and|vs|versus|with)\s+(.+?)(?:\?|$)", query, re.IGNORECASE)
            if comp:
                data["item_a"] = comp.group(1).strip()
                data["item_b"] = comp.group(2).strip()
            # Extract bullet points or numbered items from answer
            items = re.findall(r"[-•]\s*(.+?)(?:\n|$)", answer)
            data["items"] = items[:10]

        elif viz_type == "timeline":
            # Extract dates and events
            dates = re.findall(r"\b((?:19|20)\d{2})\b", answer)
            data["dates"] = dates[:10]
            # Extract sentences with dates
            events = []
            for sent in re.split(r"[.!]\s+", answer):
                if re.search(r"\b(?:19|20)\d{2}\b", sent):
                    events.append(sent.strip())
            data["events"] = events[:10]

        elif viz_type == "concept_map":
            # Extract key terms for concept nodes
            words = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", answer)
            stop = {"The", "This", "That", "These", "Those", "It", "In", "At", "For"}
            concepts = [w for w in words if w not in stop and len(w) > 3]
            data["concepts"] = list(set(concepts))[:10]

        elif viz_type == "simulation":
            # Detect physics type
            if any(w in query.lower() for w in ["orbit", "gravity", "planetary"]):
                data["sim_type"] = "orbit"
            elif any(w in query.lower() for w in ["wave", "frequency", "sine"]):
                data["sim_type"] = "wave"
            elif any(w in query.lower() for w in ["pendulum"]):
                data["sim_type"] = "pendulum"
            elif any(w in query.lower() for w in ["projectile", "throw", "launch"]):
                data["sim_type"] = "projectile"
            else:
                data["sim_type"] = "wave"  # default

        return data

    def _make_title(self, query: str, viz_type: str) -> str:
        """Generate a clean title for the visualization."""
        clean = query.strip().rstrip("?").title()
        type_labels = {
            "plot": "Plot",
            "simulation": "Simulation",
            "concept_map": "Concept Map",
            "chart": "Comparison",
            "timeline": "Timeline",
        }
        return f"{type_labels.get(viz_type, 'Visualization')}: {clean}"
