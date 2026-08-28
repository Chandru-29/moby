from google.adk.agents.llm_agent import Agent
from google.adk.tools.agent_tool import AgentTool
# from toolbox_core import ToolboxSyncClient

# from chat_boat_sql.warehouse_agent import warehouse_agent
from rag_service.rag_tool import retrieve_knowledge
# from chat_boat_sql.warehouse_agent import warehouse_agent
from chat_boat_sql.warehouse_agent import get_warehouse_agent



warehouse_agent_instance = get_warehouse_agent("default warehouse query")





root_agent = Agent(
    model="gemini-3.5-flash-lite",
    name="root_agent",
    description="Router agent that decides which specialized sub-agent should process the SQL query request.",
    instruction="""
    You are the primary conversational assistant (MOBY - Your personal agent, developed by MOBILLOR TECHNOLOGIES).
    
    Follow these strict rules:
    1. **General Chat & Greetings**: If the user says hi, hello, asks for your name, or talks casually, reply conversationally yourself. Do NOT use any tools.
    2. **Warehouse / ERP Data Queries**: If the query is related to inventory, stock, picklist, GRN, warehouse, items, locations, or database records, you MUST delegate it to the `warehouse_agent`. Pass the full user query to it.
    """,

    sub_agents=[warehouse_agent_instance]
        #  sub_agents=[ pharma_agent],
        #  sub_agents=[ warehouse_agent],
        #  sub_agents=[ wh_agent],

        #  sub_agents =[analytics_agent],
        #  tools=[   
        #     *tools  
        # ],    
)
def handle_query(user_query: str):
    """
    Called during runtime. It dynamically updates the warehouse agent instance 
    based on the exact user query to ensure token optimization and dynamic rules.
    """
    #Step 1: Create fresh dynamic warehouse agent based on current user query 
    dynamic_wh_agent = get_warehouse_agent(user_query)
    
    # Step 2: Update the sub_agents list at runtime 
    root_agent.sub_agents = [dynamic_wh_agent]
    
    # Step 3: Generate response through the root agent
    response = root_agent.generate(user_query)
    return response.text





# def handle_query(user_query):

#     routed = root_agent.generate(user_query)

#     knowledge = retrieve_knowledge(user_query)

#     if not knowledge:
#         return "No schema found"

#     knowledge_text = "\n\n".join(knowledge)


#     prompt = f"""
# You MUST ONLY use the following database knowledge:

# {knowledge_text}

# User Query:
# {user_query}
# """

#     response = warehouse_agent.generate(prompt)

#     return response.text




