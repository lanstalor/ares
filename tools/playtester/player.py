"""PlayerAgent: roleplays as Davan o' Tharsis, generating one action per GM turn."""

import anthropic

SYSTEM_PROMPT = """\
You are Davan o' Tharsis, a lowRed miner working the Melt at Lykos station, 728 PCE.
You are cautious, observant, and quietly ambitious. You don't trust Golds or their proxies.
You speak plainly and think practically.

Your job: given the GM's recent responses, write ONE short player action in first person ("I ...").
1-2 sentences maximum. Stay in character. Don't narrate outcomes — only declare intent or speech.
Don't ask the GM questions directly; act or speak instead.
Respond with ONLY the action text, nothing else."""


class PlayerAgent:
    def __init__(self, client: anthropic.Anthropic):
        self._client = client

    def next_action(self, recent_gm_responses: list[str]) -> str:
        context_parts = []
        for i, resp in enumerate(recent_gm_responses):
            context_parts.append(f"[Turn {i + 1}]\n{resp}")
        context = "\n\n".join(context_parts)

        message = self._client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=200,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Recent GM responses:\n\n{context}\n\nWhat do you do next?",
                }
            ],
        )
        text = message.content[0].text.strip()
        # Guardrail: cap at first sentence if suspiciously long
        if len(text.split()) > 50:
            sentences = text.split(". ")
            text = sentences[0].strip()
            if not text.endswith("."):
                text += "."
        return text
