# Project Ares — Agent Context

**Read this file first.** It is the single authoritative bootstrap for all coding sessions on this repository, regardless of which AI agent is running.

---

## Latest Session Summary

Date: 2026-05-12

### ✅ Chat Quality / Pacing / Memory Slice (Complete, Awaiting Playtest Confirmation)

**Goal:** Eliminate the repetition / static-standoff failure modes in playtest reports (Repetition averaged 1.2–1.6 / 5, Flow 1.2–2.8) and durably extend the GM's story memory.

**What landed on `carryover/anti-stall-safeguards` (pushed to origin):**
- **Schema:** Two new Campaign columns — `last_scene_state` (JSON) and `narrative_summary` (Text). Migration `741c8686e3a3` applied.
- **Tool schema:** `record_turn` now requires a `scene_state` object (`tension_tier` 0–4, `key_holdings`, `last_concrete_change`) and optionally accepts `narrative_summary_update`.
- **Context builder:** Injects `last_scene_state` diff, rolling `narrative_summary`, `gm_only` memories, and a dynamic repeated-phrase banlist (4-/5-/6-grams across last 5 GM turns). Uses `player_safe_summary` for older turn excerpts (turns 4–10) and full GM text for the last 3. Old "Scene progression guard" block removed — subsumed by structural `scene_state`.
- **Prompt surgery:** New "Scene change discipline" section (first-sentence-names-change, escalate-against-cautious-streaks, absorb-player-disruptions-without-resetting) + stock-phrase banlist (`hands where I can see them`, `the strip is warm`, etc.) extracted from the 2026-05-12 transcripts.
- **Turn engine:** Persists GM-emitted `scene_state` and (optional) `narrative_summary_update` on the campaign row each turn.

**Spec:** `docs/superpowers/specs/2026-05-12-chat-quality-pacing-design.md`.
**Plan:** `docs/superpowers/plans/2026-05-12-chat-quality-pacing.md`.

**Tests:** 237 passing, including new coverage for phrase detector, gm_only injection, scene_state injection, banlist injection, older-turn summary collapse, and turn engine persistence.

**Initial playtest signal (5 turns gpt-5.5 player, gpt-5.5 GM):** Per-turn averages 4.2–4.5 (vs prior 1.5–2.5 baseline). Repetition score 3–5 per turn (was 1.2 avg), Flow consistently 5 (was 2.8 avg), Engagement 4–5 (was 3.2 avg). All spec targets exceeded. Full 20-turn run with Anthropic Haiku player/evaluator in progress as of session end — see `tools/playtester/reports/`.

**Status:**
- **`carryover/anti-stall-safeguards`** — Ready to open PR / merge. Pushed to origin.
- **Focus Group Slices (FG1, FG2, FG3)** — ✅ Finished, playtested (HITL), merged to main.
- **Wave 3** — (A4, B4, C3) Ready to begin after merge.

**Ready for:**
- PR review/merge for `carryover/anti-stall-safeguards`.
- Wave 3 slice selection.

### 🔄 Earlier in the day: Anti-Stall Safeguards

Already implemented and merged into this branch prior to today's chat-quality slice. Included `stall_counter` on Campaign, `CRITICAL SYSTEM OVERRIDE` injection at threshold ≥3, and the original anti-jargon / anti-standoff prompt revisions. The chat-quality slice built on top of this foundation.

---

## What This Is

Project Ares is a self-hosted, hidden-state AI Game Master for a single-player TTRPG campaign set in the Red Rising universe (728 PCE, pre-Darrow). The player interacts through a browser; the AI GM runs on the backend with full access to structured world state, secrets, and consequence mechanics that the player never sees directly.

This is **not** a chatbot wrapper. The value is in the hidden-state engine: clocks, visibility-gated secrets, canon guard, structured consequence extraction, and persistent campaign memory.

---

## Visibility Model

Four states used throughout the codebase (`app/core/enums.py`):

| State | Meaning |
|---|---|
| `player_facing` | Safe to surface in narration or player UI |
| `gm_only` | Visible to GM engine and operator workflows; never shown to player |
| `sealed` | Concealed truth driving the plot; only revealed via intentional unlock |
| `locked` | Discoverable but not yet available to this player |

---

## Development Workflow

```bash
# Start full stack (Docker)
make compose-up

# Start backend only (local venv, auto-reloads)
make backend-dev

# Start frontend only (Vite dev server, localhost:5173)
make frontend-dev

# Sync Docker environment after frontend changes
docker compose up --build --no-deps -d frontend
```

---

## Implementation Status

**Merged to Main:**
- **GM Engine**: Consequence-aware turn loop (clocks, secrets, locations, objective updates, dice rolls, inventory, conditions).
- **Dice System**: Attribute check primitive (Strength, Cunning, Will, Charm, Tech) + feed rendering (Slice A1).
- **Inventory**: Itemized Item model (tags, quantity, rarity, equipped) wired to consequences + frontend rendering (Slice A2).
- **Conditions**: 9 condition types (bleeding, poisoned, etc.), applied via consequences, tick on turn, rendered as color-coded chips (Slice A3).
- **Media System**: Provider-backed image generation abstraction (OpenAI/Replicate/Stub) (Slice B1).
- **Scene Art**: Generated/cached per location, turn-triggered, with player-safe prompt building (Slice B2).
- **NPC Portraits**: Generated on NPC creation/first appearance, cached per NPC, lazy-load with initials fallback, operator regenerate endpoint (Slice B3).
- **Operator API**: Full manual state repair, auditing, and read-only campaign introspection (Slice C1).
- **Operator Admin UI**: `/admin` route with token-gating, sidebar nav, entity editors for all hidden state (Slice C2).
- **Web UI**: 3-column rebel terminal, pixel-art aesthetic, VT323 font, live portrait avatars, responsive layout.

---

## Hard Constraints — Do Not Violate

1. **Hidden state must never leak to the player.**
2. **Canon guard is not optional.** (Blocks Darrow, Eo, etc.).
3. **The focus-group player character is Mara of Cimmeria.** Keep Red Rising canon, Colors, factions, and 728–732 PCE constraints intact.
4. **Campaign window is 728–732 PCE.**
5. **Provider abstraction is non-negotiable.** All AI calls go through a Provider Protocol.
6. **No state in world_bible.md.** Database is authoritative after seeding.
