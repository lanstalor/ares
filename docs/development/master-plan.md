# Ares Master Development Plan

This file is the daily control surface for active development. Use it after `CLAUDE.md` and before opening chat history.

If you are switching agents after an interruption, use `docs/development/resume-cheatsheet.md` for the current file paths and copy-paste resume prompts.

## Now

| Issue | Workstream | Branch | PR | Last owner | Status | Next concrete step |
|---|---|---|---|---|---|---|
| TBD | `Backend NPC stats` | `TBD` | `TBD` | Next session | Ready to start | Define the backend data structure for real level/HP/disposition values |

## Next

| Priority | Slice | Why now |
|---|---|---|
| 1 | Live participant stat patching after turns | It completes the Scene Presence loop without requiring a full refresh |
| 2 | Memory rendering in status/feed | It exposes player-relevant continuity without leaking hidden state |
| 3 | Secret reveal display events | It improves narrative clarity when sealed facts become player-facing |

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
| 2026-04-26 | GM clarify sidebar chat | Added a non-persisted `?` sidebar for story clarification without advancing the game clock |
| 2026-04-26 | GM scene context + action guidance | Added `suggested_actions` and `scene_participants`, tightened feed rendering, wired scene art into the main app, and verified the Docker runtime on `:5180` |
| 2026-04-24 | Runtime/bootstrap reconciliation | Backend bootstrap, provider wiring, and frontend readiness were aligned to real status fields |

## Working Rules

- Every active feature slice should have one GitHub issue, one flat branch, one draft PR, and one workstream doc under `docs/development/workstreams/`.
- `CLAUDE.md` is for repo bootstrap and durable constraints. This file is for current priorities and active work.
- If an active branch or PR is missing, record `TBD` temporarily and create the missing artifact before starting substantial new work on that slice.
