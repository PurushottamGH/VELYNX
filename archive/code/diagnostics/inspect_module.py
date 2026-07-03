from backend.memory import knowledge_graph

# This prints every function/variable inside the knowledge_graph module
print("Functions available in knowledge_graph:")
for item in dir(knowledge_graph):
    if not item.startswith("__"):  # Hide system stuff, show just your code
        print(f" - {item}")
