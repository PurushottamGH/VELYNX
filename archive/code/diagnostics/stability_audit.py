import asyncio
import math
import sys
import os
from contextlib import redirect_stdout
from backend.orchestration.cognitive_loop import CognitiveOrchestrator

async def run_audit():
    orchestrator = CognitiveOrchestrator()
    
    # 1. Isolate Thermodynamics: Disable recall to prevent memory injection
    orchestrator.retriever.retrieve_by_context = lambda x: []
    
    # 2. Prevent DB Spam: Stop logging these silent audit turns as real memories
    orchestrator.memory.log_experience = lambda *args: None 
    
    print("=== COMMENCING 100-CYCLE SENSORY DEPRIVATION AUDIT ===")
    print("Isolating Phase 50 Thermodynamics. Memory recall disabled.\n")
    
    null_input = "..." 
    
    for i in range(1, 101):
        # Mute the standard print statements from the loop to keep the output clean
        with open(os.devnull, 'w') as f, redirect_stdout(f):
            await orchestrator.process_interaction(null_input, memory_source="audit")
        
        # Take a snapshot every 10 cycles (and cycle 1)
        if i == 1 or i % 10 == 0:
            conn = orchestrator._get_conn()
            cur = conn.cursor()
            cur.execute("SELECT concept, activation FROM concept_states WHERE activation > 0.0")
            states = {row[0]: float(row[1]) for row in cur.fetchall()}
            conn.close()
            
            # Calculate Phase 52.5 Metrics
            total_energy = sum(states.values())
            mean_activation = total_energy / len(states) if states else 0.0
            
            entropy = 0.0
            if total_energy > 0:
                for val in states.values():
                    p_i = val / total_energy
                    entropy -= p_i * math.log2(p_i)
                    
            active_concepts = [v for v in states.values() if v > 0.01]
            saturated_concepts = [v for v in active_concepts if v >= 0.95]
            saturation_ratio = len(saturated_concepts) / len(active_concepts) if active_concepts else 0.0
            
            top_5 = sorted(states.items(), key=lambda item: item[1], reverse=True)[:5]
            
            print(f"--- CYCLE {i} ---")
            print(f"Mean Activation: {mean_activation:.4f}")
            print(f"Graph Entropy:   {entropy:.4f} bits")
            print(f"Saturation:      {saturation_ratio*100:.1f}% ({len(saturated_concepts)} maxed)")
            print("Top Concepts:")
            for concept, act in top_5:
                print(f"  {concept.upper():<15} {act:.4f}")
            print("-" * 30)

if __name__ == "__main__":
    asyncio.run(run_audit())