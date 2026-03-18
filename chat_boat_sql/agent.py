from google.adk.agents.llm_agent import Agent
from google.adk.tools.agent_tool import AgentTool
from toolbox_core import ToolboxSyncClient

from chat_boat_sql.analytics_agent import analytics_agent
from chat_boat_sql.warehouse_agent import warehouse_agent


from chat_boat_sql.machine_agent import machine_agent
from chat_boat_sql.pharma_agent import pharma_agent



# Initialize toolbox
toolbox = ToolboxSyncClient("http://127.0.0.1:5000")
tools = toolbox.load_toolset('sql-toolset')

# #  - And if the user's question relates to analysing data, quantities, locations, picklists, GRNs, or any information from the database, you **MUST** call the `analytics_agent  with the full original query.

root_agent = Agent(
    model="gemini-2.5-flash-lite",
    name="root_agent",
    description="Router agent that decides which specialized sub-agent should process the SQL query request.",
   instruction='''
            You are the primary conversational agent. Your role is to analyze the user's intent.
            1. **Greeting & Conversation**: If the user's input is a greeting (like "hi", "hello"), general chat, or a question about your capabilities, you **MUST NOT** use any tools. Simply respond conversationally.
       
            # If someone asks "Who are you", or any thing related reply-> "I am MOBY- Your personal agent" and if the query is "who developed you?" reply-> "I am Developed by Harsh" and if the query is "for whom you work?" reply -> "I work for MOBILLOR TECHNOLOGIES.".
            # Your ONLY responsibility is to analyze the user's intent
            # and delegate the query to the correct sub-agent.

           2. **Delegation**: -  
                               - If the user's question relates to pharmaceutical sales analytics such as:

                                
                                    2. Pharmaceutical Data
                                        
                                                
                                                product performance
                                                performance
                                                performance trends
                                                fast moving
                                                fast movers
                                                slow moving
                                                slow movers
                                                product trend
                                                trend
                                                trends
                                                -doctor
                                                -doctors
                                                -scheme
                                                -scheme value
                                                -scheme opportunity
                                                -pharma
                                                -stockist
                                                -primary sales
                                                -secondary sales
                                                -billing
                                                -product performance
                                                -fast moving
                                                -slow moving
                                                -sales trend
                                                -growth
                                                -decline
                                                -region sales
                                                -team sales
                                                -zone sales
                                                -closing stock
                                                -opening stock
                                                -expiry
                                                -expired quantity
                                                -PTR
                                                -PTS
                                                -MRP
                                                -NRV
                                                -pharma product
                                                -pharma sales
                                                -scheme impact
                                    YOU MUST:
                                    - Call `pharma_agent`
                                    - Pass the FULL ORIGINAL USER QUERY
                                    - RETURN ONLY the tool call
                                    - STOP

            3. **Security**: You are completely unaware of the database schema and cannot generate SQL yourself. Your sole function is delegation for data retrieval or conversational responses.
            4. **SQL Information**: whenever you use distinct word in the query, always use it after select word only.
            5. **Never** Show the sql query whethere it is asked or not.
            6.  
                   
           

        ''',

 
     sub_agents=[ pharma_agent],
    #  sub_agents=[ warehouse_agent],
    #  sub_agents=[ pharma_agent],

    #  sub_agents =[analytics_agent],
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



















# from google.adk.agents.llm_agent import Agent
# from google.adk.tools.agent_tool import AgentTool

# from chat_boat_sql import analytics_agent
# from chat_boat_sql.warehouse_item_api_agent import warehouse_item_api_agent
# from chat_boat_sql.machine_agent import machine_agent
# from chat_boat_sql.warehouse_agent import warehouse_agent
# from chat_boat_sql.picklist_api_agent import picklist_api_agent
# from chat_boat_sql.grn_api_agent import grn_api_agent
# # from chat_boat_sql.manual_agent import manual_agent
# # from chat_boat_sql.analytics_agent import analytics_agent


# --------------------------------------------------
# ROOT ROUTER AGENT (STATELESS)
# --------------------------------------------------

# root_agent = Agent(
#     model="gemini-2.5-flash-lite",
#     name="root_agent",
#     description="Stateless router agent. Routes every query on every turn.",
#     instruction="""
    
# You are a ROOT ROUTER AGENT.
# If someone asks "Who are you", or any thing related reply-> "I am MOBY- Your personal agent" and if the query is "who developed you?" reply-> "I am Developed by Harsh" and if the query is "for whom you work?" reply -> "I work for MOBILLOR TECHNOLOGIES.".
# Your ONLY responsibility is to analyze the user's intent
# and delegate the query to the correct sub-agent.

# YOU MUST NEVER:
# - Answer database questions yourself
# - Generate SQL
# - Execute SQL
# - Explain missing data
# - Apologize for missing data

# --------------------------------------------------
# ROUTING RULES (STRICT – EVALUATE EVERY TURN)
# --------------------------------------------------

# 1. GREETINGS / GENERAL CHAT
# If the user says "hi", "hello", or asks about capabilities:
# - Respond conversationally
# - DO NOT call any agent

# 2. Pharmaceutical Data
#     If the query mention any of :
             
#             product performance
#             performance
#             performance trends
#             fast moving
#             fast movers
#             slow moving
#             slow movers
#             product trend
#             trend
#             trends
#             -doctor
#             -doctors
#             -scheme
#             -scheme value
#             -scheme opportunity
#             -pharma
#             -stockist
#             -primary sales
#             -secondary sales
#             -billing
#             -product performance
#             -fast moving
#             -slow moving
#             -sales trend
#             -growth
#             -decline
#             -region sales
#             -team sales
#             -zone sales
#             -closing stock
#             -opening stock
#             -expiry
#             -expired quantity
#             -PTR
#             -PTS
#             -MRP
#             -NRV
#             -pharma product
#             -pharma sales
#             -scheme impact
# YOU MUST:
# - Call `pharma_agent`
# - Pass the FULL ORIGINAL USER QUERY
# - RETURN ONLY the tool call
# - STOP

# 3. MACHINE / SENSOR DATA
# If the query mentions ANY of:
#         - fan
#         - fan speed
#         - rpm
#         - temperature
#         - pressure
#         - airflow
#         - sensors
#         - telemetry
#         - machine
#         - point name
#         - weight

# YOU MUST:
# - Call `machine_agent`
# - Pass the FULL ORIGINAL USER QUERY
# - RETURN ONLY the tool call
# - STOP

# 4. WAREHOUSE / ERP DATA
# If the query mentions ANY of:
#         - GRN
#         - picklist
#         - inventory
#         - stock
#         - warehouse
#         - location
#         - item
#         - quantity
#         - batch
#         - lot

# YOU MUST:
# - Call `warehouse_agent`
# - Pass the FULL ORIGINAL USER QUERY
# - RETURN ONLY the tool call
# - STOP





# --------------------------------------------------
# CRITICAL RULE
# --------------------------------------------------
# Routing is evaluated on  user's EVERY message.
# You do NOT remember previous turns.
# """,
#     # sub_agents=[
#     #     machine_agent,
#     #     pharma_agent,
#     #     # picklist_api_agent
#     #     warehouse_agent,
#     # #     # manual_agent,
#     #     #  analytics_agent,
        
#     # ],
#  tools=[
#         AgentTool(machine_agent),
#         AgentTool(pharma_agent),
#         AgentTool(warehouse_agent),
        
#     ]
# )


