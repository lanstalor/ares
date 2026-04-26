# Workstream: GM Scene Context and Action Guidance

## Goal

Extend the live turn pipeline so the GM can return scene participants and suggested next actions, and have the frontend surface them safely in the canonical game shell.

## Scope / Non-goals

- In scope: backend response shape, Anthropics tool schema, frontend session persistence for suggested actions and scene participants, Scene Presence integration, and turn-feed rendering updates needed for caste-tagged dialogue.
- Out of scope: the proposed GM clarify sidebar / `clarify` endpoint. That should be a separate feature slice with its own issue, branch, PR, and workstream doc.

## Current State

- Local changes now live on `feat-5-gm-scene-context`.
- Backend turn resolution already carries `suggested_actions` and `scene_participants`.
- Frontend `App.jsx` already persists both fields into session storage and feeds dynamic actions into `PlayerInput`.
- `buildSceneParticipants()` now accepts GM-provided participants and applies guardrails for malformed data.
- `SceneBackdrop.jsx` now uses the provided sample scene art via `frontend/public/scene-art/` instead of the abstract placeholder-only backdrop.
- `TurnFeed.jsx` now has a safer participant-aware renderer for caste-prefixed dialogue and name highlighting.
- `/ui-dev` now seeds `suggested_actions`, `scene_participants`, and caste-tagged GM dialogue so the current slice can be browser-verified without the live backend.

## Decisions Already Made

- Repo handoff docs are canonical; GitHub is a synchronized mirror, not the primary source of truth.
- This slice should stay focused on scene-context plumbing and immediate UX support, not expand into meta-GM conversation features.
- The clarify/sidebar idea is valid, but it should ship as a separate slice after this one is stabilized.

## Open Questions

- Whether `scene_participants` should eventually include live HP/level values from the backend or stay metadata-only until the dedicated NPC-stats slice lands.
- Whether the current name-highlighting behavior is sufficient for future lore-heavy narration or should eventually move from regex parsing to structured spans from the backend.

## Files Likely To Change

- `backend/app/services/anthropic_provider.py`
- `backend/app/services/turn_engine.py`
- `backend/tests/test_anthropic_provider.py`
- `backend/tests/test_turn_api_contract.py`
- `frontend/src/App.jsx`
- `frontend/src/components/TurnFeed.jsx`
- `frontend/src/lib/devUiFixture.js`

## Verification Run

- Verified on 2026-04-26:
  - `make check`
  - `make backend-test` (`62 passed`)
  - `cd frontend && npm run build`
  - `/ui-dev` browser QA at `http://127.0.0.1:5174/ui-dev`
    - scene art resolved to `/scene-art/space_docks.png`
    - seeded participants rendered in Scene Presence
    - seeded caste-prefixed GM dialogue rendered without the `[Color]` markers
    - scene backdrop copy no longer overlaps the metadata band in live mode
- Not yet verified in this workstream:
  - end-to-end live turn submission against a running backend

## Next 1-3 Steps

1. Review the current branch diff and decide whether this slice is ready for PR review as-is.
2. If the slice is stable, update PR #6 with the completed verification notes.
3. Start the GM clarify sidebar as a separate workstream on a new branch after this slice is considered done.

## GitHub Links

- Issue: #5 https://github.com/lanstalor/ares/issues/5
- Draft PR: #6 https://github.com/lanstalor/ares/pull/6
- Branch target: `feat-5-gm-scene-context`

## Session Update

- Date: 2026-04-26
- Agent: Codex
- Branch: `feat-5-gm-scene-context`
- Commit / local state: dirty working tree on the feature branch with the final feed/parser/test/dev-fixture verification pass not yet committed
- Status: in progress
- What changed: tightened `TurnFeed.jsx` parsing, added backend test coverage for the new response fields, forced the route contract test offline via the stub provider, seeded the `/ui-dev` fixture with participants/actions/caste-tagged dialogue, and browser-verified the live shell against that fixture
- Verification run: `make backend-test`, `make check`, `cd frontend && npm run build`, and Playwright browser QA on `/ui-dev`
- Known risks or unverified areas: no end-to-end live backend turn submission has been re-run yet; the current feed renderer still infers names from free text rather than using structured spans
- Exact next step: commit the final verification-backed pass, update PR #6 notes, and then split the GM clarify sidebar into its own workstream
- GitHub links: issue #5, draft PR #6
