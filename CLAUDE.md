# Project Ares — Agent Context

**Read this file first.** It is the single authoritative bootstrap for all coding sessions on this repository, regardless of which AI agent is running.

---

## What This Is

Project Ares is a self-hosted, hidden-state AI Game Master for a single-player TTRPG campaign set in the Red Rising universe (728 PCE, pre-Darrow). The player interacts through a browser; the AI GM runs on the backend with full access to structured world state, secrets, and consequence mechanics that the player never sees directly.

This is **not** a chatbot wrapper. The value is in the hidden-state engine: clocks, visibility-gated secrets, canon guard, structured consequence extraction, and persistent campaign memory.

---

## Latest Session Summary

Date: 2026-04-30 (continued)

### Pixel-art rebel terminal UI overhaul — golden slice

**Delivered (all merged to main, commit 0252225):**
- UI overhaul CSS refactor: pixel-art diegetic rebel terminal aesthetic per `docs/layout.md` + `assets/samples/ui.png`
- VT323 font loaded (Google Fonts) for pixel-style labels, tabs, metadata; body/narrative keep Chakra Petch
- Design tokens: `--shell-bg`, `--shell-bevel-hi/lo`, `--shell-rivet`, `--module-bg/inset-*`, `--screen-bg`, `--accent-tac-red/cyan/amber/green`, `--unit` (8px grid)
- Frame primitives (CSS-only, asset-swappable via CSS vars):
  * `.frame-shell` — outer chassis with bevelled inset (top/left highlight, bottom/right shadow) + corner rivets
  * `.frame-module` — bolted instrument-rack module with title stripe (top edge), corner brackets, bevel shadow
  * `.frame-screen` — monitor bezel with darker inner surface + scanline overlay
  * `.frame-cmd` — heavier console-housing variant (command line)
  * `.frame-chip` — compact tactical chip (buttons, presence cards)
- Applied to golden-slice vertical only (topbar, command line, scene viewport, sidebar):
  * `.topbar` — cyan top stripe, pixel ARES wordmark, VT323 labels, quieter contrast
  * `.input-panel.frame-cmd` — red top stripe, 78px+ housing, hardware-style EXECUTE button (bevelled, embossed, pressable), focus-state cyan glow
  * `.scene-backdrop-panel.frame-screen` — monitor bezel inset + scanline overlay
  * `.sidebar-icon-rail` + `.sidebar-popout` — amber stripe, folded into chassis as one bolted assembly (flush edge, no gap when open, active button shows side-accent)
  * `.app-shell.frame-shell` — outer chassis frame with bevel + corner rivets
- Hierarchy: older `.turn-item` entries fade via `:nth-last-child(n+6)` opacity ramp (oldest 55%, middle 78%, newest 100%)
- Asset hooks ready (CSS vars, no markup edits needed): `--shell-frame-image`, `--module-frame-image`, `--screen-frame-image`, `--cmd-frame-image`, `--ares-wordmark`
- Verification: Playwright screenshots at 1366×1024 (iPad Pro landscape): `ui-overhaul-golden-slice.png` (closed), `ui-overhaul-popout-open-v2.png` (popout open)

**Phase 1 panel styling (2026-04-30 prior session):**
- Top-edge accent strips: `--panel-accent` drives per-region color coding (green = narrative, cyan = system, gold = status, amber = relay)
- Clip-path corner notches on untouched panels (turn feed, participant strip, action bar, status panel interiors) — preserved during rolling refactor

**Out of scope (follow-up passes):**
- Turn feed, participant strip, action bar, status panel interior reskinning (still on Phase 1 styling — no half-dressed UI)
- Asset generation: corner brackets PNG/SVG, grain texture, ARES wordmark, caste icons, scene location art
- New panels or IA changes

**Code changes:** 5 files touched
- `frontend/src/styles.css` — VT323 import + ~550 lines new `UI OVERHAUL — PIXEL TERMINAL` section
- `frontend/src/App.jsx` — add `frame-shell` className to root `.app-shell`
- `frontend/src/components/PlayerInput.jsx` — add `frame-cmd` to root form, `frame-cmd-execute` to submit button
- `frontend/src/components/SceneBackdrop.jsx` — add `frame-screen` to root section
- `frontend/src/components/StatusPanel.jsx` — add `frame-module` to rail/popout, `frame-chip` to icon buttons

**How to use next session:**
- Use `make compose-up` for the full stack (postgres + backend at 8000 + frontend at 5180 via Docker). **Always test at 5180**, not the standalone Vite dev server at 5173/5174.
- Always verify UI changes with Playwright MCP `browser_navigate` + `browser_take_screenshot` — **never claim UI work done without a screenshot**.
- Frontend Docker image must be rebuilt after source changes: `docker compose up --build --no-deps -d frontend`.
- Backend Docker image must also be rebuilt after source changes: `docker compose up --build --no-deps -d backend`. `--no-deps -d` alone does NOT rebuild — source changes (prompts, routes, services) will be silently ignored.

**What's next:** See `docs/development/master-plan.md` — reskin remaining panels (turn feed, participant strip, action bar, status panels) with frame primitives. Asset generation roadmap in `docs/layout.md` §"Recommended Workflow".

---

## Where To Find Context

| Document | What it contains |
|---|---|
| `readme.md` | Original product spec, design principles, domain model, architecture layers, agent playbooks, acceptance criteria — the canonical "why" document |
| `world_bible.md` | Campaign source material: factions, areas, POIs, NPCs, secrets, lore, player character (Davan of Tharsis), clocks — seeded into the DB on first run |
| `CLAUDE.md` (this file) | Current implementation state, file map, dev workflow, hard constraints |
| `docs/development/master-plan.md` | Current priorities, active workstreams, and the fastest way to see what should happen next |
| `docs/development/workstreams/` | Canonical resume docs for interrupted feature slices; read the linked workstream before chat history |
| `docs/development/resume-cheatsheet.md` | Copy-paste prompts and current local chat artifact paths for resuming with Codex, Gemini, or Claude |

## Development Workflow Defaults

- Start each coding session with: `CLAUDE.md` -> `docs/development/master-plan.md` -> target workstream doc -> linked PR/issue -> `git status`
- Each non-trivial feature slice should have one GitHub issue, one flat branch, one draft PR, and one workstream doc under `docs/development/workstreams/`
- `CLAUDE.md` holds durable repo context and constraints; active TODO churn belongs in the master plan and workstream docs
- Before pausing or switching agents, update the workstream doc with current state, verification, risks, and the exact next step
- If GitHub artifacts are missing for an active slice, record `TBD` in the doc temporarily, then create the missing issue/branch/PR before substantial new work

---

## Implementation Status

All core phases are complete and playable as of 2026-04-30.

- **Seed pipeline**: `world_bible.md` → parser → seed_service → DB (18 factions, 24 areas, 25 POIs, 11 NPCs, 30 secrets, 1 character)
- **GM engine**: `turn_engine.py` → context assembly → Anthropic (claude-haiku-4-5) → structured tool response → consequence application → `TurnResolution`
- **Canon guard**: blocks forbidden characters (Darrow, Eo, Cassius, Virginia, Mustang), impossible tech, tonal drift
- **Consequence feedback**: location changes, fired clocks, and revealed secrets surface in the turn feed as styled system events (`system-location`, `system-clock`, `system-secret`)
- **Objective updates**: GM can complete active objectives and create new ones via `consequences.objective_updates`
- **Memory rendering**: `GET /api/v1/campaigns/{id}/memories` (player_facing only) + StatusPanel Campaign Log section
- **NPC stats**: `level`, `current_hp`, `max_hp` on NPC model; emitted in `scene_participants` per turn; live-patched in frontend without full refresh
- **Automated playtester**: `tools/playtester/run.py` — 30-turn simulation with UX scoring; reports in `tools/playtester/reports/`
- **Web UI**: React, retro terminal aesthetic, `turn-${speaker}` CSS class pattern for turn styling
- **70 backend tests passing** (`make backend-test`)

---

## Key File Map

### Backend (`backend/app/`)

| File | Role |
|---|---|
| `main.py` | FastAPI app, lifespan bootstraps DB |
| `core/config.py` | Settings via pydantic-settings — `generation_model`, `generation_provider`, `cors_origins_raw` |
| `models/` | SQLAlchemy ORM: `campaign.py`, `character.py`, `world.py`, `memory.py` |
| `services/turn_engine.py` | Core live-play loop: context → generation → consequence application |
| `services/anthropic_provider.py` | Claude API integration, structured tool call for consequence extraction |
| `services/context_builder.py` | Assembles player-safe + hidden GM context for each turn |
| `services/consequence_applier.py` | Applies parsed consequences to DB state |
| `services/canon_guard.py` | Validates narration against hard canon rules |
| `services/world_bible_parser.py` | Parses `world_bible.md` into typed seed objects |
| `services/seed_runtime.py` | Inserts seed bundle into the database, idempotent |
| `services/provider_registry.py` | Returns correct `NarrationProvider` based on `ARES_GENERATION_PROVIDER` |
| `api/routes/turns.py` | `POST /api/v1/campaigns/{id}/turns` — the live turn endpoint |
| `api/routes/memories.py` | `GET /api/v1/campaigns/{id}/memories` — player_facing memories only |
| `api/routes/seed.py` | `POST /api/v1/seed/world-bible` — creates campaign + seeds world in one call, returns `campaign_id` |
| `api/routes/campaigns.py` | Campaign CRUD |
| `api/routes/system.py` | Health (`/api/v1/health`) + system status |
| `schemas/memory.py` | `MemoryRead` Pydantic schema |
| `db/bootstrap.py` | `bootstrap_database()` — idempotent schema init, safe alongside Alembic |

### Frontend (`frontend/src/`)

| File | Role |
|---|---|
| `App.jsx` | Root state: campaigns, turns, consequence patching, turn submission |
| `lib/api.js` | All fetch calls to the backend |
| `lib/readiness.js` | Derives `shellReadiness` badges from health/status |
| `styles.css` | Single stylesheet — `turn-${speaker}` drives all turn styling |
| `components/TurnFeed.jsx` | Renders the turn list; no speaker-specific logic, uses CSS class pattern |
| `components/PlayerInput.jsx` | Text input + submit |
| `components/CampaignConsole.jsx` | Campaign selector, seed button, create form |
| `components/StatusPanel.jsx` | Character state, location, active objective, Campaign Log (memories) |
| `components/ParticipantStrip.jsx` | Scene Presence cards + per-character modal (level, HP, disposition) |
| `components/IntroOverlay.jsx` | First-time player onboarding overlay |

### Tests (`backend/tests/`)

- `test_world_bible_parser.py` — parser coverage
- `test_seed_runtime.py` — full seed-to-DB integration
- `test_turn_engine.py` — turn loop with stub provider
- `test_provider_registry.py` — provider selection, default model assertions
- Other unit tests per service layer

---

## Development Workflow

```bash
# Run backend tests (always do this before committing)
make backend-test

# Start full stack (Docker)
make compose-up

# Start backend only (local venv, auto-reloads)
make backend-dev

# Start frontend only (Vite dev server, localhost:5173)
make frontend-dev

# Run DB migrations (after schema changes)
make migrate

# Syntax check (no test runner needed)
make check
```

The Vite dev server runs on **5173** locally but is remapped to **5180** in docker-compose. Both ports must be in `ARES_CORS_ORIGINS`.

### Frontend changes at port 5180 (Docker)

**Port 5180 runs a Docker container that bakes frontend source files at build time.** Editing `frontend/src/` on the host does NOT hot-reload at 5180. You must rebuild the container after every frontend change:

```bash
docker compose up --build --no-deps -d frontend
```

This rebuilds only the frontend image (postgres and backend stay running). Takes ~15 seconds. Always verify with a Playwright screenshot at `http://localhost:5180/` after rebuilding — do not claim UI work is done without a screenshot.

Use `make frontend-dev` (port 5173/5174) only for layout iteration that doesn't need a live backend. For any work requiring real API calls (turns, clarify, seed), use the full stack at 5180.

### Environment (`.env`, not committed)

```
ARES_GENERATION_PROVIDER=anthropic   # or "stub" for offline dev
ARES_MODEL=claude-haiku-4-5
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql+psycopg://ares:ares@localhost:5432/project_ares
```

Use `ARES_GENERATION_PROVIDER=stub` during dev/test — it returns deterministic empty consequences and avoids API charges.

---

## Hard Constraints — Do Not Violate

These come from `readme.md` and are non-negotiable:

1. **Hidden state must never leak to the player.** Secrets, GM-only notes, sealed facts, unrevealed clocks — none of these may appear in the player API response, the turn feed, or the UI.
2. **Canon guard is not optional.** The characters Darrow, Eo, Cassius, Virginia, and Mustang must never appear in generated narration. Block or flag, never silently pass.
3. **The player character is Davan of Tharsis.** Do not change name, role, or starting state without operator approval.
4. **Campaign window is 728–732 PCE.** No future events, no FTL, no AI in-world.
5. **`world_bible.md` is the seed source, not a runtime editor.** After seeding, the database is authoritative. Do not re-parse the bible to answer live-play questions.
6. **Provider abstraction is non-negotiable.** All AI calls go through `NarrationProvider` / `provider_registry.py`. Never hardcode `anthropic` client calls outside `anthropic_provider.py`.
7. **Operator agents are advisory.** No agent may silently rewrite plot facts, mystery answers, character intent, or core canon. Require explicit confirmation.

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

## Architecture Invariants

- **Turn loop is synchronous per campaign.** No concurrent turns for the same campaign ID.
- **`TurnResolution`** carries `canon_guard_passed`, `clocks_fired`, `location_changed_to`, `revealed_secrets`, `context_excerpt`, `suggested_actions`, `scene_participants`, and the persisted `turn` record.
- **Consequence events in the feed** use speaker values `system-location`, `system-clock`, `system-secret` — these map to CSS classes without any conditional logic in `TurnFeed.jsx`.
- **`ConsequenceResult`** carries `revealed_secrets: list[dict]` — populated when a secret's `new_status == REVEALED`. Each entry has `label` and `content`.
- **Health endpoint** is `/api/v1/health` — not `/api/v1/system/health`.
- **`POST /api/v1/seed/world-bible`** creates the campaign AND seeds world state in one call — returns `campaign_id`. No separate `POST /api/v1/campaigns` needed.
- **`bootstrap_database()`** is idempotent and Alembic-compatible. Do not replace it with bare `Base.metadata.create_all()`.
- **Alembic** manages schema migrations. After any model change: write a migration (`alembic revision --autogenerate -m "..."`) and run `make migrate`.

---

## What's Next (as of 2026-04-30)

Core loop is fully playable. UI design pass is next. See `docs/development/master-plan.md` for current priorities.

1. **UI design CSS pass (Phase 1)** — panel enclosure system, corner markers, turn card frames, column separators. Pure CSS, no assets required. See `docs/development/workstreams/ui-design-pass.md`.
2. **UI asset generation (Phase 2)** — scene art (5 locations), caste icons (7 SVGs), panel corner piece, grain texture, ARES wordmark. All slot into existing `frontend/public/chrome/` and `scene-art/` paths without markup changes.
3. **Session prep CLI workflow** — operator command to inspect clock state, NPC agendas, and reveal candidates before a play session.
4. **Post-session continuity review** — operator workflow to audit generated memories for drift or contradiction.

Do not build Phase 5 items (multiplayer, admin dashboard, map UI) until the items above are solid.
