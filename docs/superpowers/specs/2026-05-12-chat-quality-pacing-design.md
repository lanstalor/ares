# Chat Quality, Pacing, and Memory — Design Specification

**Date:** 2026-05-12
**Track:** Carryover (post anti-stall)
**Goal:** Eliminate the repetition / static-standoff failure mode visible in 2026-05-12 playtest reports and durably extend the GM's story memory across long campaigns.

---

## Problem Statement

The 2026-05-12 playtester transcripts score average **Repetition 1.2–1.6 / 5** and **Flow 1.2–2.8 / 5**. The GM cycles the same action beats turn after turn ("hands where I can see them", "wand trained", "the strip is warm"). When the player escalates with a bold action — grabbing the lacquered strip in Turn 6, for example — the GM does not let the new power state stick; it reasserts the prior standoff at the same tension level.

Root causes:

1. **Truncated history.** `context_builder.py` feeds the GM only 300 chars of each prior GM response. The GM cannot see what it already wrote and so re-narrates the same facts.
2. **No explicit scene state.** "Change one concrete fact" is a prose rule, not a structural constraint. The GM nudges a single detail and calls it progress.
3. **No phrase-level repetition tracking.** The prompt bans repeated NPC tells but not the action loops that dominate the transcripts.
4. **Memory bleeds out after 10 turns.** `gm_only` memories are generated but never re-injected. `player_safe_summary` exists on every Turn but is unused. Anything from turn 11+ is gone.

---

## Overview

Four coordinated changes, all landing in one slice:

- **A — Context Expansion.** Richer turn excerpts plus a session-scoped repeated-phrase banlist injected into the hidden brief.
- **B — Scene State Tracker.** The GM emits a tiny structured `scene_state` each turn (tension tier, who holds what, what changed). It is persisted and surfaced as a diff next turn, forcing progression to be explicit.
- **C — Prompt Surgery.** Specific banlist of recurring stock phrases, plus three new pacing rules: first-sentence-must-name-change, escalate-against-cautious-streaks, absorb-player-disruptions.
- **D — Memory Architecture.** Wire `gm_only` memories into the hidden brief, use `player_safe_summary` for older turn history, add a rolling `narrative_summary` on Campaign for long-term arc memory.

All four ship together. They are complementary: A and D give the GM the data, B gives it the structural pressure, C gives it the rules.

---

## Architecture

### Approach A — Context Expansion

**In `context_builder.py`:**

- Player input excerpt: `120 → 200` chars.
- Most recent 3 GM responses: include **full text** (not truncated).
- GM responses 4–10: replaced by the existing `Turn.player_safe_summary` (1–2 sentence summary, already generated each turn). When `player_safe_summary` is null on a legacy turn, fall back to a 300-char `gm_response` excerpt.
- New helper: `_extract_repeated_phrases(recent_turns: list[Turn]) -> list[str]`
  - Scan the last 5 GM responses.
  - Generate 4-gram and 5-gram word sequences (lowercase, punctuation stripped).
  - Surface phrases appearing in 2+ distinct turns.
  - Return the top 6 by frequency (tie-broken by length, longer wins).
  - Injected into the hidden brief under a `Banned phrases this scene (already overused):` header.

### Approach B — Scene State Tracker

**Tool schema additions** in `anthropic_provider.py::_TOOL_SCHEMA`:

```
scene_state: {
  tension_tier: integer (0–4),       # 0 calm, 1 charged, 2 contested, 3 escalating, 4 breaking
  key_holdings: string,              # short free-form: "Mara holds strip; Gray holds wand"
  last_concrete_change: string,      # one short sentence describing what changed this turn
}
```

`scene_state` is **required** on every narrate call (forcing function — the GM has to articulate progression to satisfy the schema).

**Persistence** — add a column on `Campaign`:

```
last_scene_state: JSON  (nullable)
```

The turn engine writes the GM's emitted `scene_state` to `campaign.last_scene_state` after each turn. The context builder injects the previous turn's `last_scene_state` into the hidden brief under `Scene state at start of this turn:`.

The GM sees what it said the state was last turn and must update it (which it can only meaningfully do by changing the fiction).

**Tier semantics — surfaced to GM in the prompt:**

- 0 calm: no immediate pressure
- 1 charged: tension present, no overt threat
- 2 contested: opposed will, surveillance, leverage in play
- 3 escalating: weapon drawn, alarm, witness, deadline running
- 4 breaking: violence, capture, reveal — must resolve this or next turn

Rule: tension tier may stay flat or rise; it may only drop when the fiction explicitly de-escalates (party departs, threat neutralized). The prompt enforces this.

### Approach C — Prompt Surgery

In `_SYSTEM_PROMPT` (`anthropic_provider.py`), add three rules and a phrase banlist.

**New "Scene change discipline" section:**

- The **first sentence** of every GM response must name the concrete thing that changed since the player's prior turn — a new fact revealed, a new threat, a position shift, a piece of information. Do NOT lead with re-describing what is the same.
- If the player's last 2 inputs were cautious or incremental (small movements, hand positions, requests for time, clarifying questions), the next GM turn must escalate beyond the player's pace, independent of the player's current input. The world moves; the player does not get to set the tempo by hesitation.
- When the player takes a bold or disruptive action — grabbing a contested object, drawing a weapon, fleeing, lying overtly, breaking cover — the resulting power state is the new ground truth. Do not narrate an NPC immediately undoing it or restoring the prior standoff. The next pressure must come from a different angle: consequence, escalation by a new party, environmental shift. Never a reset.

**Phrase banlist** (extracted from 2026-05-12 transcripts):

```
"hands where I can see them"
"keep your/my hands open"
"the wand stays trained / on my chest"
"the strip is warm / hot / getting hotter"
"boots on the rail"
"keep your face out of it"
"keep my head down"
```

These are seeded, not exhaustive. The repeated-phrase detector in Approach A picks up new ones dynamically per session.

**Loosen one existing rule:** the current prompt has heavy bans on "the kind of X that Y" and similar constructions. These remain. No additions to the jargon list — the existing list is sufficient and over-banning was not the failure mode in the transcripts.

### Approach D — Memory Architecture

**Wire `gm_only` memories into the hidden brief.**

In `_render_hidden_gm_brief`, fetch the last 10 `gm_only` memories for this campaign and surface them under `GM-only observations:`. They are already being written by the consequence applier; they just need to be read back.

**Use `player_safe_summary` for older turn history.**

Already covered in Approach A: turns 1–3 get full GM text, turns 4–10 collapse to `player_safe_summary`. This both reduces token cost on older turns and gives the GM a denser semantic representation than a 300-char hard cut.

**Add `narrative_summary` on Campaign.**

```
narrative_summary: Text (nullable, default empty)
```

This is a rolling 2–4 sentence arc summary, updated by the GM via a new optional tool field:

```
narrative_summary_update: string (optional)
```

The GM emits this **only** when a major arc event has occurred (objective completed, location changed, secret revealed, significant NPC shift). The prompt instructs the GM to write it in past tense, third person from the player's perspective, no hidden state.

When emitted, the turn engine overwrites `campaign.narrative_summary` with the new value. It is surfaced in **both** briefs (player-safe and hidden) under `Story so far:`.

No automatic update logic — the GM decides when arc-level summarization is warranted. Stays simple. Avoids embedding/RAG complexity.

---

## Data Model Summary

One new column on `Campaign`:

```
last_scene_state: JSON (nullable)
narrative_summary: Text (nullable)
```

Single Alembic migration.

No new tables. No new models.

---

## Tool Schema Changes

Additions to `record_turn` input schema:

- `scene_state` (required object): `{tension_tier, key_holdings, last_concrete_change}`
- `narrative_summary_update` (optional string)

The Anthropic and OpenAI providers share the schema via `build_tool_schema()`, so both providers update together.

---

## Context Builder Output — New Shape

Hidden GM brief now contains, in order:

1. Objective GM instructions
2. Active clocks
3. **Scene state at start of this turn:** (new, from `campaign.last_scene_state`)
4. **Story so far:** (new, from `campaign.narrative_summary`)
5. **Banned phrases this scene (already overused):** (new, from repeated-phrase detector)
6. Eligible secrets
7. NPCs with hidden agendas
8. **GM-only observations:** (new, from gm_only memories)
9. Stall counter override (if applicable)

The existing "Scene progression guard" block in `_render_hidden_gm_brief` is **removed** — its purpose is subsumed by the structural scene_state diff in #3, which is both more specific and more enforceable.

Player-safe brief gains:

- **Story so far:** (from `campaign.narrative_summary`) — surfaced near the top so the player UI can render it if desired

---

## Testing Strategy

- **Unit tests** in `tests/test_context_builder.py`:
  - `_extract_repeated_phrases` returns expected ngrams when phrases repeat across turns.
  - `gm_only` memories are included in hidden brief and excluded from player-safe brief.
  - `player_safe_summary` is used for turns 4–10 when present.
  - `last_scene_state` is injected into hidden brief when present, omitted when null.
  - `narrative_summary` appears in both briefs when set.

- **Provider tests** in `tests/test_anthropic_provider.py`:
  - Tool schema includes `scene_state` as required and `narrative_summary_update` as optional.
  - Response parsing handles `scene_state` and persists it into the response object.

- **Turn engine tests** in `tests/test_turn_engine.py`:
  - After narrate, `campaign.last_scene_state` is updated with the emitted scene_state.
  - When `narrative_summary_update` is present, `campaign.narrative_summary` is overwritten.
  - When absent, narrative_summary is unchanged.

- **Playtest validation:** Re-run the playtester tool against the same campaign seed. Target metrics:
  - Repetition score: ≥ 3.0 average (current 1.2–1.6)
  - Flow score: ≥ 3.5 average (current 1.2–2.8)
  - Engagement score: ≥ 3.5 average (current 2.4–3.2)

---

## Out of Scope

- RAG / embedding-based memory retrieval. The `embedding_model` column on Memory remains unused. If `narrative_summary` plus 10 recent memories proves insufficient for very long campaigns, a separate slice can add semantic retrieval.
- Operator UI for editing `scene_state` or `narrative_summary`. Both are GM-managed; manual operator override can come later if needed.
- Cross-location NPC pool expansion. Current behavior pulls NPCs from the location's faction only. Worth fixing eventually, but not the cause of the repetition failure mode.
- Loosening any existing prompt rules. The current prose bans (jargon, similes, mind-reading) stay as-is.

---

## Rollout

Single branch, single PR. Components in dependency order:

1. Alembic migration for new Campaign columns.
2. Model + schema updates.
3. Tool schema additions (provider).
4. Context builder rewrites.
5. Prompt surgery.
6. Turn engine wiring for state persistence.
7. Tests.
8. Playtest run for validation.
