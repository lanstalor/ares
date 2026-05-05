from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Protocol


MediaKind = Literal["scene_art", "npc_portrait", "generic"]


@dataclass
class MediaRequest:
    prompt: str
    kind: MediaKind = "generic"
    subject: str | None = None
    negative_prompt: str | None = None
    width: int = 1024
    height: int = 1024
    cache_key: str | None = None


@dataclass
class MediaResponse:
    provider: str
    model: str | None
    media_type: str
    url: str | None = None
    b64_json: str | None = None
    revised_prompt: str | None = None
    cache_key: str | None = None


class MediaProvider(Protocol):
    def generate_image(self, request: MediaRequest) -> MediaResponse:
        ...


class StubMediaProvider:
    def __init__(
        self,
        *,
        placeholder_url: str = "/scene-art/mars_district.png",
    ) -> None:
        self._placeholder_url = placeholder_url

    def generate_image(self, request: MediaRequest) -> MediaResponse:
        return MediaResponse(
            provider="stub",
            model=None,
            media_type="image/png",
            url=self._placeholder_url,
            revised_prompt=request.prompt,
            cache_key=request.cache_key,
        )


class OpenAIImageProvider:
    def __init__(
        self,
        *,
        client: Any | None = None,
        model: str = "gpt-image-1",
    ) -> None:
        if not model:
            raise ValueError("OpenAIImageProvider requires a non-empty model.")
        self._client = client
        self._model = model

    def _get_client(self) -> Any:
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI()
        return self._client

    def generate_image(self, request: MediaRequest) -> MediaResponse:
        client = self._get_client()
        response = client.images.generate(
            model=self._model,
            prompt=_compose_prompt(request),
            size=f"{request.width}x{request.height}",
            n=1,
        )
        image = response.data[0]
        return MediaResponse(
            provider="openai",
            model=self._model,
            media_type="image/png",
            url=getattr(image, "url", None),
            b64_json=getattr(image, "b64_json", None),
            revised_prompt=getattr(image, "revised_prompt", None),
            cache_key=request.cache_key,
        )


class ReplicateImageProvider:
    def __init__(
        self,
        *,
        client: Any | None = None,
        model: str = "black-forest-labs/flux-schnell",
    ) -> None:
        if not model:
            raise ValueError("ReplicateImageProvider requires a non-empty model.")
        self._client = client
        self._model = model

    def _get_client(self) -> Any:
        if self._client is None:
            import replicate

            self._client = replicate.Client()
        return self._client

    def generate_image(self, request: MediaRequest) -> MediaResponse:
        client = self._get_client()
        output = client.run(
            self._model,
            input={
                "prompt": _compose_prompt(request),
                "width": request.width,
                "height": request.height,
            },
        )
        url = output[0] if isinstance(output, list) and output else output
        return MediaResponse(
            provider="replicate",
            model=self._model,
            media_type="image/png",
            url=str(url) if url is not None else None,
            revised_prompt=request.prompt,
            cache_key=request.cache_key,
        )


def _compose_prompt(request: MediaRequest) -> str:
    prompt_parts = [request.prompt.strip()]
    if request.subject:
        prompt_parts.append(f"Subject: {request.subject.strip()}")
    if request.negative_prompt:
        prompt_parts.append(f"Avoid: {request.negative_prompt.strip()}")
    return "\n".join(part for part in prompt_parts if part)
