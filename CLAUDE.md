# Project Ares — Agent Context

**Read this file first.** It is the single authoritative bootstrap for all coding sessions on this repository, regardless of which AI agent is running.

---

## Latest Session Summary

Date: 2026-05-22

### ✅ Latest Review / Handoff State

**Merged since the focus-group branch:**
- **FG1-FG3 focus-group build** — Mara of Cimmeria / Relay 19 intro, blocker patch, HITL simulation, merged via PR #15.
- **Chat quality / pacing / memory** — `stall_counter`, `last_scene_state`, `narrative_summary`, repeated-phrase banlist, GM-only memory injection, and stronger scene-change prompt discipline, merged via PR #16.
- **A4 turn-based combat mode** — GM-driven combat enter/progress/exit, initiative order, damage summary, hidden combat context, API exposure, and frontend CombatPanel, merged via PR #17.
- **Narration quality follow-up** — Length discipline, plain-language prompt rules, Section 14 world-bible rewrite, and a 20-turn playtester report.

**Important review fixes from 2026-05-22:**
- Canon-guard failures must not persist `last_scene_state`, `narrative_summary`, or `combat_state`.
- `tools/playtester/player.py` and `tools/playtester/evaluator.py` must use Mara / Relay 19 context, not the old Davan / Lykos premise.
- The 2026-05-13 report is useful as raw GM transcript evidence, but its evaluator notes/scores are suspect because the evaluator prompt still referenced Davan/Lykos.

**Current validation target:**
- Rerun the 20-turn playtester with Mara/Relay 19 prompts after OpenAI quota is available. The OpenAI benchmark is preferred for experience quality; use Anthropic only as an explicitly documented fallback.
- Compare response length, banned compound terms, repetition, flow, and engagement against `tools/playtester/reports/2026-05-13-01-10.md`.
- Latest partial rerun: `tools/playtester/reports/2026-05-22-00-24.md` captured 9 scored turns before the backend GM provider and holistic evaluator hit OpenAI quota errors.
- A later 2026-05-22 OpenAI smoke with `.env` sourced confirmed backend GM calls and evaluator calls still return `insufficient_quota`; `tools/playtester/run.py` now aborts repeated initial turn failures without writing empty benchmark reports.
- Record results under `tools/playtester/reports/` and update `docs/development/master-plan.md` plus the relevant workstream doc before handing off.

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
- **Combat Mode**: GM-driven turn-based combat state, initiative ordering, damage summary, hidden combat context, and frontend CombatPanel (Slice A4).
- **Chat Quality / Memory**: scene-state tracking, narrative summary, repeated-phrase banlist, GM-only memory reinjection, and anti-stall counter.
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
