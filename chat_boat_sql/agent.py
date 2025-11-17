from google.adk.agents.llm_agent import Agent
from google.adk.tools.agent_tool import AgentTool
from toolbox_core import ToolboxSyncClient

from chat_boat_sql.inventory_agent import inventory_agent
from chat_boat_sql.movement_agent import movement_agent


# Initialize toolbox
toolbox = ToolboxSyncClient("http://127.0.0.1:5000")
tools = toolbox.load_toolset('sql-toolset')


# Helper function: classify which child agent should handle the query
def detect_agent_context(query: str):
    """Detect which agent should handle the user's query based on keywords."""
    q = query.lower()

    # Movement-related keywords
    movement_keywords = [
        "picklist","picklists", "suid", "fgmodel", "movement", "transfer",
        "delivery", "putaway", "pallet", "vin", "bin", "shipment"
    ]

    # Inventory-related keywords
    inventory_keywords = [
        "grn", "item", "sku", "stock", "inventory", "warehouse", "location"
    ]

    if any(k in q for k in movement_keywords):
        return "movement"
    elif any(k in q for k in inventory_keywords):
        return "inventory"
    else:
        return "general"


# Define the router agent
root_agent = Agent(
    model="gemini-2.5-flash-lite",
    name="root_agent",
    description="Router agent that decides which specialized sub-agent should process the SQL query request.",
    instruction="""You are a router agent. Based on the user’s question, decide whether to use the
                   movement_agent or the inventory_agent for generating SQL. If the query does not
                   match either category, handle it using general SQL logic (read-only), If the user is greeting, DO NOT call any tools. Just answer normally.
                   Remember that if the query contains any of these words in any form like singular or plural : "picklist","picklists", "suid", "fgmodel", "movement", "transfer",
                   "delivery", "putaway", "pallet", "vin", "bin", "shipment". then you should choose the movement agent.
                    And if the query contains any of  these words in any form like singular or plural : "grn", "item", "sku", "stock", "inventory", "warehouse", "location", then you should choose Inventory agent
                    If the query is ambiguous, ask a short clarifying question.
#                   Don't use any table query that get the list of tables in the database.
#                   Put a hard limit of 100 rows in the SQL query using "TOP 100" to avoid large data retrieval.""",
    tools=[
        AgentTool(agent=inventory_agent),
        AgentTool(agent=movement_agent),
        *tools  
    ],
)


# ---------------------------------------------------------------
# ROUTING LOGIC
# ---------------------------------------------------------------
def handle_user_input(user_query: str):
    """Route query to correct agent and execute SQL safely."""
    print(f"\n Root Agent received query: {user_query}")

    agent_type = detect_agent_context(user_query)
    print(f" Detected agent type: {agent_type}")

    if agent_type == "movement":
        print(" Routing to Movement Agent...")
        response = movement_agent.generate(user_query) # type: ignore
    elif agent_type == "inventory":
        print(" Routing to Inventory Agent...")
        response = inventory_agent.generate(user_query) # type: ignore
    else:
        print(" Handling query directly via Root Agent...")
        response = root_agent.generate(user_query) # type: ignore

    sql_text = response.text.strip()
    print(f"\n Generated SQL Query:\n{sql_text}")

    # Safety filter — ensure only SELECT or WITH queries
    if not is_safe_sql(sql_text):
        print(" Unsafe query detected. Only SELECT/READ queries allowed.")
        return "Unsafe query detected. Only SELECT queries are permitted."

    # Execute via toolbox
    try:
        sql_tool = tools["execute-sql"] # type: ignore
        db_result = sql_tool.run({"query": sql_text})
        print("\n Database Result:")
        print(db_result)
        return db_result
    except Exception as e:
        print(f" SQL Execution Error: {e}")
        return str(e)


def is_safe_sql(sql_text: str) -> bool:
    """Ensure SQL is read-only."""
    forbidden = ["UPDATE", "DELETE", "DROP", "INSERT", "ALTER", "TRUNCATE"]
    sql_upper = sql_text.strip().upper()
    if sql_upper.startswith(("SELECT", "WITH")):
        return not any(word in sql_upper for word in forbidden)
    return False


# CLI for testing
if __name__ == "__main__":
    print(" Root Router Agent started (read-only SQL mode). Type 'exit' to quit.")
    while True:
        query = input("\nYou: ").strip()
        if query.lower() in ["exit", "quit"]:
            break
        result = handle_user_input(query)
        print(f"\n Result:\n{result}")














# from google.adk.agents.llm_agent import Agent
# from google.adk.tools.agent_tool import AgentTool
# from toolbox_core import ToolboxSyncClient
# import re
# from chat_boat_sql.inventory_agent import inventory_agent
# from chat_boat_sql.movement_agent import movement_agent,movement_relations, build_join_context


# # Initialize toolbox
# toolbox = ToolboxSyncClient("http://127.0.0.1:5000")
# tools = toolbox.load_toolset('sql-toolset')


# def has_word(text, word):
#     """Returns True only if 'word' appears as a whole word in the text."""
#     return re.search(rf"\b{re.escape(word)}\b", text) is not None

# # Helper function: classify which child agent should handle the query
# def detect_agent_context(query: str):
#     """Detect which agent should handle the user's query based on keywords."""
#     q = query.lower()
#     # Inventory-related keywords
   
   
#     inventory_keywords = [
#         "grn", "item", "sku", "stock", "inventory", "warehouse", "location"
#     ]


#     # Movement-related keywords
#     movement_keywords = [
#         "picklist","picklists", "suid", "fgmodel", "movement", "transfer",
#         "delivery", "putaway", "pallet", "vin", "bin", "shipment"
#     ]



#     if any(has_word(q, k) for k in movement_keywords):
#         return "movement"
#     elif any(has_word(q, k) for k in inventory_keywords):
#         return "inventory"
#     else:
#         return "general"


# # Define the router agent
# root_agent = Agent(
#     model="gemini-2.5-flash",
#     name="root_agent",
#     description="Router agent that decides which specialized sub-agent should process the SQL query request.",
#     instruction="""You are a router agent. Based on the user’s question, decide whether to use the
#                    movement_agent or the inventory_agent for generating SQL. If the query does not
#                    match either category, handle it using general SQL logic (read-only),
#                      If the query is ambiguous, ask a short clarifying question.
# #                     Don't use any table query that get the list of tables in the database.
# #                     Put a hard limit of 100 rows in the SQL query using "TOP 100" to avoid large data retrieval.

    
    
 
# """,
                    
#     tools=[
#         AgentTool(agent=inventory_agent),
#         AgentTool(agent=movement_agent),
#         *tools  
#     ],
# )

# # You are the root router agent for a warehouse data assistant.
#                     # If the user's query is about **inventory, stock, or movement**, your Python routing script will handle it.
#                     # Your job is ONLY to answer simple, general, non-SQL-related conversational questions (e.g., greetings, capabilities).
#                     # If the query is ambiguous or doesn't fit any category, ask a short clarifying question.
#                     # If you are asked about your capabilities like: 'WHAT CAN YOU DO' then reply 'i can answer all your questions related to warehouses'.
#                     # Do not generate or attempt to execute any SQL queries yourself.
# # ---------------------------------------------------------------
# # ROUTING LOGIC
# # ---------------------------------------------------------------
# def handle_user_input(user_query: str):
#     """Route query to correct agent and execute SQL safely."""
#     print(f"\n Root Agent received query: {user_query}")

#     agent_type = detect_agent_context(user_query)
#     print(f" Detected agent type: {agent_type}")

#     if agent_type == "movement":
#         print(" Routing to Movement Agent...")
#         response = movement_agent.generate(user_query) 
#     elif agent_type == "inventory":
#         print(" Routing to Inventory Agent...")
#         response = inventory_agent.generate(user_query) 
#     else:
#         print(" Handling query directly via Root Agent...")
#         response = root_agent.generate(user_query) 

#     sql_text = response.text.strip()
#     print(f"\n Generated SQL Query:\n{sql_text}")

#     # Safety filter — ensure only SELECT or WITH queries
#     if not is_safe_sql(sql_text):
#         print(" Unsafe query detected. Only SELECT/READ queries allowed.")
#         return "Unsafe query detected. Only SELECT queries are permitted."

#     # Execute via toolbox
#     try:
#         sql_tool = tools["execute-sql"] # type: ignore
#         db_result = sql_tool.run({"query": sql_text})
#         print("\n Database Result:")
#         print(db_result)
#         return db_result
#     except Exception as e:
#         print(f" SQL Execution Error: {e}")
#         return str(e)





# def is_safe_sql(sql_text: str) -> bool:
#     """Ensure SQL is read-only."""
#     forbidden = ["UPDATE", "DELETE", "DROP", "INSERT", "ALTER", "TRUNCATE"]
#     sql_upper = sql_text.strip().upper()
#     if sql_upper.startswith(("SELECT", "WITH")):
#         return not any(word in sql_upper for word in forbidden)
#     return False


# # CLI for testing
# if __name__ == "__main__":
#     print(" Root Router Agent started (read-only SQL mode). Type 'exit' to quit.")
#     while True:
#         query = input("\nYou: ").strip()
#         if query.lower() in ["exit", "quit"]:
#             break
#         result = handle_user_input(query)
#         print(f"\n Result:\n{result}")



