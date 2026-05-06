# Slice B3 — NPC Portrait Generation

| Field | Value |
|---|---|
| **Track** | B |
| **Branch** | `track-b/B3-npc-portrait-generation` |
| **PR** | https://github.com/lanstalor/ares/pull/15 |
| **Status** | finished |
| **Last agent** | Haiku 4.5 |
| **Parent spec** | `docs/superpowers/specs/2026-05-06-B3-npc-portrait-generation-design.md` |

---

## Goal

Generate and cache portraits for NPCs on creation and first appearance using the MediaProvider abstraction, with automatic fallback to character initials and operator control for manual regeneration.

## Last-known-good commit

`9dfe7bc` — `docs(B3): add Playwright screenshots`

Test status at this commit:
- backend (`make backend-test`): ✅ 145 passed
- frontend (`make check`): ✅
- frontend (`npm run build`): ✅
- alembic smoke (`DATABASE_URL=sqlite:////tmp/ares-b3-migrate.db alembic upgrade head`): ✅
- docker config (`docker compose config` with temporary `.env -> .env.example` symlink): ✅
- Docker 5180 visual checkpoint: ✅ desktop (1366×1024) + mobile (390×844) Playwright screenshots
- playwright screenshot at 5180: ✅

## Files touched

Append entries as you edit. Mark files complete with ✅, in-progress with ⚠️.

### Backend — New

- ✅ `backend/app/models/portraits.py` — NpcPortrait model with campaign/NPC FK, slug, prompt, status, error tracking.
- ✅ `backend/app/services/npc_portrait_service.py` — slugify, prompt building, caching, ensure_portrait, error handling.
- ✅ `backend/app/api/routes/portraits.py` — GET /portraits, GET /portraits/{slug}, POST /portraits/{slug}/regenerate.
- ✅ `backend/alembic/versions/{timestamp}_add_npc_portraits.py` — migration to create npc_portrait table.

### Backend — Modified

- ✅ `backend/app/models/__init__.py` — export NpcPortrait.
- ✅ `backend/app/schemas/portrait.py` — NpcPortraitSchema with status, error, prompt fields.
- ✅ `backend/app/services/bootstrap.py` — queue/trigger portrait generation on NPC creation.
- ✅ `backend/app/core/dependencies.py` — portrait cache_dir parameter injection.
- ✅ `backend/app/api/router.py` — register portraits routes.
- ✅ `backend/tests/test_npc_portrait_service.py` — unit tests for slug, prompt, caching, regenerate.
- ✅ `backend/tests/conftest.py` — test fixtures for portraits and portrait generation.

### Frontend — Modified

- ✅ `frontend/src/components/ParticipantStrip.jsx` — compute portraitSrc from character slug, add lazy-load trigger on 404.
- ✅ `frontend/public/portraits/` — directory created (gitignored in `.gitignore`).
- ✅ `frontend/src/lib/api.js` — add portrait API helpers (list, current, regenerate).

### Documentation

- ✅ `assets/samples/ui-iteration/2026-05-06-B3-npc-portraits-desktop.png` — Playwright screenshot 1366×1024 showing NPC portrait in ParticipantStrip.
- ✅ `assets/samples/ui-iteration/2026-05-06-B3-npc-portraits-mobile.png` — Playwright screenshot 390×844 showing responsive layout.

## Implementation Summary

**NpcPortrait Model:**
- Persistent tracking of portrait generation metadata (slug, prompt, status, error, provider, revised_prompt).
- FK to Campaign and Character; cascade delete on both.
- Unique constraint on (campaign_id, npc_id) to prevent duplicates.

**Portrait Service Layer:**
- `slugify_npc_name()` converts character names to URL-safe slugs.
- `build_portrait_prompt()` constructs player-facing prompts using only visible state (name, caste, role, disposition).
- `ensure_portrait()` checks cache; calls MediaProvider if missing or force=True; writes PNG to `frontend/public/portraits/{slug}.png`.
- `cache_portrait_response()` handles b64 PNG writing and error tracking.

**Generation Triggers:**
1. **Eager Generation** — On NPC creation during bootstrap, async task queued (or sync in tests).
2. **Lazy Generation** — On first appearance, if portrait file missing, API endpoint triggered.
3. **Operator Regenerate** — Manual trigger via `POST /portraits/{slug}/regenerate` with `force=True`.

**Frontend Integration:**
- ParticipantStrip computes `portraitSrc` from character slug.
- Falls back gracefully to character initials if portrait missing.
- Lazy-load trigger calls regenerate API on 404.

**Error Handling:**
- Generation failures tracked in NpcPortrait.error field.
- Frontend shows initials fallback when portrait unavailable.
- Operator can view errors via full-state API and retry via regenerate endpoint.

## Next Concrete Step

B3 is finished. All tests passing (145 backend, frontend checks/build green), Playwright screenshots captured and committed. Ready for Wave 3 Sprint 2 (A3, B4, C3) or PR review prep.

## Hard Constraints Checklist

- ✅ Hidden state does not leak to player (portrait prompts contain only player-facing content).
- ✅ Canon guard not bypassed (no mention of Darrow, Eo, or sealed secrets in prompts).
- ✅ Player character remains Davan of Tharsis.
- ✅ MediaProvider abstraction maintained (all image calls via B1).
- ✅ Stub provider works offline (no API keys required for tests).

## Verification on Completion

Before marking this slice **finished**:

- [x] `make backend-test` passes (145 tests)
- [x] `make check` passes
- [x] `npm run build` passes
- [x] Alembic migration smoke test passes
- [x] Docker 5180 visual checkpoint: Playwright screenshots saved
- [x] Workstream doc fully reflects final state
- [x] Hard constraints verified
- [x] All files touched documented

## Agent Rotation Log

Append-only. One line per session.

- `2026-05-06 22:57 UTC` — Haiku 4.5 → Completed Task 10 (Playwright screenshots) and Task 11 (documentation); committed desktop/mobile screenshots; updated workstream, master-plan, and CLAUDE.md.
