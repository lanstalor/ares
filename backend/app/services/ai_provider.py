from dataclasses import dataclass
from typing import Protocol

from app.models.campaign import Campaign


@dataclass
class NarrationRequest:
    campaign: Campaign
    player_input: str
    context_excerpt: str


@dataclass
class NarrationResponse:
    narrative: str
    player_safe_summary: str


class NarrationProvider(Protocol):
    def narrate(self, request: NarrationRequest) -> NarrationResponse:
        ...


class NullNarrationProvider:
    def narrate(self, request: NarrationRequest) -> NarrationResponse:
        return NarrationResponse(
            narrative=(
                "The hidden-state GM engine is not implemented yet. "
                "This scaffold accepts the action, preserves the API contract, "
                "and is ready for provider-backed narrative resolution."
            ),
            player_safe_summary=f"Player attempted: {request.player_input[:180]}",
        )
