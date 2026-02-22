# DeepAgent SQL Chat — Project Plan

> **Note:** All code and documentation in this project are written in English. Conversations with stakeholders may be in Chinese.

---

## 0. Conventions

- **Language:** All code, docstrings, comments, and documentation (README, design docs, this plan) are in **English**. Dialogue with the user may be in **Chinese**.
- **Development:** When implementing features or bugfixes, use **test-driven development (TDD)**:
  - Write a failing test first, then minimal code to pass, then refactor.
  - No production code without a test that failed first.
- **Progress:** After **each subtask** (within a phase):
  1. **Git commit** with a clear message (e.g. `feat(skills): add skill registry and config`).
  2. **Update this file** — mark the subtask done and add a row to the **Progress Log** (Section 11) with date, task id, and commit hash.

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

## 3b. Part II: Skill, MCP, and Human-in-the-Loop

This section refines and schedules the integration of **Skills** (agent tool registry + Cursor/Codex SKILL.md), **MCP** (agent calls external MCP tools + expose this app as MCP server), and **Human-in-the-loop** (approve SQL before execution). The structure follows a brainstormed design (context, approaches, consolidated plan). Implementation follows **TDD** (write failing test first, then minimal code, then refactor); after each subtask, **git commit** and **update the Progress Log** (Section 11) and mark the task done in the phase table below.

### Phase A: Skill Registry + Redis Checkpointer

**Goal:** Extensible skill registration for the agent and a persistent checkpointer for later HITL.

| Id | Task | Status | Notes |
|----|------|--------|-------|
| A.1 | Add `enabled_skills` and related config to `api/src/config/settings.py` | ✅ | TDD: test settings parsing. Commit + update plan. |
| A.2 | Create `api/src/skills/` with a skill registry (id, name, description, tools, target) | ✅ | TDD: test registry register/resolve. Commit + update plan. |
| A.3 | Implement one built-in skill (e.g. `export_result_csv`) and register it | ✅ | TDD: test skill tool behavior. Commit + update plan. |
| A.4 | Wire enabled skills into `deepagent_builder.py` (merge skill tools into supervisor) | ✅ | TDD: integration test or builder test. Commit + update plan. |
| A.5 | Add Redis checkpointer (replace or complement InMemorySaver) and config | ✅ | TDD: test checkpoint factory (memory/redis fallback). Commit + update plan. |

**Deliverable:** Agent can use configurable extra tools; graph state can persist in Redis.

---

### Phase B: Human-in-the-Loop (Approve SQL Before Execution)

**Goal:** Pause before executing SQL; user approves, rejects, or edits; then resume.

| Id | Task | Status | Notes |
|----|------|--------|-------|
| B.1 | Design interrupt point: split “plan SQL” vs “execute SQL” (or wrapper node with `interrupt()`) | ✅ | Design doc in `docs/plans/HITL_DESIGN.md`. Commit + update plan. |
| B.2 | Implement graph change (interrupt node / two-step flow) and emit `interrupt` payload in SSE | ✅ | HITL on sql-executor; INTERRUPT event in stream. TDD: test_streaming. Commit + update plan. |
| B.3 | Add `POST /api/chat/approve` (or `/resume`) with `thread_id`, `action`, optional `edited_sql` | ✅ | ApproveRequest schema; POST /approve; resume stream via same /stream. TDD: test_routes. Commit + update plan. |
| B.4 | Frontend: handle `interrupt` event, show SQL approval card, call approve API, resume stream | ✅ | SqlApprovalCard; useChat interruptPending/approveResume; ChatWindow/App wiring. Commit + update plan. |

**Deliverable:** User sees proposed SQL and can approve, reject, or edit before execution.

---

### Phase C: SKILL.md Loader + Agent Calls MCP Tools

**Goal:** Load Cursor/Codex SKILL.md into context; agent can call external MCP tools.

| Id | Task | Status | Notes |
|----|------|--------|-------|
| C.1 | Add `api/src/skills/skill_loader.py` — scan dirs for `**/SKILL.md`, parse to (path, title, content) | ✅ | SkillDoc, load_skills_from_dirs. TDD: test_skill_loader. Commit + update plan. |
| C.2 | Inject selected SKILL.md content into supervisor system prompt (config: `skill_dirs`, `skills_include`) | ✅ | _format_skills_section; builder loads skill_dirs, injects. TDD: test_deepagent_builder. Commit + update plan. |
| C.3 | Add `api/src/mcp/` client: connect to MCP server(s), fetch tools, convert to LangChain `BaseTool` | ✅ | mcp_tools_to_langchain; TDD: test_mcp_tools. Commit + update plan. |
| C.4 | Config `MCP_SERVERS`; wire MCP tools into `deepagent_builder.py` alongside skills | ✅ | mcp_servers in settings; get_mcp_tools_for_supervisor; builder merge. TDD: test_deepagent_builder + test_config. Commit + update plan. |

**Deliverable:** Agent has skill docs in prompt and can call external MCP tools.

---

### Phase D: Expose App as MCP Server

**Goal:** This app exposes a “natural language → SQL → result” tool via MCP for other clients.

| Id | Task | Status | Notes |
|----|------|--------|-------|
| D.1 | Add MCP server (e.g. FastMCP) with tool `query_database(question: str) -> str` calling `agent.run()` | ✅ | FastMCP + run_agent_and_collect; TDD: test_mcp_server. Commit + update plan. |
| D.2 | Mount MCP server on FastAPI (e.g. `/mcp` or separate port) and add config `MCP_SERVER_*` | ✅ | mcp_server_enabled, mcp_mount_path; combine_lifespans + mount. Commit + update plan. |
| D.3 | Document MCP server usage and auth (e.g. API key) in README or `deploy/README.md` | ✅ | README § MCP Server: endpoint, query_database, client connection, env vars. Commit + update plan. |

**Deliverable:** External MCP clients (e.g. Claude Desktop) can call this app to run NL→SQL queries.

---

### Part II Dependency Overview

```
Phase A (Skill registry + Redis)
  A.1 → A.2 → A.3 → A.4
  A.5 (Redis checkpointer, can parallel with A.1–A.4)

Phase B (HITL) depends on A.5 (Redis checkpointer)

Phase C (SKILL.md + MCP client) can start after A.2; C.4 may follow A.4

Phase D (MCP server) depends only on existing agent.run()
```

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

1. **Part I** — Phases 1–4 are complete (see Progress Log).
2. **Part II** — Start with **Phase A** (Section 3b): A.1 settings → A.2 skill registry → A.3 one built-in skill → A.4 wire into builder → A.5 Redis checkpointer. Use **TDD** for each subtask; after each, **git commit** and **update the Progress Log** (Section 11) and the Phase A table (mark task Done).
3. **Use this plan** — Refer to PROMPT.md for detailed specs; for Part II, follow the subtask tables and dependency overview in Section 3b.

---

## 11. Progress Log

### Part I (Phases 1–4)

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
| 2025-02-19 | 4.4: Chart UI (bar/line for numeric columns) | 43b368c |
| 2025-02-19 | 4.1: JWT authentication (API + UI login) | 5e3a770 |

### Part II (Skill, MCP, HITL)

After each subtask: git commit, then add one row below with date, task id, and commit hash. Mark the task **Done** in the Phase table (Section 3b).

| Date | Task | Commit |
|------|------|--------|
| 2026-02-19 | A.1: Settings for skills | 3d3bbbe |
| 2026-02-19 | A.2: Skill registry | 2cc569f |
| 2026-02-19 | A.3: Built-in skill (e.g. export_result_csv) | 0f7e2ff |
| 2026-02-19 | A.4: Wire skills into builder | 8fd21e5 |
| 2026-02-19 | A.5: Redis checkpointer | 18c519b |
| 2026-02-19 | B.1: HITL design doc | 16e9f2b |
| 2026-02-19 | B.2: Interrupt in graph + SSE | d6e00ec |
| 2026-02-19 | B.3: POST /api/chat/approve | 66f3c98 |
| 2026-02-19 | B.4: Frontend approval UI | 4687387 |
| 2026-02-19 | C.1: skill_loader.py | 6440fa2 |
| 2026-02-19 | C.2: Inject SKILL.md into prompt | 94a9643 |
| 2026-02-19 | C.3: MCP client + tool conversion | 7e70f7e |
| 2026-02-19 | C.4: Wire MCP tools into builder | dd3c3bd |
| 2026-02-19 | D.1–D.3: MCP server + mount + docs | 6636d95 |
