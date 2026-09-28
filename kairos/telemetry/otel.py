"""OpenTelemetry integration with fallback when OTLP collector is unavailable (SPEC §8)."""

from __future__ import annotations

import logging

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

logger = logging.getLogger("kairos.telemetry")
_TRACER: trace.Tracer | None = None


def init_tracer(
    service_name: str = "kairos", otlp_endpoint: str = "http://jaeger:4318"
) -> trace.Tracer:
    global _TRACER
    if _TRACER is not None:
        return _TRACER

    provider = TracerProvider()
    try:
        exporter = OTLPSpanExporter(endpoint=f"{otlp_endpoint.rstrip('/')}/v1/traces", timeout=2)
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)
    except Exception as e:  # noqa: BLE001
        logger.warning(
            f"Could not initialize OTLP exporter at {otlp_endpoint}: {e}. Falling back to NoOp tracer."
        )

    trace.set_tracer_provider(provider)
    _TRACER = trace.get_tracer(service_name)
    return _TRACER


def get_tracer() -> trace.Tracer:
    if _TRACER is None:
        return init_tracer()
    return _TRACER
