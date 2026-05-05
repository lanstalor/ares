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

`af6ac16` — `feat(C1): implement operator state repair endpoint (PATCH)`

Test status at this commit:
- backend (`make backend-test`): ✅
- frontend (`make check`): ✅
- playtester (offline, stub provider): ✅
- playwright screenshot at 5180: ✅

## In-flight WIP

- `wip af6ac16` — implemented operator schemas, full-state endpoint, and state repair (patch) endpoint; tests pass. missing: state audit endpoints.

## Files touched so far

Append entries as you edit. Mark files complete with ✅, in-progress with ⚠️.

- `docs/development/workstreams/C1-admin-api.md` — updated ⚠️
- `backend/app/schemas/operator.py` — added patch schemas ✅
- `backend/app/api/routes/operator.py` — added `patch_campaign_state` ✅
- `backend/tests/test_operator_api.py` — added patch tests ✅

## Next concrete step

Implement an audit endpoint: `GET /api/v1/operator/campaigns/{id}/audit`. This should return a list of potential issues detected in the campaign state (e.g. clocks near max, dormant secrets with met reveal conditions, or orphaned entities) to help operators focus their repair efforts.

## Open questions / blockers

- ...

## Agent rotation log

Append-only. One line per session.

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
