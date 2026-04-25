# UI Dev Session Notes - 2026-04-25

## What We Changed

- Added a dedicated Vite dev route at `/ui-dev` for UI-only iteration
- Seeded the route with local mock campaign state and mock turn history
- Skipped intro/backend fetches in dev UI mode so the screen loads directly into the game HUD
- Tightened the live narrative shell so the backdrop remains visible on tablet-sized captures
- Refined typography toward a premium sci-fi display/body split
- Compressed the shell controls, campaign cards, participant strip, input box, and action bar in dev UI mode

## Verification

- `npm run build` passes in `frontend/`
- Browser QA was done with an iPad Pro 11 landscape capture against `http://localhost:5177/ui-dev`

## Next Session Defaults

- Use `/ui-dev` for layout and typography work
- Keep the background/backdrop visible before adding any more chrome
- Shrink secondary controls before expanding the narrative panels
- Leave backend-readiness truth tied to the live API outside dev mode
