# DeepAgent SQL Chat

A real-time chat application that lets users ask **natural language questions** about a PostgreSQL database. Questions are processed by a **DeepAgent orchestrator**, converted to SQL by a **CodeAct Agent Tool**, executed against PostgreSQL, and results are **streamed back to the UI in real-time via SSE**.

> See [docs/PROMPT.md](./docs/PROMPT.md) to regenerate or extend this project with any AI coding assistant.  
> See [DeepAgent-SQL-Chat-Architecture.drawio](./DeepAgent-SQL-Chat-Architecture.drawio) for the full architecture diagram.

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                   UI Layer                       │
│   React + EventSource  │  FastAPI SSE Gateway    │
├─────────────────────────────────────────────────┤
│               DeepAgent Layer                    │
│   Orchestrator  │  LLM Backend  │  Agent Memory  │
├─────────────────────────────────────────────────┤
│              CodeAct Tool Layer                  │
│   SQL Builder  │  Schema Inspector  │  DB Pool   │
├─────────────────────────────────────────────────┤
│               Database Layer                     │
│   PostgreSQL Primary  │  Read Replica  │  Redis  │
└─────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| SSE Client | Native `EventSource` API |
| API Gateway | FastAPI, `sse-starlette` |
| Session Store | Redis (`redis-py` asyncio) |
| Agent Framework | `deepagents>=0.3.8` — `create_deep_agent` (supervisor + subagent graph) |
| Agent Streaming | `graph.astream_events(version="v2")` via LangGraph |
| LLM Backend | `init_chat_model("openai:gpt-4o")` via `langchain-openai` |
| Agent Tool | LangChain `@tool` async function → CodeAct SQL Tool |
| ORM / DB Driver | SQLAlchemy (asyncio), asyncpg / aiomysql / aiosqlite |
| Database | PostgreSQL 15 (Primary + Read Replica) |
| Result Cache | Redis |
| Containerization | Docker, Docker Compose, Nginx 1.27-alpine |

---

## Quick Start

### Option A — Docker (recommended)

```bash
cd deploy
cp .env.docker .env          # set LLM_API_KEY=sk-...
docker compose up --build    # builds all 4 services
```

| Service | URL |
|---|---|
| UI | http://localhost:3000 |
| API | http://localhost:8000 |
| Swagger docs | http://localhost:8000/docs |

Rebuild a single service after a code change:

```bash
docker compose up --build api
```

### Option B — Local development

**1. Bootstrap the database**

```bash
psql -U postgres -c "CREATE DATABASE chatdb;"
psql -U postgres -d chatdb -f db/postgress/00_run_all.sql
```

**2. Start Redis** (e.g. `redis-server` or Docker)

**3. Run the API**

```bash
cd api
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
cp .env.example .env           # fill in LLM_API_KEY
python main.py                 # http://localhost:8000
```

**4. Run the UI**

```bash
cd ui
npm install
npm run dev                    # http://localhost:3000
```

**Health check**

```bash
curl http://localhost:8000/api/health
# { "api": "ok", "postgres": "ok", "redis": "ok" }
```

---

## MCP Server

The API can expose an **MCP (Model Context Protocol) server** so external clients (e.g. Claude Desktop, other LLM apps) can run natural-language queries against the connected database via a single tool.

### Enabling and endpoint

- **Config:** Set `MCP_SERVER_ENABLED=true` (default). Optionally set `MCP_MOUNT_PATH=mcp` (default) so the MCP endpoint is at `/mcp`.
- **Endpoint:** When enabled, the MCP server is mounted at `http://<host>:<port>/mcp` (e.g. `http://localhost:8000/mcp`). Use the same host/port as the main API.

### Tool: `query_database`

| Parameter | Type   | Description |
|-----------|--------|-------------|
| `question` | string | Natural language question about the database (e.g. "How many users?", "Top 5 customers by revenue"). |

**Returns:** A single string: the agent’s final answer (and optional result row-count summary). The agent may generate and execute SQL under the hood; the tool returns the textual answer only.

**Example (conceptual):** An MCP client calls `query_database(question="How many orders in 2024?")` and receives a string like `"There were 1,234 orders in 2024."`.

### Connecting as an MCP client

1. Ensure the API is running and `MCP_SERVER_ENABLED` is true.
2. In your MCP client config, add a server with **URL** `http://localhost:8000/mcp` (or your API base URL + `/mcp`). Exact config format depends on the client (e.g. Claude Desktop uses a JSON config with `url` for HTTP/SSE transport).
3. No API key is required for the MCP endpoint by default. If you enable `AUTH_ENABLED` for the main API, MCP does not currently use the same JWT; consider running behind a reverse proxy or network policy for production.

### Disabling the MCP server

Set `MCP_SERVER_ENABLED=false` in the API environment so the `/mcp` mount is not registered.

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `APP_ENV` | `development` \| `production` | `development` |
| `DB_TYPE` | `postgresql` \| `mysql` \| `sqlite` | `postgresql` |
| `POSTGRES_HOST` | PostgreSQL host | `localhost` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `POSTGRES_DB` | Database name | `chatdb` |
| `POSTGRES_USER` | DB username | `postgres` |
| `POSTGRES_PASSWORD` | DB password | `postgres` |
| `REDIS_HOST` | Redis host | `localhost` |
| `REDIS_PORT` | Redis port | `6379` |
| `LLM_API_KEY` | OpenAI API key | **required** |
| `LLM_MODEL` | Model name | `gpt-4o` |
| `DEEPAGENT_MAX_ITERATIONS` | Max agent loop iterations | `10` |
| `DEEPAGENT_TIMEOUT_SECONDS` | Agent timeout | `120` |
| `MCP_SERVER_ENABLED` | Expose app as MCP server at `/mcp` | `true` |
| `MCP_MOUNT_PATH` | Path segment for MCP (e.g. `mcp` → `/mcp`) | `mcp` |

See `api/.env.example` for the complete list.

---

## SSE Event Types

Events streamed from the API back to the React UI:

```json
{ "type": "thinking",  "content": "Analyzing your question..." }
{ "type": "sql",       "content": "SELECT id, name FROM customers LIMIT 10" }
{ "type": "executing", "content": "Running query on PostgreSQL..." }
{ "type": "result",    "columns": ["id","name"], "rows": [...], "row_count": 10 }
{ "type": "token",     "content": "The top customer is Acme Corp..." }
{ "type": "done" }
```

---

## Project Structure

```
1.SQL-Query-execution-tool/
├── docs/
│   └── PROMPT.md              ← full design spec / AI regeneration prompt
├── deploy/                    ← all Docker / container files
│   ├── docker-compose.yml
│   ├── .env.docker
│   ├── api/Dockerfile
│   ├── ui/Dockerfile + nginx.conf
│   └── db/Dockerfile
├── db/
│   └── postgress/             ← 10 bootstrap SQL scripts (schema + 250+ rows)
├── api/
│   ├── main.py                ← FastAPI app factory + uvicorn entry point
│   ├── requirements.txt
│   └── src/
│       ├── config/settings.py   ← Pydantic BaseSettings
│       ├── db/adapters/         ← DatabaseAdapter ABC + PostgreSQL/MySQL/SQLite impls
│       ├── semantic/            ← SemanticLayer (LLM-ready schema context)
│       ├── cache/               ← Redis result cache + session history
│       ├── agent/               ← DeepAgent orchestrator + CodeAct tool + events
│       └── api/routes/          ← /chat, /health, /schema endpoints
└── ui/
    ├── package.json
    └── src/
        ├── api/chatApi.ts       ← initiateChat() + openEventStream()
        ├── hooks/useChat.ts     ← SSE lifecycle hook
        └── components/chat/     ← ChatWindow, AssistantMessage, SqlBlock, ResultTable
```

---

## Security

- Only `SELECT` statements permitted — all DDL/DML is blocked
- Parameterized queries only (no string interpolation into SQL)
- Session history strictly scoped to `session_id`
- CORS restricted to configured origins
- All secrets via environment variables (never hardcoded)

---

## License

MIT License
