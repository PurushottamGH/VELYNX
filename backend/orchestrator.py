"""
VELYNX Orchestration Layer
Chains: cross_query() → reflect() → compile_path_to_speech()
"""
import asyncio
import sys
import time
import os
from pathlib import Path

_backend_root = str(Path(__file__).parent.resolve())
if _backend_root not in sys.path:
    sys.path.insert(0, _backend_root)

from backend.knowledge.knowledge_engine import cross_query
from backend.cognition.metacog import reflect
from backend.knowledge.voice_engine import compile_path_to_speech
# LLM-free: llm_client removed
from rich.console import Console
from rich.status import Status
from cli_ui import VelynxDashboard
from backend.memory.memory_graph import MemoryCore
from backend.audio.vocal_tract import VocalTract
from backend.agency.system_bridge import SystemBridge, ExecutionQuarantine
from backend.agency.action_log import ActionLogger
from backend.agency.code_writer import CodeWriter
from backend.agency.quality_assurance import QAEngine
from backend.agency.auto_fixer import AutoFixer
from backend.agency.health_sentinel import HealthSentinel

# Phase 50 predictive core (seeded on warmup)
from backend.cognition.predictive_core import seed_concept_states_from_soul, seed_transition_rules_from_living_edges

MEMORY = MemoryCore()
_code_writer = None
_vocal_tract: VocalTract | None = None
_bridge: SystemBridge | None = None
_quarantine: ExecutionQuarantine | None = None
_health_sentinel: HealthSentinel | None = None
_warmed_up = False


def warmup_system() -> float:
    """Force the full pipeline on a no-op query so HuggingFace/CUDA load
    happens at boot time, not on the first real user query (~22s → sub-50ms)."""
    global _warmed_up
    t0 = time.perf_counter()
    # Phase 50: seed predictive tables on first boot
    seed_concept_states_from_soul()
    seed_transition_rules_from_living_edges()
    velynx_respond("warmup")  # triggers model load, DB init, index load
    elapsed_ms = (time.perf_counter() - t0) * 1000
    _warmed_up = True
    return elapsed_ms


def velynx_respond(query: str) -> dict:
    t0 = time.perf_counter()

    cognitive_packet = cross_query(query)
    meta_packet = reflect(query, parsed_result=cognitive_packet["soul_result"])
    speech = compile_path_to_speech(cognitive_packet, meta_packet)

    MEMORY.log_experience(cognitive_packet, meta_packet)

    elapsed_ms = (time.perf_counter() - t0) * 1000

    soul_nodes = len(cognitive_packet.get("soul_result", {}).get("concepts", []))
    domain_nodes = len(cognitive_packet.get("domain_concepts", []))
    bridge_nodes = len(cognitive_packet.get("bridge_connections", []))
    total_nodes = soul_nodes + domain_nodes + bridge_nodes

    return {
        "query": query,
        "speech": speech,
        "metrics": {
            "elapsed_ms": round(elapsed_ms, 2),
            "soul_nodes": soul_nodes,
            "domain_nodes": domain_nodes,
            "bridge_nodes": bridge_nodes,
            "total_nodes_traversed": total_nodes,
        },
        "cognitive_packet": cognitive_packet,
        "meta_packet": meta_packet,
    }


def _verify_domain_routing() -> bool:
    """Cross-domain routing verification: physics + finance bridge tests."""
    import json

    from knowledge.knowledge_graph import KnowledgeGraph

    kg = KnowledgeGraph()
    kg.build()

    tests = [
        {
            "query": "I feel like everything is winding down and losing energy",
            "expected_soul": "loss",
            "expected_domain": "entropy",
            "domain_label": "PHYSICS",
        },
        {
            "query": "I am stuck and cannot find any cash flow or movement",
            "expected_soul": "stagnation",
            "expected_domain": "illiquidity",
            "domain_label": "FINANCE",
        },
    ]

    all_passed = True
    total_ms = 0.0

    for i, test in enumerate(tests):
        t0 = time.perf_counter()
        result = velynx_respond(test["query"])
        elapsed = (time.perf_counter() - t0) * 1000
        total_ms += elapsed

        cp = result["cognitive_packet"]
        soul_concepts = cp.get("soul_result", {}).get("concepts", [])
        domain_concepts = cp.get("domain_concepts", [])
        bridge = cp.get("bridge_connections", [])

        soul_match = test["expected_soul"] in soul_concepts
        domain_match = test["expected_domain"] in domain_concepts
        bridge_match = any(
            b["soul"] == test["expected_soul"] and b["domain"] == test["expected_domain"]
            for b in bridge
        )

        passed = soul_match and domain_match and bridge_match
        all_passed = all_passed and passed

        status = "[green]PASS[/]" if passed else "[red]FAIL[/]"
        console.print(f"\n  [{i+1}] {status} [{test['domain_label']}] \"{test['query']}\"")
        console.print(f"      Latency: {elapsed:.1f}ms")
        console.print(f"      Soul: {soul_concepts[:4]} -> {'OK' if soul_match else 'MISSING ' + test['expected_soul']}")
        console.print(f"      Domain: {domain_concepts[:4]} -> {'OK' if domain_match else 'MISSING ' + test['expected_domain']}")
        console.print(f"      Bridge: {[(b['soul']+'->'+b['domain']) for b in bridge[:4]]}")

    # Graph telemetry
    concepts = kg.all_concepts()
    conn = kg._get_conn()
    edge_count = conn.execute("SELECT COUNT(*) FROM relationships").fetchone()[0]
    conn.close()

    console.print(f"\n  [bold]Graph Telemetry[/]")
    console.print(f"  Nodes: {len(concepts)} ({', '.join(sorted(concepts)[:15])}...)")
    console.print(f"  Edges: {edge_count}")
    console.print(f"  Avg latency: {total_ms / len(tests):.1f}ms  Target: <50ms")
    console.print(f"  Memory experiences: {MEMORY.get_experience_count()}")

    return all_passed


SYSTEM_PROMPT_CODE_GEN = (
    "You are a Senior Software Engineer. "
    "You MUST write complete, functional implementation logic. "
    "DO NOT output boilerplate stubs, placeholder comments, "
    "or print statements repeating the user's prompt. "
    "Provide only the raw, executable Python code. "
    "No explanations, no markdown fences, no commentary."
)


async def _llm_infer_filename(query: str) -> str:
    """Use the LLM to extract a sensible .py filename from the user's query."""
    if not llm_client.available:
        raise RuntimeError("LLM client unavailable — cannot infer filename")
    prompt = (
        "Extract a sensible Python filename from this user request. "
        "Return ONLY the filename (e.g. 'system_logger.py'), nothing else. "
        "Use snake_case. Prefer names that describe the tool's purpose.\n\n"
        f"Request: \"{query}\""
    )
    resp = await llm_client.chat(
        [LLMMessage(role="system", content=SYSTEM_PROMPT_CODE_GEN),
         LLMMessage(role="user", content=prompt)],
        temperature=0.1,
    )
    name = resp.content.strip().strip("`\"'").rstrip(".py") + ".py"
    import re
    name = re.sub(r"[^\w\-.]", "_", name)
    if not name.endswith(".py"):
        name += ".py"
    return name


async def _llm_generate_code(query: str) -> str:
    """Generate a complete Python script via LLM with strict anti-stub rules."""
    if not llm_client.available:
        raise RuntimeError("LLM client unavailable — cannot generate code")
    prompt = (
        f"Write a complete, functional Python program based on this request:\n\n"
        f"\"{query}\"\n\n"
        "Requirements:\n"
        "- Write COMPLETE implementation — no stubs, no 'pass', no 'TODO' placeholders.\n"
        "- Include proper error handling and edge case coverage.\n"
        "- Use only standard library modules unless the request explicitly requires otherwise.\n"
        "- Output ONLY raw Python code. No markdown fences, no explanations."
    )
    resp = await llm_client.chat(
        [LLMMessage(role="system", content=SYSTEM_PROMPT_CODE_GEN),
         LLMMessage(role="user", content=prompt)],
        temperature=0.05,
    )
    code = resp.content.strip()
    if code.startswith("```"):
        lines = code.splitlines()
        code = "\n".join(l for l in lines if not l.startswith("```"))
    return code


def _generate_tool_script(query: str) -> str:
    """Generate tool code via CodeWriter's LLM agent. Raises on failure."""
    q = query.lower()
    if "calculator" in q:
        return _calculator_script()
    if "timer" in q or "stopwatch" in q:
        return _timer_script()
    if "todo" in q or "task" in q:
        return _todo_script()
    return asyncio.run(_code_writer.generate_code(query))


def _infer_filename(query: str) -> str:
    """Infer a filename from the user query. Uses CodeWriter's LLM agent."""
    q = query.lower()
    if "calculator" in q:
        return "calculator.py"
    if "timer" in q or "stopwatch" in q:
        return "timer.py"
    if "todo" in q or "task" in q:
        return "todo.py"
    return asyncio.run(_code_writer.infer_filename(query))


def _calculator_script() -> str:
    return '''"""Simple CLI calculator."""
import sys


def main():
    if len(sys.argv) < 4:
        print("Usage: python calculator.py <num1> <op> <num2>")
        print("Operators: + - * /")
        sys.exit(1)
    a, op, b = float(sys.argv[1]), sys.argv[2], float(sys.argv[3])
    ops = {"+": a + b, "-": a - b, "*": a * b, "/": a / b if b != 0 else "Error: division by zero"}
    result = ops.get(op, f"Unknown operator: {op}")
    print(result)


if __name__ == "__main__":
    main()
'''


def _timer_script() -> str:
    return '''"""Countdown timer."""
import sys
import time


def main():
    if len(sys.argv) < 2:
        print("Usage: python timer.py <seconds>")
        sys.exit(1)
    total = int(sys.argv[1])
    for remaining in range(total, 0, -1):
        print(f"\\rTime remaining: {remaining}s", end="", flush=True)
        time.sleep(1)
    print("\\rTime's up!                ")


if __name__ == "__main__":
    main()
'''


def _todo_script() -> str:
    return '''"""Minimal todo tracker."""
import json
import os
import sys

TODO_FILE = "todo.json"


def load():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE) as f:
            return json.load(f)
    return []


def save(todos):
    with open(TODO_FILE, "w") as f:
        json.dump(todos, f, indent=2)


def main():
    todos = load()
    if len(sys.argv) < 2:
        for i, t in enumerate(todos):
            status = "✓" if t["done"] else " "
            print(f"  [{status}] {i}: {t['text']}")
        return
    cmd = sys.argv[1]
    if cmd == "add" and len(sys.argv) > 2:
        todos.append({"text": " ".join(sys.argv[2:]), "done": False})
        save(todos)
        print("Added.")
    elif cmd == "done" and len(sys.argv) > 2:
        idx = int(sys.argv[2])
        if 0 <= idx < len(todos):
            todos[idx]["done"] = True
            save(todos)
            print("Marked done.")
    elif cmd == "clear":
        save([])
        print("Cleared.")


if __name__ == "__main__":
    main()
'''


if __name__ == "__main__":
    import sys as _sys

    console = Console()
    dashboard = VelynxDashboard()

    with Status("Booting VELYNX... Allocating VRAM", spinner="dots", console=console):
        cold_start_ms = warmup_system()

    _vocal_tract = VocalTract(enabled=True)
    _bridge = SystemBridge()
    _quarantine = ExecutionQuarantine()
    _action_log = ActionLogger()
    _qa_engine = QAEngine()
    _auto_fixer = AutoFixer()
    _health_sentinel = HealthSentinel()

    console.print(
        f"[green]System ready.[/] Cold-start: {cold_start_ms:.0f}ms\n",
        style="dim",
    )

    if "--verify" in _sys.argv:
        console.print("[bold white]VELYNX Cross-Domain Verification[/]\n")
        ok = _verify_domain_routing()
        console.print(
            f"\n[bold green]All tests passed.[/]"
            if ok
            else f"\n[bold red]Some tests failed.[/]"
        )
        _sys.exit(0 if ok else 1)

    while True:
        try:
            query = console.input("[bold cyan]VELYNX > [/]").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Shutting down.[/]")
            break

        if not query:
            continue
        if query.lower() in ("exit", "quit"):
            console.print("[dim]Shutting down.[/]")
            break

        # ── 1. REFLEX LAYER (High Priority) ──
        # Execute BEFORE the brain can even think.
        # Each reflex uses its own continue to short-circuit the loop.

        if "debugging" in query.lower():
            print("DEBUG: TRIGGERING DEBUGGING BLOCK")
            try:
                git_output = _bridge.get_git_status()
                lines = [l for l in git_output.split("\n") if l.strip()]
                untracked = sum(1 for l in lines if l.startswith("??"))
                modified = len(lines) - untracked
                console.print(
                    f"[bold cyan][VELYNX RECON][/] Git status scanned. "
                    f"Found {modified} modified, {untracked} untracked files.",
                    style="dim",
                )
            except Exception:
                pass
            continue

        if "refactoring" in query.lower() or "recovery" in query.lower():
            print("DEBUG: TRIGGERING REFACTORING/RECOVERY BLOCK")
            command = "git add . && git commit -m 'chore: automated cognitive refactoring'"
            reason = "System requires recovery to clear technical debt and resolve friction."
            outcome = _quarantine.propose_command(command, reason)
            approved = "Execution aborted" not in outcome
            _action_log.record_action(
                command=command,
                reason=reason,
                approved=approved,
                exit_code=0 if approved else None,
                output=outcome.strip() if approved else None,
            )
            if approved:
                console.print(outcome.strip(), style="dim")
            else:
                console.print("[dim]Agency override aborted.[/]")
            continue

        build_keywords = ["build", "write code", "write a python", "create a", "generate a", "check the syntax", "repair"]
        if any(keyword in query.lower() for keyword in build_keywords):
            if not _health_sentinel.is_system_stable():
                console.print("🛑 [HealthSentinel] CRITICAL: System unstable. Build halted.")
                continue

            print("DEBUG: TRIGGERING BUILD BLOCK")
            generated_code = _generate_tool_script(query)
            filename = _infer_filename(query)
            filepath = os.path.join(_code_writer.ALLOWED_DIR, filename)

            write_result = _code_writer.propose_code_write(
                filepath=filepath, code_content=generated_code,
                reason="User requested automated tool generation."
            )

            if "[SUCCESS]" in write_result:
                console.print("\n[QA] Writing complete. Starting verification...")
                qa_report = _qa_engine.verify_and_report(filepath)

                if qa_report["success"]:
                    console.print(f"✅ [QA] Code verified! Lint: {qa_report['lint_status']}")
                else:
                    console.print("❌ [QA] Code failed verification. Initiating AutoFixer...")
                    repair_status = _auto_fixer.attempt_repair(filepath, qa_report)
                    console.print(f"🛠 [AutoFixer] Status: {repair_status}")
                    _health_sentinel.log_event("repair", repair_status)

                    _action_log.record_action(
                        command=f"repair {filename}",
                        reason="Automated repair attempt due to QA failure",
                        approved=True,
                        output=str(repair_status)
                    )

                _action_log.record_action(
                    command=f"write {filename}",
                    reason="Automated build with QA verify",
                    approved=True,
                    output=str(qa_report)
                )
            else:
                console.print("[dim]Code write aborted by user.[/]")
            continue

        # ── 2. COGNITIVE LAYER (Low Priority) ──
        # Full knowledge-graph pipeline for non-agency queries.
        # Wrapped in 'else' — only reached if NO reflex block fired above.

        else:
            t_start = time.perf_counter()
            temporal_context = MEMORY.retrieve_recent_state(limit=1)
            result = velynx_respond(query)

            layout = dashboard.render_response(
                query=result["query"],
                cognitive_packet=result["cognitive_packet"],
                meta_packet=result["meta_packet"],
                execution_time=result["metrics"]["elapsed_ms"],
                compiled_speech=result["speech"],
                temporal_context=temporal_context[0] if temporal_context else None,
            )

            console.print(layout)
            voice_thread = _vocal_tract.speak_async(result["speech"])
            voice_thread.join()
