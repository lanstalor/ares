# Workstream: G1 Operator Token Gate

| Field | Value |
|---|---|
| Branch | `groom/operator-token-gate` |
| Base | `journey/2026-05-07-gameplay-ux-codebase-review` |
| Status | review |
| Last agent | Codex |
| Next agent | any |

## Goal

Make the operator API fail closed behind `ARES_OPERATOR_TOKEN`, preserving hidden-state safety before gameplay/UX grooming continues.

## Last-Known-Good Commit

`eca6b87` — `docs(J1): capture gameplay UX codebase snapshot`

Verification at that commit:

- `make check`: passed
- `make backend-test`: 215 passed
- `make frontend-build`: passed

## In-Flight WIP

`clean after commit` — implementation complete and verified locally.

- Added `ARES_OPERATOR_TOKEN` setting.
- Added backend bearer-token enforcement to all `/operator/*` routes.
- Added HTTP-level tests for unconfigured, missing, wrong, and valid operator tokens.
- Added human-in-the-loop UX testing runbook.

## Files Touched So Far

- `.env.example`
- `backend/app/core/config.py`
- `backend/app/api/routes/operator.py`
- `backend/tests/test_operator_api.py`
- `docs/development/human-in-the-loop-ux-testing-process.md`
- `docs/development/workstreams/G1-operator-token-gate.md`

## Next Concrete Step

Open a PR for review, then start the next grooming branch: `groom/provider-condition-contract`.

## Open Questions / Blockers

- Decide whether `/operator/health` should remain gated. Current implementation gates it to avoid advertising the operator surface.
- C2 still needs campaign selection cleanup after token gating; `AdminApp.jsx` currently falls back to `test-campaign`.

## Agent Rotation Log

- `2026-05-07 UTC` — Codex implemented backend operator token enforcement, drafted the HITL UX testing process, and verified `make check`, `make backend-test` (`219 passed`), and `make frontend-build`.
