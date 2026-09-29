"""In-Memory Ephemeral Session Store (SPEC §7, Security Rule 4).

Holds session-bound state: active legs, retrieved chunks, claim graph,
answer version lineage, and TTL expiration with strict session isolation.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from kairos.config import load_config
from kairos.schemas import ClaimObject, CorpusChunk, Leg, VersionDiff
from kairos.session.token import generate_session_id, issue_token, verify_token

logger = logging.getLogger("kairos.session.store")


@dataclass
class SessionState:
    session_id: str
    created_at: float
    last_accessed: float
    active_legs: dict[str, Leg] = field(default_factory=dict)
    retrieved_chunks: dict[str, CorpusChunk] = field(default_factory=dict)
    claims: list[ClaimObject] = field(default_factory=list)
    answer: str = ""
    citations: list[str] = field(default_factory=list)
    current_version: int = 1
    version_history: dict[int, dict[str, Any]] = field(default_factory=dict)
    diffs_history: dict[str, VersionDiff] = field(default_factory=dict)


class SessionStore:
    def __init__(self, max_sessions: int | None = None, ttl_seconds: int | None = None) -> None:
        cfg = load_config()
        self.max_sessions = max_sessions if max_sessions is not None else cfg.session.max_sessions
        self.ttl_seconds = ttl_seconds if ttl_seconds is not None else cfg.session.ttl_s
        self.sessions: dict[str, SessionState] = {}

    def create_session(self, secret: str) -> tuple[SessionState, str, float]:
        """Create a new ephemeral session and issue a signed authentication token."""
        self.cleanup_expired()

        # Enforce max sessions cap by evicting oldest session if at limit
        if len(self.sessions) >= self.max_sessions:
            oldest_id = min(self.sessions.keys(), key=lambda sid: self.sessions[sid].last_accessed)
            logger.info(f"Evicting oldest session {oldest_id} to satisfy max_sessions limit.")
            self.clear_session(oldest_id)

        session_id = generate_session_id()
        now = time.time()
        token, expires_at = issue_token(session_id, secret, ttl_seconds=self.ttl_seconds)

        state = SessionState(
            session_id=session_id,
            created_at=now,
            last_accessed=now,
        )
        self.sessions[session_id] = state
        return state, token, expires_at

    def get_or_create(self, session_id: str) -> SessionState:
        """Retrieve existing session or create an unauthenticated local replay session."""
        if session_id not in self.sessions:
            now = time.time()
            self.sessions[session_id] = SessionState(
                session_id=session_id,
                created_at=now,
                last_accessed=now,
            )
        return self.sessions[session_id]

    def get_session(self, session_id: str, token: str, secret: str) -> SessionState | None:
        """Authenticate token and retrieve session state.

        Returns None if token is invalid or session does not exist / expired (Security Rule 4).
        """
        if not verify_token(session_id, token, secret):
            return None

        state = self.sessions.get(session_id)
        if state is None:
            return None

        now = time.time()
        if now - state.last_accessed > self.ttl_seconds:
            self.clear_session(session_id)
            return None

        state.last_accessed = now
        return state

    def clear_session(self, session_id: str) -> bool:
        """Explicitly clear session state and claim graph."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Session {session_id} state cleared from memory.")
            return True
        return False

    def save_version(
        self,
        session_id: str,
        answer: str,
        claims: list[ClaimObject],
        citations: list[str],
        diff: VersionDiff | None = None,
        is_refinement: bool | None = None,
    ) -> int:
        """Record an answer version snapshot in session history.

        A new question starts at v1; only a late detail makes v2.
        """
        state = self.sessions.get(session_id)
        if state is None:
            return 1

        refinement = is_refinement if is_refinement is not None else (diff is not None)
        if refinement:
            new_version = state.current_version + 1
        else:
            new_version = 1
            state.version_history.clear()
            state.diffs_history.clear()

        state.current_version = new_version
        state.answer = answer
        state.claims = claims
        state.citations = citations

        state.version_history[new_version] = {
            "answer": answer,
            "claims": [c.model_dump() for c in claims],
            "citations": list(citations),
            "timestamp": time.time(),
        }

        if diff is not None:
            diff_key = f"{new_version - 1}->{new_version}"
            state.diffs_history[diff_key] = diff

        return new_version

    def get_diff(self, session_id: str, from_v: int, to_v: int) -> VersionDiff | None:
        """Retrieve stored version diff between two answer versions."""
        state = self.sessions.get(session_id)
        if state is None:
            return None

        diff_key = f"{from_v}->{to_v}"
        return state.diffs_history.get(diff_key)

    def cleanup_expired(self) -> int:
        """Remove all sessions exceeding TTL."""
        now = time.time()
        expired_ids = [
            sid for sid, s in self.sessions.items() if now - s.last_accessed > self.ttl_seconds
        ]
        for sid in expired_ids:
            del self.sessions[sid]
        return len(expired_ids)
