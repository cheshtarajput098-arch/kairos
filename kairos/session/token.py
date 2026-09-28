"""Session Token Generation & HMAC Verification (SPEC §7, §13.3).

Provides server-issued 128-bit random session IDs with cryptographically
signed HMAC-SHA256 tokens to prevent session enumeration and tampering.
"""

from __future__ import annotations

import base64
import hmac
import time
import uuid
from hashlib import sha256


def generate_session_id() -> str:
    """Generate cryptographically secure 128-bit random session ID (32 hex chars)."""
    return uuid.uuid4().hex


def issue_token(session_id: str, secret: str, ttl_seconds: int = 3600) -> tuple[str, float]:
    """Issue HMAC-signed session token.

    Returns:
        (token_string, expires_at_epoch)
    """
    expires_at = time.time() + ttl_seconds
    payload = f"{session_id}:{expires_at:.3f}"
    signature = hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).decode("utf-8").rstrip("=")
    token = f"{payload}:{sig_b64}"
    return token, expires_at


def verify_token(session_id: str, token: str, secret: str) -> bool:
    """Verify HMAC signature and check that token matches session ID and has not expired.

    Constant-time comparison is used to mitigate timing attacks.
    """
    if not token or not session_id or not secret:
        return False

    parts = token.split(":")
    if len(parts) != 3:
        return False

    tok_session_id, exp_str, sig_b64 = parts

    # Enforce strict session_id match
    if tok_session_id != session_id:
        return False

    # Check expiration
    try:
        expires_at = float(exp_str)
        if time.time() > expires_at:
            return False
    except ValueError:
        return False

    # Verify HMAC signature
    payload = f"{tok_session_id}:{exp_str}"
    expected_sig = hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), sha256).digest()
    expected_sig_b64 = base64.urlsafe_b64encode(expected_sig).decode("utf-8").rstrip("=")

    return hmac.compare_digest(sig_b64, expected_sig_b64)
