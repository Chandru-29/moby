from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

app = FastAPI()

model = SentenceTransformer("all-MiniLM-L6-v2")

class Query(BaseModel):
    text: str

@app.post("/embed")
def embed_text(query: Query):

    embedding = model.encode(query.text).tolist()

    return {
        "embedding": embedding
    }