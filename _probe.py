import os
os.environ.setdefault("VELYNX_TEST_MODE", "1")

from backend.knowledge.predicate_resolver import extract_predicate, predicate_resolver
from backend.knowledge.ontology_loader import install_combined_registry
from backend.knowledge.world_model_context import schema_context_for_concepts, get_registry

q = "Does a Tesla Model 3 have wheels?"
print("extract_predicate:", repr(extract_predicate(q)))
print("resolve(have):", repr(predicate_resolver.resolve("have")))
print("resolve(has):", repr(predicate_resolver.resolve("has")))
print("predicates_match(have, has):", predicate_resolver.predicates_match("have", "has"))

reg = install_combined_registry()
print("registry installed:", reg is not None)
ent = reg.get_entity("Tesla Model 3")
print("entity:", ent)
if ent is not None:
    schema = ent._resolved_schema()
    print("resolved schema keys:", list(schema.keys()))
    for a in schema:
        print("   ", a, "=", repr(ent.get(a)))
    print("type:", ent.type.name, "ancestors:", ent.type.ancestors())
    print("facets:", [f.name for f in getattr(ent, "facets", []) or []])

print("---- schema_context_for_concepts ----")
for blk in schema_context_for_concepts(["Tesla Model 3"]):
    print(blk)
