"""Terminal chat with VELYNX — live conversation interface."""

import asyncio
import json
import sys
import os
import httpx

BASE = "http://127.0.0.1:8000"
SESSION_ID = "terminal-chat"


async def query(text: str) -> dict:
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(f"{BASE}/query", json={"text": text, "session_id": SESSION_ID})
        return resp.json()


async def chat():
    print("\033[1;36m" + "=" * 60)
    print("  VELYNX — Live Terminal Chat")
    print("=" * 60 + "\033[0m")
    print("\033[90m  Type your message and press Enter. 'quit' to exit.\033[0m\n")

    # Health check
    try:
        async with httpx.AsyncClient(timeout=5.0) as c:
            r = await c.get(f"{BASE}/health")
            h = r.json()
            subs = {s["name"]: s["status"] for s in h.get("subsystems", [])}
            ok = sum(1 for v in subs.values() if v == "healthy")
            print(f"\033[90m  Systems: {ok}/{len(subs)} healthy\033[0m\n")
    except Exception:
        print("\033[1;31m  ERROR: Backend not running! Start it first:\033[0m")
        print("    cd backend; python -m uvicorn app.main:app --reload --port 8000\n")
        return

    turn = 0
    while True:
        try:
            user_input = input("\033[1;33m  You: \033[0m").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\033[90m  Goodbye.\033[0m\n")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("\n\033[90m  Goodbye.\033[0m\n")
            break

        turn += 1
        print(f"\033[90m  [{turn}] Thinking...\033[0m", end="", flush=True)

        try:
            result = await query(user_input)
        except Exception as e:
            print(f"\r\033[1;31m  ERROR: {e}\033[0m\n")
            continue

        # Clear "thinking" line
        print("\r" + " " * 40 + "\r", end="")

        # Confidence badge
        conf = result.get("confidence", "UNKNOWN")
        colors = {
            "CERTAIN": "\033[1;32m",
            "PROBABLE": "\033[1;36m",
            "DEBATED": "\033[1;33m",
            "LOW": "\033[1;31m",
            "UNKNOWN": "\033[90m",
        }
        conf_color = colors.get(conf, "\033[0m")

        # Dialogue act
        d_act = result.get("dialogue_act", "")
        mode = result.get("debug", {}).get("reasoning_mode", "")

        # Answer
        answer = result.get("answer", "No answer.")
        sources = result.get("sources", [])
        gaps = result.get("gaps", [])
        contradictions = result.get("contradictions", [])

        print(f"\n\033[1;36m  VELYNX:\033[0m {answer}\n")

        # Metadata line
        meta_parts = [f"{conf_color}{conf}\033[0m"]
        if d_act:
            meta_parts.append(f"\033[90mact:{d_act}\033[0m")
        if mode:
            meta_parts.append(f"\033[90mmode:{mode}\033[0m")
        if sources:
            meta_parts.append(f"\033[90m{len(sources)} sources\033[0m")
        print(f"  \033[90m[{' | '.join(meta_parts)}]\033[0m")

        # Sources
        if sources:
            print(f"\n  \033[1;34mSources:\033[0m")
            for i, s in enumerate(sources[:5], 1):
                title = s.get("title") or s.get("url") or f"Source {i}"
                url = s.get("url", "")
                score = s.get("score", 0)
                print(f"    \033[90m[{i}]\033[0m {title} \033[90m({score:.2f})\033[0m")
                if url:
                    print(f"        \033[90m{url}\033[0m")

        # Contradictions
        if contradictions:
            print(f"\n  \033[1;31mContradictions:\033[0m")
            for c in contradictions:
                print(f"    - {c}")

        # Gaps
        if gaps:
            print(f"\n  \033[1;33mGaps:\033[0m")
            for g in gaps:
                print(f"    - {g}")

        print()


if __name__ == "__main__":
    asyncio.run(chat())
