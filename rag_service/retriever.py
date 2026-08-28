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













# #before domain wise retrieval


# from rag_service.embedding import embed
# from rag_service.vectorr_store import collection


# # ==============================
# # 1. Resolve Tables (NEROLAC SCHEMA)
# # ==============================
# def resolve_tables(query: str):
#     q = query.lower()
#     domains = set()
#     tables = set()

#     # picklist intent
#     if "picklist" in q or "picking" in q:
#         tables.update(["pickuplist", "ss_picklist", "ss_picklistview", "pickuplistmapping"])

#     # item intent
#     if "item" in q:
#         tables.update(["item", "assetmaster", "pallet"])

#     # stock / inventory intent
#     if "stock" in q or "inventory" in q or "location" in q:
#         tables.update(["ss_sulocation", "store", "location", "ss_location", "pivallocation"])

#     # batch / production / piv intent
#     if "piv" in q or "batch" in q or "production" in q:
#         tables.update(["pivheaders", "pivphases", "pivmaterialissueslip", "pivallocation", "intermediatefilling", "productionfilling"])

#     # movement / transfer intent
#     if "movement" in q or "transfer" in q:
#         tables.update(["movementheaders", "movementlineitems", "movementpickuplist", "movementsuidmapping"])

#     # quality / revalidation intent
#     if "quality" in q or "revalidation" in q or "inspection" in q:
#         tables.update(["qualityinspector", "rejmaterialdetails", "revalidation", "updateqistatuslog"])

#     # user intent
#     if "user" in q or "assigned" in q or "operator" in q:
#         tables.add("user")

#     return tables


# # ==============================
# # 2. Query Enhancement
# # ==============================
# def enhance_query(query: str, tables):
#     context = []

#     for t in tables:
#         context.append(f"{t} schema columns relationships rules status query pattern")

#     # if len(tables) > 1:
#     #     context.append("join relationships foreign keys workflow business logic")

#     # MySQL time awareness
#     if "last 30 days" in query.lower():
#         context.append("filter using cd >= DATEADD(day, -30, GETDATE())")

#     return query + " " + " ".join(context)


# # # ==============================
# # # 3. Detect Type
# # # ==============================
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
# # 4. Retrieve & Assemble (Optimized & Clean)
# # ==============================
# def retrieve(query: str):
#     # 1. resolve table from the query 
#     tables = resolve_tables(query)
#     # table_list = list(tables)
    
#     # 2. enhance Query  & embedding 
#     enhanced_query = enhance_query(query, tables)
#     query_embedding = embed(enhanced_query)

#     # it takes only the required tables data
#     results = collection.query(
#         query_embeddings=[query_embedding],
#         n_results=8,
#     #where={"table": {"$in": table_list}} if table_list else None
#     )
    
#     docs = results.get("documents", [[]])[0]
    
    
#     if not docs:
#         return []

#     # 4. Duplicate removal
#     seen = set()
#     unique_docs = []
#     for doc in docs:
#         if doc not in seen:
#             unique_docs.append(doc)
#             seen.add(doc)

#     return unique_docs[:6]



# # ==============================
# # 4. Retrieve & Assemble
# # ==============================
# def retrieve(query: str):
#     tables = resolve_tables(query)

#     # Detect primary table anchor based on Nerolac terms
#     primary_table = None
#     q = query.lower()

#     if "picklist" in q or "picking" in q:
#         primary_table = "pickuplist"
#     elif "item" in q:
#         primary_table = "item"
#     elif "piv" in q or "batch" in q:
#         primary_table = "pivheaders"
#     elif "movement" in q:
#         primary_table = "movementheaders"

#     enhanced_query = enhance_query(query, tables)
#     query_embedding = embed(enhanced_query)

#     # Force primary table search
#     primary_docs = []
#     if primary_table:
#         primary_results = collection.query(
#             query_embeddings=[query_embedding],
#             n_results=10,
#             where={"table": primary_table}
#         )
#         primary_docs = primary_results.get("documents", [[]])[0]

#     # General search
#     results = collection.query(
#         query_embeddings=[query_embedding],
#         n_results=30
#     )
#     docs = results.get("documents", [[]])[0]

#     # Combine documents
#     docs = primary_docs + docs
#     if not docs:
#         return []

#     # Classification buckets
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

#     # Deterministic Assembly (Single Clean Block - No Duplication)
#     final_docs = []

#     # 1. Primary table match first
#     for doc in schema_docs:
#         if primary_table and f"table: {primary_table}" in doc.lower():
#             final_docs.append(doc)

#     # 2. Add standard schemas, relationships, and queries
#     final_docs.extend(schema_docs[:4])
#     final_docs.extend(relationship_docs[:3])
#     final_docs.extend(query_docs[:2])

#     # 3. Fill remaining slots up to 8 documents
#     for doc in other_docs:
#         if len(final_docs) >= 8:
#             break
#         final_docs.append(doc)

#     # Remove duplicates while preserving order
#     seen = set()
#     unique_docs = []
#     for doc in final_docs:
#         if doc not in seen:
#             unique_docs.append(doc)
#             seen.add(doc)

#     return unique_docs[:8]





import re
from rag_service.embedding import embed
from rag_service.vectorr_store import collection

# Dynamic word boundary checker for short keywords
def has_word(query_text: str, target: str) -> bool:
    return bool(re.search(rf"\b{re.escape(target)}\b", query_text))

# ==============================
# 1. Resolve Domains & Entire Domain Tables (Smart Routing)
# ==============================
def resolve_domains_and_tables(query: str):
    q = query.lower()
    words = set(re.findall(r'\b\w+\b', q))  # Pre-tokenized word set for O(1) exact word matching
    domains = set()
    tables = set()

    # Domain 0: Global / User / Logs
    if any(k in words for k in ["user", "creator", "assigned", "operator", "weight", "weighbridge", "log", "gateway"]) or has_word(q, "who") or "created by" in q:
        domains.add("domain_0")
        tables.update(["user", "log", "gatewaylogs"])

    # Domain 1: Picklist & Warehouse Picking
    if any(k in q for k in ["picklist", "picking", "pickup"]):
        domains.add("domain_1")
        tables.update([
            "pickuplist", "ss_picklist", "ss_picklistview", "pickuplistmapping",
            "ss_document", "ss_transactionm", "ss_mvt", "ss_supersedefefomapping"
        ])

    # Domain 2: Inventory, Store & Location
    if any(k in words for k in ["item", "stock", "inventory", "location", "bin"]):
        domains.add("domain_2")
        tables.update([
            "item", "store", "ss_sulocation", "location", "ss_location", 
            "warehouse", "ss_warehouse", "ss_whlocmap", "ss_whtypemap", 
            "ss_itemcategory", "ss_relationalloctype", "ss_itemlocacnmap", "pivallocation"
        ])

    # Domain 3: Production Orders & PIV
    if any(k in words for k in ["piv", "batch", "production"]) or "process order" in q:
        domains.add("domain_3")
        tables.update([
            "pivheaders", "pivphases", "pivmaterialissueslip", "pivallocation"
        ])

    # Domain 4: Material Movement & Transfers
    if "movement" in q or "transfer" in q:
        domains.add("domain_4")
        tables.update([
            "movementheaders", "movementlineitems", "movementpickuplist", 
            "movementsuidmapping", "movementtypes", "ss_mvt"
        ])

    # Domain 5: Roles, Permissions & Assets
    if any(k in words for k in ["asset", "pallet", "printer", "role", "resource", "access", "quality", "inspector", "revalidation", "reject"]):
        domains.add("domain_5")
        tables.update([
            "accesses", "action", "submodules", "department", "qualityinspector", 
            "rejmaterialdetails", "revalidation", "updateqistatuslog", "reqtypes", 
            "assetmaster", "pallet", "tempassetmapping", "resource", "printer"
        ])

    # Domain 6: Filling & Weight Operations
    if any(k in q for k in ["filling", "weight", "scale", "stainer"]):
        domains.add("domain_6")
        tables.update([
            "intermediatefilling", "intermediatefillinggrn", "productionfilling", 
            "stainersmanualweightlogs", "gatewaylogs"
        ])

    return domains, tables


# ==============================
# 2. Query Enhancement
# ==============================
def enhance_query(query: str, tables: set) -> str:
    # Separate table names with spaces so embedding models read them correctly
    table_str = " ".join(sorted(tables)) if tables else ""
    return f"{query} [Tables: {table_str}]" if table_str else query


# ==============================
# 3. Retrieve & Assemble (Targeted Domain Fetch)
# ==============================
def retrieve(query: str) -> list[str]:
    # 1. Resolve domains and tables based on query intent
    _, tables = resolve_domains_and_tables(query)

    # 2. Enhance Query & Embedding
    enhanced_query = enhance_query(query, tables)
    query_embedding = embed(enhanced_query)

    docs = []

    # 3. Targeted query with Metadata Filter
    if tables:
        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=10,
                where={
                    "$or": [
                        {"table": {"$in": list(tables)}},
                        {"type": "global_rule"}
                    ]
                }
            )
            docs = results.get("documents", [[]])[0]
        except Exception:
            docs = []

    # 4. Fallback Safety Net (if no match or tables empty)
    if not docs:
        fallback_results = collection.query(
            query_embeddings=[query_embedding],
            n_results=10,
        )
        docs = fallback_results.get("documents", [[]])[0]

    # 5. Prioritize global rules in Python memory (No 2nd DB Query)
    rule_docs = [d for d in docs if "global_rule" in d.lower() or "type: global_rule" in d.lower()]
    other_docs = [d for d in docs if d not in rule_docs]
    
    combined_docs = rule_docs + other_docs

    # 6. Deduplicate preserving priority order
    seen = set()
    unique_docs = []
    for doc in combined_docs:
        if doc not in seen:
            unique_docs.append(doc)
            seen.add(doc)

    return unique_docs[:15]
