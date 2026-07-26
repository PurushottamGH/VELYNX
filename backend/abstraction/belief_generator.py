import sqlite3
import json
import hashlib
from typing import List, Dict, Optional
from contextlib import contextmanager

from backend.memory._sqlite import connect as open_connection
from backend.memory.memory_store import MemoryStore
from backend.abstraction.belief_store import BeliefStore
from backend.abstraction.belief_models import CandidateBelief


class BeliefGenerator:
    def __init__(self, db_path: str = "velynx_state.db"):
        self.db_path = db_path
        self.memory_store = MemoryStore(db_path)
        self.belief_store = BeliefStore(db_path)

    @contextmanager
    def _conn(self):
        conn = open_connection(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _compute_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    def _extract_transitions(self, batch_id: str) -> Dict[str, List[Dict]]:
        """Extract all concept transitions from a batch's memory log."""
        with self._conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT state_delta_json, dominant_concepts_json, user_input
                FROM memory_log
                WHERE batch_id = ?
                ORDER BY turn_index
            """, (batch_id,))
            
            transitions = {}
            for row in cursor.fetchall():
                delta_json = row[0]
                dominant_json = row[1]
                
                try:
                    delta = json.loads(delta_json)
                    dominant = json.loads(dominant_json)
                except json.JSONDecodeError:
                    continue
                
                # Find source concepts (those with positive delta that were in dominant)
                for source_concept, source_activation in dominant.items():
                    if source_activation > 0.01:
                        if source_concept not in transitions:
                            transitions[source_concept] = []
                        
                        # Find target concepts that gained energy
                        for target_concept, delta_val in delta.items():
                            if delta_val > 0.01 and target_concept != source_concept:
                                transitions[source_concept].append({
                                    "target": target_concept,
                                    "effect": delta_val,
                                    "source_activation": source_activation
                                })
            
            return transitions

    def generate_candidates_for_batch(self, batch_id: str, target_concepts: List[str]):
        """Generate candidate beliefs from a single batch."""
        transitions = self._extract_transitions(batch_id)
        
        for concept in target_concepts:
            if concept not in transitions:
                continue
            
            # Aggregate transitions by target
            target_effects = {}
            for t in transitions[concept]:
                target = t["target"]
                effect = t["effect"]
                if target not in target_effects:
                    target_effects[target] = []
                target_effects[target].append(effect)
            
            # Build belief statements for each target with sufficient support
            for target, effects in target_effects.items():
                if len(effects) < 2:  # Minimum 2 observations
                    continue
                
                mean_effect = sum(effects) / len(effects)
                support = len(effects)
                
                # Create belief text
                if mean_effect > 0:
                    belief_text = f"#{concept} leads to #{target}"
                else:
                    belief_text = f"#{concept} reduces #{target}"
                
                belief_hash = self._compute_hash(belief_text)
                
                # Confidence based on support and consistency
                confidence = min(0.95, 0.5 + (support * 0.1) + (mean_effect * 0.2))
                
                # Promotion score (higher = more promotable)
                promotion_score = confidence * support * abs(mean_effect)
                
                # Determine if promotable
                promoted = support >= 3 and confidence > 0.7 and abs(mean_effect) > 0.1
                reason = ""
                if not promoted:
                    if support < 3:
                        reason = "Insufficient support"
                    elif confidence <= 0.7:
                        reason = "Low confidence"
                    else:
                        reason = "Weak effect magnitude"
                
                candidate = CandidateBelief(
                    belief_text=belief_text,
                    belief_hash=belief_hash,
                    support_count=support,
                    belief_confidence=confidence,
                    mean_effect=mean_effect,
                    promotion_score=promotion_score,
                    promoted=promoted,
                    reason=reason
                )
                
                self.belief_store.upsert_candidate(concept, batch_id, candidate)


def generate_beliefs_for_batch(batch_id: str):
    """Entry point for generating beliefs from a batch."""
    target_concepts = ["grief", "confusion", "contentment", "loneliness", "meaning", "resilience", "hope", "love", "vulnerability", "courage", "empathy", "understanding", "epiphany", "focus", "curiosity", "doubt", "patience"]
    generator = BeliefGenerator()
    generator.generate_candidates_for_batch(batch_id, target_concepts)
    print(f"Generated candidates for {batch_id}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        generate_beliefs_for_batch(sys.argv[1])
    else:
        print("Usage: python -m backend.abstraction.belief_generator <batch_id>")