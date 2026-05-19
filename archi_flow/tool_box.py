from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from toolbox_core import ToolboxSyncClient
import re

app = FastAPI()

# MCP Toolbox connection
toolbox = ToolboxSyncClient("http://127.0.0.1:8001")
tools = toolbox.load_toolset("sql-toolset")

# pick SQL tool
if not tools:
    raise Exception("No tools found in sql-toolset")

sql_tool = tools[0]  

print("[INIT] Loaded tools:", tools)

# Request schema
class ExecuteQueryRequest(BaseModel):
    query: str


# API
@app.post("/execute-query")
def execute_query(request: ExecuteQueryRequest):
    query = request.query.strip()

    print("\n[API] Received Query:", query)

    # Rule 1: Only allow SELECT queries
    if not query.upper().startswith("SELECT"):
        raise HTTPException(
            status_code=400,
            detail="Only SELECT queries are allowed"
        )

    # Rule 2: Block dangerous keywords (word-based, not substring)
    forbidden = ["DROP", "DELETE", "TRUNCATE", "UPDATE", "INSERT", "ALTER"]

    query_upper = query.upper()

    if any(re.search(rf"\b{word}\b", query_upper) for word in forbidden):
        raise HTTPException(
            status_code=400,
            detail="Unsafe query detected"
        )

    try:
        print("[API] Sending query to MCP tool...")

        #  Calling MCP tool (same as agent)
        result = sql_tool(query)

        print("[API] MCP execution successful")

        return {
            "message": "Query executed via MCP toolbox",
            "executedQuery": query,
            "result": result
        }

    except Exception as e:
        print("[ERROR]", str(e))

        raise HTTPException(
            status_code=500,
            detail=f"MCP execution failed: {str(e)}"    
        )