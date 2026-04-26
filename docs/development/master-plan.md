# Ares Master Development Plan

This file is the daily control surface for active development. Use it after `CLAUDE.md` and before opening chat history.

If you are switching agents after an interruption, use `docs/development/resume-cheatsheet.md` for the current file paths and copy-paste resume prompts.

## Now

| Issue | Workstream | Branch | PR | Last owner | Status | Next concrete step |
|---|---|---|---|---|---|---|
| #5 | [GM scene context + action guidance](./workstreams/gm-scene-context-and-guidance.md) | `feat-5-gm-scene-context` | #6 | Codex | In progress | Commit the final verification-backed pass, update PR #6 notes, then split the GM clarify sidebar into a separate branch/issue/PR |

## Next

| Priority | Slice | Why now |
|---|---|---|
| 1 | Backend NPC stats in live scene participants | It is already the top slice in `CLAUDE.md` and the frontend hook is in place |
| 2 | Live participant stat patching after turns | It completes the Scene Presence loop without requiring a full refresh |
| 3 | Memory rendering in status/feed | It exposes player-relevant continuity without leaking hidden state |
| 4 | Secret reveal display events | It improves narrative clarity when sealed facts become player-facing |
| 5 | GM clarify sidebar | It addresses player confusion directly and should stay separate from the current scene-context plumbing slice |

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
| 2026-04-26 | Cinematic UI promoted to canonical live shell | `mode-live` is now the default play UI; `mode-staging` remains the operator entry point |
| 2026-04-24 | Runtime/bootstrap reconciliation | Backend bootstrap, provider wiring, and frontend readiness were aligned to real status fields |

## Working Rules

- Every active feature slice should have one GitHub issue, one flat branch, one draft PR, and one workstream doc under `docs/development/workstreams/`.
- `CLAUDE.md` is for repo bootstrap and durable constraints. This file is for current priorities and active work.
- If an active branch or PR is missing, record `TBD` temporarily and create the missing artifact before starting substantial new work on that slice.
