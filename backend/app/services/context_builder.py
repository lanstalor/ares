from app.models.campaign import Campaign


def build_turn_context(campaign: Campaign, player_input: str) -> str:
    return "\n".join(
        [
            f"Campaign: {campaign.name}",
            f"Tagline: {campaign.tagline or 'N/A'}",
            f"Date: {campaign.current_date_pce} PCE",
            "Hidden state is server-managed and omitted from this excerpt.",
            f"Player intent: {player_input}",
        ]
    )
