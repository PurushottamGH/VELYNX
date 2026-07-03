from backend.memory.knowledge_graph import KnowledgeGraph

# This will create an instance just like your API does
kg = KnowledgeGraph()

# This loop finds the secret file path that your code is actually using
print("Looking for the secret database path...")
for attr in dir(kg):
    if "path" in attr.lower():
        print(f"I found it! The database is living here: {getattr(kg, attr)}")
