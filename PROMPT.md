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

- **DeepAgent Orchestrator** manages the full agent lifecycle
- **LLM Backend** (OpenAI GPT-4o / Claude) for:
  - Natural language understanding
  - SQL intent parsing
  - Result summarization
  - Context-aware multi-turn conversation
- **Agent Memory** — short-term memory via Redis (last 10 conversation turns)
- **Tool Registry** — registers and routes tool calls to CodeAct SQL Tool

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
- **PostgreSQL Read Replica** — read-only query execution, analytics
- **Redis Cache** — caches query results by SHA-256 hash of SQL, with TTL

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

| Layer            | Technology                                      |
|------------------|-------------------------------------------------|
| Frontend         | React 18, TypeScript, Vite, Tailwind CSS        |
| SSE Client       | Native `EventSource` API                        |
| API Gateway      | FastAPI, `sse-starlette`                        |
| Session Store    | Redis (`redis-py` asyncio)                      |
| Agent Framework  | DeepAgent                                       |
| LLM Backend      | OpenAI GPT-4o / Anthropic Claude                |
| Agent Tool       | CodeAct Agent Tool                              |
| ORM / DB Driver  | SQLAlchemy (asyncio), asyncpg                   |
| Database         | PostgreSQL 15 (Primary + Read Replica)          |
| Result Cache     | Redis                                           |

---

## 📁 Required Directory Structure

```
1.SQL-Query-execution-tool/
├── README.md
├── PROMPT.md
├── DeepAgent-SQL-Chat-Architecture.drawio
│
├── api/
│   ├── main.py                          ← uvicorn entry point
│   ├── pyproject.toml                   ← poetry dependencies
│   ├── .env.example                     ← environment variable template
│   └── src/
│       ├── main.py                      ← FastAPI app factory + CORS
│       ├── config/
│       │   └── settings.py              ← Pydantic BaseSettings
│       ├── db/
│       │   ├── engine.py                ← async SQLAlchemy engine + session
│       │   ├── schema_inspector.py      ← PostgreSQL schema introspection
│       │   └── query_executor.py        ← safe SELECT-only executor
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
│               └── health.py            ← GET /health (postgres + redis check)
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

```bash
# API
cd api
poetry install
cp .env.example .env
poetry run python main.py       # → http://localhost:8000
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
| Add Docker support | "Based on this PROMPT.md, create a `docker-compose.yml` for the full stack" |
| Add authentication | "Based on this PROMPT.md, add JWT authentication to the FastAPI API" |
| Add CSV export | "Based on this PROMPT.md, add a Download CSV button to ResultTable" |
| Add tests | "Based on this PROMPT.md, create pytest tests for the CodeAct tool and query executor" |
| Add schema browser | "Based on this PROMPT.md, add a sidebar component to the UI showing all PostgreSQL tables and columns" |
| Multi-database support | "Based on this PROMPT.md, extend the architecture to support both PostgreSQL and MySQL" |
