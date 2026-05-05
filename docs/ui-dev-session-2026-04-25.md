# UI Dev Session Notes - 2026-04-25

> **Historical document.** The `/ui-dev` route and these notes applied to the April 25 typography pass. Current UI-overhaul work targets the direct game shell at `http://localhost:5180/`. For the active co-development workflow, see `docs/development/workstreams/ui-design-pass.md` §"VS Code Co-Dev Loop".

## What We Changed

- Added a dedicated Vite dev route at `/ui-dev` for UI-only iteration
- Seeded the route with local mock campaign state and mock turn history
- Skipped intro/backend fetches in dev UI mode so the screen loads directly into the game HUD
- Tightened the live narrative shell so the backdrop remains visible on tablet-sized captures
- Refined typography toward a premium sci-fi display/body split
- Compressed the shell controls, campaign cards, participant strip, input box, and action bar in dev UI mode

## Verification

- `npm run build` passes in `frontend/`
- Browser QA was originally done against `/ui-dev`; current UI-overhaul testing should use the direct game shell at `http://localhost:5180/` with `localStorage.ares_intro_seen=1`.

## Next Session Defaults

- Use the direct game shell at `http://localhost:5180/` for layout and typography work; seed `localStorage.ares_intro_seen=1` to skip the intro during screenshots.
- Keep the background/backdrop visible before adding any more chrome
- Shrink secondary controls before expanding the narrative panels
- Leave backend-readiness truth tied to the live API outside dev mode
