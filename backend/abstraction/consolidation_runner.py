from typing import List
from backend.abstraction.belief_store import BeliefStore
from backend.abstraction.belief_models import CandidateBelief

def generate_audit_report(target_concept: str, candidates: List[CandidateBelief]):
    promotable = [c for c in candidates if c.promoted]
    
    print("\n" + "="*40)
    print(f"=== PHASE 52 AUDIT: #{target_concept.upper()} ===")
    print("="*40)
    print(f"Total Candidates: {len(candidates)}")
    print(f"Promotable (if unlocked): {len(promotable)}")
    
    if candidates:
        mean_support = sum(c.support_count for c in candidates) / len(candidates)
        mean_conf = sum(c.belief_confidence for c in candidates) / len(candidates)
        print(f"System Mean Support: {mean_support:.1f}")
        print(f"System Mean Confidence: {mean_conf:.2f}")
    
    print("\n--- TOP CANDIDATES ---")
    # Sort by the engine's holistic promotion score
    top_candidates = sorted(candidates, key=lambda c: c.promotion_score, reverse=True)[:5]
    
    for i, c in enumerate(top_candidates, 1):
        status = "[PROMOTABLE]" if c.promoted else f"[QUARANTINED: {c.reason}]"
        print(f"\n{i}. {c.belief_text} {status}")
        print(f"   Signature: {c.belief_hash[:8]}...")
        print(f"   Support: {c.support_count}")
        print(f"   Confidence: {c.belief_confidence:.2f}")
        print(f"   Mean Effect: {c.mean_effect:.2f}")

def run_diagnostic_consolidation(target_concepts: List[str] = ["grief", "confusion", "contentment", "loneliness"]):
    store = BeliefStore()
    
    for concept in target_concepts:
        # inspect_candidates runs the engine without writing to core_beliefs
        candidates = store.inspect_candidates(concept)
        if candidates:
            generate_audit_report(concept, candidates)
        else:
            print(f"\n=== PHASE 52 AUDIT: #{concept.upper()} ===")
            print("No evidence found to form candidate beliefs.")

if __name__ == "__main__":
    run_diagnostic_consolidation()