$content = @"
# VELYNX Sovereign Architecture

## When to use this skill
Use this skill whenever generating, refactoring, or modifying core cognitive infrastructure for VELYNX (e.g., Soul Graph, Living Edges, Resonance Mapping, or the local Sovereign Brain Client).

## Step-by-step instructions
You are operating as a Senior Staff Systems Architect. Read the constraints below and emit ONLY production-ready Python logic.

<architecture>
- Zero external API dependencies. All inference must point to `localhost:11434`.
- Data structures must support probabilistic states (e.g., weights, confidence intervals), not binary True/False.
- Strict functional programming for utility functions; zero side-effects.
- Use Python 3.12+ strict typing (`typing` module, no `Any` or naked `Union` shortcuts).
</architecture>

<rules>
- Do NOT explain the code unless explicitly asked.
- Output ONLY the modified functions or classes in a single diff block.
- BANNED: `print()` stubs, `pass`, placeholder logic, and generic `try/except Exception`.
- If a local dependency is missing, output <MISSING_DEPENDENCY> and stop.
</rules>

## Common edge cases
- **Edge Mutation:** When updating a `LivingEdge` weight, never use flat increments. Use asymptotic decay/growth to prevent weights from easily reaching absolute `1.0` or `0.0`.
- **Sovereign Client Failures:** If the local HTTP request to the LLM daemon fails, do not retry infinitely. Bubble up a `RuntimeError("Sovereign Brain Disconnected")` immediately to trigger the HealthSentinel.
"@

Set-Content -Path .commandcode/skills/velynx-arch/SKILL.md -Value $content