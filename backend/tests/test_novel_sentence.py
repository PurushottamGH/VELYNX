import asyncio
import json
import sys

# Ensure backend is in path
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.pipeline.agentic_loop import agentic_controller

async def run_stress_test():
    print("=" * 72)
    print("VELYNX SYMBOLIC DECOMPOSER: STRESS TEST")
    print("=" * 72)

    query = "What is the population of the country where the founder of my favorite 3D software lives?"
    print(f"\n[USER QUERY]: {query}\n")

    # 1. Test the Router
    should_plan = agentic_controller.should_plan(query)
    print(f"[ROUTER DECISION]: should_plan = {should_plan}")

    if not should_plan:
        print("FAIL: Router rejected the complex sentence.")
        return

    # 2. Test the Decomposer
    print("\n[FORMULATING PLAN VIA SPACY GRAMMAR...]")
    plan = agentic_controller.formulate_plan(query)

    print("\n[GENERATED DAG]:")
    print(json.dumps(plan.to_dict(), indent=2))

    print("\n" + "=" * 72)
    print("Analyze the DAG above. Did it successfully extract the nested chunks?")
    print("=" * 72)

if __name__ == "__main__":
    asyncio.run(run_stress_test())
