# Taste (Continuously Learned by [CommandCode][cmd])

[cmd]: https://commandcode.ai/


# code-quality
- After bulk edits across multiple files, verify all necessary imports are present and syntax is valid in every modified file. Confidence: 0.70

# architecture
- VELYNX must be self-contained — never fall back to external LLMs when memory/retrieval returns empty; return honest "I don't have enough evidence" responses instead. Confidence: 0.85
