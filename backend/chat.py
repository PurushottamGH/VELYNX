import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app.pipeline import answer_question


async def chat_loop():
    print("=" * 50)
    print("VELYNX Live Interactive CLI")
    print("Type 'exit' or 'quit' to stop.")
    print("=" * 50)

    while True:
        try:
            user_input = input("\nYou: ")
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if user_input.lower() in ("exit", "quit"):
            break
        if not user_input.strip():
            continue

        try:
            response = await answer_question(user_input)
        except Exception as exc:
            print(f"\n[Error]: {type(exc).__name__}: {exc}")
            continue

        answer = getattr(response, "answer", str(response))
        confidence = getattr(response, "confidence", None)
        if confidence:
            print(f"\nVELYNX [{confidence}]: {answer}")
        else:
            print(f"\nVELYNX: {answer}")


if __name__ == "__main__":
    try:
        asyncio.run(chat_loop())
    except KeyboardInterrupt:
        pass
