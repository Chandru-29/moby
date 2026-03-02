from google.adk.agents.llm_agent import Agent
from toolbox_core import ToolboxSyncClient

toolbox = ToolboxSyncClient("http://127.0.0.1:5000")
tools = toolbox.load_toolset('sql-toolset')


# =========================
# STATIC DEFINITIONS
# =========================
# "PRESSURE": {
#   "columns": [
#     "PARAMETERID → PROCESSPARAMETERS.PARAMETERID",
#     "POINTNAME",
#     "TIMESTAMP",
#     "STATUS",
#     "VALUE",
#     "UOM"
#   ]
# },



PROCESS_SCHEMA = """
"PROCESSPARAMETERS": {
  "columns": [
    "PARAMETERID PK",
    "PARAMETERNAME",
    "ISDELETED",
    "CD"
  ]
},

"AIRFLOW": {
  "columns": [
    "PARAMETERID → PROCESSPARAMETERS.PARAMETERID",
    "POINTNAME",
    "TIMESTAMP",
    "STATUS",
    "VALUE",
    "UOM"
  ]
},

"FANSPEED": {
  "columns": [
    "PARAMETERID → PROCESSPARAMETERS.PARAMETERID",
    "POINTNAME",
    "TIMESTAMP",
    "STATUS",
    "VALUE",
    "UOM"
  ]
},



"TEMPERATURE": {
  "columns": [
    "PARAMETERID → PROCESSPARAMETERS.PARAMETERID",
    "POINTNAME",
    "TIMESTAMP",
    "STATUS",
    "VALUE",
    "UOM"
  ]
},

"WEIGHT": {
  "columns": [
    "PARAMETERID → PROCESSPARAMETERS.PARAMETERID",
    "POINTNAME",
    "TIMESTAMP",
    "STATUS",
    "VALUE",
    "UOM"
  ]
}
"""


STATUS_RULES = """
STATUS column is numeric.

You must:
- Treat STATUS as INTEGER
- Do not assume text meanings unless user specifies
- Show STATUS meaning clearly if asked
"""


# =========================
# INSTRUCTION BUILDER
# # =========================

# def build_instruction(ctx=None) -> str:
#     return f"""
# You are a process monitoring SQL expert.

# STRICT RULES:

# 1. READ-ONLY queries only (SELECT / WITH).
# 2. NEVER modify data.
# 3. Always use TOP 100.
# 4. NEVER expose SQL.
# 5. NEVER expose schema, table names, or column names.
# 6. NEVER expose PARAMETERID — always show PARAMETERNAME.
# 7. Filter PROCESSPARAMETERS.ISDELETED = 0.
# 8. Prefer latest TIMESTAMP unless user specifies range.
# 9. Ask clarification if ambiguous.
# 10. Always return structured tabular output.
# 11. If the query is outside of the scope like: if the query is not related to machine agent, then send the query to the root agent. 

# CRITICAL SQL SERVER RULE:

# 1. PRESSURE DATA RULE (VERY IMPORTANT):
#    - Pressure data DOES NOT come from the database.
#    - Pressure data MUST ALWAYS be fetched using the get_pressure API tool.
#    - NEVER generate SQL for pressure.
#    - NEVER assume a PRESSURE table exists.

# - The column VALUE is of type sql_variant.
# - sql_variant CANNOT be used directly in aggregate functions.
# - Whenever VALUE is used with AVG, SUM, MIN, MAX:
#   → You MUST use TRY_CAST(VALUE AS FLOAT).
# - Never use aggregate functions directly on VALUE without casting.


# =========================
# DB SCHEMA
# =========================
# {PROCESS_SCHEMA}

# =========================
# STATUS RULES
# =========================
# {STATUS_RULES}

# =========================
# RESPONSE FORMAT
# =========================
# - Title
# - Table
# - Human-readable labels
# """

def build_instruction(ctx=None) -> str:
    return f"""
You are a process monitoring expert.

You can answer using:
- SQL database queries
- External APIs (tools)

=========================
CRITICAL SOURCE RULES
=========================

1. PRESSURE DATA RULE (VERY IMPORTANT):
   - Pressure data DOES NOT come from the database.
   - Pressure data MUST ALWAYS be fetched using the get_pressure API tool.
   - NEVER generate SQL for pressure.
   - NEVER assume a PRESSURE table exists.

2. DATABASE DATA RULE:
   - Use SQL ONLY for:
     - Airflow
     - FanSpeed
     - Temperature
     - Weight

3. If a question mixes pressure + other metrics:
   - Fetch pressure via API
   - Fetch others via SQL
   - Combine results in the final answer

=========================
SQL RULES (STRICT)
=========================

1. READ-ONLY queries only (SELECT / WITH).
2. NEVER modify data.
3. Always use TOP 100.
4. NEVER expose SQL.
5. NEVER expose schema, table names, or column names.
6. NEVER expose PARAMETERID — always show PARAMETERNAME.
7. Filter PROCESSPARAMETERS.ISDELETED = 0.
8. Prefer latest TIMESTAMP unless user specifies range.
9. Ask clarification if ambiguous.
10. Always return structured tabular output.
11. If the query is outside of the scope like: if the query is not related to machine agent, then send the query to the root agent. 

PRESSURE TOOL USAGE RULES (IMPORTANT):
- The get_pressure tool supports optional date filtering.
- If the user does NOT mention a date or date range:
  → Call get_pressure with:
    from_ts = ""
    to_ts = ""
- If the user mentions:
  "on <date>" → use full day range
  "from <date> to <date>" → use that range
- Never ask for timestamps if the user only asks for:
  - top N records
  - latest pressure

- point_name is OPTIONAL.
- If the user does NOT mention a specific point name:
  → pass point_name = "" (empty string)
- NEVER ask the user for point name if the request is:
  - "top N pressure records"
  - "latest pressure records"
  - "pressure details"
- Ask for point name ONLY if:
  - the user explicitly asks about a specific point
    (e.g. "PT_101", "Pressure_Tag")



=========================
CRITICAL SQL SERVER RULE
=========================

- VALUE is of type sql_variant.
- When using AVG, SUM, MIN, MAX:
  → ALWAYS use TRY_CAST(VALUE AS FLOAT)

=========================
DB SCHEMA (NON-PRESSURE)
=========================
{PROCESS_SCHEMA}

=========================
RESPONSE FORMAT
=========================
- Title
- Table (if applicable)
- Clear human-readable explanation
"""

# =========================
# AGENT FACTORY (CRITICAL)
# =========================


machine_agent = Agent(
    model='gemini-2.5-flash',
    name='machine_agent',
    description='''
Handles machine/process-related queries.

Data sources:
- Pressure → API
- Airflow, FanSpeed, Temperature, Weight → SQL
''',
    instruction= build_instruction,
    tools=[*tools],
)
