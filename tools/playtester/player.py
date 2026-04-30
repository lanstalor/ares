"""PlayerAgent: roleplays as Davan o' Tharsis, generating one action per GM turn."""

from llm import TextGenerator

SYSTEM_PROMPT = """\
You are Davan o' Tharsis, a lowRed miner working the Melt at Lykos station, 728 PCE.
You are cautious, observant, and quietly ambitious. You don't trust Golds or their proxies.
You speak plainly and think practically.

Your job: given the GM's recent responses, write ONE short player action in first person ("I ...").
1-2 sentences maximum. Stay in character. Don't narrate outcomes — only declare intent or speech.
Don't ask the GM questions directly; act or speak instead.
Respond with ONLY the action text, nothing else."""


class PlayerAgent:
    def __init__(self, llm: TextGenerator):
        self._llm = llm

    def next_action(self, recent_gm_responses: list[str]) -> str:
        context_parts = []
        for i, resp in enumerate(recent_gm_responses):
            context_parts.append(f"[Turn {i + 1}]\n{resp}")
        context = "\n\n".join(context_parts)

        text = self._llm.generate(
            system=SYSTEM_PROMPT,
            user=f"Recent GM responses:\n\n{context}\n\nWhat do you do next?",
        )
        # Guardrail: cap at first sentence if suspiciously long
        if len(text.split()) > 50:
            sentences = text.split(". ")
            text = sentences[0].strip()
            if not text.endswith("."):
                text += "."
        return text
