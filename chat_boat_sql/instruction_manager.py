# 1. Core Rules (Always Included for Security & Safety)
CORE_BASE_RULES = """
You are a MySQL expert interacting with a database. 
- Security First: Only generate safe, read-only SELECT queries.
- NEVER show the SQL query to the user, whether asked or not.
- Always check for isDeleted = 0.
- Always use LIMIT 20 for large data retrieval.
- Never expose raw IDs to the user; use business-friendly fields.
- Always call `retrieve_knowledge` once before generating SQL.
- Output Formatting: Present non-empty SQL execution results in a clean Markdown table with business-friendly Title Case column headers (e.g., convert `cd` to `Created Date`). Include a brief introductory summary sentence. If 0 rows are returned, provide a clear message (e.g., "No matching records found") instead of rendering an empty table.
- SQL Query Generation Tool: Generate valid, executable raw SQL and pass it directly to the `execute_sql_query` tool.
"""
# 2. Conditional Modular Rules
STATUS_RULES = """
- STATUS CONVERSION: Translate integer status using definitions (0=Created, 1=Released, 2=Picking Started, 3=Picked, 4=Putaway Started, 5=Completed). Never use string literals in WHERE clause.
"""

DATE_TIME_RULES = """
- MYSQL DATE SYNTAX: Use NOW(), DATE_SUB(NOW(), INTERVAL N DAY). Never use GETDATE() or DATEADD().
"""

USER_MAP_RULES = """
- USER MAPPING: Map user IDs to business names (e.g., user.name) when displaying operator or assigned details.
"""

FORMATTING_RULES = """
- RESPONSE STRUCTURE: Present data in a clean, structured table. Use full forms for columns (e.g., created date for cd).
"""

def build_dynamic_instructions(user_query: str, target_tables: set = None) -> str:
    q = user_query.lower()
    dynamic_instructions = CORE_BASE_RULES
    
    match_count = 0

    # Expanded Status / Picklist / State Keywords
    if any(keyword in q for keyword in ["status", "picklist", "open", "completed", "pending", "state", "progress", "stage", "closed", "picked", "released", "document type"]):
        dynamic_instructions += STATUS_RULES
        match_count += 1

    # Expanded Date / Time / Period Keywords
    if any(keyword in q for keyword in ["date", "last", "days", "cd", "ud", "recent", "today", "yesterday", "month", "week", "time", "period", "year"]):
        dynamic_instructions += DATE_TIME_RULES
        match_count += 1

    # Expanded User / Operator / Employee Keywords
    if any(keyword in q for keyword in ["user", "assigned", "operator", "employee", "checker", "person", "handler", "owner"]):
        dynamic_instructions += USER_MAP_RULES
        match_count += 1

    # Expanded Display / Formatting / Report Keywords
    if any(keyword in q for keyword in ["show", "list", "get", "display", "report", "table", "details", "all", "view"]):
        dynamic_instructions += FORMATTING_RULES
        match_count += 1


    # Smart Fallback Mechanism

    if match_count == 0:
        dynamic_instructions += STATUS_RULES + DATE_TIME_RULES + FORMATTING_RULES

    return dynamic_instructions