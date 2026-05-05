# Slice C1 — Admin Api

> Template — copy to `{slice-id}-admin-api.md` and fill in. `make bootstrap-slice SLICE=C1` does this automatically.

| Field | Value |
|---|---|
| **Track** | C |
| **Branch** | `track-c/C1-admin-api` |
| **Worktree** | `~/ares-track-c/C1` |
| **PR** | TBD |
| **Status** | in-flight |
| **Last agent** | Gemini |
| **Next agent** | any |
| **Parent plan** | `~/.claude/plans/a-i-happy-matsumoto.md` |

---

## Goal

Provide a set of backend API endpoints accessible only to operator workflows that expose the full hidden state of a campaign (clocks, agendas, sealed secrets, GM-only notes) for the purpose of setup, review, and repair.

## Last-known-good commit

`f147057` — `chore(C1): bootstrap slice — branch + workstream doc`

Test status at this commit:
- backend (`make backend-test`): ✅
- frontend (`make check`): ✅
- playtester (offline, stub provider): ✅
- playwright screenshot at 5180: ✅

## In-flight WIP

- `clean` — no uncommitted edits, last commit is a `chore:`.

## Files touched so far

Append entries as you edit. Mark files complete with ✅, in-progress with ⚠️.

- `docs/development/workstreams/C1-admin-api.md` — initialized ✅

## Next concrete step

Create `backend/app/api/routes/operator.py` with a basic health check and a `GET /api/v1/operator/campaigns/{id}/full-state` endpoint that returns the complete, visibility-unfiltered campaign state (including all world entities, characters, objectives, turns, memories, clocks, and secrets).

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
