from app.services.anthropic_provider import AnthropicNarrationProvider
from app.services.ai_provider import NullNarrationProvider
from app.services.provider_registry import get_narration_provider


def test_stub_provider_returns_null() -> None:
    provider = get_narration_provider("stub")
    assert isinstance(provider, NullNarrationProvider)


def test_anthropic_provider_returned_when_configured() -> None:
    provider = get_narration_provider("anthropic", "claude-test-model")
    assert isinstance(provider, AnthropicNarrationProvider)
    assert provider._model == "claude-test-model"


def test_anthropic_provider_uses_default_model_when_none_given() -> None:
    provider = get_narration_provider("anthropic")
    assert isinstance(provider, AnthropicNarrationProvider)
    assert provider._model == "claude-haiku-4-5"


def test_unknown_provider_falls_back_to_null() -> None:
    provider = get_narration_provider("nonexistent-thing")
    assert isinstance(provider, NullNarrationProvider)
