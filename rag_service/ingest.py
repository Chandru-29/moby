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










import os
import re
from embedding import embed
from vectorr_store import collection

print("Using collection:", collection.name)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_PATH = os.path.join(BASE_DIR, "knowledge")

print("Resolved knowledge path:", KNOWLEDGE_PATH)


# ==============================
# 1. Smart Chunking
# ==============================
def smart_chunk(content):
    chunks = []
    current_chunk = []

    for line in content.split("\n"):
        if line.startswith("# "):
            if current_chunk:
                chunks.append("\n".join(current_chunk).strip())
                current_chunk = []
        current_chunk.append(line)

    if current_chunk:
        chunks.append("\n".join(current_chunk).strip())

    return chunks


# ==============================
# 2. Safe Metadata Extraction
# ==============================
def extract_metadata(chunk: str):

    lower = chunk.lower()

    metadata = {
        "type": "general",
        "table": "",
        "tables": ""
    }

    # ---- TYPE ----
    if "type: schema" in lower:
        metadata["type"] = "schema"
    elif "type: relationship" in lower:
        metadata["type"] = "relationship"
    elif "type: query" in lower:
        metadata["type"] = "query"
    elif "type: logic" in lower:
        metadata["type"] = "logic"
    elif "type: guidance" in lower:
        metadata["type"] = "guidance"

    # ---- PRIMARY TABLE ----
    table_match = re.search(r"# table:\s*([\w\[\]]+)", lower)
    if table_match:
        metadata["table"] = table_match.group(1)

    # ---- MULTI TABLE DETECTION ----
    known_tables = [
        "item", "skuitem", "sulocation", "location",
        "picklist", "picklistitem", "picklistview",
        "grn", "[user]"
    ]

    found_tables = []
    for t in known_tables:
        if t in lower:
            found_tables.append(t)

    # IMPORTANT: convert list → string (Chroma safe)
    metadata["tables"] = ",".join(found_tables)

    # FINAL SAFETY (force string)
    metadata = {
        "type": str(metadata["type"]),
        "table": str(metadata["table"]),
        "tables": str(metadata["tables"])
    }

    return metadata


# ==============================
# 3. Ingestion (SAFE VERSION)
# ==============================
def ingest_documents():

    print("\n Knowledge files:", os.listdir(KNOWLEDGE_PATH))

    total_inserted = 0

    for file in os.listdir(KNOWLEDGE_PATH):

        if file.endswith(".md"):

            file_path = os.path.join(KNOWLEDGE_PATH, file)

            print(f"\n Processing file: {file}")

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            chunks = smart_chunk(content)

            print(f"🔹 Total chunks: {len(chunks)}")

            for i, chunk in enumerate(chunks):

                try:
                    metadata = extract_metadata(chunk)

                    # DEBUG (first few only)
                    if i < 3:
                        print("\n--- SAMPLE CHUNK ---")
                        print(chunk[:200])
                        print("Metadata:", metadata)

                    embedding = embed(chunk)

                    collection.add(
                        documents=[chunk],
                        embeddings=[embedding],
                        metadatas=[metadata],
                        ids=[f"{file}_{i}"]
                    )

                    total_inserted += 1

                except Exception as e:
                    print(f" Error inserting chunk {i}:", e)

    print("\n Knowledge ingested successfully")
    print("Inserted chunks:", total_inserted)
    print("Total documents stored:", collection.count())


# ==============================
# 4. Run
# ==============================
if __name__ == "__main__":
    ingest_documents()