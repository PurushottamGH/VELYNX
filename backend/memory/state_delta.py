from typing import Dict

def calculate_state_delta(pre_state: Dict[str, float], post_state: Dict[str, float]) -> Dict[str, float]:
    """Calculates the exact thermodynamic shift between two states."""
    delta = {}
    keys = set(pre_state) | set(post_state)

    for key in keys:
        diff = post_state.get(key, 0.0) - pre_state.get(key, 0.0)
        # Only store meaningful changes to keep the JSON footprint clean
        if abs(diff) > 0.001:
            delta[key] = diff

    return delta