from google.adk.agents.llm_agent import Agent
from chat_boat_sql.picklist_api_tool import get_picklists


picklist_api_agent = Agent(
    model="gemini-2.5-flash",
    name="picklist_api_agent",
    description="Handles picklist queries using Picklist API.",
    instruction="""
You are a Picklist expert.

RULES:
- Picklist data comes ONLY from Picklist API
- API is PAGINATED
- Never fetch all pages automatically

SEARCH:
- By picklistCode
- By status
- By documentType

PAGINATION:
- Show first page
- Ask before next page

RESPONSE:
- Use tables for lists
- Explain status meaning clearly
""",
    tools=[get_picklists],
)
