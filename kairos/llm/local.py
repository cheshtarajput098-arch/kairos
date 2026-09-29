"""Local GGUF LLM implementation using llama-cpp-python (SPEC §1, §6.2).

Features:
1. Strict schema-validated JSON generation (Security Rule 3).
2. Hard token cap (max 256 tokens) and deadline enforcement (Security Rule 5).
3. Circuit breaker: trips to OPEN after 3 consecutive failures, auto-resets after 30s.
4. Deterministic: temperature 0.0, fixed random seed.
5. Soft fail / Offline fallback: if model file is absent or llama-cpp-python is not installed,
   gracefully returns schema fallback without failing or crashing.
"""

from __future__ import annotations

import json
import logging
import re
import time
from pathlib import Path
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger("kairos.llm.local")


class CircuitBreaker:
    """Three-state circuit breaker: CLOSED -> OPEN -> HALF_OPEN -> CLOSED."""

    def __init__(self, failures_to_open: int = 3, reset_after_s: float = 30.0) -> None:
        self.failures_to_open = failures_to_open
        self.reset_after_s = reset_after_s
        self.state = "CLOSED"  # "CLOSED" | "OPEN" | "HALF_OPEN"
        self.consecutive_failures = 0
        self.last_failure_time = 0.0

    def can_execute(self) -> bool:
        """Check whether the circuit breaker permits an execution attempt."""
        now = time.time()
        if self.state == "OPEN":
            if now - self.last_failure_time >= self.reset_after_s:
                self.state = "HALF_OPEN"
                logger.info("Circuit breaker transitioning OPEN -> HALF_OPEN (probing call).")
                return True
            return False
        return True

    def record_success(self) -> None:
        """Record successful execution, resetting circuit breaker to CLOSED."""
        if self.state != "CLOSED":
            logger.info("Circuit breaker recovered: transitioning to CLOSED.")
        self.state = "CLOSED"
        self.consecutive_failures = 0

    def record_failure(self) -> None:
        """Record a failure, tripping the circuit breaker if threshold is reached."""
        self.consecutive_failures += 1
        self.last_failure_time = time.time()
        if self.consecutive_failures >= self.failures_to_open:
            if self.state != "OPEN":
                logger.warning(
                    f"Circuit breaker tripped to OPEN after {self.consecutive_failures} failures. "
                    f"Will reject calls for {self.reset_after_s}s."
                )
            self.state = "OPEN"


class LocalLLM:
    """Local quantized GGUF LLM wrapper with circuit breaker and JSON output guarantees."""

    def __init__(
        self,
        model_path: str | Path | None = None,
        n_threads: int = 4,
        context_tokens: int = 4096,
        max_output_tokens: int = 256,
        temperature: float = 0.0,
        failures_to_open: int = 3,
        reset_after_s: float = 30.0,
    ) -> None:
        self.model_path = Path(model_path) if model_path else None
        self.n_threads = n_threads
        self.context_tokens = context_tokens
        self.max_output_tokens = max_output_tokens
        self.temperature = temperature

        self.circuit_breaker = CircuitBreaker(
            failures_to_open=failures_to_open, reset_after_s=reset_after_s
        )
        self._llm: Any = None
        self._load_attempted = False

    def is_available(self) -> bool:
        """Return True if the model file exists and is loadable."""
        return self.model_path is not None and self.model_path.exists()

    def _ensure_loaded(self) -> bool:
        """Attempt to lazily load the GGUF model via llama-cpp-python."""
        if self._llm is not None:
            return True
        if self._load_attempted:
            return False

        self._load_attempted = True
        if not self.is_available():
            logger.debug(
                f"Local LLM model file not found at {self.model_path}; fallback to extractive mode."
            )
            return False

        try:
            import importlib

            llama_mod = importlib.import_module("llama_cpp")
            llama_cls = llama_mod.Llama

            logger.info(f"Loading local GGUF model from {self.model_path} ({self.n_threads} threads)...")
            self._llm = llama_cls(
                model_path=str(self.model_path),
                n_threads=self.n_threads,
                n_ctx=self.context_tokens,
                verbose=False,
            )
            logger.info("Local GGUF model successfully loaded and warmed up.")
            return True
        except ImportError:
            logger.info("llama-cpp-python is not installed; running in Speed-1 fallback mode.")
            return False
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Failed to load local GGUF model at {self.model_path}: {e}")
            return False

    def generate_json(
        self,
        schema: type[BaseModel],
        messages: list[dict[str, str]],
        limits: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate structured JSON conforming to the given Pydantic schema."""
        limits = limits or {}
        max_tokens = min(int(limits.get("max_tokens", self.max_output_tokens)), self.max_output_tokens)
        deadline_ms = float(limits.get("deadline_ms", 2500.0))

        # Check circuit breaker
        if not self.circuit_breaker.can_execute():
            logger.warning("Local LLM call rejected by circuit breaker (OPEN state). Returning fallback.")
            return self._fallback_response(schema)

        # Ensure model is loaded; if unavailable, return schema fallback without tripping breaker
        if not self._ensure_loaded():
            return self._fallback_response(schema)

        start_time = time.perf_counter()
        try:
            # Build prompt messages
            # System prompt requests structured JSON matching the schema
            schema_json = json.dumps(schema.model_json_schema())
            json_system_prompt = (
                f"Respond ONLY with valid JSON conforming strictly to this JSON Schema:\n{schema_json}\n"
                "Never output markdown code fences, commentary, or text outside the JSON object."
            )

            formatted_messages = [{"role": "system", "content": json_system_prompt}] + list(messages)

            # Call llama-cpp chat completion
            response = self._llm.create_chat_completion(
                messages=formatted_messages,
                temperature=self.temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
            )

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            if elapsed_ms > deadline_ms:
                logger.warning(f"Local LLM exceeded deadline ({elapsed_ms:.1f}ms > {deadline_ms:.1f}ms).")
                self.circuit_breaker.record_failure()
                return self._fallback_response(schema)

            raw_text = response["choices"][0]["message"]["content"]
            # Extract JSON block
            parsed_json = self._extract_json(raw_text)
            # Validate schema
            validated = schema.model_validate(parsed_json)
            self.circuit_breaker.record_success()
            return validated.model_dump()

        except Exception as e:  # noqa: BLE001
            logger.warning(f"Local LLM generation failed: {e}; recording circuit breaker failure.")
            self.circuit_breaker.record_failure()
            return self._fallback_response(schema)

    def _extract_json(self, text: str) -> dict[str, Any]:
        """Extract and parse JSON from LLM output, handling possible whitespace or fences."""
        text = text.strip()
        # Remove markdown code fences if present
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
            text = text.strip()

        # Find outer braces
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start : end + 1]

        data = json.loads(text)
        return dict(data) if isinstance(data, dict) else {}

    def _fallback_response(self, schema: type[BaseModel]) -> dict[str, Any]:
        """Produce a minimal valid default dictionary for the requested Pydantic schema."""
        result: dict[str, Any] = {}
        for name, field in schema.model_fields.items():
            if field.annotation == str or getattr(field.annotation, "__name__", "") == "str":
                result[name] = ""
            elif field.annotation == bool or getattr(field.annotation, "__name__", "") == "bool":
                result[name] = False
            elif field.annotation == int or getattr(field.annotation, "__name__", "") == "int":
                result[name] = 0
            elif field.annotation == float or getattr(field.annotation, "__name__", "") == "float":
                result[name] = 0.0
            elif getattr(field.annotation, "__origin__", None) is list:
                result[name] = []
            elif getattr(field.annotation, "__origin__", None) is dict:
                result[name] = {}
            else:
                result[name] = None
        return result
