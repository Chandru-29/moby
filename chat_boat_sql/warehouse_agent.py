from google.adk.agents.llm_agent import Agent
# from toolbox_core import ToolboxSyncClient

from rag_service.rag_tool import retrieve_knowledge

from chat_boat_sql.instruction_manager import build_dynamic_instructions


# toolbox = ToolboxSyncClient("http://127.0.0.1:8001")
# tools = toolbox.load_toolset('sql-toolset')

import httpx

REMOTE_DB_API_URL = "https://dlzfnf88-8010.inc1.devtunnels.ms/execute-query"

def execute_sql_query(query: str) -> dict:
    """Executes a read-only SELECT query against the remote Mobillor Database API."""
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(REMOTE_DB_API_URL, json={"query": query})
            if response.status_code != 200:
                return {"error": f"API error: {response.text}"}
            return response.json()
    except Exception as e:
        return {"error": f"Connection failed: {str(e)}"}

def get_warehouse_agent(user_query: str):
    # 1. Dynamically build the instructions based on user query
    dynamic_instruction = build_dynamic_instructions(user_query)
    
    # 2. Create and return the agent inside the function
    warehouse_agent = Agent(
        model='gemini-3.5-flash-lite',
        name='warehouse_agent',
        description='A specialized sql query generator for a Nerolac database (read-only MySQL).',
        instruction=dynamic_instruction,
        tools=[retrieve_knowledge, execute_sql_query]
    )
    
    return warehouse_agent