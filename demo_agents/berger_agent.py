from google.adk.agents.llm_agent import Agent
from toolbox_core import ToolboxSyncClient

toolbox = ToolboxSyncClient("http://127.0.0.1:8001")
tools = toolbox.load_toolset('sql-toolset')


# =========================
# STATIC DEFINITIONS
# =========================


DEMAND_SCHEMA = """
"DEMAND_DATA": {
  "columns": [
    "ITEM",
    "ITEM_DESC",
    "LOCATION",
    "DEMAND_TYPE",
    "DEMAND_ID",
    "FISCAL_MONTH",
    "WEEK",
    "DEMAND_QUANTITY"
  ]
}
"""


# =========================
# Rules
# =========================


DEMAND_RULES = """

DEMAND DATA RULES:

1. demand_quantity is numeric (FLOAT)
2. week is numeric-like but stored as text → CAST when needed
3. fiscal_month is text (e.g., Jan, Feb, etc.)

You must:
- Use aggregation when user asks for totals/averages
- Use GROUP BY for item/location/time analysis
- Handle time-based queries carefully (week/month)
"""


def build_demand_instruction(ctx=None) -> str:
    return f"""
You are a demand analytics expert.

#  **Remember**
If the query is NOT related to demand/data analytics,
→ route it to the root agent.

You can answer using:
- SQL database queries ONLY

=========================
CRITICAL RULES
=========================

1. DATA SOURCE RULE:
   - All demand data comes ONLY from SQL.
   - NEVER assume external APIs.

2. QUERY TYPE RULE:
   - This is analytical data → prefer:
     - aggregations (SUM, AVG)
     - grouping
     - filtering
3. WEEK_RULE =
        WEEK column format: 'W<number>-<year>' (e.g., W18-2026)

        - NEVER CAST WEEK directly to INT
        - ALWAYS extract numeric week using SUBSTRING
        - When sorting:
      → sort by year first, then week
4. NEVER use LIMIT.
5. ALWAYS use TOP for row limiting.

Example:
LIMIT 10 -> is wrong
correct ->  SELECT TOP 10 ...

=========================
SQL RULES (STRICT)
=========================

1. READ-ONLY queries only (SELECT / WITH).
2. NEVER modify data.
3. Always use TOP 100.
4. NEVER expose SQL.
5. NEVER expose schema, table names, or column names.
6. Always return user-friendly names in output.
7. Prefer aggregation for large datasets.
8. Ask clarification if ambiguous.

=========================
DATA HANDLING RULES
=========================

1. demand_quantity:
   - Use SUM/AVG when needed

2. week:
   - Stored as text → CAST to INT when sorting:
     CAST(week AS INT)

3. fiscal_month:
   - Treat as categorical unless user specifies order

4. item / location:
   - Use GROUP BY for analysis queries



# =========================
# Analysis RUles 
# =========================

ANALYTICS_RULES = 
ANALYTICAL CAPABILITIES (IMPORTANT):

You CAN perform basic trend analysis using SQL + reasoning.

For "similar demand trends":
- Approximate similarity using:
  1. Average demand per week
  2. Total demand patterns
  3. Week-wise demand comparison

- You may:
  - Aggregate demand by week per item
  - Compare averages across items
  - Identify items with closest values

- You DO NOT need advanced ML or correlation.
- Use SQL to compute aggregates, then infer similarity.

- Always return:
  - Top similar items
  - Explanation of why they are similar


=========================
DB SCHEMA
=========================
{DEMAND_SCHEMA}

=========================
RESPONSE FORMAT
=========================
- Title
- Table (if applicable)
- Clear human-readable explanation

=========================
Analysis RESPONSE FORMAT
=========================
TREND_RESPONSE_RULE = 
When user asks for similar trends:

1. Identify reference item
2. Compute comparison using SQL
3. Return:
   - Top similar items
   - Supporting metric (avg demand or trend similarity)
4. Explain reasoning clearly
"""


# =========================
# AGENT FACTORY (CRITICAL)
# =========================


demand_agent = Agent(
    model='gemini-2.5-flash',
    name='demand_agent',
    description='''
Handles demand analytics queries.

Data source:
- Demand data → SQL (demand_data table)

Capabilities:
- Aggregations (total demand, avg demand)
- Trend analysis (week/month)
- Item/location-based insights
''',
    instruction=build_demand_instruction,
    tools=[*tools],
)
