import sys
import random
import asyncio
from backend.orchestration.cognitive_loop import CognitiveOrchestrator

SCENARIOS = {
    "grief": [
        "I lost my friend and the pain is destroying my hope.",
        "The grief comes in waves, overwhelming me at random moments.",
        "I miss them so much it physically hurts.",
        "Every memory feels like a knife in my chest.",
        "I don't know how to exist without them.",
    ],
    "confusion": [
        "I am completely lost and don't know what to do.",
        "Everything feels unclear and baffling right now.",
        "I can't make sense of what happened.",
        "My thoughts are a blur, I can't focus on anything.",
        "I keep questioning everything I thought I knew.",
    ],
    "contentment": [
        "I finished a difficult task and feel satisfied.",
        "The weather is quiet today and I feel at peace.",
        "I completed my work and can finally rest.",
        "Everything feels right in this moment.",
        "I accomplished what I set out to do.",
    ],
    "loneliness": [
        "I feel so alone even in a crowded room.",
        "No one truly understands what I'm going through.",
        "The silence in my apartment is deafening.",
        "I reach out but no one reaches back.",
        "Isolation has become my normal state.",
    ],
    "meaning": [
        "I found a new purpose that gives my life direction.",
        "This work matters deeply to me and others.",
        "I finally understand why I went through all that pain.",
        "My suffering had meaning after all.",
        "I am building something that will outlast me.",
    ],
    "resilience": [
        "I got through another day even when I wanted to quit.",
        "I survived the worst and I'm still standing.",
        "Each failure taught me how to be stronger.",
        "I have endured more than I thought possible.",
        "My scars are proof that I heal.",
    ],
}

def get_seed():
    """Get seed from command line or default to 42."""
    if len(sys.argv) > 1:
        try:
            return int(sys.argv[1])
        except ValueError:
            pass
    return 42

async def run_simulation(seed: int):
    """Run a full life simulation with the given seed."""
    random.seed(seed)
    orchestrator = CognitiveOrchestrator()
    batch_id = f"batch_{seed}"
    
    print(f"\n{'='*60}")
    print(f"LIFE SIMULATOR - SEED: {seed} (Batch: {batch_id})")
    print(f"{'='*60}")
    
    # Run 30 interactions across emotional domains
    all_phrases = []
    for domain, phrases in SCENARIOS.items():
        all_phrases.extend([(domain, p) for p in phrases])
    
    # Shuffle with seed
    random.shuffle(all_phrases)
    selected = all_phrases[:30]
    
    for i, (domain, phrase) in enumerate(selected):
        print(f"\n[Turn {i+1}] Domain: {domain.upper()}")
        print(f"Input: {phrase}")
        result = await orchestrator.process_interaction(
            phrase, 
            memory_source="simulator", 
            simulation_batch_id=batch_id
        )
        print(f"Response: {result['response']}")
        print(f"Error: {result['system_error']:.4f}")
    
    print(f"\n{'='*60}")
    print(f"SIMULATION COMPLETE - SEED: {seed} (Batch: {batch_id})")
    print(f"{'='*60}")
    return batch_id

if __name__ == "__main__":
    seed = get_seed()
    batch_id = asyncio.run(run_simulation(seed))
    print(f"\nBatch ID for cross-seed validation: {batch_id}")