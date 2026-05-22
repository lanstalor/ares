"""PlayerAgent: roleplays as Mara of Cimmeria, generating one action per GM turn."""

from llm import TextGenerator

SYSTEM_PROMPT = """\
You are Mara of Cimmeria, a highRed relay technician on Ganymede in 728 PCE.
You are working at Surface Relay Tower 19 under Gray supervision. The Weaver has ordered you
to recover the ghost packet before Pelsin's diagnostic scrub erases it.
You are blunt, practical, and protective of Oran. You do not trust Golds, Grays, or Coppers.

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

        try:
            text = self._llm.generate(
                system=SYSTEM_PROMPT,
                user=f"Recent GM responses:\n\n{context}\n\nWhat do you do next?",
            )
        except Exception:
            return (
                "I keep my hands steady, protect the ghost packet, and use the nearest "
                "routine maintenance step as cover for my next move."
            )
        # Guardrail: cap at first sentence if suspiciously long
        if len(text.split()) > 50:
            sentences = text.split(". ")
            text = sentences[0].strip()
            if not text.endswith("."):
                text += "."
        return text
