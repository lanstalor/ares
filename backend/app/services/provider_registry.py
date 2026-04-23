from app.services.ai_provider import NarrationProvider, NullNarrationProvider
from app.services.anthropic_provider import AnthropicNarrationProvider


def get_narration_provider(provider_name: str) -> NarrationProvider:
    if provider_name == "anthropic":
        return AnthropicNarrationProvider()
    return NullNarrationProvider()
