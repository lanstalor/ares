# Project Ares — Agent Context

**Read this file first.** It is the single authoritative bootstrap for all coding sessions on this repository, regardless of which AI agent is running.

---

## Latest Session Summary

Date: 2026-05-06

### ✅ Wave 2 Sprint 1 Complete — A2, B2, C2 All Merged to Main

**Delivered (all merged):**
- **A2: Itemized Inventory** (merged commit 67700ab)
  - Item model (tags, quantity, rarity, equipped status).
  - Inventory delta consequences (items_added, items_removed).
  - GM engine integration via consequence applier.
  - Frontend rendering in SceneBackdrop.
  
- **B2: Scene Art Generation Pipeline** (merged commit bf4b759)
  - SceneArt cache model + Alembic migration.
  - Player-safe scene art service using MediaProvider (B1).
  - API endpoints: list/current/regenerate.
  - Backend file serving for generated PNGs.
  - Turn-triggered generation + frontend fetch/render with fallback.
  
- **C2: Operator React Admin App** (merged commit 1f2b994)
  - Separate `/admin` route (lazy-loaded, token-gated).
  - Sidebar navigation + 5 entity pages (Campaign, Objectives, Clocks, Secrets, NPCs).
  - Reusable EntityTable + EntityModal for CRUD workflows.
  - useOperatorApi hook with tests.
  - Full integration testing + Playwright screenshots.

**Status:**
- **Wave 1** (A1, B1, C1) — ✅ Finished & merged.
- **Wave 2 Sprint 1** (A2, B2, C2) — ✅ **All merged to main.**
- Backend tests: 105 passing.
- All hard constraints respected (no hidden-state leaks, canon guard intact).

**Ready for:**
- Wave 3 Sprint 1 kickoff: A3, B3, C3
- Next agent session can start fresh with clean main branch.

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
- **GM Engine**: Consequence-aware turn loop (clocks, secrets, locations, objective updates, dice rolls, inventory).
- **Dice System**: Attribute check primitive (Strength, Cunning, Will, Charm, Tech) + feed rendering (Slice A1).
- **Inventory**: Itemized Item model (tags, quantity, rarity, equipped) wired to consequences + frontend rendering (Slice A2).
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
