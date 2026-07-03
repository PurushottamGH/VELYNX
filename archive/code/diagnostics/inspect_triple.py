import inspect
from backend.memory.knowledge_graph import KnowledgeGraph

kg = KnowledgeGraph()
print("Correct signature for add_triple:")
print(inspect.signature(kg.add_triple))
