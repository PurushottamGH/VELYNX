from backend.memory.knowledge_graph import KnowledgeGraph
from backend.knowledge.epistemic_manager import initialize_epistemic_schema

print("Bootstrapping VELYNX Database...")

# 1. Initialize the Main Knowledge Graph
# Instantiating the class usually triggers the schema creation in __init__
kg = KnowledgeGraph()
print("Main Knowledge Graph initialized.")

# 2. Initialize the Epistemic Schema
# We know this function works from our previous work
initialize_epistemic_schema()
print("Epistemic tables created.")

print("Success! Schema is ready.")
