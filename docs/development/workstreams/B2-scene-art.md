# Slice B2 — Scene Art

> Template — copy to `{slice-id}-scene-art.md` and fill in. `make bootstrap-slice SLICE=B2` does this automatically.

| Field | Value |
|---|---|
| **Track** | B |
| **Branch** | `track-b/B2-scene-art` |
| **Worktree** | `~/ares-track-b/B2` |
| **PR** | https://github.com/lanstalor/ares/pull/13 |
| **Status** | in-flight |
| **Last agent** | Codex |
| **Next agent** | any |
| **Parent plan** | `~/.claude/plans/a-i-happy-matsumoto.md` |

---

## Goal

Generate, cache, and surface player-safe scene art for the current campaign location through the existing MediaProvider abstraction, with offline stub behavior as the default.

## Last-known-good commit

`99d2782` — `feat(B2): add scene art generation pipeline`

Test status at this commit:
- backend (`make backend-test`): ✅ 105 passed
- frontend (`make check`): ✅
- frontend (`npm run build`): ✅
- alembic smoke (`DATABASE_URL=sqlite:////tmp/ares-b2-migrate.db alembic upgrade head`): ✅
- docker config (`docker compose config` with temporary `.env -> .env.example` symlink): ✅
- playtester (offline, stub provider): not-run
- playwright screenshot at 5180: not-run

## In-flight WIP

`wip 99d2782` — tests pass; scene-art service/cache, API route, turn-trigger, and frontend consumption are implemented. Remaining: run the Docker 5180 visual checkpoint, decide whether to add a small operator-facing regenerate control in the UI, and create/update the draft PR description.

## Files touched so far

Append entries as you edit. Mark files complete with ✅, in-progress with ⚠️.

- ✅ `.env.example` — documented media provider and scene-art cache settings.
- ✅ `docker-compose.yml` — passes media provider/cache settings into the backend container.
- ✅ `backend/alembic/env.py` — imports the media model for migrations.
- ✅ `backend/alembic/versions/c4b16f7a8b2d_add_scene_art_cache.py` — adds the scene-art cache table.
- ✅ `backend/app/models/media.py` — adds `SceneArt`.
- ✅ `backend/app/models/campaign.py` / `backend/app/models/__init__.py` — wires campaign scene-art relationship and model exports.
- ✅ `backend/app/schemas/media.py`, `backend/app/schemas/campaign.py`, `backend/app/schemas/turn.py` — adds scene-art API/read schemas and state/turn fields.
- ✅ `backend/app/services/scene_art.py` — builds player-safe prompts, calls `MediaProvider`, caches b64 images, and reuses cached records.
- ✅ `backend/app/api/routes/media.py`, `backend/app/api/router.py` — adds list/current/regenerate endpoints plus backend file serving for generated PNGs.
- ✅ `backend/app/api/routes/campaigns.py` — includes cached current scene art in campaign state.
- ✅ `backend/app/api/routes/turns.py` — triggers scene-art generation when a turn changes location.
- ✅ `frontend/src/lib/api.js` — adds scene-art API helpers.
- ✅ `frontend/src/App.jsx` — fetches current scene art when the active location changes and stores turn-triggered art.
- ✅ `frontend/src/components/SceneBackdrop.jsx` — renders API-backed scene art with static-library fallback.
- ✅ `backend/tests/test_scene_art.py` — covers prompt safety, caching, routes, and slugging.

## Next concrete step

Start the Docker truth checkpoint at 5180, open a campaign, and confirm the scene backdrop uses the API-provided `scene_art.image_url` without layout regressions. Then add a focused Playwright screenshot under `assets/samples/ui-iteration/` and mark the slice ready for review if the visual pass is clean.

## Open questions / blockers

- Draft PR: https://github.com/lanstalor/ares/pull/13
- The backend serves generated b64 PNGs at `/api/v1/media/scene-art/{filename}` so Docker does not require the frontend container to see backend-written files.
- The frontend still falls back to the existing static scene-art library when the scene-art API is unavailable.
- No in-app regenerate button was added yet; the API endpoint exists at `POST /api/v1/campaigns/{campaign_id}/scene-art/regenerate`.

## Agent rotation log

Append-only. One line per session.

- `2026-05-06 09:02 UTC` — Codex → Created draft PR #13 and pushed branch; next: Docker 5180 visual checkpoint and PR polish.
- `2026-05-06 08:59 UTC` — Codex → Bootstrapped B2, added scene-art model/migration/service/API/frontend wiring, verified backend/frontend checks; next: Docker 5180 visual checkpoint and PR polish.

## Verification on completion

Before marking this slice **review**:

- [x] `make backend-test` passes
- [x] `make check` passes
- [ ] Playtester runs 30 turns clean with feature flag off (default) and on
- [ ] Playwright screenshot at 5180 (UI slices only) saved under `assets/samples/ui-iteration/`
- [ ] Workstream doc fully reflects final state
- [x] Draft PR description summarizes the slice
- [ ] `CLAUDE.md` "Recently Finished" updated if this is a major capability

## Hard constraints checklist

- [x] Hidden state does not leak to player
- [x] Canon guard not bypassed
- [x] Player character remains Davan of Tharsis
- [x] All AI/media/TTS calls go through a Provider Protocol
- [x] Stub provider works offline (no API key required for `make backend-test`)
