import requests

RAG_URL = "http://127.0.0.1:9000/retrieve"

def retrieve_knowledge(query: str) -> str:
    """
    Retrieve relevant warehouse knowledge from the RAG service.
    """

    try:
        response = requests.post(
            RAG_URL,
            json={"query": query},
            timeout=5
        )

        data = response.json()
        docs = data.get("context", [])

        # return "\n".join(docs)
        return f"""
        RELEVANT DATABASE KNOWLEDGE:

        {chr(10).join(docs)}

        STRICT RULES:
        - Use ONLY the tables and columns above
        - Do NOT invent schema
        - Follow relationships if joins are needed
"""

    except Exception as e:
        return f"RAG retrieval failed: {str(e)}"