"""Ground-truth specification for the PredictiveCore module.

This is the immutable law of the architecture — every LLM-generated payload
must conform to this spec before being merged.
"""

from __future__ import annotations

from typing import Any

PREDICTIVE_CORE_SPEC: dict[str, Any] = {
    "module": "backend.cognition.predictive_core",
    "exports": {
        "PredictiveEngine": {
            "type": "class",
            "methods": {
                "__init__": {
                    "args": ["self", "decay_rate", "confidence_threshold"],
                    "returns": "None",
                },
                "predict_next_state": {
                    "args": [
                        "self",
                        "concept_states",
                        "transition_rules",
                        "active_sources",
                    ],
                    "returns": "dict",
                },
            },
        },
        "calculate_prediction_error": {
            "type": "function",
            "args": ["target_state", "predicted_state"],
            "returns": "float",
        },
    },
}
