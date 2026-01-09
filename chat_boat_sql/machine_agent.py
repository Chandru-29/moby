from google.adk.agents.llm_agent import Agent
from toolbox_core import ToolboxSyncClient

toolbox = ToolboxSyncClient("http://127.0.0.1:5000")
tools = toolbox.load_toolset('sql-toolset')


# =========================
# STATIC DEFINITIONS
# =========================

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

"PRESSURE": {
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

def build_instruction(ctx=None) -> str:
    return f"""
You are a process monitoring SQL expert.

STRICT RULES:

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

CRITICAL SQL SERVER RULE:

- The column VALUE is of type sql_variant.
- sql_variant CANNOT be used directly in aggregate functions.
- Whenever VALUE is used with AVG, SUM, MIN, MAX:
  → You MUST use TRY_CAST(VALUE AS FLOAT).
- Never use aggregate functions directly on VALUE without casting.


=========================
DB SCHEMA
=========================
{PROCESS_SCHEMA}

=========================
STATUS RULES
=========================
{STATUS_RULES}

=========================
RESPONSE FORMAT
=========================
- Title
- Table
- Human-readable labels
"""



# =========================
# AGENT FACTORY (CRITICAL)
# =========================


machine_agent = Agent(
    model='gemini-2.5-flash',
    name='machine_agent',
    description='A specialized SQL query generator for a WMS database (read-only).',
    instruction= build_instruction,
    tools=tools,
)
