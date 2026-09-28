# Multi-stage Dockerfile for Kairos (SPEC §13.3)
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir build wheel

# Final runtime image
FROM python:3.11-slim AS runtime

WORKDIR /app

# Non-root user setup
RUN useradd -m -u 10001 kairosuser

COPY --from=builder /usr/local /usr/local
COPY . /app

RUN pip install --no-cache-dir -e .

# Security hardening: non-root user
USER kairosuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/v1/health')" || exit 1

CMD ["uvicorn", "kairos.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
