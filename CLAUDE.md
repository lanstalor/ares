# Project Ares — Agent Context

**Read this file first.** It is the single authoritative bootstrap for all coding sessions on this repository, regardless of which AI agent is running.

---

## Latest Session Summary

Date: 2026-05-07

### ✅ A3: Conditions System Completed

**Delivered:**
- **A3: Conditions + Status Effects** (ready to merge)
  - ConditionType enum (9 types: bleeding, poisoned, ident_flagged, wounded, exhausted, stunned, disarmed, prone, panicked).
  - Condition model + Alembic migration (campaign/character FK, duration tracking, source attribution).
  - ConditionService (apply, remove, tick, query).
  - Consequence integration: `ConditionUpdate` consequences → automatic application.
  - Turn resolution: `process_conditions()` decrements/expires on each turn.
  - ParticipantStrip rendering: color-coded condition chips below character name.
  - API fix: selectinload(Character.conditions) → conditions now returned in campaign state.
  - 70+ condition tests, 215 total tests passing.
  - Desktop (1366×1024) and mobile (390×844) screenshots captured.

**Status:**
- **Wave 1** (A1, B1, C1) — ✅ Finished & merged.
- **Wave 2 Sprint 1** (A2, B2, C2) — ✅ Finished & merged.
- **Wave 2 Sprint 2** (A3) — ✅ Complete. B3, C3 in parallel.
- Backend tests: 215 passing (70+ condition-specific).
- All hard constraints verified (hidden state safe, canon guard intact, stub provider works offline).

**Ready for:**
- A3 to merge to main.
- B3 and C3 completion.
- Wave 3 Sprint 1 planning.

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
3. **The player character is Davan of Tharsis.**
4. **Campaign window is 728–732 PCE.**
5. **Provider abstraction is non-negotiable.** All AI calls go through a Provider Protocol.
6. **No state in world_bible.md.** Database is authoritative after seeding.
