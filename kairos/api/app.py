"""FastAPI /v1 Application Entrypoint (SPEC §10, §13.3)."""
from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from kairos.api.middleware import RequestTracingMiddleware, SecurityHeadersMiddleware
from kairos.config import load_config
from kairos.index.store import IndexStore
from kairos.ingest.manifest import verify_corpus_manifest
from kairos.schemas import ErrorDetail, ErrorEnvelope

logging.basicConfig(level=logging.INFO, format='{"time":"%(asctime)s", "level":"%(levelname)s", "message":"%(message)s"}')
logger = logging.getLogger("kairos.api")

settings = load_config()

# Disable OpenAPI /docs in production
docs_url = None if settings.app.env == "prod" else "/docs"
redoc_url = None if settings.app.env == "prod" else "/redoc"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Automatic index build, load, and warm-up on container startup."""
    corpus_dir = Path("data/corpus")
    index_dir = Path("index")
    chunks_file = index_dir / "chunks.json"

    is_valid, _ = verify_corpus_manifest(corpus_dir)
    store = IndexStore(index_dir=index_dir, corpus_dir=corpus_dir)

    if not chunks_file.exists() or not is_valid:
        logger.info("Corpus index missing or manifest changed; building index on startup...")
        try:
            store.build()
            logger.info("Index build completed successfully.")
        except Exception as e:  # noqa: BLE001
            logger.error(f"Failed to build index on startup: {e}")

    try:
        if chunks_file.exists():
            store.load()
            _ = store.dense_index.search("warmup query", top_k=1)
            logger.info("Index loaded and dense model warmed up.")
            app.state.index_store = store
            app.state.is_ready = True
    except Exception as e:  # noqa: BLE001
        logger.error(f"Failed to load/warmup index: {e}")
        app.state.is_ready = False

    yield


app = FastAPI(
    title="Kairos Streaming Live RAG Engine",
    version="0.0.1",
    docs_url=docs_url,
    redoc_url=redoc_url,
    lifespan=lifespan,
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
    corpus_dir = Path("data/corpus")
    index_dir = Path("index")
    chunks_file = index_dir / "chunks.json"

    is_valid, _ = verify_corpus_manifest(corpus_dir)
    store = IndexStore(index_dir=index_dir, corpus_dir=corpus_dir)

    if not chunks_file.exists() or not is_valid:
        try:
            store.build()
        except Exception as e:  # noqa: BLE001
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            return {"status": "not_ready", "reason": f"Index build failed: {e}"}

    if not getattr(app.state, "is_ready", False):
        try:
            store.load()
            _ = store.dense_index.search("warmup query", top_k=1)
            app.state.index_store = store
            app.state.is_ready = True
        except Exception as e:  # noqa: BLE001
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            return {"status": "not_ready", "reason": f"Index load failed: {e}"}

    return {"status": "ready", "service": "kairos"}


# Mount static frontend directory if present
static_dir = Path("kairos/api/static")
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
