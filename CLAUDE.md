# Project Ares — Agent Context

**Read this file first.** It is the single authoritative bootstrap for all coding sessions on this repository, regardless of which AI agent is running.

---

## Latest Session Summary

Date: 2026-05-05

### Wave 1 Consolidation — Slices A1, B1, C1 Merged + UI Restore

**Delivered (all merged to main, commit 9838d11):**
- **A1: Dice + Skill Check Primitive:**
  - Added attribute check primitive (Strength, Cunning, Will, Charm, Tech).
  - Integrated into Anthropic and OpenAI providers.
  - New `system-roll` feed events with amber/copper styling.
  - Gated behind `ARES_ENABLE_DICE` (default off).
- **A2: Itemized Inventory:**
  - `Item` model added (tags, quantity, rarity, equipped status).
  - GM engine wired to add/update/remove items via consequences.
  - Rendered in frontend `SceneBackdrop`.
- **B1: MediaProvider Abstraction:**
  - Implemented `MediaProvider` Protocol for image generation.
  - Providers: OpenAI (DALL-E 3), Replicate, and offline Stub.
  - Registry selection via `ARES_MEDIA_PROVIDER` setting.
- **C1: Operator-only API Surface:**
  - `GET /full-state`: Visibility-unfiltered campaign/world data.
  - `PATCH /state`: Manual state repair for any entity (Clocks, Secrets, NPCs, etc.).
  - `GET /audit`: Automated detection of state drift or logic issues.
- **UI Restoration:**
  - Recovered and committed "lost" UI improvements: 3-column layout, portrait avatars, and ARES wordmark.
  - Rebuilt Docker images at 5180 to sync live environment.

**Status:**
- Wave 1 (Mechanical/Sensory/Operator foundations) is **Finished**.
- Slice A2 is **Finished**.
- All tests passing (101 total backend tests).
- Workspace is clean; stale slice worktrees removed.

**Next:**
- **Track A:** A3 (Conditions + status effects)
- **Track B:** B2 (Scene Art Generation pipeline)
- **Track C:** C2 (Operator React App)

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

- **GM Engine**: Consequence-aware turn loop (clocks, secrets, locations, objective updates).
- **Dice System**: Attribute check primitive + feed rendering (Slice A1).
- **Media System**: Provider-backed image generation abstraction (Slice B1).
- **Operator API**: Full manual state repair and auditing (Slice C1).
- **Web UI**: 3-column rebel terminal, pixel-art aesthetic, VT323 font, live portrait avatars.

---

## Hard Constraints — Do Not Violate

1. **Hidden state must never leak to the player.**
2. **Canon guard is not optional.** (Blocks Darrow, Eo, etc.).
3. **The player character is Davan of Tharsis.**
4. **Campaign window is 728–732 PCE.**
5. **Provider abstraction is non-negotiable.** All AI calls go through a Provider Protocol.
6. **No state in world_bible.md.** Database is authoritative after seeding.
