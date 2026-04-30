"""EvaluatorAgent: scores GM responses per-turn and produces a holistic summary."""

import json
import anthropic

DIMENSIONS = ["realism", "continuity", "engagement", "repetition", "quality", "flow"]

PER_TURN_SYSTEM = """\
You are a critical evaluator of AI game master (GM) responses for a single-player TTRPG set in
the Red Rising universe, 728 PCE (pre-Darrow). The player character is Davan o' Tharsis,
a lowRed miner at Lykos station. Score the GM's latest response on six dimensions.

Scoring dimensions (1–5 each):
- realism: Fits 728 PCE Red Rising setting. No anachronisms, correct caste voice, plausible
  technology and social dynamics. 1=egregious anachronism or canon violation, 5=seamless fit.
- continuity: Acknowledges prior events, NPCs, and location. Doesn't contradict established facts.
  1=contradicts established facts, 5=perfect continuity.
- engagement: Pulls the player forward. Stakes feel real, scene has tension or intrigue, not just
  description. 1=flat and passive, 5=compelling and urgent.
- repetition: No recycled phrases, sentence openers, atmospheric beats, or NPC gestures vs prior
  turns. 1=heavy repetition, 5=fully fresh language and beats.
- quality: Prose clarity, caste-appropriate voice, sentence rhythm. Avoids interiority, explanatory
  similes, editorial metaphors, stacked atmospheric filler. 1=poor prose, 5=excellent prose.
- flow: Length calibrated to action scope. Ends at a natural decision point. Doesn't over-explain.
  1=wildly miscalibrated length or weak ending, 5=perfect pacing and landing.

Respond ONLY with a JSON object matching this exact schema, no other text:
{
  "realism":     {"score": <1-5>, "note": "<one short sentence>"},
  "continuity":  {"score": <1-5>, "note": "<one short sentence>"},
  "engagement":  {"score": <1-5>, "note": "<one short sentence>"},
  "repetition":  {"score": <1-5>, "note": "<one short sentence>"},
  "quality":     {"score": <1-5>, "note": "<one short sentence>"},
  "flow":        {"score": <1-5>, "note": "<one short sentence>"}
}"""

HOLISTIC_SYSTEM = """\
You are a critical evaluator reviewing a full 30-turn AI game master session for a single-player
TTRPG set in the Red Rising universe, 728 PCE. The player character is Davan o' Tharsis.
You have the full transcript and per-turn scores. Write a concise holistic analysis in markdown.

Structure your response with exactly these sections:
## Arc Summary
Did the story go somewhere interesting over 30 turns? Assess narrative progression and coherence.

## Worst Recurring Issues
Patterns that appeared across multiple turns (not one-offs). Be specific — quote examples.

## Best Moments
2-3 specific turns that stood out positively. Explain why.

## Score Averages
A markdown table of average scores per dimension across all 30 turns.

## Top 3 Recommendations
Concrete, actionable changes to the GM system prompt that would most improve quality.
Focus on prompt-level fixes, not content changes."""


class TurnScore:
    def __init__(self, data: dict):
        self.data = data

    def average(self) -> float:
        scores = [v["score"] for v in self.data.values()]
        return round(sum(scores) / len(scores), 1)

    def to_markdown_table(self) -> str:
        lines = ["| Dimension | Score | Note |", "|---|---|---|"]
        labels = {
            "realism": "Realism",
            "continuity": "Continuity",
            "engagement": "Engagement",
            "repetition": "Repetition",
            "quality": "Quality",
            "flow": "Flow",
        }
        for key in DIMENSIONS:
            entry = self.data.get(key, {"score": "?", "note": ""})
            lines.append(f"| {labels[key]} | {entry['score']} | {entry['note']} |")
        return "\n".join(lines)


class EvaluatorAgent:
    def __init__(self, client: anthropic.Anthropic):
        self._client = client

    def score_turn(
        self,
        turn_number: int,
        player_input: str,
        gm_response: str,
        transcript: list[dict],
    ) -> TurnScore:
        transcript_text = _format_transcript(transcript)
        user_content = (
            f"Full transcript so far:\n\n{transcript_text}\n\n"
            f"--- Latest Turn ({turn_number}) ---\n"
            f"Player: {player_input}\n"
            f"GM: {gm_response}\n\n"
            "Score the GM response above."
        )
        message = self._client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=600,
            system=PER_TURN_SYSTEM,
            messages=[{"role": "user", "content": user_content}],
        )
        raw = message.content[0].text.strip()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            # Fallback: extract JSON from the response if there's surrounding text
            start = raw.find("{")
            end = raw.rfind("}") + 1
            data = json.loads(raw[start:end]) if start != -1 else _neutral_score()
        return TurnScore(data)

    def holistic_summary(
        self,
        transcript: list[dict],
        scores: list[TurnScore],
    ) -> str:
        transcript_text = _format_transcript(transcript)
        scores_text = _format_scores_summary(scores)
        user_content = (
            f"Full transcript:\n\n{transcript_text}\n\n"
            f"Per-turn scores:\n\n{scores_text}\n\n"
            "Write the holistic analysis."
        )
        message = self._client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            system=HOLISTIC_SYSTEM,
            messages=[{"role": "user", "content": user_content}],
        )
        return message.content[0].text.strip()


def _format_transcript(transcript: list[dict]) -> str:
    parts = []
    for entry in transcript:
        parts.append(
            f"Turn {entry['turn_number']}\n"
            f"Player: {entry['player_input']}\n"
            f"GM: {entry['gm_response']}"
        )
    return "\n\n---\n\n".join(parts)


def _format_scores_summary(scores: list[TurnScore]) -> str:
    lines = []
    for i, score in enumerate(scores, 1):
        dim_parts = ", ".join(
            f"{k}={score.data.get(k, {}).get('score', '?')}" for k in DIMENSIONS
        )
        lines.append(f"Turn {i}: {dim_parts} | avg={score.average()}")
    return "\n".join(lines)


def _neutral_score() -> dict:
    return {dim: {"score": 3, "note": "parse error — defaulted to neutral"} for dim in DIMENSIONS}
