from nltk.stem import PorterStemmer, WordNetLemmatizer

s = PorterStemmer()
l = WordNetLemmatizer()

pairs = [
    ("forgave", "forgiveness"),
    ("plans", "planning"),
    ("angry", "anger"),
    ("lonely", "loneliness"),
    ("grieving", "grief"),
    ("betray", "betrayal"),
    ("betrayed", "betrayal"),
    ("loves", "love"),
    ("hoping", "hope"),
    ("sad", "depression"),
    ("painful", "pain"),
    ("courageous", "courage"),
    ("trusting", "trust"),
    ("regretful", "regret"),
    ("grateful", "gratitude"),
    ("jealous", "jealousy"),
    ("forgiven", "forgiveness"),
    ("forgive", "forgiveness"),
]

print(f"{'Query':15s} {'Concept':15s} {'StemQ':10s} {'StemC':10s} {'Match':8s}")
print("-" * 60)
for q, concept in pairs:
    s_q = s.stem(q)
    s_c = s.stem(concept)
    # stem: exact or substring overlap
    stem_match = (
        (s_q == s_c)
        or (len(s_q) >= 4 and s_q[:4] == s_c[:4])
        or (len(s_c) >= 4 and s_c[:4] == s_q[:4])
    )

    # Lemmatization approach
    lemma_match = False
    for pos in ["v", "n", "a"]:
        l_q = l.lemmatize(q, pos)
        l_c = l.lemmatize(concept, pos)
        if l_q == l_c:
            lemma_match = True

    print(f"{q:15s} {concept:15s} {s_q:10s} {s_c:10s} {str(stem_match or lemma_match):8s}")
