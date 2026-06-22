from typing import List
from backend.abstraction.belief_store import BeliefStore

def validate_cross_seed_stability(target_concepts: List[str], batches: List[str]):
    store = BeliefStore()
    
    for concept in target_concepts:
        print("\n" + "="*50)
        print(f"=== CROSS-SEED STABILITY: #{concept.upper()} ===")
        print("="*50)
        
        # Dictionary to track: belief_hash -> { 'text': str, 'found_in': List[str] }
        belief_tracker = {}
        
        # 1. Gather all candidate beliefs from all batches
        for batch in batches:
            candidates = store.inspect_candidates(concept, batch_id=batch)
            for c in candidates:
                if c.belief_hash not in belief_tracker:
                    belief_tracker[c.belief_hash] = {
                        "text": c.belief_text,
                        "found_in": []
                    }
                belief_tracker[c.belief_hash]["found_in"].append(batch)
                
        if not belief_tracker:
            print(f"No candidate beliefs formed for {concept} in any batch.")
            continue
            
        # 2. Calculate Stability and Sort
        results = []
        for b_hash, data in belief_tracker.items():
            stability = len(data["found_in"]) / len(batches)
            results.append((data["text"], data["found_in"], stability))
            
        # Sort by highest stability, then alphabetical
        results.sort(key=lambda x: (-x[2], x[0]))
        
        # 3. Print the Audit
        for text, found_in, stability in results:
            print(f"\nBELIEF SIGNATURE")
            print(f"--------------------------------")
            print(f"{text}")
            print()
            for batch in batches:
                status = "found" if batch in found_in else "absent"
                print(f"{batch:<10} : {status}")
            print(f"\nCross-seed stability: {stability:.2f}")

if __name__ == "__main__":
    # Example usage based on your defined parameters
    target_concepts = ["confusion", "contentment", "loneliness", "understanding", "grief", "meaning"]
    batches = ["batch_42", "batch_1337", "batch_2026"]
    
    validate_cross_seed_stability(target_concepts, batches)