# Taste (Continuously Learned by [CommandCode][cmd])

[cmd]: https://commandcode.ai/


# code-quality
- After bulk edits across multiple files, verify all necessary imports are present and syntax is valid in every modified file. Confidence: 0.70

# architecture
- VELYNX must be self-contained — never fall back to external LLMs when memory/retrieval returns empty; return honest "I don't have enough evidence" responses instead. Confidence: 0.85
- When running from the VELYNX root directory, all Python imports must use the `backend.` prefix (e.g., `from backend.pipeline.constitution_loader` instead of `from pipeline.constitution_loader`). Confidence: 0.70
- Keep orchestrator scripts thin (under 200 lines) by placing logic in dedicated components rather than in the entry-point script. Confidence: 0.70
- Maintain clean API encapsulation by adding thin passthrough methods on public classes rather than allowing direct access to private (`_`-prefixed) attributes. Confidence: 0.65

# python
- Use `dataclasses` for configuration and data structures (e.g., BenchmarkConfig, AnomalyRecord, RegressionResult). Confidence: 0.70
- Use the `abc` module to define abstract interface contracts. Confidence: 0.65
