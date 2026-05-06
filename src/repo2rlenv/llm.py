"""LiteLLM wrapper — single entry point across providers.

The pipelines call `complete(input, prompt)`; we resolve the API key from
either the LLMSpec hint or the provider-default env var, then dispatch.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from repo2rlenv.auth import resolve_llm_api_key
from repo2rlenv.spec.input import LLMSpec


@dataclass(slots=True)
class LLMResponse:
    content: str
    usage: dict | None = None


def complete(
    spec: LLMSpec,
    *,
    system: str | None = None,
    user: str,
    max_tokens: int = 1024,
    temperature: float = 0.7,
) -> LLMResponse:
    """Single chat-completion call. Honors LLMSpec.endpoint for self-hosted endpoints."""
    import litellm  # type: ignore[import-untyped]

    api_key = resolve_llm_api_key(spec.provider, spec.api_key_env)
    if api_key is None:
        raise RuntimeError(
            f"no API key resolved for provider {spec.provider!r}. "
            f"Set {spec.api_key_env or 'the provider-default env var'}."
        )

    messages: list[dict] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})

    kwargs: dict = {
        "model": spec.qualified_name,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "api_key": api_key,
        "timeout": spec.timeout_sec,
    }
    if spec.endpoint:
        kwargs["api_base"] = spec.endpoint

    # HF inference router quirk: LiteLLM expects the model in `Qwen/...:provider`
    # form for the HF router; users pass that shape directly via spec.model.
    if spec.provider == "huggingface" and spec.endpoint is None:
        kwargs.setdefault(
            "api_base", "https://router.huggingface.co/v1"
        )

    response = litellm.completion(**kwargs)
    choice = response.choices[0]
    content = choice.message.content or ""
    usage = getattr(response, "usage", None)
    return LLMResponse(
        content=content,
        usage=dict(usage) if usage else None,
    )
