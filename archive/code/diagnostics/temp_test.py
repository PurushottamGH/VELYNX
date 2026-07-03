import asyncio
from backend.orchestration.cognitive_loop import CognitiveOrchestrator

async def run_sequence():
    orchestrator = CognitiveOrchestrator()
    inputs = [
        "I lost my friend and the pain is destroying my hope.",
        "The weather is quiet today.",
        "I need to focus on work.",
        "I finished a task."
    ]
    for i, txt in enumerate(inputs):
        result = await orchestrator.process_interaction(txt)
        print(f"\n--- Turn {i} ---")
        print("Response:", result["response"])
        print("Top states:")
        for line in result["response"].split('->')[1].strip('[]').split(', '):
            print(' ', line)
        print("Full state (top 3):", {k: v for k, v in sorted(result['new_state'].items(), key=lambda item: item[1], reverse=True)[:3]})

if __name__ == '__main__':
    asyncio.run(run_sequence())
