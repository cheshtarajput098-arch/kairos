"""Stage 5 Session Management & Delta Engine (SPEC §7).

Ephemeral in-memory session store, HMAC token validation, and state-preserving delta engine.
"""

from kairos.session.delta import DeltaEngine
from kairos.session.store import SessionState, SessionStore
from kairos.session.token import generate_session_id, issue_token, verify_token

__all__ = [
    "DeltaEngine",
    "SessionState",
    "SessionStore",
    "generate_session_id",
    "issue_token",
    "verify_token",
]
