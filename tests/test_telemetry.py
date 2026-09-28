"""Unit tests for telemetry, JSONL event logging, and PII redaction."""

import json
import pathlib

from kairos.telemetry.events import JSONLEventWriter, redact_obj, redact_pii_text
from kairos.telemetry.otel import get_tracer, init_tracer


def test_pii_redaction() -> None:
    text = "Contact user at john.doe@example.com or call +1 555-123-4567 with card 4111-2222-3333-4444."
    redacted = redact_pii_text(text)
    assert "john.doe@example.com" not in redacted
    assert "[REDACTED_EMAIL]" in redacted
    assert "[REDACTED_PHONE]" in redacted
    assert "[REDACTED_CARD]" in redacted


def test_redact_obj_masking() -> None:
    data = {
        "user_email": "alice@test.org",
        "long_raw_text": "A" * 300,
    }
    redacted_no_text = redact_obj(data, log_text=False)
    assert redacted_no_text["user_email"] == "[REDACTED_EMAIL]"
    assert "[TEXT_HASH:" in redacted_no_text["long_raw_text"]

    redacted_with_text = redact_obj(data, log_text=True)
    assert redacted_with_text["user_email"] == "[REDACTED_EMAIL]"
    assert redacted_with_text["long_raw_text"] == "A" * 300


def test_jsonl_event_writer(tmp_path: pathlib.Path) -> None:
    writer = JSONLEventWriter(runs_dir=tmp_path, run_id="test_run", log_text=False)
    writer.write_event({"turn_id": "t1", "info": "secret user@domain.com"})

    log_file = tmp_path / "test_run" / "events.jsonl"
    assert log_file.exists()
    lines = log_file.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    event = json.loads(lines[0])
    assert event["info"] == "secret [REDACTED_EMAIL]"


def test_otel_tracer_fallback() -> None:
    tracer = init_tracer("kairos-test", otlp_endpoint="http://invalid-localhost:9999")
    assert tracer is not None
    assert get_tracer() is tracer
