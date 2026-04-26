# Project Ares — Agent Context

**Read this file first.** It is the single authoritative bootstrap for all coding sessions on this repository, regardless of which AI agent is running.

---

## What This Is

Project Ares is a self-hosted, hidden-state AI Game Master for a single-player TTRPG campaign set in the Red Rising universe (728 PCE, pre-Darrow). The player interacts through a browser; the AI GM runs on the backend with full access to structured world state, secrets, and consequence mechanics that the player never sees directly.

This is **not** a chatbot wrapper. The value is in the hidden-state engine: clocks, visibility-gated secrets, canon guard, structured consequence extraction, and persistent campaign memory.

---

## Latest Session Summary

Date: 2026-04-26

### GM Clarify sidebar + narrative feed quality pass

**GM Clarify sidebar (`feat-7-gm-clarify-sidebar` → merged to main):**
- Backend `POST /api/v1/campaigns/{id}/clarify` endpoint — non-persisted, no state mutation.
- `ClarifySidebar` React component: markdown rendering (paragraphs, headings, lists, bold/italic), ESC closes, `?` topbar button.
- Fixed sidebar header scroll bug: `--topbar-height` CSS variable was never defined; added ResizeObserver in `App.jsx` to set it dynamically from the actual topbar element.
- Clarify system prompt rewritten: no markdown headers, no chatbot-style endings ("What would you like to do?"), brevity-first, 2–3 sentence target for simple questions.

**Narrative feed rendering:**
- GM turn text now splits on `\n\n` into separate `<p>` elements inside a `.turn-body` div — multi-paragraph responses render as readable prose, not a wall of text.
- `renderText` → `renderInline` refactor: handles `**bold**`, `*italic*`, `[Caste]"quote"` (caste color), and plain `"quote"` (neutral italic) inline within each paragraph.
- Dialogue coloring fixed: only `[Caste]"..."` tagged lines get a caste color; plain quotes are neutral italic. The old `.turn-dialogue-gm` gold class is removed.

**GM system prompt improvements:**
- Pacing discipline: calibrate length to action scope; don't re-establish ambient facts.
- Anti-filler rule: stacked atmospheric sentences ("The station hums… Jupiter hangs…") are explicitly banned unless they advance action, tension, character, or information.
- Sentence rhythm: vary length fluidly; not uniform staccato, not uniform purple prose.
- Naming conventions: Gold `au`, Copper `cu`, Silver `si`, Gray `te`, Red `ne`, Blue `de`, Obsidian `ka`. "Ares" banned as a family name.
- Clarify prompt: brevity-first, no headers, no chatbot endings.

**Canon fix:**
- Player character renamed **Davan o' Tharsis** (correct lowRed apostrophe convention, like Darrow o' Lykos) in `world_bible.md`, all DB rows, and tests.

**How to use next session:**
- Use `make compose-up` for the full stack (postgres + backend at 8000 + frontend at 5180 via Docker). **Always test at 5180**, not the standalone Vite dev server at 5173/5174.
- Always verify UI changes with Playwright MCP `browser_navigate` + `browser_take_screenshot` — **never claim UI work done without a screenshot**.
- Frontend Docker image must be rebuilt after source changes: `docker compose up --build --no-deps -d frontend`.

**What's next (priority order from master plan):**
1. Backend NPC stats — emit `level`, `current_hp`/`max_hp`, `disposition` from turn engine into `scene_participants`; replace mock fallback in `buildSceneParticipants`.
2. Live stat patching after turns — patch participant HP/disposition from `TurnResolution` without full refresh.
3. Memory rendering — surface player-relevant memories in the status panel or feed.
4. Secret reveal display — in-feed event when a sealed secret becomes player-facing.
5. Update the active objective from GM responses — currently stuck at "Check the Melt before shift" across 34 turns.

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
- **`TurnResolution`** is the return type of `turn_engine.submit_turn()`. It carries `canon_guard_passed`, `clocks_fired`, `location_changed_to`, `context_excerpt`, and the persisted `turn` record.
- **Consequence events in the feed** use speaker values `system-location` and `system-clock` — these map to CSS classes `.turn-system-location` and `.turn-system-clock` without any conditional logic in `TurnFeed.jsx`.
- **`bootstrap_database()`** is idempotent and Alembic-compatible. Do not replace it with bare `Base.metadata.create_all()`.
- **Alembic** manages schema migrations. After any model change: write a migration (`alembic revision --autogenerate -m "..."`) and run `make migrate`.

---

## What's Next (as of 2026-04-26)

UI is now the canonical game shell. Core loop is fully playable. Next engineering slices in priority order:

1. **GM clarify sidebar chat** — add a `?` entry point in the live shell that opens a non-persisted GM sidebar conversation. The backend endpoint should explain the current story plainly, break the fourth wall if needed, and must not create a turn or mutate campaign state.
2. **Backend NPC stats** — emit `level`, `current_hp`/`max_hp`, and `disposition` per scene participant from the turn engine. `buildSceneParticipants` already has the hook; just replace mock fallback with real values. Disposition must be player-facing read (from observable NPC behavior), not sealed GM intent.
3. **Live stat patching after turns** — patch `participant.hp` and `participant.disposition` from `TurnResolution` without a full refresh, mirroring how `clocks_fired` and `location_changed_to` already surface as feed events.
4. **Memory rendering** — surface player-relevant turn memories in the status panel or turn feed
5. **Secret reveal display** — show an in-feed event when a sealed secret becomes player-facing
6. **Session prep CLI workflow** — operator command to inspect clock state, NPC agendas, and reveal candidates before a play session
7. **Post-session continuity review** — operator workflow to audit generated memories for drift or contradiction

Do not build Phase 5 items (multiplayer, admin dashboard, map UI) until the items above are solid.
