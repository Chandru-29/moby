# import os
# from embedding import embed
# from vectorr_store import collection

# print("Using collection:", collection.name)


# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# KNOWLEDGE_PATH = os.path.join(BASE_DIR, "knowledge")

# print("Resolved knowledge path:", KNOWLEDGE_PATH)



# def smart_chunk(content):
#     chunks = []
#     current_chunk = []

#     for line in content.split("\n"):
#         if line.startswith("# "):
#             if current_chunk:
#                 chunks.append("\n".join(current_chunk).strip())
#                 current_chunk = []
#         current_chunk.append(line)

#     if current_chunk:
#         chunks.append("\n".join(current_chunk).strip())

#     return chunks


# def ingest_documents():

#     print("Knowledge files:", os.listdir(KNOWLEDGE_PATH))

#     for file in os.listdir(KNOWLEDGE_PATH):

#         if file.endswith(".md"):

#             file_path = os.path.join(KNOWLEDGE_PATH, file)

#             with open(file_path, "r", encoding="utf-8") as f:
#                 content = f.read()


#             chunks = smart_chunk(content)

#             for i, chunk in enumerate(chunks):


#                 chunk_for_embedding = f"""
#                 Warehouse Management System Knowledge:

#                 {chunk}
#                 """

#                 embedding = embed(chunk_for_embedding)

#                 collection.add(
#                     documents=[chunk],
#                     embeddings=[embedding],
#                     ids=[f"{file}_{i}"]
#                 )

#     print("Knowledge ingested successfully")
#     print("Total documents stored:", collection.count())


# if __name__ == "__main__":
#     ingest_documents()







# chuncking the data in TABLE wise with metadata 28-08-2026  


import os
import re
import hashlib
try:
    from rag_service.embedding import embed
    from rag_service.vectorr_store import collection
except ImportError:
    from embedding import embed
    from vectorr_store import collection

print("Using collection:", collection.name)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_PATH = os.path.join(BASE_DIR, "knowledge")

print("Resolved knowledge path:", KNOWLEDGE_PATH)


# ==============================
# 1. Table-Level Granular Chunking
# ==============================
def smart_chunk(content):
    """Splits content first by Domain, then further breaks it down
    into Table-level chunks using '### TABLE:' or '# table:' headers.
    """
    chunks = []
    
    # Split by Domain sections
    domain_sections = content.split("# DOMAIN:")

    for section in domain_sections:
        if not section.strip():
            continue
        
        domain_text = "# DOMAIN:" + section.strip()

        # Further split each domain into individual table blocks using '### TABLE:' or '# table:'
        table_splits = re.split(r"(?=[#]{1,3}\s+(?:TABLE|table):\s*[\w\[\]]+)", domain_text)

        for split in table_splits:
            if not split.strip():
                continue
            chunks.append(split.strip())

    return chunks


# ==============================
# 2. Safe Metadata Extraction (With Smart Fallback)
# ==============================
def extract_metadata(chunk: str, all_discovered_tables: set):
    lower = chunk.lower()

    metadata = {"type": "general", "table": "", "tables": ""}

    # ---- TYPE EXTRACTION ----
    # Fix: Ensure global_rule matches retriever.py query filters!
    if "type: global_rule" in lower or "global_rule" in lower or "global rules" in lower:
        metadata["type"] = "global_rule"
    elif "type: schema" in lower or "schema_domain" in lower or "### table:" in lower or "# table:" in lower:
        metadata["type"] = "schema"
    elif "type: relationship" in lower or "join" in lower:
        metadata["type"] = "relationship"
    elif "type: query" in lower or "select" in lower:
        metadata["type"] = "query"
    elif "type: logic" in lower:
        metadata["type"] = "logic"
    elif "type: guidance" in lower:
        metadata["type"] = "guidance"
    else:
        metadata["type"] = "context"

    # ---- 1. EXPLICIT TABLE MATCH (# table: or ### TABLE:) ----
    table_match = re.search(r"(?:#|###)\s+table:\s*([\w\[\]]+)", lower)
    if table_match:
        metadata["table"] = table_match.group(1).lower()

    # ---- 2. DYNAMIC MULTI TABLE DETECTION ----
    found_tables = []
    for t in all_discovered_tables:
        if t and re.search(r"\b" + re.escape(t) + r"\b", lower):
            found_tables.append(t)

    # ---- 3. SMART INHERITANCE (If explicit table is missing, pick from found tables) ----
    if not metadata["table"] and found_tables:
        metadata["table"] = found_tables[0]

    metadata["tables"] = ",".join(list(set(found_tables)))

    # FINAL SAFETY (force string)
    metadata = {
        "type": str(metadata["type"]),
        "table": str(metadata["table"]),
        "tables": str(metadata["tables"]),
    }

    return metadata


# ==============================
# 3. Ingestion (GRANULAR & SAFE)
# ==============================
def ingest_documents():
    if not os.path.exists(KNOWLEDGE_PATH):
        print(f" Error: Knowledge path {KNOWLEDGE_PATH} does not exist!")
        return

    print("\nKnowledge files:", os.listdir(KNOWLEDGE_PATH))

    total_inserted = 0
    all_discovered_tables = set()

    # Step 1: Auto-discover table names cleanly from markdown files
    for file in os.listdir(KNOWLEDGE_PATH):
        if file.endswith(".md"):
            file_path = os.path.join(KNOWLEDGE_PATH, file)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            for line in content.split("\n"):
                lower_line = line.lower()
                # Matches "### TABLE: table_name" or "TARGET TABLES: t1, t2, t3"
                if "table:" in lower_line or "target tables:" in lower_line:
                    parts = line.split(":")
                    if len(parts) > 1:
                        # Split by comma in case of multi-table headers
                        raw_tables = parts[1].split(",")
                        for raw_t in raw_tables:
                            tbl = re.sub(r"[^\w]", "", raw_t.strip().lower())
                            if tbl and tbl not in ["none"]:
                                all_discovered_tables.add(tbl)

    print(f"[-] Dynamically Discovered Tables ({len(all_discovered_tables)}): {sorted(list(all_discovered_tables))}")

    # Step 2: Chunk and Insert/Upsert into ChromaDB
    for file in os.listdir(KNOWLEDGE_PATH):
        if file.endswith(".md"):
            file_path = os.path.join(KNOWLEDGE_PATH, file)
            print(f"\nProcessing file: {file}")

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            chunks = smart_chunk(content)
            print(f"[-] Total granular chunks: {len(chunks)}")

            for i, chunk in enumerate(chunks):
                try:
                    metadata = extract_metadata(chunk, all_discovered_tables)

                    # DEBUG (first few only)
                    if i < 3:
                        print("\n--- SAMPLE GRANULAR CHUNK ---")
                        print(chunk[:250] + "...")
                        print("Metadata:", metadata)

                    embedding = embed(chunk)

                    # Deterministic hash to prevent duplicate entries on re-run
                    hash_suffix = hashlib.md5(chunk.encode("utf-8")).hexdigest()[:8]
                    chunk_id = f"{file}_chunk_{i}_{hash_suffix}"

                    # Upsert handles both new insertions and re-ingestion cleanly
                    collection.upsert(
                        documents=[chunk],
                        embeddings=[embedding],
                        metadatas=[metadata],
                        ids=[chunk_id]
                    )

                    total_inserted += 1

                except Exception as e:
                    print(f" Error inserting chunk {i}:", e)

    print("\n Knowledge ingested successfully!")
    print("Inserted/Upserted chunks:", total_inserted)
    print("Total documents stored in collection:", collection.count())


# ==============================
# 4. Run
# ==============================
if __name__ == "__main__":
    ingest_documents()