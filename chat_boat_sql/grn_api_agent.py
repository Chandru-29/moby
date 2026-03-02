from google.adk.agents.llm_agent import Agent
from chat_boat_sql.grn_api_tool import get_grns


grn_api_agent = Agent(
    model="gemini-2.5-flash",
    name="grn_api_agent",
    description="Handles GRN queries using GRN API.",
    instruction="""
You are a GRN expert.

RULES:
- GRN data comes ONLY from GRN API
- API is PAGINATED

SEARCH:
- By grnNumber
- By vendor
- By date

PAGINATION:
- First page only
- Ask before next page

RESPONSE:
- Table for multiple GRNs
- Summary for single GRN
""",
    tools=[get_grns],
)
