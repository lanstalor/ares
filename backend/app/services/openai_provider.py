from __future__ import annotations

import json
from typing import Any, Callable

from app.core.enums import SecretStatus, Visibility
from app.services.ai_provider import NarrationProvider, NarrationRequest, NarrationResponse
from app.services.consequence_applier import (
    ClockTick,
    Consequences,
    LocationChange,
    MemoryDraft,
    SecretStatusChange,
)

_TOOL_NAME = "record_turn"

# Re-use the same system prompt text from the Anthropic provider
from app.services.anthropic_provider import _CLARIFY_SYSTEM_PROMPT
from app.services.anthropic_provider import _build_response, _format_user_message
from app.services.anthropic_provider import build_system_prompt, build_tool_schema


class OpenAINarrationProvider:
    def __init__(
        self,
        *,
        client: Any | None = None,
        model: str = "gpt-5.4-mini",
        max_tokens: int = 4096,
        enable_dice: bool = False,
    ) -> None:
        if not model:
            raise ValueError("OpenAINarrationProvider requires a non-empty model.")
        self._client = client
        self._model = model
        self._max_tokens = max_tokens
        self._enable_dice = enable_dice

    def _get_client(self) -> Any:
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI()
        return self._client

    def narrate(self, request: NarrationRequest) -> NarrationResponse:
        client = self._get_client()
        tool_schema = build_tool_schema(enable_dice=self._enable_dice)

        # Convert Anthropic tool schema to OpenAI function schema
        tool = {
            "type": "function",
            "function": {
                "name": tool_schema["name"],
                "description": tool_schema["description"],
                "parameters": tool_schema["input_schema"],
            },
        }

        response = client.chat.completions.create(
            model=self._model,
            max_completion_tokens=self._max_tokens,
            messages=[
                {"role": "system", "content": build_system_prompt(enable_dice=self._enable_dice)},
                {"role": "user", "content": _format_user_message(request)},
            ],
            tools=[tool],
            tool_choice={"type": "function", "function": {"name": _TOOL_NAME}},
        )

        tool_call = _find_tool_call(response)
        if tool_call is None:
            raise RuntimeError(
                f"OpenAI provider expected a {_TOOL_NAME} tool call but got none."
            )

        tool_input = json.loads(tool_call.function.arguments)
        return _build_response(tool_input)

    def clarify(self, request: NarrationRequest) -> str:
        client = self._get_client()

        response = client.chat.completions.create(
            model=self._model,
            max_completion_tokens=self._max_tokens,
            messages=[
                {"role": "system", "content": _CLARIFY_SYSTEM_PROMPT},
                {"role": "user", "content": _format_user_message(request)},
            ],
        )

        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("OpenAI provider returned empty content for clarification.")
        return content


def _find_tool_call(response: Any) -> Any | None:
    message = response.choices[0].message
    for tc in getattr(message, "tool_calls", []) or []:
        if tc.function.name == _TOOL_NAME:
            return tc
    return None
