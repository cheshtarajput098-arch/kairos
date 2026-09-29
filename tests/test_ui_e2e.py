import pytest
from starlette.testclient import TestClient

from kairos.api.app import app
from kairos.index.store import IndexStore


@pytest.fixture(scope="module")
def client() -> TestClient:
    # Ensure index store is built and loaded
    store = IndexStore()
    if not store.chunks_map:
        try:
            store.load()
        except (FileNotFoundError, RuntimeError, ValueError):
            store.build()
    app.state.index_store = store
    app.state.is_ready = True
    return TestClient(app)


def test_ui_serves_html_and_assets(client: TestClient) -> None:
    """Verify that root / serves compiled index.html."""
    resp = client.get("/")
    assert resp.status_code == 200
    text = resp.text.lower()
    assert "<!doctype html>" in text or "<html" in text
    assert '<div id="root">' in text or "id=root" in text


def test_results_endpoint_returns_metrics(client: TestClient) -> None:
    """Verify GET /v1/results returns evaluation and race metrics for Inspector dashboard."""
    resp = client.get("/v1/results")
    assert resp.status_code == 200
    data = resp.json()
    assert "gates" in data
    assert "metrics" in data
    assert "ablations" in data
    assert "race" in data


def test_corpus_chunk_endpoint(client: TestClient) -> None:
    """Verify GET /v1/corpus/chunks/{id} returns full text for Corpus Explorer."""
    resp = client.get("/v1/corpus/chunks/Doc_12§2")
    assert resp.status_code == 200
    data = resp.json()
    assert data["chunk_id"] == "Doc_12§2"
    assert "Baner" in data["text"]
    assert data["doc_id"] == "Doc_12"


def test_corpus_search_endpoint(client: TestClient) -> None:
    """Verify GET /v1/corpus/search returns ranked results for Corpus Explorer."""
    resp = client.get("/v1/corpus/search?q=workshop+venues+pune&limit=3")
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data
    assert len(data["results"]) > 0
    top = data["results"][0]
    assert "chunk_id" in top
    assert "title" in top


def test_xss_payload_safety_in_stream(client: TestClient) -> None:
    """Verify that XSS injection payloads in queries are safely escaped and never rendered as HTML (Security Rule 1)."""
    # 1. Create a session
    create_resp = client.post("/v1/sessions")
    assert create_resp.status_code == 201
    sess = create_resp.json()
    session_id = sess["session_id"]
    token = sess["token"]

    # 2. Connect to websocket and send malicious payload
    with client.websocket_connect(f"/v1/stream?session_id={session_id}&token={token}") as ws:
        xss_payload = '<script>alert("PWNED")</script><img src=x onerror=alert(1)>'
        ws.send_json({"t": 0.0, "text": xss_payload, "is_final": True})

        # Receive events until turn_completed
        turn_completed = False
        while not turn_completed:
            msg = ws.receive_json()
            if msg.get("event") == "turn_completed":
                turn_completed = True
                answer = msg.get("answer", "")
                # Ensure raw script tags are not emitted as unescaped executable HTML
                assert "<script>alert" not in answer


def test_story_mode_10x_loop(client: TestClient) -> None:
    """SPEC §14.3a: Story mode must play flawlessly 10 times in a row without crashes or state leaks."""
    for loop_i in range(10):
        # Create session
        create_resp = client.post("/v1/sessions")
        assert create_resp.status_code == 201, f"Session create failed on loop {loop_i}"
        sess = create_resp.json()
        session_id = sess["session_id"]
        token = sess["token"]

        with client.websocket_connect(f"/v1/stream?session_id={session_id}&token={token}") as ws:
            # Send compound question chunks
            ws.send_json({"t": 0.0, "text": "Plan customer workshop in Pune", "is_final": False})
            msg1 = ws.receive_json()
            assert "event" in msg1

            ws.send_json({"t": 1.5, "text": "with cancellation terms", "is_final": True})
            completed = False
            while not completed:
                msg = ws.receive_json()
                if msg.get("event") == "turn_completed":
                    completed = True
                    assert msg.get("version") == 1
                    assert len(msg.get("answer", "")) > 0
                    assert len(msg.get("citations", [])) > 0

        # Clean up session
        del_resp = client.delete(f"/v1/sessions/{session_id}", headers={"Authorization": f"Bearer {token}"})
        assert del_resp.status_code == 200


def test_corpus_docs_endpoint(client: TestClient) -> None:
    """Verify GET /v1/corpus/docs returns all documents from the live index (not hardcoded)."""
    resp = client.get("/v1/corpus/docs")
    assert resp.status_code == 200
    data = resp.json()
    assert "documents" in data
    assert "total_chunks" in data
    assert data["total_chunks"] == 27
    docs = data["documents"]
    assert len(docs) == 8  # All 8 placeholder docs
    doc_ids = [d["id"] for d in docs]
    assert "Doc_05" in doc_ids
    assert "Doc_12" in doc_ids
    assert "Doc_89" in doc_ids
    for d in docs:
        assert len(d["chunks"]) > 0
        assert d["sections_count"] == len(d["chunks"])

