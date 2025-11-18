
from google.adk.agents.llm_agent import Agent

from toolbox_core import ToolboxSyncClient

toolbox = ToolboxSyncClient("http://127.0.0.1:5000")
tools = toolbox.load_toolset('sql-toolset')




inventory_agent = Agent( 
    
    model='gemini-2.5-flash',
    name='inventory_agent',
    # schema= compressed_schema ,
    description='A helpful assistant that can understand user questions and query the MSSQL database (read-only).',
    instruction=''' You are a SQL assistant that interacts with a MSSQL database.
                    Never create any new table name by youself, always use the db schema provided.
                    You must only generate safe, read-only SQL queries (i.e., SELECT queries).
                    Do NOT generate or execute any queries that modify data such as UPDATE, DELETE, INSERT, DROP, ALTER, or TRUNCATE.
                    If the user asks for such an operation, respond with:
                    "I am restricted to read-only access and cannot modify the database."
                    "If the user asks a question that requires data retrieval, your output MUST be a complete, executable SQL SELECT query and nothing else.
                      Do NOT include any narrative text, greetings, or explanations before the SQL query. 
                    Don't use any table query that get the list of tables in the database.
                     Put a hard limit of 50 rows in the SQL query using "TOP 50" to avoid large data retrieval.

     
        
   db schema:

                       
  "ITEM": {
    "columns": [
      "itemId PK",
      "itemCode UNIQUE",
      "itemTypeId",
      "itemDescription",
      "itemGroup",
      "uom",
      "issueType",
      "status",
      "procurementType",
      "shelfLife",
      "isDeleted",
      "cd datetime",
      "ud datetime",
      "cdBy",
      "udBy",
      "movementType",
      "controlType",
      "weight",
      "kittingType",
      "qaRequired",
      "userId"
    ]
  },

  "SKUITEM": {
    "columns": [
      "skuId PK",
      "sku",
      "grnNumber",
      "grnLineNumber",
      "asnCode",
      "vendorCode",
      "vendorName",
      "itemId → ITEM.itemId",
      "qty",
      "mfgDate",
      "lotNumber",
      "serialNumber",
      "uom",
      "isDeleted",
      "cd",
      "ud datetime",
      "cdBy",
      "udBy"
    ]
  },

  "LOCATION": {
    "columns": [
      "locationId PK",
      "locationCode UNIQUE",
      "locationName",
      "parentId",
      "parentCode",
      "isLocation",
      "rltId",
      "status",
      "isEmpty",
      "isDeleted",
      "cd datetime",
      "ud datetime",
      "cdBy",
      "udBy"
    ]
  },

  "SULOCATION": {
    "columns": [
      "suidId PK",
      "suid",
      "skuId → SKUITEM.skuId",
      "qty",
      "locationId → LOCATION.locationId",
      "palletId",
      "binId",
      "isDeleted",
      "cd datetime",
      "ud datetime",
      "cdBy",
      "udBy",
      "inTransit",
      "picklistId",
      "isAllocated",
      "status",
      "rejectionReason",
      "documentId",
      "onHold",
      "tempAssetId",
      "grnLineNumber",
      "serialNumber",
      "isGrouped",
      "kittingType"
    ]
  },

  "GRN": {
    "columns": [
      "grnId PK",
      "grnNumber",
      "grnLineNumber",
      "asnCode",
      "vendorCode",
      "vendorName",
      "itemCode",
      "qty",
      "mfgDate",
      "grnDate",
      "batchNumber",
      "serialNumber",
      "lotNumber",
      "isPrinted",
      "isDeleted",
      "cd datetime",
      "ud datetime",
      "cdBy",
      "udBy",
      "movement",
      "plant",
      "documentHeaderText",
      "qaStatus",
      "storageLocation",
      "expiryDate",
      "oldGrnNumber",
      "uom",
      "isCancelled"
    ],
    "unique": [
      ["grnNumber", "grnLineNumber"],
      ["grnNumber", "grnLineNumber", "itemCode", "batchNumber"]
    ]
  }
                     

                -- IMPORTANT RELATIONSHIPS FOR JOINING:
                -- SULOCATION.skuId joins SKUITEM.skuId
                -- SULOCATION.locationId joins LOCATION.locationId
                -- SKUITEM.itemId joins ITEM.itemId 
                
    "ITEM": {
    "SKUITEM": "ITEM.itemId = SKUITEM.itemId"
    },
    "SKUITEM": {
        "ITEM": "SKUITEM.itemId = ITEM.itemId",
        "SULOCATION": "SKUITEM.skuId = SULOCATION.skuId",
        "GRN": "SKUITEM.grnNumber = GRN.grnNumber AND SKUITEM.grnLineNumber = GRN.grnLineNumber"
    },
    "SULOCATION": {
        "SKUITEM": "SULOCATION.skuId = SKUITEM.skuId",
        "LOCATION": "SULOCATION.locationId = LOCATION.locationId"
    },
    "LOCATION": {
        "SULOCATION": "LOCATION.locationId = SULOCATION.locationId"
    },
    "GRN": {
        "SKUITEM": "GRN.grnNumber = SKUITEM.grnNumber AND GRN.grnLineNumber = SKUITEM.grnLineNumber"
    }''',

    
                #     compressed_schema ={
                        
                #     "ITEM": {
                #         "columns": [
                #         "itemId PK",
                #         "itemCode UNIQUE",
                #         "itemTypeId",
                #         "itemDescription",
                #         "itemGroup",
                #         "uom",
                #         "issueType",
                #         "status",
                #         "procurementType",
                #         "shelfLife",
                #         "isDeleted",
                #         "cd datetime",
                #         "ud datetime",
                #         "cdBy",
                #         "udBy",
                #         "movementType",
                #         "controlType",
                #         "weight",
                #         "kittingType",
                #         "qaRequired",
                #         "userId"
                #         ]
                #     },

                #     "SKUITEM": {
                #         "columns": [
                #         "skuId PK",
                #         "sku",
                #         "grnNumber",
                #         "grnLineNumber",
                #         "asnCode",
                #         "vendorCode",
                #         "vendorName",
                #         "itemId → ITEM.itemId",
                #         "qty",
                #         "mfgDate",
                #         "lotNumber",
                #         "serialNumber",
                #         "uom",
                #         "isDeleted",
                #         "cd",
                #         "ud datetime",
                #         "cdBy",
                #         "udBy"
                #         ]
                #     },

                #     "LOCATION": {
                #         "columns": [
                #         "locationId PK",
                #         "locationCode UNIQUE",
                #         "locationName",
                #         "parentId",
                #         "parentCode",
                #         "isLocation",
                #         "rltId",
                #         "status",
                #         "isEmpty",
                #         "isDeleted",
                #         "cd datetime",
                #         "ud datetime",
                #         "cdBy",
                #         "udBy"
                #         ]
                #     },

                #     "SULOCATION": {
                #         "columns": [
                #         "suidId PK",
                #         "suid",
                #         "skuId → SKUITEM.skuId",
                #         "qty",
                #         "locationId → LOCATION.locationId",
                #         "palletId",
                #         "binId",
                #         "isDeleted",
                #         "cd datetime",
                #         "ud datetime",
                #         "cdBy",
                #         "udBy",
                #         "inTransit",
                #         "picklistId",
                #         "isAllocated",
                #         "status",
                #         "rejectionReason",
                #         "documentId",
                #         "onHold",
                #         "tempAssetId",
                #         "grnLineNumber",
                #         "serialNumber",
                #         "isGrouped",
                #         "kittingType"
                #         ]
                #     },

                #     "GRN": {
                #         "columns": [
                #         "grnId PK",
                #         "grnNumber",
                #         "grnLineNumber",
                #         "asnCode",
                #         "vendorCode",
                #         "vendorName",
                #         "itemCode",
                #         "qty",
                #         "mfgDate",
                #         "grnDate",
                #         "batchNumber",
                #         "serialNumber",
                #         "lotNumber",
                #         "isPrinted",
                #         "isDeleted",
                #         "cd datetime",
                #         "ud datetime",
                #         "cdBy",
                #         "udBy",
                #         "movement",
                #         "plant",
                #         "documentHeaderText",
                #         "qaStatus",
                #         "storageLocation",
                #         "expiryDate",
                #         "oldGrnNumber",
                #         "uom",
                #         "isCancelled"
                #         ],
                #         "unique": [
                #         ["grnNumber", "grnLineNumber"],
                #         ["grnNumber", "grnLineNumber", "itemCode", "batchNumber"]
                #         ]
                #     }
                # }




    tools=tools, 
)





