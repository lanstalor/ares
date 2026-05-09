# Slice FG1 — New Protagonist Intro

| Field | Value |
|---|---|
| **Track** | Focus Group |
| **Branch** | `focus-group/new-protagonist-intro` |
| **Worktree** | `~/ares` |
| **PR** | https://github.com/lanstalor/ares/pull/15 |
| **Status** | review |
| **Last agent** | Codex |
| **Next agent** | any |
| **Parent plan** | `docs/development/human-in-the-loop-ux-testing-process.md` |

---

## Goal

Prepare an initial focus-group build with the same Red Rising canon, factions, Colors, and world-bible foundation, but replace Davan with a more compelling Red protagonist, a new starting zone, a new opening objective, and restored campaign intro screens/assets.

## Last-known-good commit

`bedc8e4` — `fix(G1): gate operator API behind bearer token`

Test status at this commit:
- backend (`make backend-test`): passed, 219 tests
- frontend (`make check`): passed
- frontend build (`npm run build`): passed
- playwright screenshot at 5176: passed, title screen desktop/mobile captured

## In-flight WIP

- `clean after commit` — FG1 implementation is complete pending PR/review. The branch replaces Davan with Mara of Cimmeria while keeping the 728–732 PCE Red Rising canon frame intact.

## Files touched so far

- `world_bible.md` ✅ — new HighRed protagonist Mara of Cimmeria, Surface Relay Tower 19 start zone, ghost-packet opening, updated image asset tracker.
- `backend/app/services/world_bible_parser.py` ✅ — generalized class-feature parsing and captures player-character HP from the world bible.
- `backend/app/schemas/seed.py` ✅ — seed player-character schema includes max HP.
- `backend/app/services/seed_runtime.py` ✅ — starting location now derives from the campaign-start POI and default objective is Relay 19 specific.
- `backend/app/api/routes/campaigns.py` ✅ — bootstrap fallback now creates Mara instead of Davan.
- `backend/app/services/anthropic_provider.py` ✅ — second-person narration rule no longer names Davan.
- `backend/app/services/context_builder.py` ✅ — removed hardcoded Delta Sorin relationship line.
- `backend/tests/test_world_bible_parser.py` ✅ — expects Mara, Relay 19, and HP parsing.
- `backend/tests/test_turn_api_contract.py` ✅ — expects Mara and Relay 19 on seeded campaigns.
- `frontend/src/lib/introContent.js` ✅ — restored campaign-specific intro slides around Ghost Packet / Relay 19.
- `frontend/src/components/IntroOverlay.jsx` ✅ — title screen and story slides use campaign-specific copy and image backgrounds.
- `frontend/src/components/TurnFeed.jsx` ✅ — empty-feed GM opening now defines the Weaver, Relay 19, the ghost packet, and the first actionable scene.
- `frontend/src/lib/portraitLibrary.js` ✅ — Mara portrait mapped; ephemeral GM participants no longer force missing generated portrait URLs.
- `frontend/src/styles.css` ✅ — intro overlay now sits above app chrome; generated splash/slide assets wired as backgrounds.
- `frontend/public/intro/fg1/` ✅ — compressed generated WebP intro assets.
- `frontend/public/portraits/mara-of-cimmeria.png` ✅ — generated avatar crop from the FG1 Mara relay slide.
- `frontend/src/lib/devUiFixture.js` ✅ — dev fixture now reflects Mara and Relay 19.
- `frontend/src/components/SceneBackdrop.jsx` ✅ — default scene/map labels point to Relay 19.
- `frontend/src/lib/sceneArtLibrary.js` ✅ — scene-art keyword lookup recognizes Relay 19.
- `docs/development/human-in-the-loop-ux-testing-process.md` ✅ — added FG1 intro scenario.
- `docs/development/master-plan.md` ✅ — added FG1 to Now dashboard.
- `docs/development/workstreams/FG1-new-protagonist-intro.md` ✅ — tracking stream for resumability.
- `assets/samples/ui-iteration/2026-05-08-FG1-title-final-desktop.png` ✅ — desktop visual evidence.
- `assets/samples/ui-iteration/2026-05-08-FG1-title-final-mobile.png` ✅ — mobile visual evidence.

## Next concrete step

Run the FG1 Intro Scenario from the HITL process with one human player before adding more mechanics.

## Open questions / blockers

- No current blocker.
- Optional later pivot: between *Golden Son* and *Morning Star*, but that should be a separate campaign-era branch because it requires changing the hard campaign window and named-character restrictions.

## Agent rotation log

- `2026-05-08 00:00 UTC` — Codex → created FG1 branch/workstream from `groom/operator-token-gate`; started campaign refresh; user corrected protagonist should remain Red.
- `2026-05-08 18:10 UTC` — Codex → completed Mara/Relay 19 campaign refresh, generated intro assets, wired intro flow, verified tests/build/screenshots; ready for review.
- `2026-05-09 00:10 UTC` — Codex → opened draft PR #15, ran Docker-backed seed/state/frontend smoke, and added `docs/development/focus-group/FG1-hitl-smoke-and-test-plan-2026-05-09.md`.
- `2026-05-09 00:25 UTC` — Codex → made FG1 story slides player-paced, slowed intro image pan, rebuilt frontend Docker container, and verified the first slide remains stable until Continue is clicked.
- `2026-05-09 00:50 UTC` — Codex → clarified intro terminology around the Weaver, Relay 19, the ghost packet, and Pelsin's scrub; added the opening GM stage-setting message and Mara portrait asset.

## Verification on completion

- [x] `make backend-test` passes
- [x] `make check` passes
- [x] `make frontend-build` passes
- [x] Intro flow visually checked at desktop and mobile
- [x] Workstream doc fully reflects final state
- [x] Branch pushed for handoff

## Hard constraints checklist

- [x] Hidden state does not leak to player
- [x] Canon guard not bypassed
- [x] Red Rising canon/factions/Color rules remain intact
- [x] Player character is intentionally no longer Davan of Tharsis for FG1
- [x] All AI/media calls go through Provider Protocols or documented generation tooling
- [x] Stub provider works offline
