# Slice C2 — Operator App

| Field | Value |
|---|---|
| **Track** | C |
| **Branch** | `track-c/C2-operator-app` |
| **Worktree** | `~/ares-track-c/C2` |
| **PR** | TBD |
| **Status** | review |
| **Last agent** | Codex |
| **Next agent** | any |
| **Parent plan** | `~/.claude/plans/a-i-happy-matsumoto.md` |

---

## Goal

Provide operators a web-based admin interface (`/admin`) to view and edit campaign hidden state (Objectives, Clocks, Secrets, NPCs, Campaign metadata) without touching the player-facing game UI.

## Last-known-good commit

`cc11f5a` — `docs(C2): add Playwright screenshots of operator admin UI`

Test status at this commit:
- backend (`make backend-test`): ✅ 105 passed (no changes to backend in this slice)
- frontend (`make check`): ✅ passed
- frontend (`npm run build`): ✅ passed
- playtester (offline, stub provider): ✅ not-run (no feature flag changes)
- playwright screenshot at 5180: ✅ captured (desktop + mobile)

## In-flight WIP

`clean after commit` — all 14 implementation tasks complete. Slice ready for PR review.

## Files touched so far

### Frontend - New (Created)
- ✅ `frontend/src/admin/AdminApp.jsx` — main admin app, token-gating, context provider
- ✅ `frontend/src/admin/AdminLogin.jsx` — token input form
- ✅ `frontend/src/admin/hooks/useOperatorApi.js` — API client for C1 endpoints
- ✅ `frontend/src/admin/__tests__/useOperatorApi.test.js` — API client tests
- ✅ `frontend/src/admin/components/AdminSidebar.jsx` — navigation sidebar
- ✅ `frontend/src/admin/components/EntityTable.jsx` — reusable table component
- ✅ `frontend/src/admin/components/EntityModal.jsx` — reusable modal/form component
- ✅ `frontend/src/admin/pages/CampaignPage.jsx` — campaign metadata editor
- ✅ `frontend/src/admin/pages/ObjectivesPage.jsx` — objectives table + editor
- ✅ `frontend/src/admin/pages/ClocksPage.jsx` — clocks table + editor
- ✅ `frontend/src/admin/pages/SecretsPage.jsx` — secrets table + editor
- ✅ `frontend/src/admin/pages/NPCsPage.jsx` — NPCs table + editor

### Frontend - Modified
- ✅ `frontend/src/App.jsx` — added /admin route with lazy loading
- ✅ `frontend/src/main.jsx` — wrapped App with BrowserRouter
- ✅ `frontend/src/styles.css` — added admin-specific styling (352 lines)

### Documentation - Created
- ✅ `docs/superpowers/specs/2026-05-06-C2-operator-app-design.md` — design spec
- ✅ `docs/superpowers/plans/2026-05-06-C2-operator-app.md` — implementation plan

### Assets - Created
- ✅ `assets/samples/ui-iteration/2026-05-06-C2-operator-app-desktop.png` — desktop screenshot
- ✅ `assets/samples/ui-iteration/2026-05-06-C2-operator-app-mobile.png` — mobile screenshot

## Next concrete step

Open or update the draft PR for review. After merge, update `docs/development/master-plan.md` and `CLAUDE.md` from the main checkout if they are not already current.

## Open questions / blockers

None currently.

## Agent rotation log

Append-only. One line per session.

- `2026-05-06 09:30 UTC` — Codex → Brainstormed C2 design (separate /admin route, sidebar nav, modal editors, token-gating). Design spec written and approved. Implementation plan created with 14 tasks (foundation → navigation → entity pages → polish).
- `2026-05-06 10:15 UTC` — Subagents → Executed all 14 implementation tasks via subagent-driven-development: routes/auth/API (tasks 1-4), navigation/campaign (tasks 5-6), reusable components (task 7), entity pages (tasks 8-11), styles/testing/screenshots (tasks 12-14). All tasks complete, committed, and verified.
- `2026-05-07 UTC` — Codex → Cleaned the workstream doc from template state, restored accidentally deleted root screenshots, and prepared the branch for PR review.

## Verification on completion

Before marking this slice **review**:

- [x] `make backend-test` passes
- [x] `make check` passes
- [ ] Playtester runs 30 turns clean with feature flag off (default) and on — not run; no turn-loop changes in C2
- [x] Playwright screenshot at 5180 (UI slices only) saved under `assets/samples/ui-iteration/`
- [x] Workstream doc fully reflects final state
- [ ] Draft PR description summarizes the slice
- [x] `CLAUDE.md` "Recently Finished" updated if this is a major capability

## Hard constraints checklist

- [x] Hidden state does not leak to player
- [x] Canon guard not bypassed
- [x] Player character remains Davan of Tharsis
- [x] All AI/media/TTS calls go through a Provider Protocol
- [x] Stub provider works offline (no API key required for `make backend-test`)
