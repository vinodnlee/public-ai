# ─────────────────────────────────────────────────────────────────────────────
# Stage 1 — dependency installer (keeps image lean via build cache)
# Build context: project root (1.SQL-Query-execution-tool/)
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# System libs needed to compile asyncpg and other C-extension wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install pip deps into an isolated prefix so we can copy just them
COPY api/requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt


# ─────────────────────────────────────────────────────────────────────────────
# Stage 2 — runtime image
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

LABEL maintainer="DeepAgent SQL Chat App"
LABEL description="FastAPI + deepagents SQL query execution API"

# Runtime-only system deps (asyncpg needs libpq at runtime)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy pre-built Python packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY api/main.py .
COPY api/src/ ./src/

# Non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser

EXPOSE 8000

# Healthcheck — FastAPI /health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production server: uvicorn with multiple workers
# (override CMD via docker-compose for local dev with --reload)
CMD ["python", "-m", "uvicorn", "src.main:app", \
    "--host", "0.0.0.0", \
    "--port", "8000", \
    "--workers", "2", \
    "--loop", "uvloop", \
    "--http", "httptools"]
