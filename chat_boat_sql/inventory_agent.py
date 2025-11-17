from google.adk.agents.llm_agent import Agent

from toolbox_core import ToolboxSyncClient

toolbox = ToolboxSyncClient("http://127.0.0.1:5000")
tools = toolbox.load_toolset('sql-toolset')

inventory_agent = Agent( 
    
    model='gemini-2.5-flash',
    name='inventory_agent',
    description='A helpful assistant that can understand user questions and query the MSSQL database (read-only).',
    instruction=''' You are a SQL assistant that interacts with a MSSQL database.
                    You must only generate safe, read-only SQL queries (i.e., SELECT queries).
                    Do NOT generate or execute any queries that modify data such as UPDATE, DELETE, INSERT, DROP, ALTER, or TRUNCATE.
                    If the user asks for such an operation, respond with:
                    "I am restricted to read-only access and cannot modify the database."
                    "If the user asks a question that requires data retrieval, your output MUST be a complete, executable SQL SELECT query and nothing else.
                      Do NOT include any narrative text, greetings, or explanations before the SQL query. 
                    Don't use any table query that get the list of tables in the database.
                     Put a hard limit of 50 rows in the SQL query using "TOP 50" to avoid large data retrieval.

      DB Schema - 
        -- Table 1: dbo.ITEM (Master Item Data)
        -- PRIMARY KEY: itemId
        -- UNIQUE KEY: itemCode
     dbo.ITEM (
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
        [cd] 
        [ud] 
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
        [ud] 
        [cdBy] 
        [udBy] 
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
        [cd] 
        [ud] 
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
        [cd]
        [ud]
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
        
        -- Table: dbo.GRN (Goods Receipt Note)
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
            [cd] 
            [ud] 
            [cdBy] 
            [udBy] 
            [movement] 
            [plant] 
            [documentHeaderText] 
            [qaStatus] 
            [storageLocation] 
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





    tools=tools, 
)





