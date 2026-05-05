from types import SimpleNamespace

from app.services.media_provider import (
    MediaRequest,
    OpenAIImageProvider,
    ReplicateImageProvider,
    StubMediaProvider,
)


def test_stub_media_provider_returns_local_placeholder() -> None:
    provider = StubMediaProvider(placeholder_url="/scene-art/test.png")

    response = provider.generate_image(
        MediaRequest(
            prompt="A Red mining district under amber dust",
            kind="scene_art",
            cache_key="lykos-station",
        )
    )

    assert response.provider == "stub"
    assert response.model is None
    assert response.media_type == "image/png"
    assert response.url == "/scene-art/test.png"
    assert response.cache_key == "lykos-station"


def test_openai_image_provider_uses_injected_client() -> None:
    calls = []

    class Images:
        def generate(self, **kwargs):
            calls.append(kwargs)
            return SimpleNamespace(
                data=[
                    SimpleNamespace(
                        url="https://example.test/image.png",
                        b64_json=None,
                        revised_prompt="revised",
                    )
                ]
            )

    client = SimpleNamespace(images=Images())
    provider = OpenAIImageProvider(client=client, model="gpt-image-test")

    response = provider.generate_image(
        MediaRequest(
            prompt="Lykos station maintenance deck",
            subject="Davan of Tharsis",
            negative_prompt="forbidden canon cameos",
            width=512,
            height=768,
        )
    )

    assert calls[0]["model"] == "gpt-image-test"
    assert calls[0]["size"] == "512x768"
    assert "Subject: Davan of Tharsis" in calls[0]["prompt"]
    assert "Avoid: forbidden canon cameos" in calls[0]["prompt"]
    assert response.provider == "openai"
    assert response.url == "https://example.test/image.png"
    assert response.revised_prompt == "revised"


def test_replicate_image_provider_uses_injected_client() -> None:
    calls = []

    class Client:
        def run(self, model, input):
            calls.append((model, input))
            return ["https://example.test/replicate.png"]

    provider = ReplicateImageProvider(client=Client(), model="owner/model")

    response = provider.generate_image(
        MediaRequest(
            prompt="A rebel terminal",
            width=640,
            height=640,
        )
    )

    assert calls == [
        (
            "owner/model",
            {
                "prompt": "A rebel terminal",
                "width": 640,
                "height": 640,
            },
        )
    ]
    assert response.provider == "replicate"
    assert response.url == "https://example.test/replicate.png"
