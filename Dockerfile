# Multi-stage Dockerfile for Kairos (SPEC §13.3, §15.1)

# Stage 1: Build React web frontend with Node (no Node at runtime)
FROM node:20-slim AS web-builder

WORKDIR /web
COPY web/package.json web/package-lock.json* ./
RUN npm install
COPY web/ ./
RUN npm run build

# Stage 2: Build Python virtualenv with frozen dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy lockfile and pyproject
COPY pyproject.toml uv.lock ./

# Create virtual environment and install frozen dependencies including dev
ENV UV_LINK_MODE=copy
RUN uv sync --frozen --all-extras --no-install-project

# Stage 3: Final runtime image (pure Python, non-root, read-only root)
FROM python:3.11-slim AS runtime

WORKDIR /app

# Install make and curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv in runtime
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Non-root user setup
RUN useradd -m -u 10001 kairosuser

# Set up paths and cache directories
ENV PATH="/app/.venv/bin:$PATH"
ENV FASTEMBED_CACHE_PATH="/app/models/fastembed"
ENV HF_HOME="/app/models/hf"
ENV PYTHONUNBUFFERED=1
ENV RUFF_CACHE_DIR="/tmp/.ruff_cache"
ENV MYPY_CACHE_DIR="/tmp/.mypy_cache"
ENV PYTHONPYCACHEPREFIX="/tmp/pycache"
ENV COVERAGE_FILE="/tmp/.coverage"

# Copy virtualenv from builder
COPY --from=builder /app/.venv /app/.venv

# Copy source repository
COPY . /app

# Copy compiled frontend from web-builder
COPY --from=web-builder /web/dist /app/kairos/api/static

# Pre-download and cache FastEmbed model during build (offline-capable rule)
RUN python -c "from fastembed import TextEmbedding; TextEmbedding('BAAI/bge-small-en-v1.5')"

# Install kairos project in editable mode without reinstalling dependencies
RUN uv pip install --no-deps -e .

# Create writable runtime directories and set ownership
RUN mkdir -p /app/index /app/runs /tmp /app/models \
    && chown -R kairosuser:kairosuser /app /home/kairosuser

USER kairosuser

EXPOSE 8000

HEALTHCHECK --interval=5s --timeout=3s --start-period=5s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/v1/health')" || exit 1

CMD ["uvicorn", "kairos.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
