# Mobillor AI Agents

A multi-agent AI platform built by **Mobillor Technologies** for warehouse management, pharmaceutical analytics, machine process monitoring, demand forecasting, and document OCR. The system uses Google's Agent Development Kit (ADK) with Gemini models, a RAG (Retrieval Augmented Generation) pipeline backed by ChromaDB, and MCP Toolbox for safe SQL execution against an MSSQL database.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        User Interface                            │
│              (Streamlit Web App / API Proxy)                     │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Root Agent (Router)                         │
│               Google ADK - Gemini 2.5 Flash Lite                │
│         Classifies intent → delegates to sub-agents             │
└────┬──────────┬──────────┬──────────┬──────────┬────────────────┘
     │          │          │          │          │
     ▼          ▼          ▼          ▼          ▼
┌─────────┐┌─────────┐┌─────────┐┌─────────┐┌─────────┐
│Warehouse││ Pharma  ││ Machine ││ Demand  ││  OCR    │
│ Agent   ││ Agent   ││ Agent   ││ Agent   ││ Agent   │
└────┬────┘└────┬────┘└────┬────┘└────┬────┘└────┬────┘
     │          │          │          │          │
     ▼          ▼          ▼          ▼          ▼
┌──────────────────────────────────────────┐  ┌──────────┐
│          RAG Service (ChromaDB)          │  │  Gemini  │
│   Knowledge Retrieval + Embeddings       │  │  Vision  │
└────────────────────┬─────────────────────┘  └──────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│                MCP Toolbox (SQL Execution)                       │
│        Safe, read-only SQL against MSSQL Server                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Workflow

1. **User** sends a query via the Streamlit web app or the FastAPI proxy endpoint.
2. **Root Agent** (Gemini 2.5 Flash Lite) analyzes intent and routes the query to the appropriate domain-specific sub-agent.
3. **Sub-Agent** (Gemini 2.5 Flash) calls the RAG service to retrieve relevant schema/knowledge context, then generates a safe SELECT-only SQL query.
4. **MCP Toolbox** validates and executes the SQL query against the MSSQL database.
5. **Response** flows back through the agent chain and is presented to the user in a structured format.
6. **Token Tracking** runs in the background, recording API usage (prompt/completion tokens) per user and session.

---

## Project Structure

```
mobillor-ai-agents/
├── api-proxy/              # FastAPI proxy layer & session management
├── apps/                   # Streamlit web UI
├── archi_flow/             # Architecture flow agents (warehouse-only)
├── chat_boat_sql/          # SQL chatbot with RAG integration
├── demo_agents/            # Multi-domain demo agents (pharma, machine, demand)
├── ocr_agent/              # Document OCR pipeline
├── rag_service/            # RAG knowledge retrieval service
├── knowledge/              # Knowledge base (DB schema markdown)
├── mcp-toolbox/            # MCP Toolbox configuration (tools.yaml)
├── embedding_service.py    # Standalone embedding microservice
├── clear_pycache.py        # Cache cleanup utility
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables
```

---

## Modules

### `api-proxy/` — FastAPI Proxy Layer

| File                   | Purpose                                                                                                                 |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `main.py`              | Main FastAPI app. Proxies requests to the remote ADK backend and manages session lifecycle (create, list, get, delete). |
| `run_api.py`           | Handles`/dev/proxy/run` — forwards user messages to ADK, tracks token usage in background.                              |
| `db.py`                | MSSQL connection (pyodbc). Provides`upsert_token_usage()` for tracking API token consumption per user/session.          |
| `create_session.py`    | Creates a new session for a user and app.                                                                               |
| `get_session.py`       | Retrieves an existing session.                                                                                          |
| `list_session.py`      | Lists all sessions for a user and app.                                                                                  |
| `delete_session.py`    | Deletes a specific session.                                                                                             |
| `deleteAll_session.py` | Deletes all sessions for a user and app.                                                                                |

### `apps/` — Web Interface

| File           | Purpose                                                                                                                                                |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `web_agent.py` | Streamlit chat interface. Auto-creates sessions, displays chat history, sends messages to the local ADK server, and renders SQL results as DataFrames. |

### `archi_flow/` — Architecture Flow Agents

| File          | Purpose                                                                                             |
| ------------- | --------------------------------------------------------------------------------------------------- |
| `agent.py`    | Root router agent that classifies intent and delegates warehouse/ERP queries.                       |
| `wh_agent.py` | Warehouse SQL generator agent with full WMS schema embedded. Generates read-only MSSQL queries.     |
| `tool_box.py` | FastAPI endpoint (`/execute-query`) that validates SQL is SELECT-only and executes via MCP Toolbox. |

### `chat_boat_sql/` — SQL Chatbot with RAG

| File                 | Purpose                                                                                                      |
| -------------------- | ------------------------------------------------------------------------------------------------------------ |
| `agent.py`           | Root router agent that delegates warehouse queries to the warehouse agent.                                   |
| `warehouse_agent.py` | SQL expert agent that always calls RAG before generating SQL. Uses MCP Toolbox for execution.                |
| `analytics_agent.py` | Advanced analytics agent for stock analysis, demand forecasting, picklist efficiency, and material planning. |

### `demo_agents/` — Multi-Domain Demo

| File               | Purpose                                                                                    |
| ------------------ | ------------------------------------------------------------------------------------------ |
| `agent.py`         | Root router that delegates to domain sub-agents based on intent keywords.                  |
| `pharma_agent.py`  | Pharmaceutical sales analytics — primary/secondary sales, scheme analysis, product trends. |
| `machine_agent.py` | Process monitoring — queries Airflow, FanSpeed, Temperature, Weight data.                  |
| `berger_agent.py`  | Demand analytics — item/location demand forecasting.                                       |

### `ocr_agent/` — Document OCR Pipeline

| File                                 | Purpose                                                                                                           |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| `agent.py`                           | Gemini-based OCR agent for text extraction from images.                                                           |
| `process_document.py`                | Full pipeline orchestrator: OCR → field extraction → table reconstruction → LLM structuring → merged JSON output. |
| `structure_document.py`              | Uses Gemini 2.5 Pro to convert raw OCR text into structured JSON.                                                 |
| `parse_table.py`                     | Parses HTML tables (BeautifulSoup) into JSON.                                                                     |
| `extraction/extract_fields.py`       | Regex-based field extraction from OCR text.                                                                       |
| `extraction/layout_reconstructor.py` | Reconstructs document layout from bounding boxes.                                                                 |
| `parsing/markdown_table_parser.py`   | Parses markdown-formatted tables from OCR output.                                                                 |

### `rag_service/` — RAG Knowledge Service

| File               | Purpose                                                                                                                            |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------- |
| `main.py`          | FastAPI endpoint (`POST /retrieve`) — accepts a query and returns relevant knowledge chunks.                                       |
| `embedding.py`     | Text embeddings using`sentence-transformers/all-MiniLM-L6-v2`.                                                                     |
| `ingest.py`        | Reads markdown from`knowledge/`, smart-chunks by headers, extracts metadata, embeds, and stores in ChromaDB.                       |
| `retriever.py`     | Smart retrieval — resolves intent to tables, metadata-filtered vector search, classifies docs by type, assembles balanced context. |
| `rag_tool.py`      | HTTP client that calls the RAG service and formats retrieved knowledge for agent use.                                              |
| `vectorr_store.py` | ChromaDB collection setup and management.                                                                                          |

### `mcp-toolbox/` — SQL Execution Layer

| File         | Purpose                                                                                                                                               |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tools.yaml` | Defines MSSQL data source and tools:`search-items` (parameterized item search) and `execute-sql` (dynamic query execution). Bundled as `sql-toolset`. |

---

## Tech Stack

| Component     | Technology                                              |
| ------------- | ------------------------------------------------------- |
| AI Framework  | Google ADK (Agent Development Kit)                      |
| LLM Models    | Gemini 2.5 Flash, Gemini 2.5 Flash Lite, Gemini 2.5 Pro |
| API Layer     | FastAPI + Uvicorn                                       |
| Web UI        | Streamlit                                               |
| Vector Store  | ChromaDB                                                |
| Embeddings    | sentence-transformers (all-MiniLM-L6-v2)                |
| SQL Execution | MCP Toolbox                                             |
| Database      | Microsoft SQL Server                                    |
| DB Driver     | pyodbc                                                  |
| HTTP Client   | httpx                                                   |

---

## Getting Started

### Prerequisites

- Python 3.10+
- ODBC Driver 17 for SQL Server
- Access to Google Cloud (for Gemini models)
- MSSQL Server instance

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd mobillor-ai-agents

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. Create a `.env` file with the required environment variables (Google Cloud credentials, database connection strings, etc.).
2. Start the MCP Toolbox server (serves on port 8001):

   ```bash
   cd mcp-toolbox
   ./toolbox.exe  # or appropriate binary for your OS
   ```

3. Ingest knowledge into ChromaDB:

   ```bash
   cd rag_service
   python ingest.py
   ```

### Running Services

```bash
# Start the RAG service (port 9000)
uvicorn rag_service.main:app --port 9000

# Start the API proxy (port 8000)
uvicorn api-proxy.main:app --port 8000

# Start the Streamlit web app
streamlit run apps/web_agent.py

# (Optional) Start the embedding microservice
uvicorn embedding_service:app --port 8002
```

---

## Key Design Decisions

- **Multi-agent routing**: A lightweight root agent (Flash Lite) handles classification cheaply, delegating complex SQL generation to more capable models (Flash/Pro).
- **RAG-first SQL generation**: Agents must retrieve schema knowledge from ChromaDB before generating any SQL, preventing hallucinated table/column names.
- **Read-only safety**: All SQL execution is restricted to SELECT queries. Forbidden keywords (DROP, DELETE, UPDATE, INSERT, ALTER, TRUNCATE) are blocked at multiple layers.
- **Token tracking**: Background task records per-session token consumption for cost monitoring.
- **Modular agents**: Each domain (warehouse, pharma, machine, demand, OCR) is an independent module that can be swapped in/out of the root agent.

---

## License

Proprietary — Mobillor Technologies

python -m uvicorn api-proxy.main:app --port 8000 --reload
