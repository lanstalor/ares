from app.services.ai_provider import NarrationProvider, NullNarrationProvider
from app.services.anthropic_provider import AnthropicNarrationProvider
from app.services.openai_provider import OpenAINarrationProvider


def get_narration_provider(
    provider_name: str,
    model: str | None = None,
    *,
    enable_dice: bool = False,
) -> NarrationProvider:
    if provider_name == "anthropic":
        kwargs: dict = {"enable_dice": enable_dice}
        if model:
            kwargs["model"] = model
        return AnthropicNarrationProvider(**kwargs)
    if provider_name == "openai":
        kwargs = {"model": model} if model else {}
        return OpenAINarrationProvider(**kwargs)
    return NullNarrationProvider()
