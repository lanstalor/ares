# Project Ares — Agent Context

**Read this file first.** It is the single authoritative bootstrap for all coding sessions on this repository, regardless of which AI agent is running.

---

## Latest Session Summary

Date: 2026-05-12

### 🔄 Anti-Stall Safeguards (In Progress)

**Current Focus:**
- Addressing the LLM GM "Mexican Standoff" loops where it stalls on repetitive micro-actions without pushing the scene forward.
- Swapped active model to `gpt-5.5` in `.env`.
- Rewrote the GM system prompt (`anthropic_provider.py`) to heavily restrict mechanical jargon ("seam", "rip", "lane") and formally BAN static standoffs and mirroring player delay tactics.
- Added a `stall_counter` to the `Campaign` model and database schema to track turns without concrete consequences.
- Updated `turn_engine.py` to reset or increment the counter, and `context_builder.py` to inject a `CRITICAL SYSTEM OVERRIDE` into the GM prompt if `stall_counter >= 3`.

**Status:**
- **Pre-Wave Carryover** — Anti-stall feature is fully implemented, tests passed, and playtester verified on branch `carryover/anti-stall-safeguards`.
- **Focus Group Slices (FG1, FG2, FG3)** — ✅ Finished, playtested (HITL), merged to main. Root noise cleaned up.
- **Wave 3** — (A4, B4, C3) Ready to begin once anti-stall is formally wrapped.

**Ready for:**
- PR review/merge for `carryover/anti-stall-safeguards`.
- Wave 3 slice selection.

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
