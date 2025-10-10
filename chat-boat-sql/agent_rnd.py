from google.adk.agents.llm_agent import Agent

from toolbox_core import ToolboxSyncClient

toolbox = ToolboxSyncClient("http://127.0.0.1:5000")
tools = toolbox.load_toolset('sql-toolset')

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='''You can trigger the tools to answer user questions. If you are genring SQL queries, ensure they are syntactically correct. and that 
    that is for mssql server. If the user query is ambiguous, ask a concise counter question to get more details from the user.
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
       ,''',
    tools=tools,
)
