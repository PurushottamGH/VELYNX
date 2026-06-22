from typing import Dict, List, Any

def calculate_prediction_error(predicted: Dict[str, float], observed: Dict[str, float]) -> float:
    """Calculates the mean absolute error between state dicts."""
    total = 0.0
    count = 0
    keys = set(predicted) | set(observed)
    for k in keys:
        total += abs(float(predicted.get(k, 0.0)) - float(observed.get(k, 0.0)))
        count += 1
    return total / count if count else 0.0

class PredictiveEngine:
    def __init__(self):
        self.DECAY_RATES = {
            "epiphany": 0.30, "confusion": 0.20, "doubt": 0.15, "frustration": 0.15,
            "anticipation": 0.12, "focus": 0.10, "anger": 0.12, "joy": 0.10,
            "pain": 0.08, "loneliness": 0.07, "contentment": 0.05, "empathy": 0.05,
            "grief": 0.03, "hope": 0.02, "trust": 0.01, "love": 0.01, "resilience": 0.01,
            "meaning": 0.005, "duty": 0.005, "vulnerability": 0.005
        }
        self.DEFAULT_DECAY = 0.05

    def apply_epistemic_decay(self, current_states: Dict[str, float]) -> Dict[str, float]:
        """Applies turn-based metabolic cooling."""
        decayed_states = {}
        for concept, activation in current_states.items():
            activation = float(activation)
            if activation > 0.01:
                rate = self.DECAY_RATES.get(concept, self.DEFAULT_DECAY)
                decayed_states[concept] = max(0.0, activation * (1.0 - rate))
            else:
                decayed_states[concept] = 0.0
        return decayed_states

    def predict_next_state(
        self,
        concept_states: Dict[str, float],
        transition_rules: Dict[str, List[Dict[str, Any]]],
        active_sources: List[str],
    ) -> Dict[str, float]:
        """Propagates energy through the rule graph."""
        next_state = dict(concept_states)

        for source in active_sources:
            source_activation = float(concept_states.get(source, 0.0))
            if source_activation <= 0.0:
                continue

            for rule in transition_rules.get(source, []):
                target = rule.get("target")
                weight = float(rule.get("weight", 0.0))
                confidence = float(rule.get("confidence", 1.0))

                if not target:
                    continue

                delta = source_activation * weight * confidence
                next_state[target] = max(0.0, min(1.0, float(next_state.get(target, 0.0)) + delta))

        return next_state
