# from google.adk.agents.llm_agent import Agent
# from toolbox_core import ToolboxSyncClient


# toolbox = ToolboxSyncClient("http://127.0.0.1:5000")
# tools = toolbox.load_toolset('sql-toolset')

# STATUS_DEFINITIONS = """
# #  PICKLIST & PICKLISTITEM status:
# # 0 = Created
# # 1 = Released
# # 2 = Picking Started
# # 3 = All Picked
# # 4 = Putaway Started
# # 5 = Putaway Completed

# # ✔ "Open Picklist" → status IN (1,2,3,4)
# # ✔ "Pending Picklist" → status IN (0,1)
# # ✔ "Picking in progress" → status = 2
# # ✔ "Picked" → status = 3
# # ✔ "Putaway pending" → status IN (3,4)
# # ✔ "Closed Picklist" → status = 5

# # PICKLISTVIEW
# # 2 = Created
# # 3 = Picked
# # 5 = Putaway Done

# # ✔ "Open picklist view" → status IN (2,3)
# # ✔ "Completed picklist view" → status = 5

# #  SULOCATION (movement)
# # 0 = Inactive
# # 1 = Active
# # 2 = First Level Quarantine
# # 3 = Second Level Quarantine / Scrapped
# # 4 = First Level Rejection
# # 5 = Second Level Rejection / Scrapped / RTV
# # 6 = Unplanned Issue / Material Request

# # DOCUMENT TYPE INFORMATION
# # 1  ->	GRN  ->	Goods Received Note
# # 16 -> TO ->	Transfer Order
# # 18 ->	SF -> Shop Floor
# # 19 ->	KT -> Kitting
# # 20 ->	PO -> Production Order
# # 21 ->	WO -> Work Order
# # 22 ->	SO -> Sales Order
# # 23 ->	REJ->	Rejection
# # 24 ->	QR -> Quarantine
# # 25 ->	SFG->	Semi Finished Goods
# # 26 ->	UI -> Unplanned Issue
# # 27 ->	FG -> Finished Goods
# # 32 -> MR -> Material Reservation
# # 37 -> AFSSO->	After Sales Sales Order
# """

# DB_SCHEMA = """
# "ITEM": {
#   "columns": [
#     "itemId PK", "itemCode UNIQUE", "itemTypeId", "itemDescription", "itemGroup", "uom",
#     "issueType", "status", "procurementType", "shelfLife", "isDeleted", "cd datetime",
#     "ud datetime", "cdBy", "udBy", "movementType", "controlType", "weight",
#     "kittingType", "qaRequired", "userId"
#   ]
# },
# "SKUITEM": {
#   "columns": [
#     "skuId PK", "sku", "grnNumber", "grnLineNumber", "asnCode", "vendorCode", 
#     "vendorName", "itemId → ITEM.itemId", "qty", "mfgDate", "lotNumber", 
#     "serialNumber", "uom", "isDeleted", "cd", "ud datetime", "cdBy", "udBy"
#   ]
# },
# "LOCATION": {
#   "columns": [
#     "locationId PK", "locationCode UNIQUE", "locationName", "parentId", "parentCode",
#     "isLocation", "rltId", "status", "isEmpty", "isDeleted", "cd datetime", 
#     "ud datetime", "cdBy", "udBy"
#   ]
# },
# "SULOCATION": {
#   "columns": [
#     "suidId PK", "suid", "skuId → SKUITEM.skuId", "qty", "locationId → LOCATION.locationId", 
#     "palletId", "binId", "isDeleted", "cd datetime", "ud datetime", "cdBy", "udBy", 
#     "inTransit", "picklistId", "isAllocated", "status", "rejectionReason", 
#     "documentId", "onHold", "tempAssetId", "grnLineNumber", "serialNumber", 
#     "isGrouped", "kittingType"
#   ]
# },
# "FGMODEL": {
#   "columns": [
#     "fgModelId PK", "fgModelCode", "fgModelName", "itemId → ITEM.itemId", 
#     "isDeleted", "cd datetime", "ud datetime", "cdBy", "udBy"
#   ]
# },
# "ITEMLOCACNMAP": {
#   "columns": [
#     "itemLocAcnMapId PK", "categoryId", "itemId → ITEM.itemId", "warehouseId", 
#     "locationId → LOCATION.locationId", "acnId", "zoneId", "sectionId", 
#     "rackId", "isDeleted", "cd datetime", "ud datetime", "cdBy", "udBy"
#   ]
# },
# "FGTRANSACTION": {
#   "columns": [
#     "fgTransactionId PK", "fgCode", "vin", "sNo", "putawayTime", 
#     "suidId → SULOCATION.suidId", "isSFG", "isPutaway", "isDelivered", 
#     "locationId → LOCATION.locationId", "isVinHold", "isAccepted", 
#     "isAccessed", "isDeleted", "cd datetime", "ud datetime", "cdBy", 
#     "udBy", "isEol"
#   ]
# },
# "SUIDACTIVITYLOG": {
#   "columns": [
#     "suidActivityLogId PK", "suidId → SULOCATION.suidId", "picklistId", 
#     "status", "remark", "isDeleted", "cd datetime", "ud datetime", "cdBy", "udBy"
#   ]
# },
# "PICKLIST": {
#   "columns": [
#     "picklistId PK", "picklistCode", "documentTypeId", "documentNumber", 
#     "mvtId", "status", "assignedUser", "isDeleted", "cd datetime", 
#     "ud datetime", "cdBy", "udBy"
#   ]
# },
# "PICKLISTITEM": {
#   "columns": [
#     "picklistItemId PK", "picklistId → PICKLIST.picklistId", "itemId → ITEM.itemId", 
#     "qty", "source", "destination", "pickedQty", "status", "isDeleted", 
#     "cd datetime", "ud datetime", "picklistViewExists"
#   ]
# },
# "PICKLISTVIEW": {
#   "columns": [
#     "picklistViewId PK", "picklistId → PICKLIST.picklistId", "itemId → ITEM.itemId", 
#     "suidId → SULOCATION.suidId", "suid", "sourceLocId → LOCATION.locationId", 
#     "sourcePalletId", "sourceBinId", "status", "isDeleted", "cd datetime", "ud datetime"
#   ]
# },
# "GRN": {
#   "columns": [
#     "grnId PK", "grnNumber", "grnLineNumber", "asnCode", "vendorCode", 
#     "vendorName", "itemCode", "qty", "mfgDate", "grnDate", "batchNumber", 
#     "serialNumber", "lotNumber", "isPrinted", "isDeleted", "cd datetime", 
#     "ud datetime", "cdBy", "udBy", "movement", "plant", "documentHeaderText", 
#     "qaStatus", "storageLocation", "expiryDate", "oldGrnNumber", "uom", "isCancelled"
#   ],
#   "unique": [
#     ["grnNumber", "grnLineNumber"],
#     ["grnNumber", "grnLineNumber", "itemCode", "batchNumber"]
#   ]
# }
# """
# Table_mapping ='''============================
# #     KEY RELATIONSHIPS
# #     ============================
# #     -- FGMODEL.itemId → ITEM.itemId
# #     -- FGTRANSACTION.suidId → SULOCATION.suidId
# #     -- SUIDACTIVITYLOG.suidId → SULOCATION.suidId
# #     -- SUIDACTIVITYLOG.picklistId → PICKLIST.picklistId
# #     -- PICKLISTITEM.itemId → ITEM.itemId
# #     -- PICKLISTITEM.picklistId → PICKLIST.picklistId
# #     -- PICKLISTVIEW.picklistId → PICKLIST.picklistId
# #     -- PICKLISTVIEW.itemId → ITEM.itemId
# #     -- PICKLISTVIEW.suidId → SULOCATION.suidId
       
# #     ========================================================'''





# analytics_agent = Agent(
#         model="gemini-2.5-flash",
#         name="StockAnalyticsAgent",
#         description='An intelligent warehouse analytics agent responsible for performing the analysis for the user. ',
#         instruction=f""" You are the Stock Analytics Agent.
#                 Your job is to analyze warehouse stock data and generate insights using SQL queries.
#                 Use ONLY the schema and mappings provided below. Do NOT invent new columns or tables.
#                 **Query Limit**: Put a hard limit of 25 rows in the SQL query using "TOP 25" to avoid large data retrieval.
#                 ===========================
#                 SUPPORTED ANALYSIS
#                 ===========================
#                 1. Stock per item / per group / per location
#                 2. Stock ageing
#                 3. Slow-moving items
#                 4. Fast-moving items
#                 5. Dead stock
#                 6. Stock availability (free stock = qty - allocated - onHold - rejected)
#                 ===========================
#                 RULES
#                 ===========================
#                 - Always determine the required analysis first.
#                 - Use ONLY SELECT queries.
#                 - Table joins MUST follow the provided mapping.
#                 - NEVER hallucinate table names or columns.
#                 - Movement timestamp = MAX(SULOCATION.ud, SUIDACTIVITYLOG.ud, FGTRANSACTION.cd)
#                 - Ageing uses GRN.grnDate or SKUITEM.mfgDate
#                 - Dead stock = LAST movement older than X days

#                 ==============================================
#                 SQL important Rules
#                 ===============================================
#                 - Do NOT use STRING_AGG (it doesn't exist in MySQL). Use GROUP_CONCAT instead.
#                 - Avoid DISTINCT inside CASE expressions — rewrite without THEN DISTINCT.
#                 - Ensure every non-aggregated column in SELECT is included in GROUP BY.
#                 - Avoid ambiguous column references — fully qualify columns when joins are present.
#                 - Prevent duplicated aggregates from joins — use subqueries or DISTINCT inside COUNT(), GROUP_CONCAT(), etc., when needed.
#                 - Make date comparisons safe — use STR_TO_DATE() or CAST() if columns may be stored as strings.

#                 ===========================
#                 EXTENDED ANALYTICS TABLE USAGE RULES
#                 ===========================
#                 You may use additional tables ONLY for the following analysis types:

#                 1. ITEMLOCACNMAP
#                 - Use for zone/section/rack-based analytics.
#                 - Allowed for: stock by zone, stock ageing by zone, dead stock by section, warehouse heatmap.

#                 2. PICKLIST and PICKLISTITEM
#                 - Use for operational analytics such as:
#                     pick accuracy, pick efficiency, open picklist load, line fill rate.
#                 - Do NOT use these tables for stock ageing or dead stock.

#                 3. PICKLISTVIEW
#                 - Use for pick-path efficiency and SLA monitoring.
#                 - Never use it for stock or ageing calculations.

#                 4. SUIDACTIVITYLOG
#                 - Use for movement-based analytics such as:
#                     last movement, dead stock detection, movement frequency.
#                 - Allowed when calculating:
#                     movement_age = DATEDIFF(day, MAX(ud), GETDATE()).

#                 5. FGTRANSACTION
#                 - Use for finished goods analytics:
#                     FG stock distribution, putaway ageing, FG deliveries.

#                 You MUST NOT use any of these tables unless the user’s question clearly requires them.
#                 Keep SQL simple and select only the columns required for that analysis type.


#     ===========================
#     WAREHOUSE DB SCHEMA (READ ONLY)
#     ===========================
#     DB schema:
#         {DB_SCHEMA}

#         ========================================================
#         STATUS DEFINITIONS (USE THESE NUMERICAL MAPPINGS ALWAYS)
#         ========================================================
#         {STATUS_DEFINITIONS}
#         =====================================
#         table mapping
#         ====================================
#         {Table_mapping}

#     ===========================================
#         RESPONSE STRUCTURE...
#     ===========================================
#   For all analytical questions, you MUST use a stable, consistent response structure:

# 1. Short summary (2–3 lines max)
# 2. A table with fixed columns for that analysis type
# 3. Final notes (only if necessary)

# Do NOT produce long narratives. Keep explanations minimal and consistent.



#     """,
#         tools=tools,
#     )











# prediction, planning and analyssis agent 


from google.adk.agents.llm_agent import Agent
from toolbox_core import ToolboxSyncClient


# --------------------------------------------------
# TOOLING
# --------------------------------------------------
toolbox = ToolboxSyncClient("http://127.0.0.1:8001")
tools = toolbox.load_toolset("sql-toolset")


# --------------------------------------------------
# STATUS DEFINITIONS (AUTHORITATIVE)
# --------------------------------------------------
STATUS_DEFINITIONS = """
#  PICKLIST & PICKLISTITEM status:
# 0 = Created
# 1 = Released
# 2 = Picking Started
# 3 = All Picked
# 4 = Putaway Started
# 5 = Putaway Completed

# ✔ Open Picklist → status IN (1,2,3,4)
# ✔ Pending Picklist → status IN (0,1)
# ✔ Picking in progress → status = 2
# ✔ Picked → status = 3
# ✔ Putaway pending → status IN (3,4)
# ✔ Closed Picklist → status = 5

# PICKLISTVIEW
# 2 = Created
# 3 = Picked
# 5 = Putaway Done

#  SULOCATION (movement)
# 0 = Inactive
# 1 = Active
# 2 = First Level Quarantine
# 3 = Second Level Quarantine / Scrapped
# 4 = First Level Rejection
# 5 = Second Level Rejection / Scrapped / RTV
# 6 = Unplanned Issue / Material Request

# DOCUMENT TYPES
# 27 -> FG  (Finished Goods)
# 25 -> SFG (Semi Finished Goods)
# 20 -> PO
# 21 -> WO
# 22 -> SO
"""


# --------------------------------------------------
# DATABASE SCHEMA (READ ONLY)
# --------------------------------------------------
DB_SCHEMA = """
"ITEM": {
  "columns": [
    "itemId PK", "itemCode UNIQUE", "itemTypeId", "itemDescription", "itemGroup", "uom",
    "issueType", "status", "procurementType", "shelfLife", "isDeleted", "cd datetime",
    "ud datetime", "cdBy", "udBy", "movementType", "controlType", "weight",
    "kittingType", "qaRequired", "userId"
  ]
},
"SKUITEM": {
  "columns": [
    "skuId PK", "sku", "grnNumber", "grnLineNumber", "asnCode", "vendorCode", 
    "vendorName", "itemId → ITEM.itemId", "qty", "mfgDate", "lotNumber", 
    "serialNumber", "uom", "isDeleted", "cd", "ud datetime", "cdBy", "udBy"
  ]
},
"LOCATION": {
  "columns": [
    "locationId PK", "locationCode UNIQUE", "locationName", "parentId", "parentCode",
    "isLocation", "rltId", "status", "isEmpty", "isDeleted", "cd datetime", 
    "ud datetime", "cdBy", "udBy"
  ]
},
"SULOCATION": {
  "columns": [
    "suidId PK", "suid", "skuId → SKUITEM.skuId", "qty", "locationId → LOCATION.locationId", 
    "palletId", "binId", "isDeleted", "cd datetime", "ud datetime", "cdBy", "udBy", 
    "inTransit", "picklistId", "isAllocated", "status", "rejectionReason", 
    "documentId", "onHold", "tempAssetId", "grnLineNumber", "serialNumber", 
    "isGrouped", "kittingType"
  ]
},
"FGMODEL": {
  "columns": [
    "fgModelId PK", "fgModelCode", "fgModelName", "itemId → ITEM.itemId", 
    "isDeleted", "cd datetime", "ud datetime", "cdBy", "udBy"
  ]
},
"ITEMLOCACNMAP": {
  "columns": [
    "itemLocAcnMapId PK", "categoryId", "itemId → ITEM.itemId", "warehouseId", 
    "locationId → LOCATION.locationId", "acnId", "zoneId", "sectionId", 
    "rackId", "isDeleted", "cd datetime", "ud datetime", "cdBy", "udBy"
  ]
},
"FGTRANSACTION": {
  "columns": [
    "fgTransactionId PK", "fgCode", "vin", "sNo", "putawayTime", 
    "suidId → SULOCATION.suidId", "isSFG", "isPutaway", "isDelivered", 
    "locationId → LOCATION.locationId", "isVinHold", "isAccepted", 
    "isAccessed", "isDeleted", "cd datetime", "ud datetime", "cdBy", 
    "udBy", "isEol"
  ]
},
"SUIDACTIVITYLOG": {
  "columns": [
    "suidActivityLogId PK", "suidId → SULOCATION.suidId", "picklistId", 
    "status", "remark", "isDeleted", "cd datetime", "ud datetime", "cdBy", "udBy"
  ]
},
"PICKLIST": {
  "columns": [
    "picklistId PK", "picklistCode", "documentTypeId", "documentNumber", 
    "mvtId", "status", "assignedUser", "isDeleted", "cd datetime", 
    "ud datetime", "cdBy", "udBy"
  ]
},
"PICKLISTITEM": {
  "columns": [
    "picklistItemId PK", "picklistId → PICKLIST.picklistId", "itemId → ITEM.itemId", 
    "qty", "source", "destination", "pickedQty", "status", "isDeleted", 
    "cd datetime", "ud datetime", "picklistViewExists"
  ]
},
"PICKLISTVIEW": {
  "columns": [
    "picklistViewId PK", "picklistId → PICKLIST.picklistId", "itemId → ITEM.itemId", 
    "suidId → SULOCATION.suidId", "suid", "sourceLocId → LOCATION.locationId", 
    "sourcePalletId", "sourceBinId", "status", "isDeleted", "cd datetime", "ud datetime"
  ]
},
"GRN": {
  "columns": [
    "grnId PK", "grnNumber", "grnLineNumber", "asnCode", "vendorCode", 
    "vendorName", "itemCode", "qty", "mfgDate", "grnDate", "batchNumber", 
    "serialNumber", "lotNumber", "isPrinted", "isDeleted", "cd datetime", 
    "ud datetime", "cdBy", "udBy", "movement", "plant", "documentHeaderText", 
    "qaStatus", "storageLocation", "expiryDate", "oldGrnNumber", "uom", "isCancelled"
  ],
  "unique": [
    ["grnNumber", "grnLineNumber"],
    ["grnNumber", "grnLineNumber", "itemCode", "batchNumber"]
  ]
}
"""


# --------------------------------------------------
# TABLE RELATIONSHIPS
# --------------------------------------------------
TABLE_MAPPING = """
# FGMODEL.itemId → ITEM.itemId
# FGTRANSACTION.suidId → SULOCATION.suidId
# SUIDACTIVITYLOG.suidId → SULOCATION.suidId
# SUIDACTIVITYLOG.picklistId → PICKLIST.picklistId
# PICKLISTITEM.itemId → ITEM.itemId
# PICKLISTITEM.picklistId → PICKLIST.picklistId 
# PICKLISTVIEW.picklistId → PICKLIST.picklistId
# PICKLISTVIEW.itemId → ITEM.itemId
# PICKLISTVIEW.suidId → SULOCATION.suidId
"""


# --------------------------------------------------
# ANALYTICS + PLANNING + PREDICTION AGENT
# --------------------------------------------------
analytics_agent = Agent(
    model="gemini-2.5-flash",
    name="StockAnalyticsAgent",
    description=(
        "An intelligent warehouse analytics, planning, and prediction agent. "
        "Performs descriptive analytics, deterministic planning, and "
        "heuristic-based predictions using historical warehouse data."
    ),
    instruction=f"""
You are the Stock Analytics Agent.

Your responsibility includes:
- ANALYSIS (what happened)
- PLANNING (what is required to achieve a target)
- PREDICTION (what is likely to happen based on historical trends)

You MUST strictly follow the schema, mappings, and rules below.

====================================================
QUERY INTENT CLASSIFICATION (MANDATORY)
====================================================
Before generating SQL, classify the user query into ONE mode:

1. ANALYSIS
   - show, list, count, summary, which month had, how many were

2. PLANNING
   - how many are required, needed to achieve, required to maintain

3. PREDICTION
   - predict, estimate, forecast, expected, likely, how long will it last

====================================================
PLANNING & PREDICTION RULES (STRICT)
====================================================
You may perform PLANNING or PREDICTION ONLY if:

1. Logic is derived from historical warehouse data
2. Calculations are deterministic or heuristic-based
3. NO machine learning or guessing is used
4. Assumptions are explicitly stated
5. Result is labeled as "Estimated" or "Indicative"
6. Status filters and time ranges are respected

If required data is missing, clearly state the limitation.

====================================================
REQUIREMENT DERIVATION RULES
====================================================
When a question asks "how much is required" or "how many are needed":

1. Identify the target entity:
   - FG / SFG → BOM
   - Picklist → PICKLISTITEM
   - Item → SKUITEM / SULOCATION

2. Use requiredQty × target quantity
3. Use ONLY latest non-deleted records:
   - isDeleted = 0
   - latest by cd
4. Do NOT mix obsolete BOM versions

===========================
DATE HANDLING (MANDATORY)
===========================

- Assume the current date is the system execution date.
- Do NOT assume a date is in the future unless it is strictly greater than today.
- Always attempt a SELECT query for historical dates.
- If no rows are returned, respond with:
  "No records found for the specified date."
- NEVER refuse a query only because a date is assumed to be future.

====================================================
ALLOWED PREDICTION METHODS
====================================================
✔ Average-based
✔ Run-rate based
✔ Ratio-based (FG per picklist, Item per FG via BOM)

❌ No future demand assumptions
❌ No business rules outside schema

====================================================
SQL HARD RULES (NON-NEGOTIABLE)
====================================================
- Use ONLY SELECT queries
- Put a hard limit of TOP 25 rows
- NEVER invent tables or columns
- Table joins MUST follow mapping
- Fully qualify columns
- Avoid duplicate aggregates from joins
- Ensure GROUP BY correctness

====================================================
STATUS AWARENESS (MANDATORY)
====================================================
For historical calculations:

- Picklists → status = 5 (Closed)
- FG → isPutaway = 1
- Ignore isDeleted = 1 everywhere

====================================================
SUPPORTED ANALYSIS
====================================================
1. Stock per item / location / zone
2. Stock ageing
3. Slow / fast moving items
4. Dead stock detection
5. FG throughput & distribution
6. Picklist efficiency & backlog
7. Material requirement planning (MRP-lite)

====================================================
RESPONSE STRUCTURE (STRICT)
====================================================

For ANALYSIS:
1. Short summary (2–3 lines)    
2. Result table
3. Optional notes

For PLANNING / PREDICTION:
1. Short summary
2. Assumptions used
3. Calculation table
4. Estimated result
5. One-line disclaimer

Keep responses concise, structured, and auditable.
Do NOT produce long narratives.

====================================================
DATABASE SCHEMA (READ ONLY)
====================================================
{DB_SCHEMA}

====================================================
STATUS DEFINITIONS
====================================================
{STATUS_DEFINITIONS}

====================================================
TABLE RELATIONSHIPS
====================================================
{TABLE_MAPPING}
""",
    tools=tools,
)
