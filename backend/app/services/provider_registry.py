from app.services.ai_provider import NarrationProvider, NullNarrationProvider


def get_narration_provider(provider_name: str) -> NarrationProvider:
    if provider_name in {"openai", "anthropic", "stub"}:
        return NullNarrationProvider()
    return NullNarrationProvider()
