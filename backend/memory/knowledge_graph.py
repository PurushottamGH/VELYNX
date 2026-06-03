from difflib import SequenceMatcher

class KnowledgeGraph:
    def __init__(self):
        pass

    async def load(self):
        pass

    async def fast_query(self, query):
        # fast_query is not implemented yet — placeholder for future graph lookup
        return None

    async def _semantic_matches(self, hit_topic: str, query: str) -> bool:
        """Guard against cross-topic false positives in fast_query."""
        if not hit_topic:
            return False
        similarity = SequenceMatcher(None, query.lower(), hit_topic.lower()).ratio()
        return similarity >= 0.25

    async def store_answer(self, query, answer, confidence, sources):
        pass

    async def add_triple(self, triple):
        pass

    async def get_understanding(self, topic):
        return None

    async def store_understanding(self, topic, summary):
        pass
