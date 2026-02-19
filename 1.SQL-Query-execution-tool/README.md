# DeepAgent SQL Chat

A chat application that lets you ask natural language questions about your data. Queries are translated into SQL, executed against PostgreSQL (or MySQL/SQLite), and results are streamed back in real-time via SSE.

## Architecture

- **UI Layer:** React + EventSource, FastAPI API Gateway, Redis session store
- **DeepAgent Layer:** Supervisor + sql-executor subagent (LangGraph), LLM (OpenAI GPT-4o)
- **CodeAct Tool Layer:** SQL generation, Semantic Layer, DatabaseAdapter (PostgreSQL/MySQL/SQLite)
- **Database Layer:** PostgreSQL, Redis cache

See [DeepAgent-SQL-Chat-Architecture.drawio](./DeepAgent-SQL-Chat-Architecture.drawio) for the full diagram.

## Quick Start

### Option A — Docker (recommended)

```bash
cd deploy
cp .env.docker .env
# Edit .env and set LLM_API_KEY=sk-...
docker compose up --build
```

- **UI:** http://localhost:3000  
- **API docs:** http://localhost:8000/docs  

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
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set LLM_API_KEY=sk-...
python main.py
```

**4. Run the UI**

```bash
cd ui
npm install
npm run dev
```

- **UI:** http://localhost:3000  
- **API:** http://localhost:8000  

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_TYPE` | `postgresql` \| `mysql` \| `sqlite` | `postgresql` |
| `POSTGRES_*` | PostgreSQL connection | localhost:5432/chatdb |
| `REDIS_HOST`, `REDIS_PORT` | Redis connection | localhost:6379 |
| `LLM_API_KEY` | OpenAI API key | **required** |
| `LLM_MODEL` | Model name | `gpt-4o` |

See `api/.env.example` for the full list.

## Project Structure

```
1.SQL-Query-execution-tool/
├── api/           # FastAPI + DeepAgent
├── ui/            # React + Vite + Tailwind
├── db/postgress/  # PostgreSQL bootstrap scripts
├── deploy/        # Docker Compose + Dockerfiles
├── PROMPT.md      # Full design spec
└── PROJECT_PLAN.md
```

## Security

- Only `SELECT` statements are permitted
- Parameterized queries only (no string interpolation)
- Session history scoped to `session_id`
- CORS restricted to configured origins

## License

See repository root.
