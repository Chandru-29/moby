from rag_service.embedding import embed
from rag_service.vectorr_store import collection


# Query Enhancement
def enhance_query(query: str):

    q = query.lower()

    context = []

    if "picklist" in q:
        context.append("picklist table schema columns status")

    if "status" in q:
        context.append("status meaning values business logic")

    if "item" in q:
        context.append("item table columns relationships")

    if "location" in q:
        context.append("location sulocation schema inventory")

    return query + " " + " ".join(context)


#  Keyword Scoring (light reranking)
def score_doc(doc: str, query: str):
    score = 0
    for word in query.lower().split():
        if word in doc.lower():
            score += 1
    return score


#  Type Detection (from chunk text)
def detect_type(doc: str):
    d = doc.lower()

    if "type: schema" in d:
        return "schema"
    if "type: column" in d:
        return "column"
    if "type: relationship" in d:
        return "relationship"
    if "type: query" in d:
        return "query"

    return "general"


def retrieve(query: str):

    
    enhanced_query = enhance_query(query)

    query_embedding = embed(enhanced_query)

    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=12
    )

    docs = results.get("documents", [[]])[0]

    if not docs:
        return []


    scored = []
    for doc in docs:
        score = score_doc(doc, query)
        dtype = detect_type(doc)

        # weight boost
        if dtype == "schema":
            score += 3
        elif dtype == "column":
            score += 2
        elif dtype == "relationship":
            score += 2

        scored.append((doc, score, dtype))


    scored.sort(key=lambda x: x[1], reverse=True)


    final_docs = []
    used_types = set()

    for doc, score, dtype in scored:

        # ensure mix of useful info
        if dtype not in used_types or len(final_docs) < 3:
            final_docs.append(doc)
            used_types.add(dtype)

        if len(final_docs) >= 6:
            break

    return final_docs