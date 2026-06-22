from typing import Dict, Any, Optional

class CognitiveAuditor:
    def __init__(self):
        self.TIER_0, self.TIER_1, self.TIER_2, self.TIER_3 = "LEVEL_0_NORMAL", "LEVEL_1_WARNING", "LEVEL_2_CRITICAL", "LEVEL_3_EMERGENCY"

    def safe_delta(self, current: Any, previous: Any) -> float:
        if isinstance(current, (int, float)) and isinstance(previous, (int, float)):
            return float(current - previous)
        return 0.0

    def classify_anomaly(self, current: Dict[str, Any], previous: Dict[str, Any], tracker_data: Dict[str, Any]) -> tuple:
        sat_delta = self.safe_delta(current.get("saturation_health"), previous.get("saturation_health"))
        div_delta = self.safe_delta(current.get("diversity_health"), previous.get("diversity_health"))
        bel_delta = self.safe_delta(current.get("belief_health"), previous.get("belief_health"))
        rec_delta = self.safe_delta(current.get("recall_health"), previous.get("recall_health"))

        if sat_delta <= -0.15:
            return "SATURATION_SPIKE", tracker_data.get("top_activated_concept", "unknown"), sat_delta
        if rec_delta <= -0.15:
            return "RECALL_LOOP", tracker_data.get("top_recalled_memory", "unknown"), rec_delta
        if bel_delta <= -0.15:
            return "BELIEF_FRACTURE", tracker_data.get("top_contradicted_belief", "unknown"), bel_delta
        if div_delta <= -0.10:
            return "DIVERSITY_COLLAPSE", "entropy_collapse", div_delta

        long_term_div_delta = tracker_data.get("30_cycle_diversity_trend", 0.0)
        if long_term_div_delta <= -0.15 and current.get("global_health", 1.0) >= 0.70:
            return "BASELINE_DRIFT", "cognitive_narrowing", long_term_div_delta

        global_delta = current.get("health_delta", 0.0)
        if global_delta >= 0.10:
            return "POSITIVE_RECOVERY", "system_stabilization", global_delta
        return "HEALTHY_STASIS", "none", global_delta

    def run_audit(self, health_report: Dict[str, Any], previous_health_report: Optional[Dict[str, Any]], tracker_aggregates: Dict[str, Any]) -> Dict[str, Any]:
        curr = health_report["metrics"]
        conf = curr["confidence_score"]
        if not previous_health_report:
            return self._build_artifact("HEALTHY_STASIS", "cold_start", 0.0, self.TIER_0, conf)
        audit_type, driver, delta = self.classify_anomaly(curr, previous_health_report["metrics"], tracker_aggregates)
        tier = self.TIER_3 if curr["global_health"] < 0.3 else self.TIER_2 if curr["global_health"] < 0.5 else self.TIER_1 if curr["global_health"] < 0.7 or health_report["velocity_warning"] else self.TIER_0
        return self._build_artifact(audit_type, driver, delta, tier, conf)

    def _build_artifact(self, audit_type: str, driver: str, delta: float, tier: str, confidence: float) -> Dict[str, Any]:
        return {"audit_type": audit_type, "primary_driver": driver, "driver_delta": round(delta, 4), "recommended_circuit_breaker": tier, "audit_confidence": round(confidence, 4)}