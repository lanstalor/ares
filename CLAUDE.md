# Project Ares — Agent Context

**Read this file first.** It is the single authoritative bootstrap for all coding sessions on this repository, regardless of which AI agent is running.

---

## Latest Session Summary

Date: 2026-05-06

### Wave 2 Sprint — Slices B2 + C2 Completed; Ready for Full Review & Merge

**Delivered:**
- **B2: Scene Art Generation Pipeline** (merged to main, commit bf4b759)
  - SceneArt cache model + Alembic migration.
  - Player-safe scene art prompt/service using MediaProvider (B1).
  - API endpoints: list/current/regenerate scene art.
  - Backend file serving for generated b64 PNGs.
  - Turn-triggered scene art generation on location changes.
  - Frontend fetch/render with static fallback, mobile stacking fix.
  - 105 backend tests passing; all verification checks ✅.

- **C2: Operator React Admin App** (draft PR #14 ready for review)
  - Separate `/admin` route (lazy-loaded from main app).
  - Token-gated login (localStorage-persisted ARES_OPERATOR_TOKEN).
  - Sidebar nav + 5 entity pages: Campaign, Objectives, Clocks, Secrets, NPCs.
  - Reusable EntityTable + EntityModal components for CRUD workflows.
  - Single source of truth: full state from C1 GET /operator/campaigns/{id}/full-state.
  - Refetch after PATCH to keep UI in sync.
  - 14 implementation tasks completed via subagent-driven-development.
  - Full integration testing + Playwright screenshots (desktop + mobile).

**Status:**
- **Wave 1** (Foundations A1, B1, C1) — ✅ **Finished & merged**.
- **Wave 2 Sprint 1** (A2, B2, C2) — ✅ **A2 & B2 merged; C2 in draft PR #14**.
- All tests passing (105 backend tests).
- Ready for full wave 2 review before pushing C2 to main.

**Next Steps (Session Priority):**
1. **Review A2, B2, C2** — Ensure all three slices meet spec/quality bar before final merge.
2. **Merge C2** (PR #14) once review passes.
3. **Update CLAUDE.md** with A2/B2/C2 in "Recently Finished" and implementation status.
4. **Reset for next wave** (Track A: A3, Track B: B3, Track C: C3).

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
- **Operator API**: Full manual state repair, auditing, and read-only campaign introspection (Slice C1).
- **Web UI**: 3-column rebel terminal, pixel-art aesthetic, VT323 font, live portrait avatars, responsive layout.

**In Draft PR (C2):**
- **Operator Admin UI**: `/admin` route with token-gating, sidebar nav, entity editors for all hidden state (Objectives, Clocks, Secrets, NPCs, Campaign metadata).

---

## Hard Constraints — Do Not Violate

1. **Hidden state must never leak to the player.**
2. **Canon guard is not optional.** (Blocks Darrow, Eo, etc.).
3. **The player character is Davan of Tharsis.**
4. **Campaign window is 728–732 PCE.**
5. **Provider abstraction is non-negotiable.** All AI calls go through a Provider Protocol.
6. **No state in world_bible.md.** Database is authoritative after seeding.
