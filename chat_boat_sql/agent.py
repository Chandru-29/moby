from google.adk.agents.llm_agent import Agent
from google.adk.tools.agent_tool import AgentTool
from toolbox_core import ToolboxSyncClient

from chat_boat_sql.analytics_agent import analytics_agent
from chat_boat_sql.warehouse_agent import warehouse_agent
from rag_service.rag_tool import retrieve_knowledge
from chat_boat_sql.warehouse_agent import warehouse_agent


root_agent = Agent(
    model="gemini-2.5-flash-lite",
    name="root_agent",
    description="Router agent that decides which specialized sub-agent should process the SQL query request.",
   instruction='''
            You are the primary conversational agent. Your role is to analyze the user's intent.
            1. **Greeting & Conversation**: If the user's input is a greeting (like "hi", "hello"), general chat, or a question about your capabilities, you **MUST NOT** use any tools. Simply respond conversationally.
       
            # If someone asks "Who are you", or any thing related reply-> "I am MOBY- Your personal agent" and if the query is "who developed you?" reply-> "I am Developed by Harsh" and if the query is "for whom you work?" reply -> "I work for MOBILLOR TECHNOLOGIES.".
            # Your ONLY responsibility is to analyze the user's intent and delegate the query to the correct sub-agent.

           2. **Delegation**: -  
                                                               
                                   WAREHOUSE / ERP DATA
If the query mentions ANY of:
        - GRN
        - picklist
        - inventory
        - stock
        - warehouse
        - location
        - item
        - quantity
        - batch
        - lot

YOU MUST:
- Call `warehouse_agent`
- Pass the FULL ORIGINAL USER QUERY
- RETURN ONLY the tool call
- STOP

            3. **Security**: You are completely unaware of the database schema and cannot generate SQL yourself. Your sole function is delegation for data retrieval or conversational responses.
            4. **SQL Information**: whenever you use distinct word in the query, always use it after select word only.
            5. **Never** Show the sql query whethere it is asked or not.
            6.  
                   
           

        ''',

 
    #  sub_agents=[ pharma_agent],
     sub_agents=[ warehouse_agent],
    #  sub_agents=[ wh_agent],

    #  sub_agents =[analytics_agent],
    #  tools=[   
    #     *tools  
    # ],
        
      
)






def handle_query(user_query):

    routed = root_agent.generate(user_query)

    knowledge = retrieve_knowledge(user_query)

    if not knowledge:
        return "No schema found"

    knowledge_text = "\n\n".join(knowledge)


    prompt = f"""
You MUST ONLY use the following database knowledge:

{knowledge_text}

User Query:
{user_query}
"""

    response = warehouse_agent.generate(prompt)

    return response.text




