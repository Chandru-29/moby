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
                    Put a hard limit of 100 rows in the SQL query using "TOP 100" to avoid large data retrieval.
                    
    DB Schema - 
        -- Table 1: dbo.ITEM (Master Item Data)
        -- PRIMARY KEY: itemId
        -- UNIQUE KEY: itemCode
        CREATE TABLE dbo.ITEM (
            itemId [int] IDENTITY(1,1) NOT NULL,
        [itemCode] [varchar](45) NOT NULL,
        [itemTypeId] [int] NOT NULL,
        [itemDescription] [varchar](200) NULL,
        [itemGroup] [varchar](45) NULL,
        [uom] [varchar](45) NOT NULL,
        [issueType] [varchar](45) NULL,
        [status] [int] NOT NULL,
        [procurementType] [varchar](45) NULL,
        [shelfLife] [int] NULL,
        [isDeleted] [int] NULL,
        [cd] [datetime] NOT NULL,
        [ud] [datetime] NOT NULL,
        [cdBy] [varchar](100) NULL,
        [udBy] [varchar](100) NULL,
        [movementType] [varchar](45) NULL,
        [controlType] [int] NOT NULL,
        [weight] [int] NOT NULL,
        [kittingType] [int] NOT NULL,
        [qaRequired] [varchar](50) NULL,
        [userId] [uniqueidentifier] NULL,
        );

        -- Table 2: dbo.SKUITEM (Stock Keeping Unit / GRN Data)
        -- PRIMARY KEY: skuId
        -- FOREIGN KEY: itemId REFERENCES dbo.ITEM(itemId)
        CREATE TABLE dbo.SKUITEM (
        [skuId] [int] IDENTITY(1,1) NOT NULL,
        [sku] [varchar](45) NOT NULL,
        [grnNumber] [varchar](45) NOT NULL,
        [grnLineNumber] [varchar](45) NOT NULL,
        [asnCode] [varchar](45) NULL,
        [vendorCode] [varchar](200) NULL,
        [vendorName] [varchar](45) NULL,
        [itemId] [int] NOT NULL,
        [qty] [float] NOT NULL,
        [mfgDate] [datetime] NULL,
        [lotNumber] [varchar](45) NULL,
        [serialNumber] [varchar](45) NULL,
        [uom] [varchar](45) NOT NULL,
        [isDeleted] [int] NULL,
        [cd] [datetime] NOT NULL,
        [ud] [datetime] NOT NULL,
        [cdBy] [varchar](100) NULL,
        [udBy] [varchar](100) NULL,
        );

        -- Table 3: dbo.LOCATION (Warehouse Locations)
        -- PRIMARY KEY: locationId
        -- UNIQUE KEY: locationCode
        CREATE TABLE dbo.LOCATION (
        [locationId] [int] IDENTITY(1,1) NOT NULL,
        [locationCode] [varchar](100) NOT NULL,
        [locationName] [varchar](100) NOT NULL,
        [parentId] [int] NOT NULL,
        [parentCode] [varchar](45) NULL,
        [isLocation] [int] NOT NULL,
        [rltId] [int] NOT NULL,
        [status] [int] NOT NULL,
        [isEmpty] [int] NOT NULL,
        [isDeleted] [int] NULL,
        [cd] [datetime] NOT NULL,
        [ud] [datetime] NOT NULL,
        [cdBy] [varchar](100) NULL,
        [udBy] [varchar](100) NULL,
        );

        -- Table 4: dbo.SULOCATION (Stock Unit Location - Where the SKUs actually are)
        -- PRIMARY KEY: suidId
        -- FOREIGN KEY 1: skuId REFERENCES dbo.SKUITEM(skuId)
        -- FOREIGN KEY 2: locationId REFERENCES dbo.LOCATION(locationId)
        CREATE TABLE dbo.SULOCATION (
            [suidId] [int] IDENTITY(1,1) NOT NULL,
        [suid] [varchar](45) NOT NULL,
        [skuId] [int] NOT NULL,
        [qty] [float] NULL,
        [locationId] [int] NOT NULL,
        [palletId] [int] NULL,
        [binId] [int] NULL,
        [isDeleted] [int] NULL,
        [cd] [datetime] NOT NULL,
        [ud] [datetime] NOT NULL,
        [cdBy] [varchar](100) NULL,
        [udBy] [varchar](100) NULL,
        [inTransit] [tinyint] NOT NULL,
        [picklistId] [int] NULL,
        [isAllocated] [tinyint] NULL,
        [status] [int] NOT NULL,
        [rejectionReason] [varchar](225) NULL,
        [documentId] [int] NULL,
        [onHold] [tinyint] NOT NULL,
        [tempAssetId] [int] NULL,
        [grnLineNumber] [int] NULL,
        [serialNumber] [varchar](50) NULL,
        [isGrouped] [bit] NULL,
        [kittingType] [int] NULL,
        );


        Table 5: dbo.FGMODEL (Finished Goods Model)
    CREATE TABLE dbo.FGMODEL (
        fgModelId INT IDENTITY(1,1) PRIMARY KEY,
        fgModelCode VARCHAR(45) NOT NULL,
        fgModelName VARCHAR(45) NOT NULL,
        itemId INT NOT NULL,
        isDeleted TINYINT DEFAULT 0,
        cd DATETIME2 NOT NULL DEFAULT GETDATE(),
        ud DATETIME2 NULL,
        cdBy VARCHAR(45),
        udBy VARCHAR(45)
    );

    -- Table 6: dbo.ITEMLOCACNMAP (Item-Location Mapping)
    CREATE TABLE dbo.ITEMLOCACNMAP (
        itemLocAcnMapId INT IDENTITY(1,1) PRIMARY KEY,
        categoryId INT NOT NULL,
        itemId INT NOT NULL,
        warehouseId INT NOT NULL,
        locationId INT NULL,
        acnId INT NOT NULL,
        zoneId INT NULL,
        sectionId INT NULL,
        rackId INT NULL,
        isDeleted INT DEFAULT 0,
        cd DATETIME DEFAULT GETDATE(),
        ud DATETIME DEFAULT GETDATE(),
        [cdBy] [varchar](100) NULL,
	    [udBy] [varchar](100) NULL
    );

    -- Table 7: dbo.FGTRANSACTION (Finished Goods Movement / Putaway)
    CREATE TABLE dbo.FGTRANSACTION (
        fgTransactionId INT IDENTITY(1,1) PRIMARY KEY,
        fgCode VARCHAR(40) NOT NULL,
        vin VARCHAR(40) NOT NULL,
        sNo VARCHAR(40) NOT NULL,
        putawayTime DATETIME NULL,
        suidId INT NULL,
        isSFG INT DEFAULT 0,
        isPutaway INT DEFAULT 0,
        isDelivered INT DEFAULT 0,
        locationId INT DEFAULT 0,
        isVinHold INT DEFAULT 0,
        isAccepted INT DEFAULT 0,
        isAccessed INT DEFAULT 0,
        isDeleted TINYINT DEFAULT 0,
        cd DATETIME2 DEFAULT GETDATE(),
        ud DATETIME2 NULL,
        cdBy VARCHAR(45),
        udBy VARCHAR(45),
        isEol BIT DEFAULT 0
    );

    -- Table 8: dbo.SUIDACTIVITYLOG (Tracks SU Movements & Picklists)
    CREATE TABLE dbo.SUIDACTIVITYLOG (
        suidActivityLogId INT IDENTITY(1,1) PRIMARY KEY,
        suidId INT NOT NULL,
        picklistId INT NULL,
        status INT NOT NULL,
        remark VARCHAR(500),
        isDeleted INT DEFAULT 0,
        cd DATETIME DEFAULT GETDATE(),
        ud DATETIME DEFAULT GETDATE(),
        cdBy VARCHAR(100),
        udBy VARCHAR(100)
    );

    -- Table 9: dbo.PICKLIST (Picklist Header)
    CREATE TABLE dbo.PICKLIST (
        picklistId INT IDENTITY(1,1) PRIMARY KEY,
        picklistCode VARCHAR(45) NOT NULL UNIQUE,
        documentTypeId INT NOT NULL,
        documentNumber VARCHAR(45) NOT NULL,
        mvtId INT NOT NULL,
        status INT DEFAULT 0,
        assignedUser VARCHAR(45),
        isDeleted INT DEFAULT 0,
        cd DATETIME DEFAULT GETDATE(),
        ud DATETIME DEFAULT GETDATE(),
        cdBy VARCHAR(100),
        udBy VARCHAR(100)
    );

    -- Table 10: dbo.PICKLISTITEM (Line items in a picklist)
    CREATE TABLE dbo.PICKLISTITEM (
        picklistItemId INT IDENTITY(1,1) PRIMARY KEY,
        picklistId INT NOT NULL,
        itemId INT NOT NULL,
        qty FLOAT NOT NULL,
        source VARCHAR(45),
        destination VARCHAR(45),
        pickedQty FLOAT DEFAULT 0,
        status INT DEFAULT 0,
        isDeleted INT DEFAULT 0,
        cd DATETIME DEFAULT GETDATE(),
        ud DATETIME DEFAULT GETDATE(),
        picklistViewExists INT DEFAULT 0
    );

    -- Table 11: dbo.PICKLISTVIEW (View of Picklist Items and SUIDs)
    CREATE TABLE dbo.PICKLISTVIEW (
        picklistViewId INT IDENTITY(1,1) PRIMARY KEY,
        picklistId INT NOT NULL,
        itemId INT NOT NULL,
        suidId INT NOT NULL,
        suid VARCHAR(45) NOT NULL,
        sourceLocId INT NOT NULL,
        sourcePalletId INT NULL,
        sourceBinId INT NULL,
        status INT DEFAULT 0,
        isDeleted INT DEFAULT 0,
        cd DATETIME DEFAULT GETDATE(),
        ud DATETIME DEFAULT GETDATE()
    );

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
       

 ''',

    tools=tools,   # type: ignore
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

