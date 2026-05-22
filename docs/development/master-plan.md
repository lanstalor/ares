# Ares Master Development Plan

This file is the daily control surface for active development. Use it after `CLAUDE.md` and `docs/development/agent-handoff-protocol.md`, and before opening chat history.

If you are switching agents after an interruption, use `docs/development/resume-cheatsheet.md` for copy-paste resume prompts.

**Current wave:** fables.gg gap-closing roadmap — parent plan at `~/.claude/plans/a-i-happy-matsumoto.md`. Three parallel tracks (A: Mechanical Depth, B: Sensory Polish, C: Operator Depth), 15 slices total. Bootstrap a slice with `make bootstrap-slice SLICE=A1`.

**Current focus-group premise:** Mara of Cimmeria, a highRed relay technician on Ganymede in 728 PCE, opens at Surface Relay Tower 19 with a Weaver dead-channel order to pull the ghost packet before Pelsin's diagnostic scrub. Older Davan references in completed workstreams are historical unless an active slice explicitly says otherwise.

## Now (In-Flight Slices)

| Slice | Branch | Worktree | Agent | Status | Next step |
|---|---|---|---|---|---|
| Narration QA follow-up | `main` | `~/ares` | Codex | blocked | OpenAI quota stopped the 2026-05-22 rerun after 9 scored turns and still blocks a later smoke; rerun 20 turns on OpenAI when quota is available and compare against `tools/playtester/reports/2026-05-13-01-10.md`. |

## Wave Backlog (Fables.gg Gap-Closing)

Pick any slice from a different track and run `make bootstrap-slice SLICE=<id>`. Within a track, slices are sequential.

### Track A — Mechanical Depth

| Slice | Title | Status |
|---|---|---|
| A1 | Dice + skill check primitive | finished |
| A2 | Itemized inventory | finished |
| A3 | Conditions + status effects | finished |
| A4 | Turn-based combat mode | finished |
| A5 | Abilities/equipment registry | not-started |

### Track B — Sensory Polish

| Slice | Title | Status |
|---|---|---|
| B1 | MediaProvider abstraction | finished |
| B2 | Scene art generation pipeline | finished |
| B3 | NPC portrait generation | finished |
| B4 | TTS narration | not-started |
| B5 | World map + token movement | not-started |

### Track C — Operator Depth

| Slice | Title | Status |
|---|---|---|
| C1 | Operator-only API surface | finished |
| C2 | Operator React app | finished |
| C3 | Lore-page authoring | not-started |
| C4 | Session prep workflow | not-started |
| C5 | Post-session continuity review | not-started |

## Pre-Wave Carryover

| Slice | Status | Next step |
|---|---|---|
| UI overhaul (golden slice merged) | finished | Completed in session 2026-05-05 |
| GM anti-stall safeguards | finished | Merged through PR #16; current follow-up is playtester validation with Mara/Relay 19 prompts. |

## Later

| Theme | Notes |
|---|---|
| Session prep CLI workflow | Keep it CLI-first and operator-facing |
| Post-session continuity review | Use scorecards and narrow repair workflows |
| Broader operator workflow automation | Add only after the handoff and GitHub discipline is stable |

## Blocked

| Blocker | Impact | Next step |
|---|---|---|
| OpenAI quota exhausted during playtester rerun | `tools/playtester/reports/2026-05-22-00-24.md` captured 9 scored turns, then backend GM calls and holistic evaluation returned quota errors. A later OpenAI smoke with `.env` sourced confirmed `insufficient_quota`; no additional benchmark report was written. | Restore OpenAI quota, then rerun `ARES_PLAYTESTER_TURNS=20 python3 tools/playtester/run.py`. Use Anthropic only as an explicitly documented fallback. |

## Recently Finished

| Date | Slice | Notes |
|---|---|---|
| 2026-05-13 | Narration quality | Added length discipline, plain-language prompt rules, Section 14 world-bible rewrite, and 20-turn report. Retargeted playtester prompts to Mara/Relay 19 in the 2026-05-22 follow-up before the next benchmark. |
| 2026-05-12 | A4: Turn-based combat mode | GM-driven enter/progress/exit combat state, initiative order, damage summary, hidden combat context, API exposure, and frontend CombatPanel. Merged via PR #17. |
| 2026-05-12 | Chat quality / pacing / memory | Scene-state persistence, narrative summary, repeated-phrase banlist, GM-only memory injection, stall counter, and stronger scene-change prompt discipline. Merged via PR #16. |
| 2026-05-11 | FG1, FG2, FG3: Focus Group | Blockers patched, hardening verified, HITL playtest simulated successfully. Merged to main. |
| 2026-05-06 | A3: Conditions + status effects | ConditionType enum, Condition model + migration, ConditionService, consequence integration, turn-triggered ticking, ParticipantStrip rendering with color-coded chips, 70+ tests, 215 total passing |
| 2026-05-06 | B3: NPC portrait generation | NpcPortrait model + service, eager generation on NPC creation, lazy generation on first appearance, operator regenerate endpoint, MediaProvider integration, frontend lazy-load with initials fallback |
| 2026-05-06 | C2: Operator React app | Separate /admin route with token-gating, sidebar nav, entity editors (Campaign, Objectives, Clocks, Secrets, NPCs), reusable table/modal components |
| 2026-05-06 | B2: Scene art generation | SceneArt cache model, player-safe prompt building, MediaProvider integration, turn-triggered generation, API endpoints, frontend rendering |
| 2026-05-06 | A2: Itemized inventory | Structured Item model, inventory consequences, GM context, operator schemas, frontend inventory rendering |
| 2026-05-05 | C1: Operator-only API surface | GET /full-state, PATCH /state, GET /audit endpoints for manual repair |
| 2026-05-05 | B1: MediaProvider abstraction | MediaProvider protocol + OpenAI/Replicate/Stub implementations |
| 2026-05-05 | A1: Dice + skill check primitive | Attribute checks (Strength, Cunning, etc.) with system-roll feed events |
| 2026-05-05 | UI Design Pass Phase 2 | Restored 3-column layout, branding assets, portrait avatars, utility rail |
| 2026-04-30 | Icon sidebar + 4:3 scene aspect ratio | Status panel replaced with 56px icon rail + popout overlay; scene backdrop locked to 4:3 aspect ratio |
| 2026-04-30 | UI design pass Phase 1 (CSS frames) | Panel accent strips, grain texture slot, column separator, caste icon slot |
| 2026-04-30 | Playtester prompt pass + OpenAI benchmark | Shared GM prompt tightened, playtester made provider-configurable, and the first OpenAI benchmark documented that prompt-only changes did not yet fix repetition or scene stall |
| 2026-04-30 | Backend NPC stats | level/HP on NPC model, parsed from world_bible, emitted in scene_participants |
| 2026-04-30 | Objective updates | GM can complete/create objectives via consequences tool call |
| 2026-04-30 | Memory rendering | GET /memories endpoint + StatusPanel Campaign Log section |
| 2026-04-30 | Live stat patching | HP/disposition patched from TurnResolution per turn, no full refresh |
| 2026-04-30 | Secret reveal display | Purple in-feed event when sealed secret flips to revealed |
| 2026-04-30 | Automated playtester | 30-turn campaign simulation with per-turn UX scoring and holistic report |
| 2026-04-26 | GM clarify sidebar chat | Non-persisted `?` sidebar for story clarification |
| 2026-04-26 | GM scene context + action guidance | suggested_actions, scene_participants, scene art wired |
| 2026-04-24 | Runtime/bootstrap reconciliation | Backend bootstrap, provider wiring, frontend readiness aligned |

## Working Rules

- Every active feature slice should have one GitHub issue, one flat branch, one draft PR, and one workstream doc under `docs/development/workstreams/`.
- `CLAUDE.md` is for repo bootstrap and durable constraints. This file is for current priorities and active work.
- If an active branch or PR is missing, record `TBD` temporarily and create the missing artifact before starting substantial new work on that slice.
- When a playtester benchmark materially changes the outlook, record the report path and the concrete learning in the relevant workstream doc before starting the next slice.

## UI Co-Dev Loop (VS Code)

Standard loop for all UI-iteration work:

| Phase | Scope | Port | When |
|---|---|---|---|
| Fast local | CSS tweaks, colour, spacing — no API calls needed | 5173 (`make frontend-dev`) | While editing, for live HMR |
| Truth checkpoint | Layout changes, JSX restructures, anything that touches state or API contract | 5180 (`make compose-up`) | End of each slice, before marking complete |

**Canonical test URL:** `http://localhost:5180/` — seed `localStorage.ares_intro_seen=1` to skip the intro.

**Viewport:** 1366×1024 (Playwright MCP screenshot). Also capture 390×844 (mobile) at milestone boundaries.

**Slice contract:** see `docs/development/workstreams/ui-design-pass.md` §"VS Code Co-Dev Loop".

**Visual aids in VS Code:**
- Keep the integrated browser (Simple Browser) open at 5173 or 5180 for continuous watching.
- Use Playwright MCP captures for durable before/after evidence at slice boundaries.

**Screenshot storage:** `assets/samples/ui-iteration/` — name files `{date}-{slice}-{before|after}.png`.
