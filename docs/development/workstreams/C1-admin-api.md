# Slice C1 — Admin Api

> Template — copy to `{slice-id}-admin-api.md` and fill in. `make bootstrap-slice SLICE=C1` does this automatically.

| Field | Value |
|---|---|
| **Track** | C |
| **Branch** | `track-c/C1-admin-api` |
| **Worktree** | `~/ares-track-c/C1` |
| **PR** | TBD |
| **Status** | review |
| **Last agent** | Gemini |
| **Next agent** | any |
| **Parent plan** | `~/.claude/plans/a-i-happy-matsumoto.md` |

---

## Goal

Provide a set of backend API endpoints accessible only to operator workflows that expose the full hidden state of a campaign (clocks, agendas, sealed secrets, GM-only notes) for the purpose of setup, review, and repair.

## Last-known-good commit

`af6ac16` — `feat(C1): implement operator state repair endpoint (PATCH)`

Test status at this commit:
- backend (`make backend-test`): ✅
- frontend (`make check`): ✅
- playtester (offline, stub provider): ✅
- playwright screenshot at 5180: ✅

## In-flight WIP

- `clean` — all endpoints (full-state, patch, audit) implemented and verified. Ready for operator app integration (C2).

## Files touched so far

Append entries as you edit. Mark files complete with ✅, in-progress with ⚠️.

- `docs/development/workstreams/C1-admin-api.md` — updated ✅
- `backend/app/schemas/operator.py` — created full/patch/audit schemas ✅
- `backend/app/api/routes/operator.py` — created health/full-state/patch/audit routes ✅
- `backend/app/api/router.py` — registered operator router ✅
- `backend/tests/test_operator_api.py` — added comprehensive tests ✅

## Next concrete step

The operator API surface is complete. The next concrete step is to begin **Slice C2: Operator React app**, which will utilize these endpoints to provide a human-readable interface for state inspection and repair.

## Open questions / blockers

- None.

## Agent rotation log

Append-only. One line per session.

- `2026-05-05 23:45 UTC` — Gemini → Implemented `GET /audit` and expanded `PATCH` to all world entities (Area, POI, Faction, LorePage). Verified with playtester and `make check`. Slice is feature-complete for the API surface.
- `2026-05-05 23:35 UTC` — Gemini → Implemented `PATCH /operator/campaigns/{id}/state` for state repair; updated schemas and tests; all tests passing.
- `2026-05-05 23:20 UTC` — Gemini → Resumed slice; implemented `CampaignFullState` schema and operator routes (`/health`, `/full-state`); verified with new test suite; updated master plan.
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
