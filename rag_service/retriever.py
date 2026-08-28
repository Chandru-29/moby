# from rag_service.embedding import embed
# from rag_service.vectorr_store import collection


# # Query Enhancement
# def enhance_query(query: str):

#     q = query.lower()

#     context = []

#     if "picklist" in q:
#         context.append("picklist table schema columns status")

#     if "status" in q:
#         context.append("status meaning values business logic")

#     if "item" in q:
#         context.append("item table columns relationships")

#     if "location" in q:
#         context.append("location sulocation schema inventory")

#     return query + " " + " ".join(context)


# #  Keyword Scoring (light reranking)
# def score_doc(doc: str, query: str):
#     score = 0
#     for word in query.lower().split():
#         if word in doc.lower():
#             score += 1
#     return score


# #  Type Detection (from chunk text)
# def detect_type(doc: str):
#     d = doc.lower()

#     if "type: schema" in d:
#         return "schema"
#     if "type: column" in d:
#         return "column"
#     if "type: relationship" in d:
#         return "relationship"
#     if "type: query" in d:
#         return "query"

#     return "general"


# def retrieve(query: str):

    
#     enhanced_query = enhance_query(query)

#     query_embedding = embed(enhanced_query)

    
#     results = collection.query(
#         query_embeddings=[query_embedding],
#         n_results=12
#     )

#     docs = results.get("documents", [[]])[0]

#     if not docs:
#         return []


#     scored = []
#     for doc in docs:
#         score = score_doc(doc, query)
#         dtype = detect_type(doc)

#         # weight boost
#         if dtype == "schema":
#             score += 3
#         elif dtype == "column":
#             score += 2
#         elif dtype == "relationship":
#             score += 2

#         scored.append((doc, score, dtype))


#     scored.sort(key=lambda x: x[1], reverse=True)


#     final_docs = []
#     used_types = set()

#     for doc, score, dtype in scored:

#         # ensure mix of useful info
#         if dtype not in used_types or len(final_docs) < 3:
#             final_docs.append(doc)
#             used_types.add(dtype)

#         if len(final_docs) >= 6:
#             break

#     return final_docs















# from rag_service.embedding import embed
# from rag_service.vectorr_store import collection


# # ==============================
# # 1. Resolve Tables
# # ==============================
# def resolve_tables(query: str):
#     q = query.lower()
#     tables = set()

#     if "picklist" in q:
#         tables.update(["picklist", "picklistitem", "picklistview"])

#     if "item" in q:
#         tables.update(["item", "skuitem"])

#     if "stock" in q or "inventory" in q:
#         tables.add("sulocation")

#     if "location" in q:
#         tables.add("location")

#     if "grn" in q:
#         tables.add("grn")

#     if "user" in q or "assigned" in q:
#         tables.add("[user]")

#     return tables


# # ==============================
# # 2. Query Enhancement
# # ==============================
# def enhance_query(query: str, tables):
#     context = []

#     for t in tables:
#         context.append(f"{t} schema columns relationships")

#     if len(tables) > 1:
#         context.append("join relationships foreign keys")

#     return query + " " + " ".join(context)


# # ==============================
# # 3. Detect Type
# # ==============================
# def detect_type(doc: str):
#     d = doc.lower()

#     if "type: schema" in d:
#         return "schema"
#     if "type: relationship" in d:
#         return "relationship"
#     if "type: query" in d:
#         return "query"
#     if "type: logic" in d:
#         return "logic"

#     return "general"


# # ==============================
# # 4. Retrieve WITH Metadata Filtering
# # ==============================
# def retrieve(query: str):

#     tables = resolve_tables(query)

#     enhanced_query = enhance_query(query, tables)
#     query_embedding = embed(enhanced_query)

#     # 🔥 STEP 1: Metadata-based filtering
#     where_filter = {
#         "$or": [
#             {"table": {"$in": list(tables)}},
#             {"tables": {"$in": list(tables)}}
#         ]
#     }

#     results = collection.query(
#         query_embeddings=[query_embedding],
#         n_results=30,
#         where=where_filter
#     )

#     docs = results.get("documents", [[]])[0]

#     # 🔥 FALLBACK (if filtering too strict)
#     if not docs:
#         results = collection.query(
#             query_embeddings=[query_embedding],
#             n_results=25
#         )
#         docs = results.get("documents", [[]])[0]

#     if not docs:
#         return []

#     # ==============================
#     # 5. Smart Classification
#     # ==============================
#     schema_docs = []
#     query_docs = []
#     relationship_docs = []
#     other_docs = []

#     for doc in docs:
#         dtype = detect_type(doc)

#         if dtype == "schema":
#             schema_docs.append(doc)
#         elif dtype == "query":
#             query_docs.append(doc)
#         elif dtype == "relationship":
#             relationship_docs.append(doc)
#         else:
#             other_docs.append(doc)

#     # ==============================
#     # 6. Deterministic Assembly
#     # ==============================
#     final_docs = []

#     # MUST: schemas
#     final_docs.extend(schema_docs[:3])

#     # MUST: query patterns
#     final_docs.extend(query_docs[:2])

#     # MUST: relationships
#     final_docs.extend(relationship_docs[:2])

#     # fill remaining
#     for doc in other_docs:
#         if len(final_docs) >= 7:
#             break
#         final_docs.append(doc)

#     # remove duplicates
#     seen = set()
#     unique_docs = []
#     for doc in final_docs:
#         if doc not in seen:
#             unique_docs.append(doc)
#             seen.add(doc)

#     return unique_docs[:7]
















from rag_service.embedding import embed
from rag_service.vectorr_store import collection


# ==============================
# 1. Resolve Tables (NEROLAC SCHEMA)
# ==============================
def resolve_tables(query: str):
    q = query.lower()
    tables = set()

    # picklist intent
    if "picklist" in q or "picking" in q:
        tables.update(["pickuplist", "ss_picklist", "ss_picklistview", "pickuplistmapping"])

    # item intent
    if "item" in q:
        tables.update(["item", "assetmaster", "pallet"])

    # stock / inventory intent
    if "stock" in q or "inventory" in q or "location" in q:
        tables.update(["ss_sulocation", "store", "location", "ss_location", "pivallocation"])

    # batch / production / piv intent
    if "piv" in q or "batch" in q or "production" in q:
        tables.update(["pivheaders", "pivphases", "pivmaterialissueslip", "pivallocation", "intermediatefilling", "productionfilling"])

    # movement / transfer intent
    if "movement" in q or "transfer" in q:
        tables.update(["movementheaders", "movementlineitems", "movementpickuplist", "movementsuidmapping"])

    # quality / revalidation intent
    if "quality" in q or "revalidation" in q or "inspection" in q:
        tables.update(["qualityinspector", "rejmaterialdetails", "revalidation", "updateqistatuslog"])

    # user intent
    if "user" in q or "assigned" in q or "operator" in q:
        tables.add("user")

    return tables


# ==============================
# 2. Query Enhancement
# ==============================
def enhance_query(query: str, tables):
    context = []

    for t in tables:
        context.append(f"{t} schema columns relationships")

    if len(tables) > 1:
        context.append("join relationships foreign keys")

    # MySQL time awareness
    if "last 30 days" in query.lower():
        context.append("filter using cd >= DATE_SUB(NOW(), INTERVAL 30 DAY)")

    return query + " " + " ".join(context)


# ==============================
# 3. Detect Type
# ==============================
def detect_type(doc: str):
    d = doc.lower()

    if "type: schema" in d:
        return "schema"
    if "type: relationship" in d:
        return "relationship"
    if "type: query" in d:
        return "query"
    if "type: logic" in d:
        return "logic"

    return "general"


# ==============================
# 4. Retrieve & Assemble
# ==============================
def retrieve(query: str):
    tables = resolve_tables(query)

    # Detect primary table anchor based on Nerolac terms
    primary_table = None
    q = query.lower()

    if "picklist" in q or "picking" in q:
        primary_table = "pickuplist"
    elif "item" in q:
        primary_table = "item"
    elif "piv" in q or "batch" in q:
        primary_table = "pivheaders"
    elif "movement" in q:
        primary_table = "movementheaders"

    enhanced_query = enhance_query(query, tables)
    query_embedding = embed(enhanced_query)

    # Force primary table search
    primary_docs = []
    if primary_table:
        primary_results = collection.query(
            query_embeddings=[query_embedding],
            n_results=10,
            where={"table": primary_table}
        )
        primary_docs = primary_results.get("documents", [[]])[0]

    # General search
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=30
    )
    docs = results.get("documents", [[]])[0]

    # Combine documents
    docs = primary_docs + docs
    if not docs:
        return []

    # Classification buckets
    schema_docs = []
    query_docs = []
    relationship_docs = []
    other_docs = []

    for doc in docs:
        dtype = detect_type(doc)
        if dtype == "schema":
            schema_docs.append(doc)
        elif dtype == "query":
            query_docs.append(doc)
        elif dtype == "relationship":
            relationship_docs.append(doc)
        else:
            other_docs.append(doc)

    # Deterministic Assembly (Single Clean Block - No Duplication)
    final_docs = []

    # 1. Primary table match first
    for doc in schema_docs:
        if primary_table and f"table: {primary_table}" in doc.lower():
            final_docs.append(doc)

    # 2. Add standard schemas, relationships, and queries
    final_docs.extend(schema_docs[:4])
    final_docs.extend(relationship_docs[:3])
    final_docs.extend(query_docs[:2])

    # 3. Fill remaining slots up to 8 documents
    for doc in other_docs:
        if len(final_docs) >= 8:
            break
        final_docs.append(doc)

    # Remove duplicates while preserving order
    seen = set()
    unique_docs = []
    for doc in final_docs:
        if doc not in seen:
            unique_docs.append(doc)
            seen.add(doc)

    return unique_docs[:8]