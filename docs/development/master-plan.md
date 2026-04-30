# Ares Master Development Plan

This file is the daily control surface for active development. Use it after `CLAUDE.md` and before opening chat history.

If you are switching agents after an interruption, use `docs/development/resume-cheatsheet.md` for the current file paths and copy-paste resume prompts.

## Now

| Issue | Workstream | Branch | PR | Last owner | Status | Next concrete step |
|---|---|---|---|---|---|---|
| TBD | `UI design pass` | `TBD` | `TBD` | Claude | Phase 1 ready | CSS panel enclosure system — see `docs/development/workstreams/ui-design-pass.md` |

## Next

| Priority | Slice | Why now |
|---|---|---|
| 1 | UI asset generation | Scene art (5 locations), caste icons (7), panel corner piece, grain texture, ARES wordmark — see asset inventory in ui-design-pass.md |
| 2 | Session prep CLI workflow | Keep it CLI-first and operator-facing |
| 3 | Post-session continuity review | Use scorecards and narrow repair workflows |

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
