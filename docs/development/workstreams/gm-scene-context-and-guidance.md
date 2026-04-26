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
- `TurnFeed.jsx` is still mid-edit and is the most likely place where the interrupted session left unfinished work.

## Decisions Already Made

- Repo handoff docs are canonical; GitHub is a synchronized mirror, not the primary source of truth.
- This slice should stay focused on scene-context plumbing and immediate UX support, not expand into meta-GM conversation features.
- The clarify/sidebar idea is valid, but it should ship as a separate slice after this one is stabilized.

## Open Questions

- Whether `scene_participants` should eventually include live HP/level values from the backend or stay metadata-only until the dedicated NPC-stats slice lands.
- Whether `TurnFeed.jsx` needs additional normalization for malformed caste tags beyond the current parsing work.

## Files Likely To Change

- `backend/app/services/anthropic_provider.py`
- `backend/app/services/turn_engine.py`
- `frontend/src/App.jsx`
- `frontend/src/components/TurnFeed.jsx`
- `frontend/src/lib/uiTheme.js`

## Verification Run

- Verified on 2026-04-26:
  - `make check`
  - `cd frontend && npm run build`
- Not yet verified in this workstream:
  - end-to-end live turn submission against a running backend
  - UI screenshot QA for the final `TurnFeed` rendering behavior

## Next 1-3 Steps

1. Finish and review the interrupted `TurnFeed.jsx` changes so caste-prefixed dialogue renders correctly and safely.
2. Run `make check` and `cd frontend && npm run build` again after the feed work is completed.
3. Create and publish the linked draft PR, then start the GM clarify sidebar as a new workstream after this slice is stabilized.

## GitHub Links

- Issue: #5 https://github.com/lanstalor/ares/issues/5
- Draft PR: #6 https://github.com/lanstalor/ares/pull/6
- Branch target: `feat-5-gm-scene-context`

## Session Update

- Date: 2026-04-26
- Agent: Codex
- Branch: `feat-5-gm-scene-context`
- Commit / local state: dirty working tree on the feature branch with backend/frontend edits related to scene participants and suggested actions plus repo workflow scaffolding
- Status: in progress
- What changed: bootstrap workstream doc created, GitHub issue opened, local work moved onto a flat feature branch, sample scene art wired into the live shell, and draft PR #6 opened so the interrupted slice can be resumed without reading prior chat first
- Verification run: existing local state passes `make check` and `cd frontend && npm run build`
- Known risks or unverified areas: `TurnFeed.jsx` changes were interrupted mid-session; no live browser verification has been recorded for the final feed behavior
- Exact next step: inspect and finish the `TurnFeed.jsx` rendering pass before starting the clarify sidebar work
- GitHub links: issue #5, draft PR #6
