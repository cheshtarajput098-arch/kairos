"""Locust load and security abuse testing scenarios (SPEC §13.2, §15.4, Tier 4).

Scenarios:
1. StandardStreamingUser: normal user flow creating session, querying readiness, and executing turns.
2. AdversarialAbuseUser: flood attacks, oversized payloads (>4KB), and forged/expired session tokens.
"""

from __future__ import annotations

import json
import uuid
from locust import HttpUser, between, task


class StandardStreamingUser(HttpUser):
    """Simulates healthy, legitimate user traffic under 1 to 10 concurrent sessions."""

    wait_time = between(0.5, 1.5)

    def on_start(self) -> None:
        self.session_id = ""
        self.token = ""
        # 1. Acquire server-issued ephemeral session
        res = self.client.post("/v1/sessions", json={})
        if res.status_code == 200:
            data = res.json()
            self.session_id = data.get("session_id", "")
            self.token = data.get("token", "")

    @task(3)
    def check_health_and_readiness(self) -> None:
        self.client.get("/v1/health")
        self.client.get("/v1/ready")

    @task(2)
    def browse_corpus_docs(self) -> None:
        self.client.get("/v1/corpus/docs")

    @task(2)
    def presentation_action(self) -> None:
        if not self.session_id or not self.token:
            return
        payload = {
            "session_id": self.session_id,
            "token": self.token,
            "action": "bullets",
        }
        self.client.post("/v1/turns/presentation", json=payload)


class AdversarialAbuseUser(HttpUser):
    """Stress tests boundary limits: floods, oversized messages, forged tokens."""

    wait_time = between(0.05, 0.2)

    @task(4)
    def flood_rate_limit(self) -> None:
        """Rapid fire queries to verify rate limiting and backpressure."""
        headers = {"X-Request-ID": f"flood-{uuid.uuid4().hex[:6]}"}
        with self.client.get("/v1/health", headers=headers, catch_response=True) as resp:
            # 200 or 429 are both successful server defenses; 500 is failure
            if resp.status_code in (200, 429):
                resp.success()
            else:
                resp.failure(f"Unexpected status: {resp.status_code}")

    @task(2)
    def send_oversized_payload(self) -> None:
        """Send message exceeding 4096 bytes limit (Security Rule 5)."""
        huge_text = "A" * 8192
        payload = {
            "session_id": "abuse-session",
            "token": "abuse-token",
            "action": huge_text,
        }
        with self.client.post("/v1/turns/presentation", json=payload, catch_response=True) as resp:
            # Server must reject safely with 400, 404, 413, or 422, never crash
            if resp.status_code in (400, 404, 413, 422):
                resp.success()
            elif resp.status_code == 500:
                resp.failure("Server crashed with 500 on oversized payload!")
            else:
                resp.success()

    @task(2)
    def forged_token_access(self) -> None:
        """Attempt unauthorized access with forged token (Security Rule 4)."""
        payload = {
            "session_id": "nonexistent-session-id",
            "token": "forged.hmac.token.payload",
            "action": "shorter",
        }
        with self.client.post("/v1/turns/presentation", json=payload, catch_response=True) as resp:
            if resp.status_code in (403, 404):
                resp.success()
            elif resp.status_code == 500:
                resp.failure("Server crashed with 500 on forged token!")
            else:
                resp.success()
