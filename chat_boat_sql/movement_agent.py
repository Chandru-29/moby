from google.adk.agents.llm_agent import Agent
from toolbox_core import ToolboxSyncClient
import re

# Connect to your existing toolbox service
toolbox = ToolboxSyncClient("http://127.0.0.1:5000")
tools = toolbox.load_toolset('sql-toolset')

movement_agent = Agent(
    model='gemini-2.5-flash',
    name='movement_agent',
 description='A helpful assistant that can understand user questions and query the MSSQL database (read-only).',
    instruction=''' You are a SQL assistant that interacts with a MSSQL database.
                    You must only generate safe, read-only SQL queries (i.e., SELECT queries).
                    Do NOT generate or execute any queries that modify data such as UPDATE, DELETE, INSERT, DROP, ALTER, or TRUNCATE.
                    If the user asks for such an operation, respond with:
                    "I am restricted to read-only access and cannot modify the database."
                    If the query is ambiguous, ask a short clarifying question.
                    Don't use any table query that get the list of tables in the database.
                    Put a hard limit of 50 rows in the SQL query using "TOP 50" to avoid large data retrieval.
                    
                    
    DB Schema - 
        -- Table 1: dbo.ITEM (Master Item Data)
        -- PRIMARY KEY: itemId
        -- UNIQUE KEY: itemCode
        CREATE TABLE dbo.ITEM (
            itemId
        [itemCode] 
        [itemTypeId] 
        [itemDescription]
        [itemGroup]
        [uom] 
        [issueType] 
        [status] 
        [procurementType] 
        [shelfLife]
        [isDeleted] 
        [cd] [datetime] 
        [ud] [datetime] 
        [cdBy] 
        [udBy] 
        [movementType] 
        [controlType]
        [weight] 
        [kittingType] 
        [qaRequired] 
        [userId] 
        );

        -- Table 2: dbo.SKUITEM (Stock Keeping Unit / GRN Data)
        -- PRIMARY KEY: skuId
        -- FOREIGN KEY: itemId REFERENCES dbo.ITEM(itemId)
        CREATE TABLE dbo.SKUITEM (
        [skuId] 
        [sku] 
        [grnNumber] 
        [grnLineNumber] 
        [asnCode] 
        [vendorCode] 
        [vendorName] 
        [itemId]
        [qty]
        [mfgDate] 
        [lotNumber] 
        [serialNumber] 
        [uom] 
        [isDeleted] 
        [cd] 
        [ud] [datetime]
        [cdBy] [varchar]
        [udBy] [varchar]
        );

        -- Table 3: dbo.LOCATION (Warehouse Locations)
        -- PRIMARY KEY: locationId
        -- UNIQUE KEY: locationCode
        CREATE TABLE dbo.LOCATION (
        [locationId] 
        [locationCode] 
        [locationName] 
        [parentId] 
        [parentCode] 
        [isLocation] 
        [rltId] 
        [status] 
        [isEmpty] 
        [isDeleted] 
        [cd] [datetime] 
        [ud] [datetime] 
        [cdBy] 
        [udBy] 
        );

        -- Table 4: dbo.SULOCATION (Stock Unit Location - Where the SKUs actually are)
        -- PRIMARY KEY: suidId
        -- FOREIGN KEY 1: skuId REFERENCES dbo.SKUITEM(skuId)
        -- FOREIGN KEY 2: locationId REFERENCES dbo.LOCATION(locationId)
        CREATE TABLE dbo.SULOCATION (
            [suidId] 
        [suid] 
        [skuId] 
        [qty] 
        [locationId] 
        [palletId] 
        [binId] 
        [isDeleted] 
        [cd] [datetime] 
        [ud] [datetime] 
        [cdBy] 
        [udBy] 
        [inTransit] 
        [picklistId] 
        [isAllocated] 
        [status] 
        [rejectionReason] 
        [documentId] 
        [onHold] 
        [tempAssetId] 
        [grnLineNumber] 
        [serialNumber] 
        [isGrouped] 
        [kittingType] 
        );


        Table 5: dbo.FGMODEL (Finished Goods Model)
    CREATE TABLE dbo.FGMODEL (
        fgModelId 
        fgModelCode 
        fgModelName 
        itemId
        isDeleted 
        cd DATETIME2 
        ud DATETIME2
        cdBy 
        udBy 
    );

    -- Table 6: dbo.ITEMLOCACNMAP (Item-Location Mapping)
    CREATE TABLE dbo.ITEMLOCACNMAP (
        itemLocAcnMapId 
        categoryId
        itemId 
        warehouseId 
        locationId 
        acnId 
        zoneId
        sectionId 
        rackId  
        isDeleted 
        cd DATETIME  
        ud DATETIME  (),
        [cdBy]
	    [udBy] 
    );

    -- Table 7: dbo.FGTRANSACTION (Finished Goods Movement / Putaway)
    CREATE TABLE dbo.FGTRANSACTION (
        fgTransactionId 
        fgCode 
        vin 
        sNo 
        putawayTime  
        suidId 
        isSFG 
        isPutaway 
        isDelivered 
        locationId 
        isVinHold 
        isAccepted 
        isAccessed 
        isDeleted 
        cd DATETIME2 
        ud DATETIME2 ,
        cdBy 
        udBy 
        isEol BIT DEFAULT 0
    );

    -- Table 8: dbo.SUIDACTIVITYLOG (Tracks SU Movements & Picklists)
    CREATE TABLE dbo.SUIDACTIVITYLOG (
        suidActivityLogId 
        suidId 
        picklistId 
        status 
        remark 
        isDeleted 
        cd DATETIME 
        ud DATETIME
        cdBy 
        udBy 
    );

    -- Table 9: dbo.PICKLIST (Picklist Header)
    CREATE TABLE dbo.PICKLIST (
        picklistId 
        picklistCode 
        documentTypeId 
        documentNumber LL,
        mvtId 
        status 
        assignedUser 
        isDeleted 
        cd DATETIME 
        ud DATETIME 
        cdBy 
        udBy 
    );

    -- Table 10: dbo.PICKLISTITEM (Line items in a picklist)
    CREATE TABLE dbo.PICKLISTITEM (
        picklistItemId 
        picklistId 
        itemId 
        qty 
        source 
        destination 
        pickedQty 
        status 
        isDeleted 
        cd DATETIME 
        ud DATETIME 
        picklistViewExists 
    );

    -- Table 11: dbo.PICKLISTVIEW (View of Picklist Items and SUIDs)
    CREATE TABLE dbo.PICKLISTVIEW (
        picklistViewId 
        picklistId 
        itemId 
        suidId
        suid 
        sourceLocId 
        sourcePalletId
        sourceBinId 
        status 
        isDeleted 
        cd DATETIME 
        ud DATETIME 
    );



      -- Table 12: dbo.GRN (Goods Receipt Note)
        -- PRIMARY KEY: grnId
        -- UNIQUE KEYS:
        --   1) (grnNumber, grnLineNumber)
        --   2) (grnNumber, grnLineNumber, itemCode, batchNumber)

        CREATE TABLE [dbo].[GRN](
            [grnId] 
            [grnNumber] 
            [grnLineNumber] 
            [asnCode] 
            [vendorCode] 
            [vendorName] 
            [itemCode] 
            [qty] 
            [mfgDate] 
            [grnDate] 
            [batchNumber] 
            [serialNumber] 
            [lotNumber] 
            [isPrinted] 
            [isDeleted] 
            [cd] [datetime] 
            [ud] [datetime] 
            [cdBy] 
            [udBy] 
            [movement] 
            [plant] 
            [documentHeaderText] 
            [qaStatus] 
            [storageLocation] ,
            [expiryDate] 
            [oldGrnNumber] 
            [uom] 
            [isCancelled] 
            );

            -- Primary Key      
            ALTER TABLE dbo.GRN
            ADD CONSTRAINT PK_GRN PRIMARY KEY CLUSTERED (grnId);

            -- Unique Key #1: GRN header-level uniqueness
         ALTER TABLE dbo.GRN
            ADD CONSTRAINT UQ_GRN_NumberLine UNIQUE (grnNumber, grnLineNumber);

            -- Unique Key #2: GRN line + item + batch uniqueness
            ALTER TABLE dbo.GRN
            ADD CONSTRAINT UQ_GRN_NumberLineItemBatch 
                UNIQUE (grnNumber, grnLineNumber, itemCode, batchNumber);

     

    ============================
    KEY RELATIONSHIPS
    ============================
    -- FGMODEL.itemId → ITEM.itemId
    -- FGTRANSACTION.suidId → SULOCATION.suidId
    -- SUIDACTIVITYLOG.suidId → SULOCATION.suidId
    -- SUIDACTIVITYLOG.picklistId → PICKLIST.picklistId
    -- PICKLISTITEM.itemId → ITEM.itemId
    -- PICKLISTITEM.picklistId → PICKLIST.picklistId
    -- PICKLISTVIEW.picklistId → PICKLIST.picklistId
    -- PICKLISTVIEW.itemId → ITEM.itemId
    -- PICKLISTVIEW.suidId → SULOCATION.suidId
       
        ========================================================
    STATUS DEFINITIONS (USE THESE ALWAYS)
    ========================================================

    📌 PICKLIST & PICKLISTITEM status:
    0 = Created
    1 = Released
    2 = Picking Started
    3 = All Picked
    4 = Putaway Started
    5 = Putaway Completed

    ✔ "Open Picklist" → status IN (1,2,3,4)
    ✔ "Pending Picklist" → status IN (0,1)
    ✔ "Picking in progress" → status = 2
    ✔ "Picked" → status = 3
    ✔ "Putaway pending" → status IN (3,4)
    ✔ "Closed Picklist" → status = 5

    📌 PICKLISTVIEW
    2 = Created
    3 = Picked
    5 = Putaway Done

    ✔ "Open picklist view" → status IN (2,3)
    ✔ "Completed picklist view" → status = 5

    📌 SULOCATION (movement)
    0 = Inactive
    1 = Active
    2 = First Level Quarantine
    3 = Second Level Quarantine / Scrapped
    4 = First Level Rejection
    5 = Second Level Rejection / Scrapped / RTV
    6 = Unplanned Issue / Material Request

    
 ''',

    tools=tools,  
)



# ============================================
# RELATION SUMMARY MAP (for movement_agent)
# ============================================

movement_relations = {
    # ───────── Core Warehouse Structure ─────────
    "ITEM": {
        "joins_to": {
            "SKUITEM": "ITEM.itemId = SKUITEM.itemId",
            "FGMODEL": "ITEM.itemId = FGMODEL.itemId",
            "PICKLISTITEM": "ITEM.itemId = PICKLISTITEM.itemId",
            "PICKLISTVIEW": "ITEM.itemId = PICKLISTVIEW.itemId"
        },
        "type": "master"
    },

    "SKUITEM": {
        "joins_to": {
            "SULOCATION": "SKUITEM.skuId = SULOCATION.skuId"
        },
        "type": "transaction"
    },

    "LOCATION": {
        "joins_to": {
            "SULOCATION": "LOCATION.locationId = SULOCATION.locationId",
            "FGTRANSACTION": "LOCATION.locationId = FGTRANSACTION.locationId"
        },
        "type": "reference"
    },

    "SULOCATION": {
        "joins_to": {
            "SKUITEM": "SULOCATION.skuId = SKUITEM.skuId",
            "LOCATION": "SULOCATION.locationId = LOCATION.locationId",
            "SUIDACTIVITYLOG": "SULOCATION.suidId = SUIDACTIVITYLOG.suidId",
            "FGTRANSACTION": "SULOCATION.suidId = FGTRANSACTION.suidId",
            "PICKLISTVIEW": "SULOCATION.suidId = PICKLISTVIEW.suidId"
        },
        "type": "inventory_unit"
    },

    # ───────── Finished Goods Tracking ─────────
    "FGMODEL": {
        "joins_to": {
            "ITEM": "FGMODEL.itemId = ITEM.itemId"
        },
        "type": "master"
    },

    "FGTRANSACTION": {
        "joins_to": {
            "SULOCATION": "FGTRANSACTION.suidId = SULOCATION.suidId",
            "LOCATION": "FGTRANSACTION.locationId = LOCATION.locationId"
        },
        "type": "movement_log"
    },

    # ───────── Item-Location Mapping ─────────
    "ITEMLOCACNMAP": {
        "joins_to": {
            "ITEM": "ITEMLOCACNMAP.itemId = ITEM.itemId",
            "LOCATION": "ITEMLOCACNMAP.locationId = LOCATION.locationId"
        },
        "type": "mapping"
    },

    # ───────── Picklist and Movement ─────────
    "PICKLIST": {
        "joins_to": {
            "PICKLISTITEM": "PICKLIST.picklistId = PICKLISTITEM.picklistId",
            "PICKLISTVIEW": "PICKLIST.picklistId = PICKLISTVIEW.picklistId",
            "SUIDACTIVITYLOG": "PICKLIST.picklistId = SUIDACTIVITYLOG.picklistId"
        },
        "type": "document_header"
    },

    "PICKLISTITEM": {
        "joins_to": {
            "ITEM": "PICKLISTITEM.itemId = ITEM.itemId",
            "PICKLIST": "PICKLISTITEM.picklistId = PICKLIST.picklistId"
        },
        "type": "document_detail"
    },

    "PICKLISTVIEW": {
        "joins_to": {
            "PICKLIST": "PICKLISTVIEW.picklistId = PICKLIST.picklistId",
            "SULOCATION": "PICKLISTVIEW.suidId = SULOCATION.suidId",
            "ITEM": "PICKLISTVIEW.itemId = ITEM.itemId"
        },
        "type": "derived_view"
    },

    # ───────── Activity Logs ─────────
    "SUIDACTIVITYLOG": {
        "joins_to": {
            "SULOCATION": "SUIDACTIVITYLOG.suidId = SULOCATION.suidId",
            "PICKLIST": "SUIDACTIVITYLOG.picklistId = PICKLIST.picklistId"
        },
        "type": "audit_log"
    },
}

def build_join_context(user_query: str, relation_map: dict) -> str:
    """
    Detect relevant tables mentioned in user query and build JOIN relationship context.
    """
    user_query_upper = user_query.upper()
    matched_tables = [t for t in relation_map.keys() if t in user_query_upper]

    # infer common keywords
    if not matched_tables:
        if "VIN" in user_query_upper or "FG" in user_query_upper:
            matched_tables = ["FGTRANSACTION"]
        elif "PICKLIST" in user_query_upper:
            matched_tables = ["PICKLIST"]
        elif "LOCATION" in user_query_upper:
            matched_tables = ["LOCATION"]
        elif "SUID" in user_query_upper:
            matched_tables = ["SULOCATION"]

    relation_hints = []
    for t in matched_tables:
        joins = relation_map.get(t, {}).get("joins_to", {})
        for target, condition in joins.items():
            relation_hints.append(f"{t} joins {target} on {condition}")

    if not relation_hints:
        return ""

    context_text = "\nPossible joins based on known relationships:\n" + "\n".join(relation_hints)
    return context_text

