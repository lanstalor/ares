from dataclasses import dataclass, field
from typing import Protocol

from app.services.consequence_applier import Consequences


@dataclass
class NarrationRequest:
    campaign_name: str
    current_date_pce: int
    player_input: str
    player_safe_brief: str
    hidden_gm_brief: str


@dataclass
class NarrationResponse:
    narrative: str
    player_safe_summary: str
    consequences: Consequences = field(default_factory=Consequences)
    suggested_actions: list[dict] = field(default_factory=list)
    scene_participants: list[dict] = field(default_factory=list)


class NarrationProvider(Protocol):
    def narrate(self, request: NarrationRequest) -> NarrationResponse:
        ...

    def clarify(self, request: NarrationRequest) -> str:
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
            consequences=Consequences(),
        )

    def clarify(self, request: NarrationRequest) -> str:
        return (
            "The GM clarification engine is not implemented yet. "
            "In a real session, I would explain the current story state, "
            "break the fourth wall if needed, and help you understand the scene "
            "without advancing the game clocks."
        )
