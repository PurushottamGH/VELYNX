from backend.cognition.candidate_store import CandidateStore

def print_audit():
    store = CandidateStore()
    candidates = store.get_top_candidates(limit=10)
    
    print("\n=== PHASE 52.7 CANDIDATE AUDIT ===")
    if not candidates:
        print("No candidates logged yet.")
        return

    for c in candidates:
        print(f"\n{c['concept'].upper()}")
        print(f"  Frequency:  {c['frequency_count']}")
        print(f"  Sessions:   {c['unique_sessions']}")
        print(f"  Confidence: {c['confidence']:.2f}")
        print(f"  Status:     {c['promotion_status']}")

        # Fetch and print the latest evidence line
        details = store.get_candidate_details(c['concept'])
        if details:
            print(f"  Latest Ev:  \"{details[0]['observed_text']}\"")
            
    print("\n==================================")

if __name__ == "__main__":
    print_audit()