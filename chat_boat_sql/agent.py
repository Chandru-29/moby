from google.adk.agents.llm_agent import Agent
from google.adk.tools.agent_tool import AgentTool
from toolbox_core import ToolboxSyncClient

from chat_boat_sql.warehouse_agent import warehouse_agent
# from chat_boat_sql.movement_agent import movement_agent


# Initialize toolbox
toolbox = ToolboxSyncClient("http://127.0.0.1:5000")
tools = toolbox.load_toolset('sql-toolset')



root_agent = Agent(
    model="gemini-2.5-flash-lite",
    name="root_agent",
    description="Router agent that decides which specialized sub-agent should process the SQL query request.",
   instruction='''
            You are the primary conversational agent. Your role is to analyze the user's intent.
            1. **Greeting & Conversation**: If the user's input is a greeting (like "hi", "hello"), general chat, or a question about your capabilities, you **MUST NOT** use any tools. Simply respond conversationally.
            2. **Delegation**: If the user's question relates to retrieving data, quantities, locations, picklists, GRNs, or any information from the database, you **MUST** call the `warehouse_agent  with the full original query.
            3. **Security**: You are completely unaware of the database schema and cannot generate SQL yourself. Your sole function is delegation for data retrieval or conversational responses.
            4. **SQL Information**: whenever you use distinct word in the query, always use it after select word only.
            5. **Never** Show the sql query whethere it is asked or not.
        ''',
     sub_agents=[warehouse_agent],
     tools=[   
        *tools  
    ],
        
      
)

def handle_user_input(user_query: str):
    response = root_agent.generate(user_query)
    sql_text = response.text.strip()

    print("\n Generated SQL Query:")
    print(sql_text)

    if not is_safe_sql(sql_text):
        print("\n Unsafe query detected! Only SELECT queries are allowed.")
        print("The agent will not execute this command.")
        return

    try:
        sql_tool = tools['execute-sql']
        db_result = sql_tool.run({"query": sql_text})
        print("\n Database Result:")
        print(db_result)
    except Exception as e:
        print("\n Error executing SQL query:", e)


def is_safe_sql(sql_text: str) -> bool:
    """Ensure SQL is read-only."""
    forbidden = ["UPDATE", "DELETE", "DROP", "INSERT", "ALTER", "TRUNCATE"]
    sql_upper = sql_text.strip().upper()
    if sql_upper.startswith(("SELECT", "WITH")):
        return not any(word in sql_upper for word in forbidden)
    return False


if __name__ == "__main__":
    print(" Root Router Agent started (read-only SQL mode). Type 'exit' to quit.")
    while True:
        query = input("\nYou: ").strip()
        if query.lower() in ["exit", "quit"]:
            break
        result = handle_user_input(query)
        print(f"\n Result:\n{result}")
