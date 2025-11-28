from google.adk.agents.llm_agent import Agent
from toolbox_core import ToolboxSyncClient


toolbox = ToolboxSyncClient("http://127.0.0.1:5000")
tools = toolbox.load_toolset('sql-toolset')

STATUS_DEFINITIONS = """
#  PICKLIST & PICKLISTITEM status:
# 0 = Created
# 1 = Released
# 2 = Picking Started
# 3 = All Picked
# 4 = Putaway Started
# 5 = Putaway Completed

# ✔ "Open Picklist" → status IN (1,2,3,4)
# ✔ "Pending Picklist" → status IN (0,1)
# ✔ "Picking in progress" → status = 2
# ✔ "Picked" → status = 3
# ✔ "Putaway pending" → status IN (3,4)
# ✔ "Closed Picklist" → status = 5

# PICKLISTVIEW
# 2 = Created
# 3 = Picked
# 5 = Putaway Done

# ✔ "Open picklist view" → status IN (2,3)
# ✔ "Completed picklist view" → status = 5

#  SULOCATION (movement)
# 0 = Inactive
# 1 = Active
# 2 = First Level Quarantine
# 3 = Second Level Quarantine / Scrapped
# 4 = First Level Rejection
# 5 = Second Level Rejection / Scrapped / RTV
# 6 = Unplanned Issue / Material Request

# DOCUMENT TYPE INFORMATION
# 1  ->	GRN  ->	Goods Received Note
# 16 -> TO ->	Transfer Order
# 18 ->	SF -> Shop Floor
# 19 ->	KT -> Kitting
# 20 ->	PO -> Production Order
# 21 ->	WO -> Work Order
# 22 ->	SO -> Sales Order
# 23 ->	REJ->	Rejection
# 24 ->	QR -> Quarantine
# 25 ->	SFG->	Semi Finished Goods
# 26 ->	UI -> Unplanned Issue
# 27 ->	FG -> Finished Goods
# 32 -> MR -> Material Reservation
# 37 -> AFSSO->	After Sales Sales Order
"""

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
Table_mapping ='''============================
#     KEY RELATIONSHIPS
#     ============================
#     -- FGMODEL.itemId → ITEM.itemId
#     -- FGTRANSACTION.suidId → SULOCATION.suidId
#     -- SUIDACTIVITYLOG.suidId → SULOCATION.suidId
#     -- SUIDACTIVITYLOG.picklistId → PICKLIST.picklistId
#     -- PICKLISTITEM.itemId → ITEM.itemId
#     -- PICKLISTITEM.picklistId → PICKLIST.picklistId
#     -- PICKLISTVIEW.picklistId → PICKLIST.picklistId
#     -- PICKLISTVIEW.itemId → ITEM.itemId
#     -- PICKLISTVIEW.suidId → SULOCATION.suidId
       
#     ========================================================'''


warehouse_agent = Agent(
    model='gemini-2.5-flash',
    name='warehouse_agent',
    description='A specialized SQL query generator for a WMS database (read-only).',
    instruction=f''' You are a Sql expert, so always read the user query properl.
        You are a SQL expert that interacts with a MSSQL database. You must adhere to these rules strictly:
        1. **Security First**: You must only generate safe, read-only SQL queries (i.e., SELECT queries).
        2. **Forbidden Operations**: Do NOT generate or execute any queries that modify data such as UPDATE, DELETE, INSERT, DROP, ALTER, or TRUNCATE.
        3. **Query Limit**: Put a hard limit of 100 rows in the SQL query using "TOP 100" to avoid large data retrieval.
        4. **Ambiguity**: If the query is ambiguous, ask a short clarifying question instead of generating SQL.
        5. **Use JOINs**: Use the relationships provided below to join tables when needed.
        6. **NEVER** create new table or column names; always use the provided schema.
        7. **Never** Give the reponse in the raw format or JSON formate, always structure the repsonse properly specially when you are showing the data.
        8. 🔥 **STATUS CONVERSION (CRITICAL)**: The `status` column in all tables is an **INTEGER**. You **MUST** translate all natural language status requests (e.g., "Picked", "Open Picklist") into their corresponding **NUMERICAL VALUES** or **NUMERICAL RANGES** using the `STATUS_DEFINITIONS` below. **NEVER** use string literals (e.g., 'Picked') in a WHERE clause for status.
        9. **Never** Show the sql query whethere it is asked or not.
        10. Never return full unfiltered data from any table.
        11. If the user requests “select *” or “display table”, ask them "what specefic you are looking for?".
        12. For large tables, only return sample rows (max 10 rows).
        13. If user requests to display entire table data:
            - Do NOT execute query.
            - Instead respond: "The table has many rows. Please specify What are looking for ?"
        14. *Never* Reveal the name of the columns and tables you have access. 


        DB schema:
        {DB_SCHEMA}

        ========================================================
        STATUS DEFINITIONS (USE THESE NUMERICAL MAPPINGS ALWAYS)
        ========================================================
        {STATUS_DEFINITIONS}
        =====================================
        table mapping
        ====================================
        {Table_mapping}
    ''',
    tools=tools,
)

