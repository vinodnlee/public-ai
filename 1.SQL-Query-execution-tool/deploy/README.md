# Local Deploy

This guide runs **DeepAgent SQL Chat** on your machine: PostgreSQL and Redis via Docker, API and UI on the host.

---

## Prerequisites

| Requirement | Description |
|-------------|-------------|
| **Docker Desktop** | For PostgreSQL and Redis (start Docker Desktop before running compose) |
| **Python 3.11+** | For the API (3.11 or 3.12 recommended; 3.13 requires compatible [requirements](../../api/requirements.txt)) |
| **Node.js 18+** | For the frontend (`npm install` / `npm run dev`) |

---

## 1. Start database and Redis

From the **project root** or the **deploy** directory:

```bash
# From project root
cd 1.SQL-Query-execution-tool/deploy
docker compose -f docker-compose.local.yml up -d

# Or from deploy directory
cd deploy
docker compose -f docker-compose.local.yml up -d
```

- **PostgreSQL**: port `5432`, database `chatdb`, user/password `postgres`/`postgres`
- **Redis**: port `6379`

Check status:

```bash
docker compose -f docker-compose.local.yml ps
```

Stop:

```bash
docker compose -f docker-compose.local.yml down
```

---

## 2. Configure API environment

```bash
cd api
cp .env.example .env
```

Edit `api/.env`. At minimum set:

| Variable | Description | Local example |
|----------|-------------|---------------|
| `POSTGRES_HOST` | Database host | `localhost` |
| `POSTGRES_PORT` | Database port | `5432` |
| `POSTGRES_DB` | Database name | `chatdb` |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` | Credentials | `postgres` / `postgres` |
| `REDIS_HOST` | Redis host | `localhost` |
| `LLM_API_KEY` | OpenAI or DashScope API key | **required** |
| `LLM_MODEL` | Model name | `gpt-4o` or `qwen-plus` |

For **Qwen (DashScope)** add:

```env
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-plus
LLM_API_KEY=sk-...your_dashscope_key...
```

Optional: disable auth for local debugging:

```env
AUTH_ENABLED=false
```

---

## 3. Run the API

```bash
cd api
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

You should see:

- `Uvicorn running on http://0.0.0.0:8000`
- `Application startup complete.`

- **API docs**: http://localhost:8000/docs  
- **Health check**: http://localhost:8000/api/health  

---

## 4. Run the frontend

In a new terminal:

```bash
cd ui
npm install
npm run dev
```

Open **http://localhost:3000** in your browser.

The UI calls the API at `http://localhost:8000`; ensure the API is running from step 3.

---

## 5. Verification

1. **Containers**: `docker compose -f deploy/docker-compose.local.yml ps` shows `db` and `redis` as `running`.
2. **API**: Open http://localhost:8000/api/health — `api`, `database`, and `redis` should be ok.
3. **Docs**: http://localhost:8000/docs loads.
4. **UI**: http://localhost:3000 loads; sending a natural-language question returns a reply or a clear error (e.g. DB connection failed if DB is not up).

---

## Troubleshooting

- **`[Errno 10061] Connect call failed ('127.0.0.1', 5432)`**  
  PostgreSQL is not running or not reachable. Run `docker compose -f docker-compose.local.yml up -d` and ensure `api/.env` has `POSTGRES_HOST=localhost` and `POSTGRES_PORT=5432`.

- **`resolution-too-deep` or pip install fails**  
  Use a **Python 3.11 or 3.12** venv in the `api` directory and run `pip install -r requirements.txt`. On 3.13, ensure SQLAlchemy, asyncpg, etc. are versions that support 3.13.

- **Docker error: "The system cannot find the file specified"**  
  Start **Docker Desktop** first, then run `docker compose`.

- **Frontend CORS or cannot reach API**  
  Ensure `api/.env` has `CORS_ORIGINS` including the UI origin (e.g. `http://localhost:3000`) and that the API is running with `APP_ENV=development` (default).

---

## Directory layout

```
deploy/
├── README.md                 # This file
├── docker-compose.local.yml  # Local: db + redis only
├── docker-compose.yml        # Full stack (API + UI + db + redis)
└── db/                       # DB init scripts, etc.
```

For local development, use **docker-compose.local.yml** and run the API and UI on the host for easier debugging.
