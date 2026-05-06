# Slice B2 — Scene Art

> Template — copy to `{slice-id}-scene-art.md` and fill in. `make bootstrap-slice SLICE=B2` does this automatically.

| Field | Value |
|---|---|
| **Track** | A / B / C |
| **Branch** | `track-b/B2-scene-art` |
| **Worktree** | `~/ares-track-b/B2` |
| **PR** | TBD |
| **Status** | not-started / in-flight / review / blocked |
| **Last agent** | — |
| **Next agent** | any |
| **Parent plan** | `~/.claude/plans/a-i-happy-matsumoto.md` |

---

## Goal

One sentence. What does "done" look like for this slice?

## Last-known-good commit

`{sha}` — `{message}`

Test status at this commit:
- backend (`make backend-test`): ✅ / ❌ / not-run
- frontend (`make check`): ✅ / ❌ / not-run
- playtester (offline, stub provider): ✅ / ❌ / not-run
- playwright screenshot at 5180: ✅ / ❌ / not-run

## In-flight WIP

State exactly one of:

- `clean` — no uncommitted edits, last commit is a `feat:` or `fix:`.
- `wip {sha}` — committed-but-incomplete; tests pass; what is still missing: ___
- `handoff {sha}` — committed-but-broken; what is broken: ___; what works: ___

## Files touched so far

Append entries as you edit. Mark files complete with ✅, in-progress with ⚠️.

- `backend/app/...` — what changed
- `frontend/src/...` — what changed

## Next concrete step

Literal 1–3 sentences. Not "continue work on inventory" — instead: "wire `Roll` into `_TOOL_SCHEMA._properties` in `anthropic_provider.py:142`, then update `_build_response` to translate `tool_input['rolls']` into `RollResult` dataclass instances."

## Open questions / blockers

- ...

## Agent rotation log

Append-only. One line per session.

- `YYYY-MM-DD HH:MM UTC` — Agent → what was done; status at end of session
- ...

## Verification on completion

Before marking this slice **review**:

- [ ] `make backend-test` passes
- [ ] `make check` passes
- [ ] Playtester runs 30 turns clean with feature flag off (default) and on
- [ ] Playwright screenshot at 5180 (UI slices only) saved under `assets/samples/ui-iteration/`
- [ ] Workstream doc fully reflects final state
- [ ] Draft PR description summarizes the slice
- [ ] `CLAUDE.md` "Recently Finished" updated if this is a major capability

## Hard constraints checklist

- [ ] Hidden state does not leak to player
- [ ] Canon guard not bypassed
- [ ] Player character remains Davan of Tharsis
- [ ] All AI/media/TTS calls go through a Provider Protocol
- [ ] Stub provider works offline (no API key required for `make backend-test`)
