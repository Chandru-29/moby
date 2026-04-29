import os
from embedding import embed
from vectorr_store import collection

print("Using collection:", collection.name)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_PATH = os.path.join(BASE_DIR, "knowledge")

print("Resolved knowledge path:", KNOWLEDGE_PATH)



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


def ingest_documents():

    print("Knowledge files:", os.listdir(KNOWLEDGE_PATH))

    for file in os.listdir(KNOWLEDGE_PATH):

        if file.endswith(".md"):

            file_path = os.path.join(KNOWLEDGE_PATH, file)

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()


            chunks = smart_chunk(content)

            for i, chunk in enumerate(chunks):


                chunk_for_embedding = f"""
                Warehouse Management System Knowledge:

                {chunk}
                """

                embedding = embed(chunk_for_embedding)

                collection.add(
                    documents=[chunk],
                    embeddings=[embedding],
                    ids=[f"{file}_{i}"]
                )

    print("Knowledge ingested successfully")
    print("Total documents stored:", collection.count())


if __name__ == "__main__":
    ingest_documents()