# Slice UI1 — Pixel Chrome Refresh

| Field | Value |
|---|---|
| **Track** | B |
| **Branch** | `ui/UI1-pixel-chrome-refresh` |
| **Worktree** | `~/ares` |
| **PR** | TBD |
| **Status** | in-flight |
| **Last agent** | GitHub Copilot |
| **Next agent** | any |
| **Parent plan** | `~/.claude/plans/a-i-happy-matsumoto.md` |

---

## Goal

Refresh the player shell with a pixel-heavy chrome treatment, bundled chrome assets, and a dev UI route alias without changing the gameplay contract.

## Last-known-good commit

`456f490` — `test: add sonnet fallback narration benchmark`

Test status at this commit:
- backend (`make backend-test`): not-run
- frontend (`npm run build`): ✅
- playtester (offline, stub provider): not-run
- playwright screenshot at 5180: not-run

## In-flight WIP

- `clean` — no uncommitted edits, last commit is planned as a `feat:` working-state checkpoint for the UI branch.

## Files touched so far

- `frontend/src/App.jsx` — add a route alias that forces the dev UI query flag and re-sync the asset overlay mode from the URL. ✅
- `frontend/src/styles.css` — replace the previous soft terminal theme with the pixel chrome pass, updated typography, panel styling, and background treatments. ✅
- `frontend/public/chrome/frames/core_panel_high_tech_illuminated_panel_wide_default.png` — add chrome frame asset used by the refresh. ✅
- `frontend/public/chrome/frames/core_panel_inset_terminal_panel_wide_default.png` — add chrome frame asset used by the refresh. ✅
- `frontend/public/chrome/ui-pool/` — add the supporting divider and panel chrome asset pool for the refreshed UI. ✅

## Next concrete step

Capture a compose-backed 5180 screenshot for the refreshed shell and decide whether the dev-only route alias should stay as part of the branch before opening a PR or merging.

## Open questions / blockers

- The untracked `.github/agents/` files and `tools/stable-diffusion-webui/` tree are intentionally excluded from this UI branch and should be handled separately if they need to be published.

## Agent rotation log

- `2026-05-30 10:13 UTC` — GitHub Copilot → created `ui/UI1-pixel-chrome-refresh`, documented the slice, validated `npm run build`, and committed `feat(UI1): refresh pixel chrome shell`; status `in-flight`

## Verification on completion

Before marking this slice **review**:

- [ ] `make backend-test` passes
- [ ] `npm run build` passes
- [ ] Playtester runs 30 turns clean with feature flag off (default) and on
- [ ] Playwright screenshot at 5180 (UI slices only) saved under `assets/samples/ui-iteration/`
- [ ] Workstream doc fully reflects final state
- [ ] Draft PR description summarizes the slice
- [ ] `CLAUDE.md` "Recently Finished" updated if this is a major capability

## Hard constraints checklist

- [x] Hidden state does not leak to player
- [x] Canon guard not bypassed
- [x] Current player-character constraint remains documented for this branch
- [x] All AI/media/TTS calls go through a Provider Protocol
- [x] Stub provider works offline (no API key required for `make backend-test`)