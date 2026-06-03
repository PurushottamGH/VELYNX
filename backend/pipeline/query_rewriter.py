"""
VELYNX Query Rewriter
Converts natural language questions into search-optimized queries.
Fixes: "coding" → biology, "Python" → snake, etc.
"""
import re

_REWRITES = [
    (r"why\s+is\s+(.+?)\s+important\??", r"\1 importance"),
    (r"what\s+can\s+i\s+do\s+with\s+(.+)", r"\1 applications"),
    (r"how\s+does\s+(.+?)\s+work\??", r"\1 how it works"),
    (r"what\s+is\s+(?:a\s+|an\s+)?(.+)\?*$", r"\1"),
    (r"why\s+does\s+(.+?)\s+happen\??", r"\1 cause"),
    (r"what\s+are\s+(?:the\s+)?benefits\s+of\s+(.+)", r"\1 benefits"),
    (r"who\s+(?:invented|created|discovered)\s+(.+)", r"\1 history"),
    (r"when\s+was\s+(.+?)\s+(?:invented|created|discovered)\??", r"\1 history"),
]

_DISAMBIGUATION = {
    "python":    "Python programming language",
    "coding":    "computer programming coding",
    "java":      "Java programming language",
    "swift":     "Swift programming language Apple",
    "rust":      "Rust programming language systems",
    "go":        "Go programming language Google",
    "gravity":   "gravity physics gravitational force",
    "mercury":   "Mercury planet solar system",
    "apple":     "Apple Inc technology company",
    "amazon":    "Amazon company technology",
    "ruby":      "Ruby programming language",
    "scala":     "Scala programming language",
    "dart":      "Dart programming language Flutter",
    "kotlin":    "Kotlin programming language JetBrains",
    "shell":     "shell scripting command line bash",
    "bash":      "bash shell scripting Linux terminal",
    "c":         "C programming language",
    "r":         "R programming language statistics",
    "django":    "Django Python web framework",
    "flask":     "Flask Python web framework",
    "pandas":    "pandas Python data analysis library",
    "numpy":     "numpy Python numerical computing library",
    "react":     "React JavaScript frontend framework",
    "angular":   "Angular JavaScript frontend framework",
    "vue":       "Vue.js JavaScript frontend framework",
    "spring":    "Spring Java framework",
    "rails":     "Ruby on Rails web framework",
}

def rewrite(query: str) -> str:
    """Rewrite natural language query for search engines."""
    q = query.strip().rstrip("?")

    # Apply pattern rewrites
    for pattern, replacement in _REWRITES:
        match = re.search(pattern, q, re.IGNORECASE)
        if match:
            q = re.sub(pattern, replacement, q, flags=re.IGNORECASE)
            break

    # Clean trailing punctuation
    q = q.rstrip("?.,!")

    # Apply disambiguation (case-insensitive word match)
    words = q.split()
    for i, word in enumerate(words):
        lower = word.lower().rstrip("?.,!")
        if lower in _DISAMBIGUATION:
            words[i] = _DISAMBIGUATION[lower]
            q = " ".join(words)
            break

    return q.strip()


def get_search_context(query: str) -> str:
    """Get domain context hint for ambiguous queries."""
    q = query.lower()
    if any(w in q for w in ["code", "coding", "program", "python", "javascript", "software", "algorithm"]):
        return "computer science programming"
    if any(w in q for w in ["gravity", "light", "quantum", "particle", "force", "energy"]):
        return "physics science"
    if any(w in q for w in ["dna", "cell", "protein", "gene", "evolution"]):
        return "biology science"
    if any(w in q for w in ["planet", "star", "galaxy", "universe", "orbit"]):
        return "astronomy space"
    return ""
