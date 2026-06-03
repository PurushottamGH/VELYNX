"""
VELYNX Simulation Detector — Phase 35
Detects which simulation to run from natural language query.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SimRequest:
    sim_type: str
    params: dict = field(default_factory=dict)
    triggered_by: str = ""


TRIGGERS = [
    (r"orbit|orbital|planet.+sun|earth.+sun|simulate.+orbit|gravity.+simulation", "orbital"),
    (r"wave|frequency|interference|standing wave|electromagnetic wave|sine wave", "wave"),
    (r"molecule|molecular|H2O|CO2|CH4|NH3|atom.+3d|benzene|water molecule", "molecular"),
    (r"solar system|planets|all planets|solar.+model|planet.+orbit", "solar_system"),
    (r"projectile|trajectory|launch.+angle|throw|ballistic", "projectile"),
    (r"pendulum|double pendulum|chaos|chaotic motion", "pendulum"),
]

PARAM_PATTERNS = {
    "velocity": r"(\d+\.?\d*)\s*m/?s",
    "angle": r"(\d+\.?\d*)\s*(?:degree|deg)",
    "frequency": r"(\d+\.?\d*)\s*(?:hz|hertz)",
    "amplitude": r"amplitude\s+(\d+\.?\d*)",
    "molecule": r"\b(H2O|CO2|CH4|NH3|benzene)\b",
    "wave_type": r"\b(standing|interference|electromagnetic|sine)\b",
    "focus": r"\b(inner|full|outer)\b",
}


class SimDetector:

    def detect(self, query: str) -> Optional[SimRequest]:
        q = query.lower()
        sim_words = ["simulat", "show", "visualiz", "animate", "plot", "3d", "model",
                     "orbit", "wave", "molecule", "pendulum", "projectile", "solar"]
        if not any(w in q for w in sim_words):
            return None

        for pattern, sim_type in TRIGGERS:
            if re.search(pattern, q, re.IGNORECASE):
                params = self._extract_params(query, sim_type)
                return SimRequest(sim_type=sim_type, params=params, triggered_by=pattern)
        return None

    def _extract_params(self, query: str, sim_type: str) -> dict:
        params = {}
        for param, pattern in PARAM_PATTERNS.items():
            m = re.search(pattern, query, re.IGNORECASE)
            if m:
                val = m.group(1)
                try:
                    params[param] = float(val)
                except ValueError:
                    params[param] = val
        return params


sim_detector = SimDetector()
