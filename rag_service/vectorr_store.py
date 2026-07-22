import chromadb
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VECTOR_DB_PATH = os.path.join(BASE_DIR, "vector_store")

client = chromadb.PersistentClient(path=VECTOR_DB_PATH)

collection = client.get_or_create_collection(
    name="knowledge"
)