import sqlite3
import asyncio
import math
import traceback
from typing import Dict, Any

from backend.cognition.perception import PerceptionLayer
from backend.cognition.predictive_engine import PredictiveEngine, calculate_prediction_error
from backend.cognition.candidate_store import CandidateStore
from backend.memory.memory_store import MemoryStore
from backend.memory.memory_retriever import MemoryRetriever
from backend.memory.recall_logger import RecallLogger
from backend.memory.state_delta import calculate_state_delta
from backend.memory import _sqlite

class CognitiveOrchestrator:
    def __init__(self, db_path: str = "velynx_state.db"):
        self.db_path = db_path
        self.perception = PerceptionLayer()
        self.engine = PredictiveEngine()
        self.memory = MemoryStore(self.db_path)
        self.retriever = MemoryRetriever(self.db_path)
        self.candidate_store = CandidateStore(self.db_path)
        self.recall_logger = RecallLogger(self.db_path)
        
    def _get_conn(self):
        return _sqlite.connect(self.db_path)

    def fetch_current_state(self) -> Dict[str, float]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT concept, activation FROM concept_states")
        states = {row[0]: float(row[1]) for row in cursor.fetchall()}
        conn.close()
        return states

    def fetch_transition_rules(self) -> Dict[str, list]:
        """Pulls the active physics, keyed by source concept."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT source_concept, target_concept, effect, decay, rule_confidence FROM transition_rules")
        
        rules_by_source = {}
        for source, target, effect, decay, confidence in cursor.fetchall():
            rule = {
                "target": target,
                "weight": float(effect),
                "decay": float(decay),
                "confidence": float(confidence)
            }
            rules_by_source.setdefault(source, []).append(rule)
            
        conn.close()
        return rules_by_source

    def update_database_state(self, new_states: Dict[str, float]):
        conn = self._get_conn()
        cursor = conn.cursor()
        for concept, activation in new_states.items():
            cursor.execute("""
                INSERT OR REPLACE INTO concept_states (concept, activation, baseline, state_confidence, source, evidence_count, updated_at)
                VALUES (
                    ?, 
                    ?, 
                    0.0, 
                    1.0, 
                    'dynamic_cognition', 
                    (SELECT COALESCE((SELECT evidence_count FROM concept_states WHERE concept = ?), 0) + 1), 
                    CURRENT_TIMESTAMP
                )
            """, (concept, float(activation), concept))
        conn.commit()
        conn.close()

    async def process_interaction(self, user_text: str, memory_source: str = "human", simulation_batch_id: str = None) -> Dict[str, Any]:
        """The pure, LLM-free cognitive loop."""
        # --- PERCEPTION PHASE ---
        perception_data = await self.perception.parse_input(user_text)
        sensory_input = perception_data.get("activations", {})
        missed_concepts = perception_data.get("missed_concepts", [])
        coverage = perception_data.get("coverage", 1.0)

        # --- PHASE 52.7: LOGGING & TELEMETRY ---
        if coverage < 1.0:
            print(f"\n[PHASE 52.7 TELEMETRY] Perception Coverage: {coverage*100:.1f}%")
            print(f"[PHASE 52.7 TELEMETRY] Missed Concepts Logged: {missed_concepts}\n")

        for candidate in missed_concepts:
            self.candidate_store.log_candidate_observation(
                concept=candidate,
                observed_text=user_text,
                session_id=simulation_batch_id or "default"
            )
        
        # --- ADD THIS DEBUG LINE ---
        print(f"[DEBUG] Raw Sensory Input Detected: {sensory_input}")
        # ---------------------------
        
        raw_current_states = self.fetch_current_state()
        rules = self.fetch_transition_rules()
        
        current_states = self.engine.apply_epistemic_decay(raw_current_states)
        
        active_sources = list(sensory_input.keys())
        for source, weight in sensory_input.items():
            current_val = current_states.get(source, 0.0)
            current_states[source] = current_val + weight * (1.0 - current_val)
            
        # 1. INPUT CONTRIBUTION
        input_contribution = sum(sensory_input.values())

        # 2. RECALL CONTRIBUTION & FUSION (The Patch)
        recall_contribution = 0.0
        # Phase 52.9B: pass a {concept: thermodynamic_weight} query so retrieval
        # scores by semantic relevance, not raw memory strength.
        recall_query = {src: float(current_states.get(src, 0.0)) for src in active_sources}
        recalled_memories = self.retriever.retrieve_by_context(recall_query)
        
        if recalled_memories:
            for mem in recalled_memories:
                raw_strength = float(mem['strength'])
                recall_contribution += raw_strength
                
                # Attenuate the memory strength to a maximum of 0.25 per memory
                # This ensures the past influences, but does not overpower, the present (which is ~0.3 - 0.6)
                attenuated_weight = min(0.25, raw_strength * 0.05)
                
                try:
                    # Safely parse the dominant concepts from the memory
                    import json
                    past_concepts = json.loads(mem.get('dominant_concepts_json', '{}'))
                    
                    for concept, past_activation in past_concepts.items():
                        # The memory only injects weight proportional to how active the concept was
                        injection_weight = past_activation * attenuated_weight
                        
                        # Apply asymptotic fusion so it pushes against the 1.0 ceiling safely
                        current_val = current_states.get(concept, 0.0)
                        current_states[concept] = current_val + injection_weight * (1.0 - current_val)
                        
                        # Add to active sources so the thermodynamic engine knows to process it
                        if concept not in active_sources:
                            active_sources.append(concept)
                            
                except Exception as e:
                    pass # Failsafe if JSON parsing fails on older memory formats

        # 3. RECALL RATIO (R = Recall / Input)
        safe_input = max(input_contribution, 0.001)
        # We calculate the ratio based on the actual attenuated energy injected, not the raw unbound strength
        actual_injected_recall = sum([min(0.25, float(m['strength']) * 0.05) for m in recalled_memories]) if recalled_memories else 0.0
        recall_ratio = actual_injected_recall / safe_input

        # Phase 50 Thermodynamics
        # --- PHASE 51 UPGRADE: Capture Pre-State ---
        pre_state = dict(current_states)
        # -------------------------------------------

        next_state = self.engine.predict_next_state(
            concept_states=current_states,
            transition_rules=rules,
            active_sources=active_sources
        )
        
        error = calculate_prediction_error(current_states, next_state)
        self.update_database_state(next_state)

        # --- PHASE 52.8: RECALL OBSERVABILITY (non-blocking telemetry) ---
        # Pure observation of the recall performed above by retrieve_by_context.
        # Placed here because recall_ratio and system_error are only resolved at
        # this point; retrieval logic itself is untouched. A telemetry failure
        # must never crash the cognitive loop.
        try:
            self.recall_logger.log_recall_event(
                trigger_concepts={c: float(current_states.get(c, 0.0)) for c in active_sources},
                retrieved_memories=recalled_memories,
                recall_energy=recall_contribution,
                recall_ratio=recall_ratio,
                system_error=error,
                # Phase 52.9A: the pre-cutoff raw pool captured during the
                # retrieve_by_context call above (top-20 before top_k slicing).
                raw_candidates=getattr(self.retriever, "last_raw_candidates", []),
            )
        except Exception as telemetry_error:
            print(f"[RECALL TELEMETRY WARNING] Failed to log recall event: {telemetry_error}")

        
        # 4. ENERGY CONCENTRATION
        total_energy = sum(next_state.values())
        if total_energy > 0:
            top_5_energy = sum(sorted(next_state.values(), reverse=True)[:5])
            energy_concentration = top_5_energy / total_energy
        else:
            energy_concentration = 0.0

        # 5. GRAPH ENTROPY (Shannon Entropy)
        entropy = 0.0
        if total_energy > 0:
            for val in next_state.values():
                if val > 0:
                    p_i = val / total_energy
                    entropy -= p_i * math.log2(p_i)

        # 6. SATURATION & DELTAS
        delta = calculate_state_delta(pre_state, next_state)
        
        active_concepts = [v for v in next_state.values() if v > 0.01]
        saturated_concepts = [v for v in active_concepts if v > 0.90]
        saturation_ratio = len(saturated_concepts) / len(active_concepts) if active_concepts else 0.0

        pos_deltas = sorted([(k, v) for k, v in delta.items() if v > 0], key=lambda x: x[1], reverse=True)[:3]
        neg_deltas = sorted([(k, v) for k, v in delta.items() if v < 0], key=lambda x: x[1], reverse=True)[:3]

        # --- THE OBSERVABILITY REPORT ---
        print("\n" + "="*40)
        print("=== THERMODYNAMIC DIAGNOSTICS ===")
        print("="*40)
        
        # Recall Analysis
        print(f"Input Energy:  {input_contribution:.2f}")
        print(f"Recall Energy: {recall_contribution:.2f}")
        if recall_ratio < 1.0:
            status = "Healthy (Present Dominates)"
        elif recall_ratio <= 3.0:
            status = "Warning (Memory Influence High)"
        else:
            status = "CRITICAL (Echo Chamber)"
        print(f"Recall Ratio:  {recall_ratio:.1f}x [{status}]")
        
        # Graph Health
        print(f"\nEnergy Concentration (Top 5): {energy_concentration*100:.1f}%")
        print(f"Graph Entropy: {entropy:.2f} bits")
        print(f"Saturation Ratio: {saturation_ratio*100:.1f}% ({len(saturated_concepts)} concepts maxed)")
        
        # Delta Vectors
        print("\nTop Thermodynamic Vectors (Deltas):")
        for k, v in pos_deltas: print(f"  +{k.upper():<12} +{v:.2f}")
        for k, v in neg_deltas: print(f"  -{k.upper():<12} {v:.2f}")
        print("========================================\n")
        
        # Phase 51: Archive the complete delta experience
        self.memory.log_experience(user_text, sensory_input, pre_state, next_state, error, simulation_batch_id)
        
        active_next = {k: v for k, v in next_state.items() if v > 0.0}
        if active_next:
            top_states = [f"{k.upper()}: {v:.2f}" for k, v in sorted(next_state.items(), key=lambda item: item[1], reverse=True)[:3]]
            symbolic_response = f"[VELYNX INTERNAL STATE SHIFT -> {', '.join(top_states)}]"
        else:
            symbolic_response = "[VELYNX: No active states.]"
            
        return {
            "sensory_activations": sensory_input,
            "new_state": next_state,
            "system_error": error,
            "response": symbolic_response
        }

async def main():
    orchestrator = CognitiveOrchestrator()
    print("=== VELYNX COGNITIVE LOOP ONLINE ===")
    
    while True:
        user_text = input("VELYNX> ").strip()
        if not user_text:
            continue
        if user_text.lower() in {"/quit", "/exit"}:
            break
        try:
            result = await orchestrator.process_interaction(user_text)
            print("\n" + "─"*40)
            print(result["response"])
            print(f"System Error: {result['system_error']:.4f}")
            print("─"*40 + "\n")
        except Exception as e:
            print("\n[FATAL ERROR]")
            traceback.print_exc()
            print()

if __name__ == "__main__":
    asyncio.run(main())