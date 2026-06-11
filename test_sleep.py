import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.soul.soul_graph import run_sleep_cycle

stats = run_sleep_cycle(decay_rate=0.01, prune_threshold=0.15)
print(stats)
