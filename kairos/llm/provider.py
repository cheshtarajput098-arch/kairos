"""Thin LLM Provider interface (SPEC §1, §6.2).

Exposes only `generate_json(schema, messages, limits)` — zero tools, zero function calling.
Supported providers: none | gemini | openai_compatible | ollama | local
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class LLMProvider:
    def __init__(self, provider_type: str = "none", model_name: str | None = None):
        self.provider_type = provider_type
        self.model_name = model_name

    def generate_json(
        self,
        schema: type[BaseModel],
        messages: list[dict[str, str]],
        limits: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate structured JSON conforming to the given Pydantic schema."""
        if self.provider_type == "none" or not self.provider_type:
            # Fallback offline generator returns empty/valid default dict matching schema fields
            return self._fallback_response(schema)

        if self.provider_type == "local":
            try:
                from kairos.config import load_config
                from kairos.llm.local import LocalLLM

                cfg = load_config()
                local_cfg = cfg.models.local_llm
                local_llm = LocalLLM(
                    model_path=self.model_name or local_cfg.gguf_file,
                    n_threads=local_cfg.n_threads,
                    context_tokens=local_cfg.context_tokens,
                    max_output_tokens=local_cfg.max_output_tokens,
                    temperature=local_cfg.temperature,
                )
                return local_llm.generate_json(schema, messages, limits)
            except Exception:  # noqa: BLE001
                return self._fallback_response(schema)

        # Placeholder for external hosted providers (gemini, openai_compatible, ollama)
        return self._fallback_response(schema)

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
