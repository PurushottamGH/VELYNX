"""
test_metacog.py — metacognitive reflection test.

For each query: call reflect(query), inspect output quality rating.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from cognition.metacog import reflect

queries = [
    "I feel lost and don't know who I am anymore",  # expect: gap
    "She trusted him and he broke her heart",  # expect: strong
    "keeping going even when everything hurts",  # expect: partial
]

for q in queries:
    result = reflect(q)
    print(result)
