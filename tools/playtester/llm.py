"""Minimal provider-agnostic text generation helpers for the playtester."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ModelConfig:
    provider: str
    model: str

    @property
    def label(self) -> str:
        return f"{self.provider}:{self.model}"


def load_model_config(role: str) -> ModelConfig:
    normalized_role = role.upper()
    provider = (
        os.getenv(f"ARES_PLAYTESTER_{normalized_role}_PROVIDER")
        or os.getenv("ARES_PLAYTESTER_PROVIDER")
        or os.getenv("ARES_GENERATION_PROVIDER")
        or "openai"
    ).strip().lower()

    model = (
        os.getenv(f"ARES_PLAYTESTER_{normalized_role}_MODEL")
        or os.getenv("ARES_PLAYTESTER_MODEL")
        or _default_model_for_provider(provider)
    ).strip()

    if provider not in {"openai", "anthropic"}:
        raise ValueError(
            f"Unsupported playtester provider '{provider}'. Expected 'openai' or 'anthropic'."
        )
    if not model:
        raise ValueError(f"Playtester {role.lower()} model must be non-empty.")

    return ModelConfig(provider=provider, model=model)


def verify_api_key(provider: str) -> None:
    env_name = "OPENAI_API_KEY" if provider == "openai" else "ANTHROPIC_API_KEY"
    if not os.getenv(env_name):
        raise RuntimeError(f"{env_name} not set. Add it to .env or environment.")


class TextGenerator:
    def __init__(self, config: ModelConfig, *, max_tokens: int) -> None:
        self.config = config
        self._max_tokens = max_tokens
        self._client: Any | None = None

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client

        if self.config.provider == "openai":
            from openai import OpenAI

            self._client = OpenAI()
        else:
            import anthropic

            self._client = anthropic.Anthropic()
        return self._client

    def generate(self, *, system: str, user: str) -> str:
        client = self._get_client()
        if self.config.provider == "openai":
            response = client.chat.completions.create(
                model=self.config.model,
                max_completion_tokens=self._max_tokens,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            content = response.choices[0].message.content
            if not content:
                raise RuntimeError("OpenAI playtester response was empty.")
            return content.strip()

        response = client.messages.create(
            model=self.config.model,
            max_tokens=self._max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        content = getattr(response, "content", [])
        if not content or getattr(content[0], "type", None) != "text":
            raise RuntimeError("Anthropic playtester response was empty.")
        return content[0].text.strip()


def _default_model_for_provider(provider: str) -> str:
    if provider == "openai":
        return os.getenv("ARES_MODEL", "gpt-5.4-mini")
    return "claude-sonnet-4-6"
