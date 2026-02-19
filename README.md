# 🌐 Public AI Projects

A collection of AI-powered applications and tools built with modern agent frameworks, LLMs, and real-time streaming architectures.

---

## 📦 Projects

### 1. [DeepAgent SQL Chat](./1.SQL-Query-execution-tool/)

A real-time chat application that lets users ask **natural language questions** about a PostgreSQL database. Questions are processed by a **DeepAgent orchestrator**, converted to SQL by a **CodeAct Agent Tool**, executed against PostgreSQL, and results are **streamed back to the UI in real-time via SSE**.

#### Architecture

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

#### Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| SSE Client | Native `EventSource` API |
| API Gateway | FastAPI, `sse-starlette` |
| Session Store | Redis |
| Agent Framework | DeepAgent |
| LLM Backend | OpenAI GPT-4o / Claude |
| Agent Tool | CodeAct Agent Tool |
| ORM / DB Driver | SQLAlchemy (async), asyncpg |
| Database | PostgreSQL (Primary + Read Replica) |
| Result Cache | Redis |

#### Quick Start

```bash
# API
cd 1.SQL-Query-execution-tool/api
poetry install
cp .env.example .env   # fill in your values
poetry run python main.py  # http://localhost:8000

# UI
cd 1.SQL-Query-execution-tool/ui
npm install
npm run dev            # http://localhost:3000
```

> See [full documentation](./1.SQL-Query-execution-tool/README.md) for detailed setup, API reference, and configuration.
> See [PROMPT.md](./PROMPT.md) to regenerate or extend this project with any AI assistant.

---

## 🗺️ Roadmap

- [x] DeepAgent SQL Chat with SSE streaming
- [ ] DeepAgent Document Q&A
- [ ] Multi-agent workflow builder
- [ ] AI-powered data visualisation

---

## 📄 License

MIT License
