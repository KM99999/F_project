"""Anthropic client factory.

The SDK auto-retries 429/5xx with exponential backoff (§6.3); we set max_retries
and a per-request timeout (§6.3: 60s per receipt). The API key comes from settings
(env), never hardcoded (§6.2).
"""

from functools import lru_cache

import anthropic

from app.config import settings


@lru_cache
def get_client() -> anthropic.Anthropic:
    if not settings.anthropic_api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY no configurada. Definirla en .env para usar el pipeline."
        )
    return anthropic.Anthropic(
        api_key=settings.anthropic_api_key,
        timeout=settings.anthropic_timeout_seconds,
        max_retries=settings.anthropic_max_retries,
    )
