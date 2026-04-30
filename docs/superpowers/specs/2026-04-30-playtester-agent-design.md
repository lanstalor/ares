# Playtester Agent — Design Spec

**Date:** 2026-04-30  
**Status:** Approved

---

## Goal

A fully automated script that simulates a 30-turn Project Ares campaign session, evaluates GM response quality per turn on six UX dimensions, and writes a markdown report. Used to identify prose quality drift, repetition, continuity failures, and pacing problems without manual playtesting.

---

## Architecture

```
tools/playtester/
├── run.py            # entrypoint — orchestrates the full loop
├── player.py         # PlayerAgent: generates Davan's next action via Claude
├── evaluator.py      # EvaluatorAgent: per-turn scoring + holistic summary
├── reporter.py       # assembles scores + holistic into a markdown report
└── reports/          # output directory (gitignored)
    └── YYYY-MM-DD-HH-MM.md
```

---

## Runtime Flow

```
run.py
  → POST /api/v1/seed/world-bible   (creates campaign + seeds world, returns campaign_id)
  → for turn in range(30):
      player.py   → Claude Sonnet   → player_input string
      HTTP POST   → /api/v1/campaigns/{id}/turns → gm_response
      evaluator.py → Claude Sonnet  → TurnScore (6 dims, 1–5 + note)
      print turn summary to stdout
  → evaluator.py → Claude Sonnet    → HolisticReport
  → reporter.py  → write markdown to tools/playtester/reports/
```

All Claude calls are independent (no shared thread). The backend must be running at `localhost:8000` before invoking the script. If a turn HTTP call fails, that turn is skipped and logged; the run continues.

---

## Player Agent (`player.py`)

**Role:** Roleplays as Davan o' Tharsis, generating one player action per turn.

**System prompt (fixed):**
```
You are Davan o' Tharsis, a lowRed miner working the Melt at Lykos 
station, 728 PCE. You are cautious, observant, and quietly ambitious. 
You don't trust Golds or their proxies. You speak plainly.

Your job: given the GM's last response, write ONE short player action 
in first person ("I ..."). 1-2 sentences. Stay in character. Don't 
narrate outcomes — only declare intent or speech. Don't ask the GM 
questions directly; act or speak instead.
```

**Context:** Last 5 GM responses (not the full transcript — mimics realistic player memory, prevents omniscience).

**Model:** `claude-sonnet-4-6`

**Guardrail:** If output exceeds 150 tokens, truncate to the first sentence and continue.

---

## Evaluator Agent (`evaluator.py`)

### Per-Turn Scoring

Called immediately after each GM response. Receives: the player input, the GM response, and the full transcript so far as a list of `{turn_number, player_input, gm_response}` objects (for repetition and continuity checks).

**Output schema (JSON, parsed by the script):**
```json
{
  "realism": { "score": 4, "note": "Copper overseer voice is credible" },
  "continuity": { "score": 3, "note": "Forgot Mira was described as hostile" },
  "engagement": { "score": 5, "note": "Quota threat lands well" },
  "repetition": { "score": 2, "note": "'air tastes of iron' appeared in turns 3 and 5" },
  "quality": { "score": 4, "note": "Clean prose; one run-on sentence" },
  "flow": { "score": 5, "note": "Good length, ends at natural decision point" }
}
```

**Scoring rubric:**

| Dimension | What it measures |
|---|---|
| Realism | Fits 728 PCE Red Rising setting — no anachronisms, correct caste voice, plausible tech and social dynamics |
| Continuity | Acknowledges prior events, NPCs, and location; doesn't contradict established facts |
| Engagement | Pulls the player forward — stakes feel real, scene has tension or intrigue |
| Repetition | No recycled phrases, sentence openers, atmospheric beats, or NPC gestures vs. prior turns |
| Dialogue/Narrative quality | Prose clarity, caste-appropriate voice, sentence rhythm, avoids banned patterns (interiority, similes, editorial metaphors) |
| Turn flow | Length calibrated to action scope, ends at a natural decision point, doesn't over-explain |

**Model:** `claude-sonnet-4-6`

### Holistic Summary

Called once at the end with the full 30-turn transcript + all per-turn scores.

**Output (free-form markdown):**
- Arc summary: did the story go somewhere interesting?
- Worst recurring issues (patterns, not one-offs)
- Best moments (specific turns worth noting)
- Average score per dimension across all turns
- Top 3 actionable recommendations for improving the GM system prompt

---

## Reporter (`reporter.py`)

Assembles per-turn scores and holistic output into a single markdown file.

**Report structure:**
```markdown
# Ares Playtester Report — 2026-04-30 14:22

## Run Summary
- Turns: 30
- Campaign ID: abc123
- Model: claude-sonnet-4-6
- Backend: localhost:8000

## Per-Turn Log

### Turn 1
**Player:** I check the quota board before heading to the drill face.
**GM:** [gm_response text]

| Dimension | Score | Note |
|---|---|---|
| Realism | 4 | ... |
...
**Overall: 4.2**

---
[repeat for all 30 turns]

## Holistic Analysis
[holistic markdown output]
```

---

## Dependencies

Listed in `tools/playtester/requirements.txt`:
- `httpx` — HTTP client for backend calls
- `anthropic` — Claude API
- `python-dotenv` — reads `ANTHROPIC_API_KEY` from repo root `.env`

---

## Running It

```bash
# Requires backend running at localhost:8000
make backend-dev   # or make compose-up

# From repo root
python tools/playtester/run.py
```

Report saves to `tools/playtester/reports/YYYY-MM-DD-HH-MM.md` automatically.

---

## Out of Scope

- Persisting playtester runs to the database
- Interactive mode or mid-run steering
- Evaluating the player input quality (only GM responses are scored)
- Running without a live backend
