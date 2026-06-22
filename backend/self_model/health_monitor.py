from typing import Dict, Any, Optional

class CognitiveHealthMonitor:
    def __init__(self, total_ontology_concepts: int):
        self.total_concepts = max(1, total_ontology_concepts)
        self.IDEAL_INPUT_MIN = 0.70
        self.IDEAL_INPUT_MAX = 0.85

    def get_saturation_health(self, saturation_ratio: float) -> float:
        return max(0.0, min(1.0, 1.0 - saturation_ratio))

    def get_diversity_health(self, unique_concepts_seen: int, entropy_score: float) -> float:
        coverage_score = unique_concepts_seen / self.total_concepts
        return max(0.0, min(1.0, (coverage_score + entropy_score) / 2.0))

    def get_belief_health(self, prediction_friction: float) -> float:
        return max(0.0, min(1.0, 1.0 - prediction_friction))

    def get_recall_health(self, input_energy: float, recall_energy: Any) -> float:
        total_energy = input_energy + recall_energy
        if total_energy == 0.0:
            return 1.0
        input_ratio = input_energy / total_energy
        if self.IDEAL_INPUT_MIN <= input_ratio <= self.IDEAL_INPUT_MAX:
            return 1.0
        if input_ratio < self.IDEAL_INPUT_MIN:
            return max(0.0, input_ratio / self.IDEAL_INPUT_MIN)
        return max(0.0, 1.0 - ((input_ratio - self.IDEAL_INPUT_MAX) / (1.0 - self.IDEAL_INPUT_MAX)))

    def get_confidence_score(self, memory_count: int) -> float:
        return max(0.0, min(1.0, memory_count / 1000.0))

    def evaluate_state(self, global_health: float) -> str:
        if global_health >= 0.90:
            return "Excellent"
        if global_health >= 0.70:
            return "Healthy"
        if global_health >= 0.50:
            return "Unstable"
        return "Pathological"

    def generate_health_report(self, memory_count: int, saturation_ratio: float, unique_concepts_seen: int, entropy_score: float, prediction_friction: float, input_energy: float, recall_energy: Any, previous_global_health: Optional[float] = None) -> Dict[str, Any]:
        sat_health = self.get_saturation_health(saturation_ratio)
        div_health = self.get_diversity_health(unique_concepts_seen, entropy_score)
        bel_health = self.get_belief_health(prediction_friction)
        confidence = self.get_confidence_score(memory_count)
        
        base_weights = {
            "saturation": 0.35,
            "belief": 0.25,
            "diversity": 0.20,
            "recall": 0.20
        }
        
        available_metrics = {"saturation": sat_health, "belief": bel_health, "diversity": div_health}
        
        if recall_energy != "unsupported":
            rec_health = self.get_recall_health(input_energy, recall_energy)
            available_metrics["recall"] = rec_health
        else:
            rec_health = "unsupported"
        
        active_weight = sum(base_weights[k] for k in available_metrics)
        global_health = sum(available_metrics[k] * base_weights[k] for k in available_metrics) / active_weight
        health_delta = global_health - previous_global_health if previous_global_health else 0.0
        
        return {
            "metrics": {
                "saturation_health": round(sat_health, 4),
                "diversity_health": round(div_health, 4),
                "belief_health": round(bel_health, 4),
                "recall_health": rec_health,
                "global_health": round(global_health, 4),
                "health_delta": round(health_delta, 4),
                "confidence_score": round(confidence, 4)
            },
            "system_state": self.evaluate_state(global_health),
            "velocity_warning": health_delta <= -0.15
        }
