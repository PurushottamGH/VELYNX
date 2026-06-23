import os
os.environ.setdefault("VELYNX_TEST_MODE", "1")

from backend.knowledge.ontology_loader import install_combined_registry
from backend.knowledge.world_model_context import world_model_facts_for_concepts

install_combined_registry()
facts = world_model_facts_for_concepts(["Tesla Model 3", "wheels"])
print("n facts:", len(facts))
for f in facts:
    print(f["subject"], "-[", f["predicate"], "]->", f["object"], f["confidence"])
