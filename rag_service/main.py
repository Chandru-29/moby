from fastapi import FastAPI
from rag_service.retriever import retrieve

app = FastAPI()

@app.post("/retrieve")
def retrieve_context(data: dict):

    query = data["query"]

    docs = retrieve(query)

    return {
        "context": docs
    }

