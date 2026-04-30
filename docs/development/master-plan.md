# Ares Master Development Plan

This file is the daily control surface for active development. Use it after `CLAUDE.md` and before opening chat history.

If you are switching agents after an interruption, use `docs/development/resume-cheatsheet.md` for the current file paths and copy-paste resume prompts.

## Now

| Issue | Workstream | Branch | PR | Last owner | Status | Next concrete step |
|---|---|---|---|---|---|---|
| TBD | `UI overhaul` | `TBD` | `TBD` | Claude | Starting | Full visual redesign — operator providing reference doc + sample image |
| TBD | `GM anti-stall safeguards` | `TBD` | `TBD` | Codex | Ready to start | Build structural scene-progression guardrails using `docs/development/workstreams/playtester-prompt-pass.md` and the `2026-04-30-00-28.md` benchmark |

## Next

| Priority | Slice | Why now |
|---|---|---|
| 1 | UI overhaul assets | Generate assets once overhaul design is locked |
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
