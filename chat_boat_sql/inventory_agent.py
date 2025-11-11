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
        CREATE TABLE SWMS.dbo.GRN (
        [grnId] [int] IDENTITY(1,1) NOT NULL,
        [grnNumber] [varchar(45)] COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
        [grnLineNumber] varchar(45) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
        [asnCode] varchar(45) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
        [vendorCode] varchar(200) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
        [vendorName] varchar(45) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
        [itemCode] varchar(45) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
        [qty] float NULL,
        [mfgDate] datetime NULL,
        [grnDate] datetime NULL,
        [batchNumber] varchar(45) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
        [serialNumber] varchar(45) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
        [lotNumber] varchar(45) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
        [isPrinted] int DEFAULT 0 NOT NULL,
        [isDeleted] int DEFAULT 0 NULL,
        cd datetime DEFAULT getdate() NOT NULL,
        ud datetime DEFAULT getdate() NOT NULL,
        cdBy varchar(100) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
        udBy varchar(100) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
        [movement] varchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
        [plant] varchar(10) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
        [documentHeaderText] varchar(10) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
        [qaStatus] varchar(10) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
        [storageLocation] varchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
        [expiryDate] datetime NULL,
        [oldGrnNumber] varchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
        [uom] varchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
        [isCancelled] int DEFAULT 0 NULL,
        CONSTRAINT PK__GRN__1E692CB8EB118ED6 PRIMARY KEY (grnId),
        CONSTRAINT UQ__GRN__1E692CB9A94C2666 UNIQUE (grnId),
        CONSTRAINT UQ__GRN__75998F03F9837176 UNIQUE (grnNumber,grnLineNumber),
        CONSTRAINT UQ__GRN__A53913494DBC9A86 UNIQUE (grnNumber,grnLineNumber,itemCode,batchNumber)

        -- IMPORTANT RELATIONSHIPS FOR JOINING:
        -- SULOCATION.skuId joins SKUITEM.skuId
        -- SULOCATION.locationId joins LOCATION.locationId
        -- SKUITEM.itemId joins ITEM.itemId ''',

    tools=tools,   # type: ignore
)


