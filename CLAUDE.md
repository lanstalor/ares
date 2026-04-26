# Project Ares — Agent Context

**Read this file first.** It is the single authoritative bootstrap for all coding sessions on this repository, regardless of which AI agent is running.

---

## What This Is

Project Ares is a self-hosted, hidden-state AI Game Master for a single-player TTRPG campaign set in the Red Rising universe (728 PCE, pre-Darrow). The player interacts through a browser; the AI GM runs on the backend with full access to structured world state, secrets, and consequence mechanics that the player never sees directly.

This is **not** a chatbot wrapper. The value is in the hidden-state engine: clocks, visibility-gated secrets, canon guard, structured consequence extraction, and persistent campaign memory.

---

## Latest Session Summary

Date: 2026-04-26

### Official game UI promotion + Gemini CSS regression fix

The cinematic layout developed in the `/ui-dev` iteration route is now the canonical `mode-live` game UI. Two sessions of work combined:

**2026-04-25 — Cinematic shell and Scene Presence pass:**
- Added `/ui-dev` route for backend-free layout iteration with full mock state
- Renamed "Roster" → **Scene Presence**, removed redundant "Participants" eyebrow
- Fixed all modal/popover overflow clipping via `createPortal` to `document.body` (escapes `overflow: hidden` on `.app-shell`)
- Added per-character stats to Scene Presence cards and detail modal:
  - `level` — mono badge overlaid on avatar (top-right corner)
  - `hp` — thin color-coded bar on cards (`good ≥66% / warn ≥33% / bad`), full meter with `current/max` readout in modal
  - `disposition` — 5-step scale (hostile / suspicious / unaware / friendly / allied); chip on cards, 5-segment lit-track in modal
- Mock data in `buildSceneParticipants` (`lib/uiTheme.js`); hooks ready for real backend NPC state

**2026-04-26 — Promoted dev-UI to official game UI:**
- `mode-live` (campaign selected) now uses single-column full-width layout: no side panel, no hud-ribbon
- `mode-staging` (no campaign selected) keeps the two-column layout with CampaignConsole, StatusPanel, and Session controls — the operator entry point
- **Audio** toggle and **Console** button (returns to staging) added to topbar in live mode
- Fixed a Gemini-introduced CSS regression: all `dev-ui-mode` selectors were incorrectly rewritten as `.mode-live, .mode-staging .X` — a fundamentally broken CSS selector pattern that applied `display: flex` to the entire app-shell element. All ~30 rules corrected to proper `.mode-live .X` descendant selectors
- Fixed `.mode-live .play-column` row count (was changed to 2 rows, cutting off the participant strip; restored to 3 rows: story-grid / participant-strip / input)
- Restored `dev-ui-mode` class on app-shell (Gemini had dropped it, breaking the dev helper bar)

**The two-mode contract:**
- `mode-staging`: two-column, side panel visible (Session + Campaign Lattice + Readiness), hud-ribbon showing. Entry point for seeding, campaign selection, shell status.
- `mode-live`: single-column, full-width. Cinematic layout with backdrop dominating, Scene Presence strip, compact input bar. Audio toggle + Console button in topbar to access staging.

How to use it next session:

- Use `make compose-up` for the full stack (postgres + backend at 8000 + frontend at 5180 via Docker)
- Use `make frontend-dev` for frontend-only iteration (Vite on 5173; auto-increments if occupied by familyquest)
- Open `/ui-dev` for backend-free layout work
- Always verify UI changes with Playwright MCP `browser_navigate` + `browser_take_screenshot` — **never claim UI work done without a screenshot**
- Disposition meter CSS: `.tone-bad/warn/muted/good/ally` on `.participant-disposition-chip` and `.participant-disposition-meter`

Current branch guidance:

- `mode-live` styling lives in `.mode-live .X` selectors — do NOT use `.mode-live, .mode-staging .X` (broken selector)
- Do not re-add the side panel or hud-ribbon to live mode — operator chrome lives in staging
- Preserve hidden-state boundaries; disposition is player-facing read, sealed GM intent stays server-only

---

## Where To Find Context

| Document | What it contains |
|---|---|
| `readme.md` | Original product spec, design principles, domain model, architecture layers, agent playbooks, acceptance criteria — the canonical "why" document |
| `world_bible.md` | Campaign source material: factions, areas, POIs, NPCs, secrets, lore, player character (Davan of Tharsis), clocks — seeded into the DB on first run |
| `CLAUDE.md` (this file) | Current implementation state, file map, dev workflow, hard constraints |
| `docs/development/master-plan.md` | Current priorities, active workstreams, and the fastest way to see what should happen next |
| `docs/development/workstreams/` | Canonical resume docs for interrupted feature slices; read the linked workstream before chat history |

## Development Workflow Defaults

- Start each coding session with: `CLAUDE.md` -> `docs/development/master-plan.md` -> target workstream doc -> linked PR/issue -> `git status`
- Each non-trivial feature slice should have one GitHub issue, one flat branch, one draft PR, and one workstream doc under `docs/development/workstreams/`
- `CLAUDE.md` holds durable repo context and constraints; active TODO churn belongs in the master plan and workstream docs
- Before pausing or switching agents, update the workstream doc with current state, verification, risks, and the exact next step
- If GitHub artifacts are missing for an active slice, record `TBD` in the doc temporarily, then create the missing issue/branch/PR before substantial new work

---

## Implementation Status

All core phases are complete and playable as of 2026-04-25.

- **Seed pipeline**: `world_bible.md` → parser → seed_service → DB (18 factions, 24 areas, 25 POIs, 11 NPCs, 30 secrets, 1 character)
- **GM engine**: `turn_engine.py` → context assembly → Anthropic (claude-haiku-4-5) → structured tool response → consequence application → `TurnResolution`
- **Canon guard**: blocks forbidden characters (Darrow, Eo, Cassius, Virginia, Mustang), impossible tech, tonal drift
- **Consequence feedback**: location changes and fired clocks surface in the turn feed as styled system events
- **Web UI**: React, retro terminal aesthetic, `turn-${speaker}` CSS class pattern for turn styling
- **62 backend tests passing** (`make backend-test`)

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
| `api/routes/seed.py` | `POST /api/v1/seed/world-bible` — operator seed trigger |
| `api/routes/campaigns.py` | Campaign CRUD |
| `api/routes/system.py` | Health + system status |
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
| `components/StatusPanel.jsx` | Character state, location, active objective |
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
- **`TurnResolution`** is the return type of `turn_engine.submit_turn()`. It carries `canon_guard_passed`, `clocks_fired`, `location_changed_to`, `context_excerpt`, and the persisted `turn` record.
- **Consequence events in the feed** use speaker values `system-location` and `system-clock` — these map to CSS classes `.turn-system-location` and `.turn-system-clock` without any conditional logic in `TurnFeed.jsx`.
- **`bootstrap_database()`** is idempotent and Alembic-compatible. Do not replace it with bare `Base.metadata.create_all()`.
- **Alembic** manages schema migrations. After any model change: write a migration (`alembic revision --autogenerate -m "..."`) and run `make migrate`.

---

## What's Next (as of 2026-04-26)

UI is now the canonical game shell. Core loop is fully playable. Next engineering slices in priority order:

1. **Backend NPC stats** — emit `level`, `current_hp`/`max_hp`, and `disposition` per scene participant from the turn engine. `buildSceneParticipants` already has the hook; just replace mock fallback with real values. Disposition must be player-facing read (from observable NPC behavior), not sealed GM intent.
2. **Live stat patching after turns** — patch `participant.hp` and `participant.disposition` from `TurnResolution` without a full refresh, mirroring how `clocks_fired` and `location_changed_to` already surface as feed events.
3. **Memory rendering** — surface player-relevant turn memories in the status panel or turn feed
4. **Secret reveal display** — show an in-feed event when a sealed secret becomes player-facing
5. **Session prep CLI workflow** — operator command to inspect clock state, NPC agendas, and reveal candidates before a play session
6. **Post-session continuity review** — operator workflow to audit generated memories for drift or contradiction

Do not build Phase 5 items (multiplayer, admin dashboard, map UI) until the items above are solid.
