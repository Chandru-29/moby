import chromadb
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VECTOR_DB_PATH = os.path.join(BASE_DIR, "vector_store")

client = chromadb.PersistentClient(path=VECTOR_DB_PATH)

collections = client.list_collections()

print("\nAvailable collections:\n")

for col in collections:
    print(col.name)

if collections:
    collection = client.get_collection(collections[0].name)
    print("\nDocument count:", collection.count())