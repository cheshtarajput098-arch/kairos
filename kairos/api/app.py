"""FastAPI /v1 Application Entrypoint (SPEC §10, §13.3)."""
from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from kairos.api.middleware import RequestTracingMiddleware, SecurityHeadersMiddleware
from kairos.config import load_config
from kairos.ingest.manifest import verify_corpus_manifest
from kairos.schemas import ErrorDetail, ErrorEnvelope

logging.basicConfig(level=logging.INFO, format='{"time":"%(asctime)s", "level":"%(levelname)s", "message":"%(message)s"}')
logger = logging.getLogger("kairos.api")

settings = load_config()

# Disable OpenAPI /docs in production
docs_url = None if settings.app.env == "prod" else "/docs"
redoc_url = None if settings.app.env == "prod" else "/redoc"

app = FastAPI(
    title="Kairos Streaming Live RAG Engine",
    version="0.0.1",
    docs_url=docs_url,
    redoc_url=redoc_url,
)

# Register Middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestTracingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.security.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def custom_global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"Unhandled exception [request_id={request_id}]: {exc}", exc_info=False)

    envelope = ErrorEnvelope(
        error=ErrorDetail(
            code="INTERNAL_SERVER_ERROR",
            message="An internal server error occurred.",
            request_id=request_id,
        )
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=envelope.model_dump(),
    )


@app.get("/v1/health", response_model=dict)
async def health_check() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok", "service": "kairos"}


@app.get("/v1/ready")
async def readiness_check(response: Response) -> dict[str, str]:
    """Readiness probe: checks corpus integrity manifest and index availability (LLM04)."""
    manifest_path = Path("data/corpus.manifest.json")
    corpus_dir = Path("data/corpus")

    is_valid, reason = verify_corpus_manifest(corpus_dir, manifest_path)
    if not is_valid:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not_ready", "reason": reason}

    chunks_file = Path("index/chunks.json")
    if not chunks_file.exists():
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not_ready", "reason": "Index not built"}

    return {"status": "ready", "service": "kairos"}


# Mount static frontend directory if present
static_dir = Path("kairos/api/static")
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
