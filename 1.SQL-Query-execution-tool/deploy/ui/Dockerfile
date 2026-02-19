# ─────────────────────────────────────────────────────────────────────────────
# Stage 1 — Node build (React + Vite + Tailwind)
# Build context: project root (1.SQL-Query-execution-tool/)
# ─────────────────────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Install deps first — cached layer when only source changes
COPY ui/package.json ui/package-lock.json* ./
RUN npm ci --legacy-peer-deps

# Copy full UI source (node_modules excluded via Dockerfile.dockerignore)
COPY ui/ .

# Inject the API base-URL at build time via ARG → VITE env var
# Override with: docker build --build-arg VITE_API_BASE_URL=http://api:8000
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

RUN npm run build          # outputs to /app/dist


# ─────────────────────────────────────────────────────────────────────────────
# Stage 2 — Nginx static file server
# ─────────────────────────────────────────────────────────────────────────────
FROM nginx:1.27-alpine AS runtime

LABEL maintainer="DeepAgent SQL Chat App"
LABEL description="React + Vite frontend served by Nginx"

# nginx config lives alongside this Dockerfile in deploy/ui/
COPY deploy/ui/nginx.conf /etc/nginx/conf.d/default.conf

# Copy compiled static assets from build stage
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -q -O /dev/null http://localhost:3000/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
