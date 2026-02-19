# DeepAgent SQL Chat — Project Plan

> **Note:** All code and documentation in this project are written in English. Conversations with stakeholders may be in Chinese.

---

## 1. Executive Summary

### Goal

Build a **Chat Application** using **DeepAgent** that allows users to ask natural language questions, which are translated into SQL queries, executed against a PostgreSQL database via a CodeAct Agent Tool, with results streamed back to the UI in real-time via SSE.

### Architecture Overview (4 Layers)

| Layer | Components | Status |
|-------|-------------|--------|
| **UI Layer** | React + EventSource, FastAPI API Gateway, Redis Session | ⚠️ Partial |
| **DeepAgent Layer** | Orchestrator, LLM Backend, Agent Memory, Tool Registry | ✅ Done |
| **CodeAct Tool Layer** | CodeAct Agent, SQL Query Builder, Semantic Layer, DatabaseAdapter | ✅ Done |
| **Database Layer** | PostgreSQL, Redis Cache, Bootstrap Scripts | ✅ Done |

### Tech Stack

- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, EventSource
- **Backend:** FastAPI, sse-starlette, Redis
- **Agent:** deepagents, LangChain, LangGraph
- **Database:** PostgreSQL 15, SQLAlchemy (asyncpg/aiomysql/aiosqlite)
- **Deploy:** Docker, Docker Compose, Nginx

---

## 2. Current Status

### ✅ Completed

| Component | Path | Notes |
|-----------|------|-------|
| API entry point | `api/main.py` | FastAPI app, CORS, lifespan |
| Config | `api/src/config/settings.py` | Pydantic BaseSettings |
| Database adapters | `api/src/db/adapters/` | base, postgres, mysql, sqlite, factory |
| Semantic layer | `api/src/semantic/` | models, registry, layer |
| Redis cache | `api/src/cache/redis_client.py` | Result cache + session history |
| Agent core | `api/src/agent/` | events, codeact_tool, deep_agent |
| API routes | `api/src/api/routes/` | chat, health, schema |
| Schemas | `api/src/api/schemas.py` | ChatRequest, ChatInitResponse |
| DB bootstrap | `db/postgress/` | 00–09 SQL scripts |
| Docker deploy | `deploy/` | docker-compose, Dockerfiles, nginx |

### ❌ Missing / Incomplete

| Component | Path | Priority |
|-----------|------|----------|
| **React UI** | `ui/` | **P0** — Done (Phase 1 complete) |
| `.env.example` | `api/.env.example` | P1 |
| `README.md` | `1.SQL-Query-execution-tool/README.md` | P1 |
| Unit tests | `api/tests/` | P2 |
| E2E tests | `ui/` or `tests/` | P3 |

---

## 3. Phased Implementation Plan

### Phase 1: UI Foundation (P0)

**Goal:** Build the React frontend so users can interact with the chat API.

**Dependencies:** API is already running (POST /api/chat, GET /api/chat/stream/{id}).

| Task | Description | Files |
|------|-------------|-------|
| 1.1 | Scaffold Vite + React + TypeScript project | `ui/package.json`, `ui/vite.config.ts`, `ui/index.html`, `ui/tsconfig.json` |
| 1.2 | Add Tailwind CSS | `ui/package.json`, `ui/tailwind.config.js`, `ui/postcss.config.js`, `ui/index.css` |
| 1.3 | Define AgentEvent types | `ui/src/types/agent.ts` |
| 1.4 | Implement chat API client | `ui/src/api/chatApi.ts` — `initiateChat()`, `openEventStream()` |
| 1.5 | Implement useChat hook | `ui/src/hooks/useChat.ts` — state, SSE lifecycle, error handling |
| 1.6 | Build ChatWindow component | `ui/src/components/chat/ChatWindow.tsx` |
| 1.7 | Build ChatInput component | `ui/src/components/chat/ChatInput.tsx` |
| 1.8 | Build AssistantMessage component | `ui/src/components/chat/AssistantMessage.tsx` |
| 1.9 | Build ThinkingIndicator | `ui/src/components/chat/ThinkingIndicator.tsx` |
| 1.10 | Build SqlBlock (syntax highlight) | `ui/src/components/chat/SqlBlock.tsx` — react-syntax-highlighter |
| 1.11 | Build ResultTable | `ui/src/components/chat/ResultTable.tsx` |
| 1.12 | Assemble App layout | `ui/src/App.tsx`, `ui/src/main.tsx` |
| 1.13 | Configure Vite proxy | `ui/vite.config.ts` — proxy /api → localhost:8000 |

**Deliverable:** End-to-end flow: User types query → EventSource receives SSE → UI renders thinking/sql/result/token/done.

---

### Phase 2: Configuration & Documentation (P1)

**Goal:** Make the project easy to run and understand.

| Task | Description | Files |
|------|-------------|-------|
| 2.1 | Add `.env.example` | `api/.env.example` — all env vars with placeholders |
| 2.2 | Write README | `README.md` — goal, architecture, run instructions (Docker + local), env vars |

---

### Phase 3: Testing (P2)

**Goal:** Add regression safety and confidence for future changes.

| Task | Description | Files |
|------|-------------|-------|
| 3.1 | Pytest setup | `api/pytest.ini`, `api/conftest.py` |
| 3.2 | Test CodeAct tool | `api/tests/test_codeact_tool.py` — SELECT-only, cache, error handling |
| 3.3 | Test DatabaseAdapter | `api/tests/test_db_adapters.py` — execute_query, get_tables |
| 3.4 | Test SemanticLayer | `api/tests/test_semantic_layer.py` |
| 3.5 | Test API routes | `api/tests/test_routes.py` — health, chat init |

---

### Phase 4: Polish & Extensions (P3)

**Goal:** Optional enhancements from PROMPT.md extension prompts.

| Task | Description | Notes |
|------|-------------|-------|
| 4.1 | JWT authentication | Auth middleware for API |
| 4.2 | CSV export | Download button in ResultTable |
| 4.3 | Schema browser | Sidebar showing tables/columns |
| 4.4 | Chart UI | Bar/line chart when result has numeric columns |

---

## 4. Task Dependency Graph

```
Phase 1 (UI)
├── 1.1 Scaffold → 1.2 Tailwind → 1.3 Types → 1.4 API client → 1.5 useChat
│                                                                    │
│   ┌────────────────────────────────────────────────────────────────┘
│   │
│   ├── 1.6 ChatWindow
│   ├── 1.7 ChatInput
│   ├── 1.8 AssistantMessage
│   │   ├── 1.9 ThinkingIndicator
│   │   ├── 1.10 SqlBlock
│   │   └── 1.11 ResultTable
│   └── 1.12 App + 1.13 Vite proxy

Phase 2 (Config & Docs)
└── 2.1 .env.example, 2.2 README (no dependencies)

Phase 3 (Tests)
└── 3.1–3.5 (can run in parallel after Phase 1)
```

---

## 5. Suggested Execution Order

**Week 1:** Phase 1 (UI Foundation) — full E2E chat flow  
**Week 2:** Phase 2 (Config & Docs) + Phase 3 (Tests)  
**Week 3+:** Phase 4 (optional extensions)

---

## 6. Directory Structure (Target)

```
1.SQL-Query-execution-tool/
├── README.md
├── PROMPT.md
├── PROJECT_PLAN.md
├── DeepAgent-SQL-Chat-Architecture.drawio
│
├── deploy/
│   ├── docker-compose.yml
│   ├── .env.docker
│   ├── api/Dockerfile
│   ├── ui/Dockerfile, nginx.conf
│   └── db/Dockerfile
│
├── db/postgress/
│   └── 00_run_all.sql … 09_insert_order_items.sql
│
├── api/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example          ← ADD
│   ├── pytest.ini            ← ADD (Phase 3)
│   ├── conftest.py           ← ADD (Phase 3)
│   ├── tests/                ← ADD (Phase 3)
│   └── src/
│       ├── config/
│       ├── db/adapters/
│       ├── semantic/
│       ├── cache/
│       ├── agent/
│       └── api/
│
└── ui/                       ← ADD (Phase 1)
    ├── index.html
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    ├── tsconfig.json
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── index.css
        ├── types/agent.ts
        ├── api/chatApi.ts
        ├── hooks/useChat.ts
        └── components/chat/
            ├── ChatWindow.tsx
            ├── ChatInput.tsx
            ├── AssistantMessage.tsx
            ├── ThinkingIndicator.tsx
            ├── SqlBlock.tsx
            └── ResultTable.tsx
```

---

## 7. Run Instructions (Quick Reference)

### Local (after Phase 1)

```bash
# API
cd api && python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # set LLM_API_KEY
python main.py

# UI
cd ui && npm install && npm run dev
# → http://localhost:3000
```

### Docker

```bash
cd deploy
cp .env.docker .env
docker compose up --build
# UI: http://localhost:3000, API: http://localhost:8000/docs
```

---

## 8. SSE Event Types (Reference)

| type | Payload | UI Behavior |
|------|---------|-------------|
| `thinking` | `content` | Animated bounce dots |
| `tool_call` | `tool`, `input` | Log / subtle hint |
| `sql` | `content` | Syntax-highlighted code block |
| `executing` | `content` | Loading indicator |
| `result` | `columns`, `rows`, `row_count` | Paginated table |
| `token` | `content` | Append to streamed text |
| `done` | — | Stop cursor, finalize |
| `error` | `content` | Error message |

---

## 9. Security Checklist

- [x] SELECT-only enforcement in QueryExecutor
- [x] Parameterized queries (no string interpolation)
- [x] Session history scoped to `session_id`
- [x] CORS restricted to configured origins
- [x] Secrets via environment variables

---

## 10. Next Steps

1. **Start Phase 1** — Create `ui/` folder and scaffold React app (Task 1.1).
2. **Verify API** — Ensure `curl http://localhost:8000/api/health` returns `{"api":"ok","postgres":"ok","redis":"ok"}` before starting UI.
3. **Use this plan** — Mark tasks complete as you go; refer to PROMPT.md for detailed specs.

---

## 11. Progress Log

| Date | Task | Commit |
|------|------|--------|
| 2025-02-19 | 1.1 + 1.2: Scaffold Vite+React+TS, Tailwind, Vite proxy | d5e5819 |
| 2025-02-19 | 1.3: AgentEvent types | 93364af |
| 2025-02-19 | 1.4: Chat API client | ef8ee54 |
| 2025-02-19 | 1.5: useChat hook | 7e1c0c8 |
| 2025-02-19 | 1.6–1.12: Chat components + App layout | 3474cc7 |
| 2025-02-19 | 2.1: .env.example | 8980755 |
| 2025-02-19 | 2.2: README.md | 799352e |
| 2025-02-19 | 3.1–3.5: Pytest setup + tests (CodeAct, DB adapter, SemanticLayer, routes) | 7801a86 |
| 2025-02-19 | 4.2: CSV export on ResultTable | b8f5aba |
| 2025-02-19 | 4.3: Schema browser sidebar | 516e2bb |
