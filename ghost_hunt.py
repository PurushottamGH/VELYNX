import asyncio
import os

# Force test mode
os.environ['VELYNX_TEST_MODE'] = '1'

from backend.tests.live_fire_harness import reset_state
from backend.app.pipeline import answer_question

async def hunt():
    print("1. Forcing Wipe & RAM Reset...")
    reset_state()
    
    print("\n2. Teaching Interstellar...")
    r1 = await answer_question("My favorite movie is Interstellar")
    
    print("\n3. Querying Favorite Movie...")
    r2 = await answer_question("What is my favorite movie?")
    
    print("\n" + "="*50)
    print("=== THE GHOST'S FACE ===")
    print("ANSWER:", r2.answer)
    print("REASONING TRACE:", r2.debug.get('reasoning_trace'))
    print("="*50)

if __name__ == "__main__":
    asyncio.run(hunt())
