# Project Ares — Agent Context

**Read this file first.** It is the single authoritative bootstrap for all coding sessions on this repository, regardless of which AI agent is running.

---

## What This Is

Project Ares is a self-hosted, hidden-state AI Game Master for a single-player TTRPG campaign set in the Red Rising universe (728 PCE, pre-Darrow). The player interacts through a browser; the AI GM runs on the backend with full access to structured world state, secrets, and consequence mechanics that the player never sees directly.

This is **not** a chatbot wrapper. The value is in the hidden-state engine: clocks, visibility-gated secrets, canon guard, structured consequence extraction, and persistent campaign memory.

---

## Latest Session Summary

Date: 2026-04-25 (afternoon)

What changed (Scene Presence pass):

- Renamed the participant strip from "Roster" to **Scene Presence** and removed the redundant "Participants" eyebrow
- Fixed character-detail popup clipping by portalling `ParticipantModal` to `document.body` via `react-dom`'s `createPortal` (escapes the `overflow: hidden` on `.app-shell`)
- Polished the modal: backdrop blur + stronger dim, `×` close button, entrance animation, atmospheric border/glow that matches the shell aesthetic
- Fixed avatar/name overlap in dev-ui-mode cards (avatar was 56px in a 28px grid column; now a matching 40px avatar with proper grid track)
- **Added per-character stats** to the Scene Presence cards and modal:
  - `level` — small mono badge overlaid on the avatar (top-right)
  - `hp` — colored thin bar on cards, full meter with `current/max` numerics in modal (good ≥66%, warn ≥33%, bad below)
  - `disposition` — 5-step scale (`hostile / suspicious / unaware / friendly / allied`); compact colored chip on cards, 5-segment lit-track meter in modal
- The player character has level + HP only (no disposition toward themselves); the system entity (Ares Relay) shows no stats
- Mock data for stats lives in `buildSceneParticipants` (`frontend/src/lib/uiTheme.js`); ready to swap for real backend NPC state when that lands

Earlier 2026-04-25 work (cinematic shell):

- Added a Vite HMR-friendly UI dev route at `/ui-dev` and `?ui-dev=1` for layout-only iteration
- Seeded the dev route with mock campaign state so the game UI can be exercised without the backend
- Reworked typography toward a display/body split instead of a mono-heavy shell
- Compressed the staging and UI-dev chrome so the scene/backdrop gets the majority of the vertical budget

How to use it next session:

- Start the frontend with `make frontend-dev`. Vite tries 5173 first; if occupied (familyquest project) it auto-increments. Use the printed Network URL.
- Open `/ui-dev` for layout-only work (mock state, no backend needed)
- For visual verification while editing, use Playwright MCP `browser_navigate` + `browser_take_screenshot`. **Never claim UI work is done without a screenshot.**
- Disposition meter colors live as `.tone-bad/warn/muted/good/ally` on `.participant-disposition-chip` and `.participant-disposition-meter`
- Backend wiring for NPC stats is the natural next step — `buildSceneParticipants` already accepts them; backend just needs to emit `level`, `hp`, `disposition` per scene participant

Current branch guidance:

- Keep follow-up UI work isolated to the dedicated dev route unless you are fixing shared components
- Do not broaden the admin shell during play mode; treat it as secondary chrome
- Preserve hidden-state boundaries and the retro text-first tone
- Disposition is **player-facing** (it's the player's read on the NPC). True hidden NPC intent stays sealed in GM-only state.

---

## Where To Find Context

| Document | What it contains |
|---|---|
| `readme.md` | Original product spec, design principles, domain model, architecture layers, agent playbooks, acceptance criteria — the canonical "why" document |
| `world_bible.md` | Campaign source material: factions, areas, POIs, NPCs, secrets, lore, player character (Davan of Tharsis), clocks — seeded into the DB on first run |
| `CLAUDE.md` (this file) | Current implementation state, file map, dev workflow, hard constraints |

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

## What's Next (as of 2026-04-25)

Core loop is playable and Scene Presence cards now visualize per-character state. Logical next slices in priority order:

1. **Backend NPC stats** — emit `level`, `current_hp`/`max_hp`, and `disposition` per scene participant from the turn engine so `buildSceneParticipants` can drop the mock fallback. Disposition must be the player-facing read (derived from observable behavior), not the sealed GM intent.
2. **Memory rendering** — surface player-relevant memories from past turns in the status panel or turn feed
3. **Secret reveal display** — show an in-feed event when a sealed secret becomes player-facing
4. **Live stat updates after turns** — patch `participant.hp` / `participant.disposition` from `TurnResolution` consequences without a full refresh, mirroring how `clocks_fired` and `location_changed_to` surface today
5. **Session prep CLI workflow** — operator command to inspect clock state, NPC agendas, and reveal candidates before a play session
6. **Post-session continuity review** — operator workflow to audit generated memories for drift or contradiction

Do not build Phase 5 items (multiplayer, admin dashboard, map UI) until the items above are solid.
