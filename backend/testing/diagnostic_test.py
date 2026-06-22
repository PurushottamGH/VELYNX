import asyncio
from backend.orchestration.cognitive_loop import CognitiveOrchestrator

async def run_diagnostic():
    print("=== VELYNX DIAGNOSTIC RUN ===")
    orchestrator = CognitiveOrchestrator()
    
    # A controlled sequence to test the physics
    sequence = [
        "The weather is quiet today.",                                 # Turn 1: Baseline
        "I have a lot of work to do.",                                 # Turn 2: Mild Stress
        "I lost my friend and the pain is destroying my hope.",        # Turn 3: The Shock
        "I miss them so much it physically hurts.",                    # Turn 4: The Echo
        "I need to focus on my coding tasks."                          # Turn 5: Distraction
    ]
    
    for i, trigger in enumerate(sequence, 1):
        print(f"\n[{i}/5] INPUT: '{trigger}'")
        await orchestrator.process_interaction(
            user_text=trigger,
            memory_source="diagnostic",
            simulation_batch_id="diagnostic_001"
        )

if __name__ == "__main__":
    asyncio.run(run_diagnostic())