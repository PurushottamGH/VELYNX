import sqlite3
import math
from typing import Dict, Any

from backend.memory._sqlite import connect as open_connection

class BaselineTracker:
    def __init__(self, state_db_path: str = "velynx_state.db", identity_db_path: str = "velynx_identity.db"):
        self.state_db = state_db_path
        self.identity_db = identity_db_path
        self.WINDOW_SIZE = 20
        self.SATURATION_THRESHOLD = 0.90
        self.ACTIVE_THRESHOLD = 0.05

    def _execute_state_query(self, query: str, params: tuple = ()) -> list:
        try:
            with open_connection(self.state_db, row_factory=sqlite3.Row) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    def get_memory_count(self) -> int:
        res = self._execute_state_query("SELECT COUNT(*) as cnt FROM memory_log")
        return res[0]["cnt"] if res else 0

    def get_energy_metrics(self) -> Dict[str, Any]:
        query = f"""
            SELECT id, emotional_energy
            FROM memory_log 
            ORDER BY turn_index DESC LIMIT {self.WINDOW_SIZE}
        """
        rows = self._execute_state_query(query)
        if not rows:
            return {"input_energy": 1.0, "recall_energy": "unsupported"}
        avg_input = sum(r["emotional_energy"] for r in rows) / len(rows)
        return {
            "input_energy": round(max(0.1, avg_input), 4),
            "recall_energy": "unsupported"
        }

    def get_concept_metrics(self) -> Dict[str, Any]:
        rows = self._execute_state_query("SELECT concept, activation, evidence_count FROM concept_states")
        if not rows:
            return {"saturation_ratio": 0.0, "top_activated_concept": "none", "unique_concepts_seen": 0, "entropy_score": 0.0}
            
        total_concepts = len(rows)
        high_act = sum(1 for r in rows if r["activation"] > self.SATURATION_THRESHOLD)
        saturation_ratio = high_act / total_concepts if total_concepts > 0 else 0.0
        
        top_concept = max(rows, key=lambda x: x["activation"])["concept"] if rows else "none"
        active_concepts = sum(1 for r in rows if r["activation"] > self.ACTIVE_THRESHOLD)
        historical_concepts = sum(1 for r in rows if r["evidence_count"] > 0)
        
        activations = [max(0.0001, r["activation"]) for r in rows]
        total_act = sum(activations)
        entropy = 0.0
        if total_act > 0:
            probs = [a / total_act for a in activations]
            entropy = -sum(p * math.log2(p) for p in probs if p > 0)
            max_entropy = math.log2(total_concepts) if total_concepts > 1 else 1.0
            entropy = min(1.0, entropy / max_entropy)
            
        return {
            "saturation_ratio": round(saturation_ratio, 4),
            "top_activated_concept": top_concept,
            "unique_concepts_seen": active_concepts,
            "historical_concepts_seen": historical_concepts,
            "entropy_score": round(entropy, 4)
        }

    def get_belief_metrics(self) -> Dict[str, Any]:
        query = f"SELECT prediction_error FROM memory_log ORDER BY turn_index DESC LIMIT {self.WINDOW_SIZE}"
        rows = self._execute_state_query(query)
        
        belief_rows = self._execute_state_query("SELECT concept, confidence FROM core_beliefs ORDER BY confidence ASC LIMIT 1")
        lowest_conf_concept = belief_rows[0]["concept"] if belief_rows else "none"
        lowest_conf_val = belief_rows[0]["confidence"] if belief_rows else 1.0
        
        if not rows:
            return {"prediction_friction": 0.0, "lowest_core_confidence": lowest_conf_val, "weakest_belief_concept": lowest_conf_concept}
            
        avg_error = sum(r["prediction_error"] for r in rows) / len(rows)
        prediction_friction = min(1.0, max(0.0, avg_error))
        
        return {
            "prediction_friction": round(prediction_friction, 4),
            "lowest_core_confidence": round(lowest_conf_val, 4),
            "weakest_belief_concept": lowest_conf_concept
        }

    def get_long_term_trends(self) -> Dict[str, Any]:
        try:
            with open_connection(self.identity_db) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT diversity_health FROM health_logs ORDER BY id DESC LIMIT 30")
                rows = cursor.fetchall()
        except sqlite3.Error:
            rows = []
            
        if len(rows) < 4:
            return {"30_cycle_diversity_trend": 0.0, "data_completeness": round(len(rows)/30.0, 4)}
            
        vals = [r[0] for r in rows[::-1]]
        mid = len(vals) // 2
        trend = (sum(vals[mid:]) / (len(vals) - mid)) - (sum(vals[:mid]) / mid)
        
        return {
            "30_cycle_diversity_trend": round(trend, 4),
            "data_completeness": min(1.0, round(len(vals) / 30.0, 4))
        }

    def generate_tracker_aggregates(self) -> Dict[str, Any]:
        data = {"memory_count": self.get_memory_count()}
        data.update(self.get_energy_metrics())
        data.update(self.get_concept_metrics())
        data.update(self.get_belief_metrics())
        data.update(self.get_long_term_trends())
        return data