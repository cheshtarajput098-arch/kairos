"""Integration tests for Session REST and WebSocket streaming endpoints (SPEC §10, §13.3)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from kairos.api.app import app
from kairos.schemas import CorpusChunk


def test_session_rest_endpoints() -> None:
    client = TestClient(app)

    # 1. POST /v1/sessions (creates session)
    resp = client.post("/v1/sessions")
    assert resp.status_code == 201
    data = resp.json()
    assert "session_id" in data
    assert "token" in data
    session_id = data["session_id"]
    token = data["token"]

    # 2. GET /v1/sessions/{id} with valid Bearer token
    resp_get = client.get(
        f"/v1/sessions/{session_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp_get.status_code == 200
    assert resp_get.json()["session_id"] == session_id

    # 3. GET /v1/sessions/{id} with INVALID token returns 404 (Security Rule 4)
    resp_invalid = client.get(
        f"/v1/sessions/{session_id}", headers={"Authorization": "Bearer bad-token"}
    )
    assert resp_invalid.status_code == 404
    assert resp_invalid.json()["error"]["code"] == "SESSION_NOT_FOUND"

    # 4. GET /v1/sessions/{id}/diff returns 200
    resp_diff = client.get(
        f"/v1/sessions/{session_id}/diff", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp_diff.status_code == 200

    # 5. DELETE /v1/sessions/{id}
    resp_del = client.delete(
        f"/v1/sessions/{session_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp_del.status_code == 200

    # After deletion, accessing session returns 404
    resp_after = client.get(
        f"/v1/sessions/{session_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp_after.status_code == 404


def test_websocket_stream_unauthorized_rejected() -> None:
    client = TestClient(app)
    # Attempt connection with invalid session_id and token
    try:
        with client.websocket_connect("/v1/stream?session_id=fake&token=invalid"):
            assert False, "Should have been rejected"
    except Exception as exc:  # noqa: BLE001
        code = getattr(exc, "code", None)
        assert (
            code == 1008
            or "1008" in repr(exc)
            or "close" in repr(exc).lower()
            or "policy" in repr(exc).lower()
        )


def test_websocket_stream_flow() -> None:
    client = TestClient(app)

    # Create session
    resp = client.post("/v1/sessions")
    session_id = resp.json()["session_id"]
    token = resp.json()["token"]

    # Ensure app state has an index mock if not built
    if not hasattr(app.state, "index_store") or app.state.index_store is None:
        mock_idx = MagicMock()
        mock_idx.chunks_map = {
            "Doc_12§2": CorpusChunk(
                chunk_id="Doc_12§2",
                doc_id="Doc_12",
                section="2",
                title="Venues",
                text="Workshop Alpha in Pune has a capacity of 50.",
                char_start=0,
                char_end=45,
            )
        }
        app.state.index_store = mock_idx

    with client.websocket_connect(f"/v1/stream?session_id={session_id}&token={token}") as ws:
        # 1. Send first chunk
        msg1 = {"t": 1.0, "text": "What is the capacity in Pune", "is_final": False}
        ws.send_text(json.dumps(msg1))

        # Receive at least controller_decision
        resp1 = json.loads(ws.receive_text())
        assert "event" in resp1

        # 2. Send final chunk
        msg2 = {"t": 2.0, "text": "for workshop venues?", "is_final": True}
        ws.send_text(json.dumps(msg2))

        # Read events until turn_completed
        turn_completed_seen = False
        for _ in range(20):
            evt = json.loads(ws.receive_text())
            if evt.get("event") == "turn_completed":
                turn_completed_seen = True
                assert "answer" in evt
                break

        assert turn_completed_seen


def test_websocket_oversized_message_rejected() -> None:
    client = TestClient(app)
    resp = client.post("/v1/sessions")
    session_id = resp.json()["session_id"]
    token = resp.json()["token"]

    with client.websocket_connect(f"/v1/stream?session_id={session_id}&token={token}") as ws:
        # Message exceeding 4096 bytes
        huge_text = "A" * 5000
        ws.send_text(huge_text)
        resp_err = json.loads(ws.receive_text())
        assert resp_err["error"]["code"] == "MESSAGE_TOO_LARGE"
