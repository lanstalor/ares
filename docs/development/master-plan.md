# Ares Master Development Plan

This file is the daily control surface for active development. Use it after `CLAUDE.md` and `docs/development/agent-handoff-protocol.md`, and before opening chat history.

If you are switching agents after an interruption, use `docs/development/resume-cheatsheet.md` for copy-paste resume prompts.

**Current wave:** fables.gg gap-closing roadmap — parent plan at `~/.claude/plans/a-i-happy-matsumoto.md`. Three parallel tracks (A: Mechanical Depth, B: Sensory Polish, C: Operator Depth), 15 slices total. Bootstrap a slice with `make bootstrap-slice SLICE=A1`.

## Now (In-Flight Slices)

| Slice | Branch | Worktree | Agent | Status | Next concrete step |
|---|---|---|---|---|---|
| C1 | `track-c/C1-admin-api` | `~/ares-track-c/C1` | Gemini | review | Merge C1, then bootstrap C2 |

## Wave Backlog (Fables.gg Gap-Closing)

Pick any slice from a different track and run `make bootstrap-slice SLICE=<id>`. Within a track, slices are sequential.

### Track A — Mechanical Depth

| Slice | Title | Status |
|---|---|---|
| A1 | Dice + skill check primitive | not-started |
| A2 | Itemized inventory | not-started |
| A3 | Conditions + status effects | not-started |
| A4 | Turn-based combat mode | not-started |
| A5 | Abilities/equipment registry | not-started |

### Track B — Sensory Polish

| Slice | Title | Status |
|---|---|---|
| B1 | MediaProvider abstraction | not-started |
| B2 | Scene art generation pipeline | not-started |
| B3 | NPC portrait generation | not-started |
| B4 | TTS narration | not-started |
| B5 | World map + token movement | not-started |

### Track C — Operator Depth

| Slice | Title | Status |
|---|---|---|
| C1 | Operator-only API surface | not-started |
| C2 | Operator React app | not-started |
| C3 | Lore-page authoring | not-started |
| C4 | Session prep workflow | not-started |
| C5 | Post-session continuity review | not-started |

## Pre-Wave Carryover

| Slice | Status | Next step |
|---|---|---|
| UI overhaul (golden slice merged) | follow-up | Reskin remaining panels (turn feed, participant strip, action bar, status panel interiors) using frame primitives — see `docs/development/workstreams/ui-design-pass.md` |
| GM anti-stall safeguards | ready | Build structural scene-progression guardrails using `docs/development/workstreams/playtester-prompt-pass.md` and the `2026-04-30-00-28.md` benchmark |

## Later

| Theme | Notes |
|---|---|
| Session prep CLI workflow | Keep it CLI-first and operator-facing |
| Post-session continuity review | Use scorecards and narrow repair workflows |
| Broader operator workflow automation | Add only after the handoff and GitHub discipline is stable |

## Blocked

None currently recorded. Add rows only for real external blockers, not general uncertainty.

## Recently Finished

| Date | Slice | Notes |
|---|---|---|
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
