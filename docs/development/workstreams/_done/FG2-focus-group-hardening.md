# Slice FG2 — Focus Group Hardening

| Field | Value |
|---|---|
| **Track** | Focus Group |
| **Branch** | `groom/fg-focus-group-hardening` |
| **Worktree** | `~/ares` |
| **PR** | TBD |
| **Status** | review |
| **Last agent** | Codex |
| **Next agent** | any |
| **Parent plan** | `docs/development/human-in-the-loop-ux-testing-process.md` |

---

## Goal

Harden the current Mara / Relay 19 focus-group build before human testing by closing concrete hidden-state leaks, provider contract gaps, opening pressure-clock gaps, and scene-stall risks.

## Last-known-good commit

`f833494` — `fix(FG1): clarify intro stakes and add Mara portrait`

Verification at that commit:
- `npm run build`: passed
- `make check`: passed
- `backend/.venv/bin/pytest backend/tests/test_world_bible_parser.py backend/tests/test_turn_api_contract.py`: passed
- Docker frontend/backend rebuilt and LAN smoke passed for FG1 intro and Mara portrait

## In-flight WIP

`clean after commit` — implementation complete and fast-forwarded into FG1 / PR #15 before the first human focus-group pass.

## Files touched so far

- `backend/app/services/anthropic_provider.py` — provider schema/parser now includes `condition_updates`; fixed module-level `self.logger` bug.
- `backend/app/api/routes/campaigns.py` — player-facing campaign state filters GM-only conditions.
- `backend/app/services/world_bible_parser.py` — parses GM-only campaign clock table from the opening section.
- `backend/app/services/seed_runtime.py` — seeds opening pressure clocks and appends clock guidance to objective GM instructions.
- `backend/app/services/context_builder.py` — hidden brief includes a scene progression guard with recent GM beats.
- `world_bible.md` — added Relay 19 opening pressure clocks.
- `docs/development/master-plan.md` — current campaign premise now names Mara/Relay 19 and marks older Davan references historical.
- `backend/tests/` — focused coverage for provider condition contract, condition visibility filtering, seeded clocks, and scene progression guard.

## Next concrete step

Run the FG1 Intro Scenario and First Meaningful Turn HITL pass from PR #15. Log findings under `docs/development/ux-tests/`.

## Open questions / blockers

- No blocker.
- Later architecture slice: field-level visibility / EntityField remains deferred until after initial HITL unless testing exposes a leak that requires it.

## Agent rotation log

- `2026-05-10 UTC` — Codex created `groom/fg-focus-group-hardening` from FG1, implemented provider condition updates, player-safe condition filtering, Relay 19 pressure clocks, scene progression guardrails, and sprint-doc alignment. Verified full backend suite, frontend build/check, Docker smoke, LAN app URL, seeded clocks, and player-safe filtering for `ident_flagged`; fast-forwarded FG1 / PR #15 to include the hardening commits.

## Verification on completion

- [x] `make backend-test` passes
- [x] `make check` passes
- [x] `npm run build` passes
- [x] Docker stack rebuilds
- [x] LAN focus-group URL loads
- [x] Workstream doc fully reflects final state
- [x] Branch pushed for handoff

## Hard constraints checklist

- [x] Hidden state does not leak to player
- [x] Canon guard not bypassed
- [x] Red Rising canon/factions/Color rules remain intact
- [x] Focus-group player character remains Mara of Cimmeria
- [x] All AI/media calls go through Provider Protocols or documented generation tooling
- [x] Stub provider works offline
