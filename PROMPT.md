# 🧠 Project Prompt — DeepAgent SQL Chat Application

> Use this prompt with any AI coding assistant (GitHub Copilot, ChatGPT, Claude, Cursor)
> to regenerate, extend, or explain the full application.

---

## 🎯 Goal

Build a **Chat Application** using **DeepAgent** that allows users to ask natural language questions,
which are translated into SQL queries, executed against a **PostgreSQL database** using a
**CodeAct Agent Tool**, and the results are streamed back to the UI in real-time.

---

## 🏗️ Architecture

Design a **4-layer architecture** with the following layers:

### New Layers Added

#### Semantic Layer (`api/src/semantic/`)
Bridges the gap between raw SQL schema and LLM understanding by adding business meaning to tables and columns.

- `SemanticColumn` — display name, plain-English description, example values, sensitivity flag
- `SemanticTable` — display name, purpose description, common query examples, join hints
- `SemanticRegistry` — central store of all SemanticTable definitions; pre-seeded with 8 tables: `departments`, `employees`, `employee_info`, `suppliers`, `products`, `customers`, `orders`, `order_items`
- `SemanticLayer` — merges physical schema from any `DatabaseAdapter` with registry definitions to produce a single LLM-ready context string. Falls back to raw schema for tables with no semantic entry.

#### Database Adapter Interface (`api/src/db/adapters/`)
Abstracts all database operations behind a single `DatabaseAdapter` ABC so the rest of the application has zero database-specific code.

- `DatabaseAdapter` (abstract) — `connect()`, `disconnect()`, `ping()`, `execute_query()`, `get_tables()`, `get_columns()`, `get_foreign_keys()`, `dialect`
- `PostgreSQLAdapter` — full production implementation via SQLAlchemy + asyncpg
- `MySQLAdapter` — implementation via SQLAlchemy + aiomysql
- `SQLiteAdapter` — implementation via SQLAlchemy + aiosqlite  
- `AdapterFactory` — reads `DB_TYPE` env var and returns the correct singleton adapter

---

### Layer 1 — UI Layer

- **React** frontend with `EventSource` for SSE streaming
- Chat interface that renders:
  - `thinking` events as subtle animated status hints
  - `sql` events as syntax-highlighted code blocks
  - `executing` events as loading indicators
  - `result` events as paginated data tables
  - `token` events as flowing streamed text
  - `done` event to finalize and stop the blinking cursor
- **FastAPI** backend as API Gateway with:
  - `POST /api/chat` — accepts the user query, returns a `stream_url`
  - `GET /api/chat/stream/{stream_id}` — SSE endpoint returning `text/event-stream`
  - `EventSourceResponse` from `sse-starlette`
  - Auth middleware placeholder
- **Redis** for session management (conversation history per `session_id`)

### Layer 2 — DeepAgent Layer

- **DeepAgent Orchestrator** — built on **`deepagents.create_deep_agent`** (supervisor + subagent graph)
  - Supervisor delegates NL queries to a `sql-executor` subagent via LangGraph routing
  - `init_chat_model(model="openai:gpt-4o")` as the backbone LLM
  - `execute_sql` registered as a LangChain `@tool` (plain async function) in the sql-executor subagent
  - `graph.astream_events(version="v2")` for fine-grained event streaming:
    - `on_chat_model_stream` → `EventType.TOKEN`
    - `on_tool_start` → `EventType.TOOL_CALL` + `EventType.SQL` + `EventType.THINKING`
    - `on_tool_end` → re-emits captured `RESULT` / `ERROR` events from CodeActSQLTool
- **LLM Backend** (`langchain-openai` / `init_chat_model`) for:
  - Natural language understanding
  - SQL intent parsing via OpenAI tool-calling
  - Result summarization
  - Context-aware multi-turn conversation
- **Agent Memory** — `InMemorySaver` (LangGraph checkpointer) keyed by `thread_id`; last 10 turns persisted to Redis per `session_id`
- **Tool Registry** — LangChain `@tool`-decorated async functions passed to subagent definition

### Layer 3 — CodeAct Tool Layer

- **CodeAct Agent Tool** — generates and executes Python/SQL code dynamically
  - SQL code generation from natural language
  - Code execution engine
  - Error handling and retry
  - Result validation
- **SQL Query Builder**
  - NL → SQL translation
  - Query optimization hints
  - Parameterized queries
  - SQL injection prevention (SELECT-only enforcement)
- **Schema Inspector** — introspects PostgreSQL for context-aware generation
  - Table discovery
  - Column types
  - Foreign key relationships
  - Schema caching
- **DB Connection Pool** using `SQLAlchemy (asyncio)` + `asyncpg`
  - Connection pooling
  - Async execution
  - Transaction management
  - Timeout handling

### Layer 4 — Database Layer

- **PostgreSQL Primary** — read/write, business data tables, port 5432
  - `departments` — company departments with budget
  - `employees` — full employee roster (self-referencing manager FK, employment type, status)
  - `employee_info` — sensitive HR data (DOB, address, emergency contact, bank last 4)
  - `suppliers` — product vendors / supplier contacts
  - `products` — product catalogue with SKU, pricing, stock, reorder levels
  - `customers` — registered customers with loyalty tier (standard/silver/gold/platinum)
  - `orders` — purchase orders with full status lifecycle
  - `order_items` — line items with computed `line_total` generated column
- **PostgreSQL Read Replica** — read-only query execution, analytics
- **Redis Cache** — caches query results by SHA-256 hash of SQL, with TTL

#### Database Bootstrap Scripts (`db/postgress/`)

| File | Purpose |
|---|---|
| `00_run_all.sql` | Master script — runs all files in order + prints row counts |
| `01_schema.sql` | All `CREATE TABLE`, indexes, FK constraints, `updated_at` triggers |
| `02_insert_departments.sql` | 10 departments |
| `03_insert_employees.sql` | 42 employees (C-suite → intern, active/on-leave/terminated) |
| `04_insert_employee_info.sql` | Extended HR data for all 42 employees |
| `05_insert_suppliers.sql` | 8 suppliers (US, UK, Germany, China, Mexico) |
| `06_insert_products.sql` | 28 products across Electronics, Office, Software, Furniture, Accessories |
| `07_insert_customers.sql` | 30 customers across all loyalty tiers |
| `08_insert_orders.sql` | 30 orders covering all status states |
| `09_insert_order_items.sql` | ~65 order line items |

```bash
# Bootstrap the database
psql -U postgres -c "CREATE DATABASE chatdb;"
psql -U postgres -d chatdb -f db/postgress/00_run_all.sql
```

---

## 🔄 End-to-End Request Flow (13 Steps)

```
1.  User types a natural language query in the Chat UI
2.  React sends POST /api/chat with { query, session_id }
3.  API Gateway stores query and returns { stream_url }
4.  React opens new EventSource(stream_url)
5.  DeepAgent is invoked with query + PostgreSQL schema context
6.  DeepAgent sends query + schema to LLM → LLM reasons and plans
7.  LLM selects CodeAct SQL Tool from Tool Registry
8.  CodeAct inspects DB schema via Schema Inspector
9.  CodeAct generates a safe parameterized SQL SELECT query
10. SQL is executed via DB Connection Pool on PostgreSQL Read Replica
11. Raw results (columns + rows) returned to CodeAct Tool
12. CodeAct returns structured result to DeepAgent
13. DeepAgent/LLM formats natural language response
    → SSE stream → React EventSource updates UI in real-time
```

---

## 📡 SSE Event Types (DeepAgent → React)

```json
{ "type": "thinking",  "content": "Analyzing your question..." }
{ "type": "thinking",  "content": "Generating SQL query..." }
{ "type": "tool_call", "tool": "codeact_sql", "input": "top 10 customers by revenue" }
{ "type": "sql",       "content": "SELECT id, name, revenue FROM customers ORDER BY revenue DESC LIMIT 10" }
{ "type": "executing", "content": "Running query on PostgreSQL..." }
{ "type": "result",    "columns": ["id","name","revenue"], "rows": [...], "row_count": 10 }
{ "type": "token",     "content": "The top customer is Acme Corp with..." }
{ "type": "done" }
```

---

## 🛠️ Tech Stack

| Layer            | Technology                                                     |
|------------------|----------------------------------------------------------------|
| Frontend         | React 18, TypeScript, Vite, Tailwind CSS                       |
| SSE Client       | Native `EventSource` API                                       |
| API Gateway      | FastAPI, `sse-starlette`                                       |
| Session Store    | Redis (`redis-py` asyncio)                                     |
| Agent Framework  | `deepagents>=0.3.8` — `create_deep_agent` (supervisor + subagent graph) |
| Agent Streaming  | `graph.astream_events(version="v2")` via LangGraph              |
| LLM Backend      | `init_chat_model("openai:gpt-4o")` via `langchain-openai`       |
| Agent Tool       | LangChain `@tool` async function → CodeAct SQL Tool             |
| LangChain Pkgs   | `deepagents>=0.3.8`, `langchain>=0.2`, `langgraph>=0.2`         |
| ORM / DB Driver  | SQLAlchemy (asyncio), asyncpg / aiomysql / aiosqlite           |
| Database         | PostgreSQL 15 (Primary + Read Replica)                         |
| Result Cache     | Redis                                                          |
| Containerization | Docker, Docker Compose, Nginx 1.27-alpine                      |

---

## 📁 Required Directory Structure

```
1.SQL-Query-execution-tool/
├── README.md
├── PROMPT.md
├── DeepAgent-SQL-Chat-Architecture.drawio
│
├── deploy/                              ← all Docker / container files
│   ├── docker-compose.yml               ← run `docker compose up --build` from here
│   ├── .env.docker                      ← env template for Docker (copy to .env)
│   ├── api/
│   │   ├── Dockerfile                   ← 2-stage Python 3.12-slim build
│   │   └── Dockerfile.dockerignore      ← per-service build context filter
│   ├── ui/
│   │   ├── Dockerfile                   ← 2-stage Node 20 → Nginx 1.27-alpine
│   │   ├── nginx.conf                   ← SPA routing + SSE proxy + asset caching
│   │   └── Dockerfile.dockerignore
│   └── db/
│       └── Dockerfile                   ← postgres:15-alpine + seed scripts
│
├── db/
│   └── postgress/
│       ├── 00_run_all.sql               ← master bootstrap script
│       ├── 01_schema.sql                ← DDL: tables, indexes, triggers
│       ├── 02_insert_departments.sql
│       ├── 03_insert_employees.sql
│       ├── 04_insert_employee_info.sql
│       ├── 05_insert_suppliers.sql
│       ├── 06_insert_products.sql
│       ├── 07_insert_customers.sql
│       ├── 08_insert_orders.sql
│       └── 09_insert_order_items.sql
│
├── api/
│   ├── main.py                          ← FastAPI app factory + CORS + uvicorn entry point
│   ├── requirements.txt                 ← pip dependencies
│   ├── .env.example                     ← environment variable template
│   └── src/
│       ├── config/
│       │   └── settings.py              ← Pydantic BaseSettings
│       ├── db/
│       │   ├── adapters/
│       │   │   ├── base.py               ← DatabaseAdapter ABC (interface)
│       │   │   ├── postgres.py           ← PostgreSQL implementation
│       │   │   ├── mysql.py              ← MySQL implementation
│       │   │   ├── sqlite.py             ← SQLite implementation
│       │   │   └── factory.py            ← get_adapter() factory (reads DB_TYPE)
│       ├── semantic/
│       │   ├── models.py                 ← SemanticColumn, SemanticTable models
│       │   ├── registry.py               ← SemanticRegistry + default seed data
│       │   └── layer.py                  ← SemanticLayer (merges schema + semantics)
│       ├── cache/
│       │   └── redis_client.py          ← result cache + session history
│       ├── agent/
│       │   ├── events.py                ← AgentEvent Pydantic models + EventType enum
│       │   ├── codeact_tool.py          ← CodeAct SQL Tool (yields AgentEvent stream)
│       │   └── deep_agent.py            ← DeepAgent orchestrator (LLM + tool loop)
│       └── api/
│           ├── schemas.py               ← ChatRequest / ChatInitResponse
│           └── routes/
│               ├── chat.py              ← POST /chat + GET /chat/stream/{id}
│               ├── health.py             ← GET /health (db adapter + redis check)
│               └── schema.py             ← GET /schema, GET /schema/{table}
│
└── ui/
    ├── index.html
    ├── package.json                     ← vite + react + tailwind + react-syntax-highlighter
    ├── vite.config.ts                   ← proxy /api → localhost:8000
    └── src/
        ├── main.tsx                     ← ReactDOM.createRoot
        ├── App.tsx                      ← root layout (header + ChatWindow + ChatInput)
        ├── index.css                    ← Tailwind directives
        ├── types/
        │   └── agent.ts                 ← AgentEvent + Message TypeScript types
        ├── api/
        │   └── chatApi.ts               ← initiateChat() + openEventStream()
        ├── hooks/
        │   └── useChat.ts               ← useChat() hook (state + SSE lifecycle)
        └── components/
            └── chat/
                ├── ChatWindow.tsx       ← scrollable message list
                ├── ChatInput.tsx        ← textarea + send button (Enter to send)
                ├── AssistantMessage.tsx ← renders all AgentEvent types
                ├── ThinkingIndicator.tsx← animated bounce dots
                ├── SqlBlock.tsx         ← Prism syntax highlighted SQL block
                └── ResultTable.tsx      ← scrollable table with column headers
```

---

## 🔒 Security Requirements

- Only `SELECT` statements permitted — block all DDL/DML in `QueryExecutor`
- Parameterized queries only — no string interpolation into SQL
- Session history scoped strictly to `session_id`
- CORS restricted to configured origins
- Environment variables for all secrets (never hardcode)

---

## ⚙️ Environment Variables

```env
# Application
APP_ENV=development

# Database type — postgresql | mysql | sqlite
DB_TYPE=postgresql
APP_HOST=0.0.0.0
APP_PORT=8000
CORS_ORIGINS=http://localhost:3000

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=chatdb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_POOL_SIZE=10
POSTGRES_MAX_OVERFLOW=20

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_TTL_SECONDS=3600

# LLM
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
LLM_API_KEY=your_api_key_here
LLM_MAX_TOKENS=4096
LLM_TEMPERATURE=0.0

# DeepAgent
DEEPAGENT_MAX_ITERATIONS=10
DEEPAGENT_TIMEOUT_SECONDS=120
```

---

## 🚀 Run Instructions

### Option A — Docker (recommended)

```bash
cd deploy
cp .env.docker .env          # then set LLM_API_KEY=sk-...
docker compose up --build    # builds all 4 services

# Access:
#   UI  → http://localhost:3000
#   API → http://localhost:8000/docs  (Swagger)

# Rebuild a single service after code change:
docker compose up --build api
```

### Option B — Local (manual)

```bash
# API
cd api
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate    # macOS / Linux
pip install -r requirements.txt
cp .env.example .env
python main.py                  # → http://localhost:8000
                                # → http://localhost:8000/docs (Swagger)

# UI
cd ui
npm install
npm run dev                     # → http://localhost:3000

# Health check
curl http://localhost:8000/api/health
# Expected: { "api": "ok", "postgres": "ok", "redis": "ok" }
```

---

## 💡 Extension Prompts

Use these follow-up prompts to extend the project:

| Goal | Prompt to use |
|---|---|
| Add Docker support | ✅ Done — see `deploy/` folder. Run: `cd deploy && cp .env.docker .env && docker compose up --build` |
| Add authentication | "Based on this PROMPT.md, add JWT authentication to the FastAPI API" |
| Add CSV export | "Based on this PROMPT.md, add a Download CSV button to ResultTable" |
| Add tests | "Based on this PROMPT.md, create pytest tests for the CodeAct tool and query executor" |
| Seed more tables | "Based on this PROMPT.md, add a `projects` and `timesheets` table to the DB scripts and semantic registry" |
| Add MySQL scripts | "Based on this PROMPT.md, create equivalent MySQL-compatible versions of the db/postgress/ scripts" |
| Add chart UI | "Based on this PROMPT.md, add a bar/line chart component that renders when the result set has numeric columns" |
| Add schema browser | "Based on this PROMPT.md, add a sidebar component to the UI showing all PostgreSQL tables and columns" |
| Multi-database support | "Based on this PROMPT.md, extend the architecture to support both PostgreSQL and MySQL" |
