"""FastAPI /v1 Application Entrypoint (SPEC §10, §13.3)."""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request, Response, WebSocket, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from kairos.api.middleware import RequestTracingMiddleware, SecurityHeadersMiddleware
from kairos.api.stream import handle_stream_websocket
from kairos.config import load_config
from kairos.index.store import IndexStore
from kairos.ingest.manifest import verify_corpus_manifest
from kairos.schemas import ErrorDetail, ErrorEnvelope, VersionDiff
from kairos.session.store import SessionStore

logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s", "level":"%(levelname)s", "message":"%(message)s"}',
)
logger = logging.getLogger("kairos.api")

settings = load_config()

# Disable OpenAPI /docs in production
docs_url = None if settings.app.env == "prod" else "/docs"
redoc_url = None if settings.app.env == "prod" else "/redoc"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Automatic index build, load, warm-up, and session store on container startup."""
    corpus_dir = Path("data/corpus")
    index_dir = Path("index")
    chunks_file = index_dir / "chunks.json"

    app.state.session_store = SessionStore()

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
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestTracingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.security.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
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


def _get_token(request: Request) -> str:
    auth = request.headers.get("Authorization")
    if auth and auth.startswith("Bearer "):
        return auth[7:].strip()
    return request.query_params.get("token", "")


@app.post("/v1/sessions", status_code=status.HTTP_201_CREATED)
async def create_session() -> dict[str, Any]:
    """Issue a new random 128-bit session ID and HMAC-signed token."""
    raw_store = getattr(app.state, "session_store", None)
    store = raw_store if isinstance(raw_store, SessionStore) else SessionStore()
    app.state.session_store = store
    state, token, expires_at = store.create_session(settings.token_secret)
    return {
        "session_id": state.session_id,
        "token": token,
        "expires_at": expires_at,
    }


@app.get("/v1/sessions/{session_id}")
async def get_session_info(session_id: str, request: Request) -> Any:
    """Retrieve session state; requires valid token (Security Rule 4: returns 404 on mismatch)."""
    token = _get_token(request)
    store: SessionStore = getattr(app.state, "session_store", None) or SessionStore()
    state = store.get_session(session_id, token, settings.token_secret)
    if state is None:
        request_id = getattr(request.state, "request_id", "unknown")
        envelope = ErrorEnvelope(
            error=ErrorDetail(
                code="SESSION_NOT_FOUND",
                message="Session not found or authentication token is invalid.",
                request_id=request_id,
            )
        )
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=envelope.model_dump())
    return {
        "session_id": state.session_id,
        "current_version": state.current_version,
        "answer": state.answer,
        "citations": state.citations,
        "claims": [c.model_dump() for c in state.claims],
        "created_at": state.created_at,
        "last_accessed": state.last_accessed,
    }


@app.get("/v1/sessions/{session_id}/diff")
async def get_session_diff(
    session_id: str, request: Request, from_v: int = 1, to_v: int = 2
) -> Any:
    """Retrieve version diff; requires valid token (404 on mismatch)."""
    token = _get_token(request)
    store: SessionStore = getattr(app.state, "session_store", None) or SessionStore()
    state = store.get_session(session_id, token, settings.token_secret)
    if state is None:
        request_id = getattr(request.state, "request_id", "unknown")
        envelope = ErrorEnvelope(
            error=ErrorDetail(
                code="SESSION_NOT_FOUND",
                message="Session not found or authentication token is invalid.",
                request_id=request_id,
            )
        )
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=envelope.model_dump())

    diff = store.get_diff(session_id, from_v, to_v)
    if diff is not None:
        return diff.model_dump()
    return VersionDiff().model_dump()


@app.delete("/v1/sessions/{session_id}")
async def delete_session(session_id: str, request: Request) -> Any:
    """Explicitly wipe session state from memory."""
    token = _get_token(request)
    store: SessionStore = getattr(app.state, "session_store", None) or SessionStore()
    state = store.get_session(session_id, token, settings.token_secret)
    if state is None:
        request_id = getattr(request.state, "request_id", "unknown")
        envelope = ErrorEnvelope(
            error=ErrorDetail(
                code="SESSION_NOT_FOUND",
                message="Session not found or authentication token is invalid.",
                request_id=request_id,
            )
        )
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=envelope.model_dump())
    store.clear_session(session_id)
    return {"status": "cleared", "session_id": session_id}


class FeedbackRequest(BaseModel):
    session_id: str
    version: int
    rating: str  # "up" | "down"


class PresentationRequest(BaseModel):
    session_id: str
    token: str
    action: str  # "shorter" | "bullets" | "simple"


@app.get("/v1/suggestions")
async def get_suggested_questions() -> dict[str, list[str]]:
    """Return 3-5 suggested questions generated from corpus headings at index time (SPEC §14.3)."""
    import json
    suggestions_file = Path("index/suggestions.json")
    if suggestions_file.exists():
        try:
            items = json.loads(suggestions_file.read_text(encoding="utf-8"))
            if isinstance(items, list) and items:
                return {"suggestions": items}
        except Exception as e:  # noqa: BLE001
            logger.debug(f"Failed to read suggestions.json: {e}")
    # Fallback to generating from in-memory chunks
    store: IndexStore = getattr(app.state, "index_store", None) or IndexStore()
    if not store.chunks_map:
        try:
            store.load()
        except Exception as e:  # noqa: BLE001
            logger.debug(f"Failed to load store: {e}")
    from kairos.index.store import generate_corpus_suggestions

    suggestions = generate_corpus_suggestions(list(store.chunks_map.values()))
    return {"suggestions": suggestions}


@app.post("/v1/telemetry/feedback")
async def record_user_feedback(req: FeedbackRequest) -> dict[str, str]:
    """Record ephemeral user thumbs up/down rating in session telemetry (SPEC §14.3, Rule 4)."""
    logger.info(
        f"User feedback: session_id={req.session_id} version={req.version} rating={req.rating}"
    )
    return {"status": "ok"}


@app.post("/v1/turns/presentation")
async def handle_presentation_turn(req: PresentationRequest, request: Request) -> Any:
    """Execute a presentation-only quick action turn with ZERO searches (SPEC §5.4, §14.3)."""
    store: SessionStore = getattr(app.state, "session_store", None) or SessionStore()
    state = store.get_session(req.session_id, req.token, settings.token_secret)
    if state is None:
        request_id = getattr(request.state, "request_id", "unknown")
        envelope = ErrorEnvelope(
            error=ErrorDetail(
                code="SESSION_NOT_FOUND",
                message="Session not found or token invalid.",
                request_id=request_id,
            )
        )
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=envelope.model_dump())

    current_answer = state.answer or ""
    # Transform presentation without searches
    if req.action == "bullets":
        sentences = [s.strip() for s in current_answer.split(".") if s.strip()]
        new_answer = "\n".join(f"• {s}." for s in sentences)
    elif req.action == "shorter":
        sentences = [s.strip() for s in current_answer.split(".") if s.strip()]
        new_answer = ". ".join(sentences[: min(2, len(sentences))]) + "."
    elif req.action == "simple":
        new_answer = current_answer.replace("layout", "seating setup").replace(
            "reimbursement", "payback"
        )
    else:
        new_answer = current_answer

    return {
        "event": "turn_completed",
        "turn_type": "presentation_only",
        "action": req.action,
        "answer": new_answer,
        "version": state.current_version,
        "citations": state.citations,
        "claims": [c.model_dump() for c in state.claims],
        "metrics": {
            "retrievals": 0,  # Zero searches
            "presentation_only": True,
        },
    }


@app.websocket("/v1/stream")
async def websocket_stream_endpoint(
    websocket: WebSocket, session_id: str = "", token: str = ""
) -> None:
    """Live streaming WebSocket connection."""
    raw_store = getattr(app.state, "session_store", None)
    store = raw_store if isinstance(raw_store, SessionStore) else SessionStore()
    app.state.session_store = store

    raw_idx = getattr(app.state, "index_store", None)
    if isinstance(raw_idx, IndexStore):
        idx_store = raw_idx
    else:
        idx_store = IndexStore()
        try:
            idx_store.load()
        except Exception:  # noqa: BLE001
            idx_store.build()
        app.state.index_store = idx_store

    await handle_stream_websocket(websocket, session_id, token, store, idx_store)


@app.get("/v1/results")
async def get_evaluation_results() -> dict[str, Any]:
    """Expose latest offline evaluation results for Inspector dashboard and Race view (SPEC §10, §14.4)."""
    import json
    eval_dir = Path("runs/eval")
    results: dict[str, Any] = {
        "status": "available" if eval_dir.exists() else "pending",
        "gates": {},
        "metrics": {},
        "ablations": {},
        "stabilisation": {},
        "robustness": {},
        "race": {},
        "redteam": {},
    }
    for key in ["gates", "metrics", "ablations", "stabilisation", "robustness", "race", "redteam"]:
        fpath = eval_dir / f"{key}.json"
        if fpath.exists():
            try:
                results[key] = json.loads(fpath.read_text(encoding="utf-8"))
            except Exception as e:  # noqa: BLE001
                results[key] = {"error": str(e)}
    return results


@app.get("/v1/corpus/docs")
async def list_corpus_documents() -> dict[str, Any]:
    """List all corpus documents with their chunks, read from the loaded index (not hardcoded)."""
    store: IndexStore = getattr(app.state, "index_store", None) or IndexStore()
    if not store.chunks_map:
        try:
            store.load()
        except Exception as e:  # noqa: BLE001
            logger.debug(f"Index load skipped: {e}")

    # Group chunks by doc_id
    docs_map: dict[str, dict[str, Any]] = {}
    for chunk in store.chunks_map.values():
        doc_id = chunk.doc_id
        if doc_id not in docs_map:
            docs_map[doc_id] = {
                "id": doc_id,
                "title": chunk.title.rsplit(" §", 1)[0] if " §" in chunk.title else chunk.title,
                "sections_count": 0,
                "summary": chunk.text[:150] + ("..." if len(chunk.text) > 150 else ""),
                "chunks": [],
            }
        docs_map[doc_id]["sections_count"] += 1
        cid = getattr(chunk, "chunk_id", f"{chunk.doc_id}§{chunk.section}")
        prov = getattr(store, "provenance_map", {}).get(cid)
        is_flagged = getattr(prov, "flagged", False) if prov else False
        docs_map[doc_id]["chunks"].append({
            "id": f"{chunk.doc_id}§{chunk.section}",
            "section": f"§{chunk.section}",
            "title": chunk.title,
            "text": chunk.text,
            "flagged": is_flagged,
        })

    # Sort by doc_id for consistency
    docs = sorted(docs_map.values(), key=lambda d: d["id"])
    return {"documents": docs, "total_chunks": len(store.chunks_map)}


@app.get("/v1/corpus/chunks/{chunk_id}")
async def get_corpus_chunk(chunk_id: str, request: Request) -> Any:
    """Retrieve full text and metadata for a chunk by ID for Inspector Corpus Explorer."""
    store: IndexStore = getattr(app.state, "index_store", None) or IndexStore()
    if not store.chunks_map:
        try:
            store.load()
        except Exception as e:  # noqa: BLE001
            logger.debug(f"Index load skipped: {e}")
    chunk = store.chunks_map.get(chunk_id)
    if not chunk:
        request_id = getattr(request.state, "request_id", "unknown")
        envelope = ErrorEnvelope(
            error=ErrorDetail(
                code="CHUNK_NOT_FOUND",
                message=f"Corpus chunk '{chunk_id}' not found.",
                request_id=request_id,
            )
        )
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=envelope.model_dump())
    return chunk.model_dump()


@app.get("/v1/corpus/search")
async def search_corpus(q: str, limit: int = 10) -> dict[str, Any]:
    """Search corpus chunks for Inspector Corpus Explorer."""
    store: IndexStore = getattr(app.state, "index_store", None) or IndexStore()
    if not store.chunks_map:
        try:
            store.load()
        except Exception as e:  # noqa: BLE001
            logger.debug(f"Index load skipped: {e}")
    clean_q = q.strip()
    if not clean_q:
        return {"query": q, "results": []}

    dense_res = store.dense_index.search(clean_q, top_k=limit)
    results = []
    for cid, score in dense_res:
        chunk = store.chunks_map.get(cid)
        if chunk:
            results.append({
                "chunk_id": cid,
                "doc_id": chunk.doc_id,
                "section": chunk.section,
                "title": chunk.title,
                "score": round(score, 4),
                "text_snippet": chunk.text[:200] + ("..." if len(chunk.text) > 200 else ""),
            })
    return {"query": q, "results": results}


class CachedStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope: Any) -> Response:
        response = await super().get_response(path, scope)
        if "/assets/" in scope.get("path", ""):
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response


# Mount static frontend directory if present
static_dir = Path("kairos/api/static")
if static_dir.exists():
    app.mount("/", CachedStaticFiles(directory=str(static_dir), html=True), name="static")
