import inspect
from backend.memory.knowledge_graph import KnowledgeGraph

# Peek at the source code for add_triple
print(inspect.getsource(KnowledgeGraph.add_triple))
