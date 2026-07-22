"""Tiered LLM client with structured output and token accounting.

All LLM calls in the pipeline go through :func:`call_structured`, which:
  * resolves the model from ``config/models.yaml`` by tier name (never hardcode
    model IDs in agent code — ARCHITECTURE D4);
  * enforces a Pydantic response schema (structured outputs);
  * records prompt/completion token usage to PostgreSQL for budget control.
"""

from __future__ import annotations

from typing import TypeVar

from openai import OpenAI
from pydantic import BaseModel

from res_pipeline.core.config import get_settings, load_yaml_config

TSchema = TypeVar("TSchema", bound=BaseModel)

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=get_settings().openai_api_key)
    return _client


def resolve_tier(tier: str) -> dict:
    tiers = load_yaml_config("models")["tiers"]
    if tier not in tiers:
        raise KeyError(f"Unknown model tier '{tier}'. Define it in config/models.yaml.")
    return tiers[tier]


# Fixed seed for reproducibility on models that support only the default temperature
# (best-effort determinism; OpenAI seeds are advisory, not a hard guarantee).
_DEFAULT_SEED = 20260714


def call_structured(
    *,
    tier: str,
    system_prompt: str,
    user_prompt: str,
    schema: type[TSchema],
    run_id: str,
) -> TSchema:
    """Call the tier's model and parse the response into ``schema``.

    ``temperature`` is only sent when the tier declares one, because some
    reasoning-tier models (e.g. gpt-5.5) reject any non-default temperature. A
    fixed seed is always sent for best-effort reproducibility.
    """
    spec = resolve_tier(tier)
    client = _get_client()

    kwargs: dict = {
        "model": spec["model"],
        "seed": _DEFAULT_SEED,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "response_format": schema,
    }
    if "temperature" in spec:
        kwargs["temperature"] = spec["temperature"]

    try:
        response = client.beta.chat.completions.parse(**kwargs)
    except Exception as exc:  # noqa: BLE001 — narrow-retry on temperature rejection
        if "temperature" in kwargs and "temperature" in str(exc).lower():
            kwargs.pop("temperature")
            response = client.beta.chat.completions.parse(**kwargs)
        else:
            raise

    usage = response.usage
    if usage is not None:
        _log_usage(run_id, tier, spec["model"], usage.prompt_tokens, usage.completion_tokens)

    parsed = response.choices[0].message.parsed
    if parsed is None:
        raise RuntimeError(f"Model {spec['model']} returned no parseable structured output")
    return parsed


def _log_usage(run_id: str, tier: str, model: str, prompt_tokens: int,
               completion_tokens: int) -> None:
    from res_pipeline.core.db import get_connection

    with get_connection() as conn:
        conn.execute(
            "INSERT INTO token_usage (run_id, tier, model, prompt_tokens, completion_tokens) "
            "VALUES (%s,%s,%s,%s,%s)",
            (run_id, tier, model, prompt_tokens, completion_tokens),
        )
