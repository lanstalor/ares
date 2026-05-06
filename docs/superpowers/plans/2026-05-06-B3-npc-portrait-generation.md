# B3: NPC Portrait Generation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate and cache NPC portraits on creation and first appearance, with operator regenerate control and player-safe prompting.

**Architecture:** Backend NpcPortrait model + npc_portrait_service mirrors B2 SceneArt pattern. Eager generation queued at NPC creation, lazy generation on first scene appearance. Portraits written to `frontend/public/portraits/{slug}.png`. Frontend ParticipantStrip reads from static path with initials fallback.

**Tech Stack:** SQLAlchemy (models), Alembic (migrations), MediaProvider (B1 pattern), FastAPI (routes), pytest + TDD (tests), React (frontend).

---

## File Structure

### Backend (New)
- **`backend/app/models/portraits.py`** — NpcPortrait SQLAlchemy model with campaign + npc FKs, slug, status, error
- **`backend/app/services/npc_portrait_service.py`** — generation logic: slug, prompt building, ensure_portrait, cache_portrait_response
- **`backend/app/api/routes/portraits.py`** — FastAPI routes: list, get, regenerate
- **`backend/alembic/versions/{hash}_add_npc_portraits.py`** — migration: create portraits table, constraints
- **`backend/tests/test_npc_portrait_service.py`** — unit tests: generation, caching, errors, stub provider

### Backend (Modified)
- **`backend/app/services/bootstrap.py`** — queue portrait generation on NPC creation (3-4 lines)

### Frontend (Modified)
- **`frontend/src/components/ParticipantStrip.jsx`** — compute portraitSrc from character, add lazy-load callback
- **`frontend/public/portraits/`** — directory for cached PNGs (will be created on first generation)

---

## Task 1: Create NpcPortrait Model

**Files:**
- Create: `backend/app/models/portraits.py`
- Modify: `backend/app/models/campaign.py`, `backend/app/models/characters.py`

**Steps:**

- [ ] Write failing test for model creation
- [ ] Create NpcPortrait model with UUIDPrimaryKeyMixin, TimestampMixin, correct fields (campaign_id FK, npc_id FK, slug, prompt, image_url, provider, status, model, revised_prompt, error)
- [ ] Add relationships to Campaign and Character models
- [ ] Run test to verify it passes
- [ ] Commit: `git add backend/app/models/portraits.py backend/app/models/campaign.py backend/app/models/characters.py && git commit -m "feat(B3): add NpcPortrait model with relationships"`

**Context:** This task creates the persistent data model. Follow the B2 SceneArt pattern exactly. The model should have a unique constraint on (campaign_id, npc_id).

---

## Task 2: Create Alembic Migration

**Files:**
- Create: `backend/alembic/versions/{timestamp}_add_npc_portraits.py`

**Steps:**

- [ ] Generate migration stub with `alembic revision -m "add npc_portraits table"`
- [ ] Write upgrade() function to create npc_portraits table with all columns and FKs
- [ ] Write downgrade() function
- [ ] Run migration with `alembic upgrade head`
- [ ] Verify table exists
- [ ] Commit: `git add backend/alembic/versions/{timestamp}_add_npc_portraits.py && git commit -m "migration: create npc_portraits table"`

**Context:** Straightforward migration following Alembic conventions. Use UniqueConstraint for (campaign_id, npc_id). Include indexes on FKs.

---

## Task 3: Implement Portrait Service — Slug & Prompt

**Files:**
- Create: `backend/app/services/npc_portrait_service.py`
- Modify: `backend/tests/test_npc_portrait_service.py` (new file)

**Steps:**

- [ ] Write failing tests for slug generation (basic, lowercase, special chars, empty, max length)
- [ ] Implement `slugify_npc_name(name: str | None) -> str` using regex pattern
- [ ] Run slug tests to verify pass
- [ ] Write failing tests for prompt building (includes name/caste, excludes gm_only)
- [ ] Implement `build_portrait_prompt(session, character) -> str` - player-facing only
- [ ] Run prompt tests to verify pass
- [ ] Commit with both functions and tests

**Context:** TDD approach. Slug pattern is `[^a-z0-9]+` → replace with "-", lowercase, strip edges. Prompt should include name, caste, disposition, exclude gm_instructions and hidden state.

---

## Task 4: Implement ensure_portrait Function

**Files:**
- Modify: `backend/app/services/npc_portrait_service.py`, `backend/tests/test_npc_portrait_service.py`

**Steps:**

- [ ] Write failing tests for `get_cached_portrait()` - found and not found cases
- [ ] Implement `get_cached_portrait(session, campaign_id, npc_id) -> NpcPortrait | None`
- [ ] Write failing tests for `ensure_portrait()` - generates if missing, returns cached, force regenerates
- [ ] Implement `ensure_portrait()` function with full error handling (status=failed, error messages)
- [ ] Implement `cache_portrait_response()` to write PNG to disk
- [ ] Run all ensure_portrait tests to verify pass
- [ ] Commit: `git add backend/app/services/npc_portrait_service.py backend/tests/test_npc_portrait_service.py && git commit -m "feat(B3): implement ensure_portrait with caching"`

**Context:** This is the core logic. Handle cache hits (return immediately), misses (generate), and errors (status=failed, store error message). Use MediaProvider pattern from B1. Write b64 PNG to `frontend/public/portraits/{slug}.png`.

---

## Task 5: Create Portrait API Routes

**Files:**
- Create: `backend/app/api/routes/portraits.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_npc_portrait_routes.py`

**Steps:**

- [ ] Write failing tests for routes (GET list, GET detail, POST regenerate)
- [ ] Create portraits.py with FastAPI router, PortraitResponse schema
- [ ] Implement list, get, regenerate endpoints
- [ ] Register router in main.py under `/api/v1`
- [ ] Run route tests to verify pass
- [ ] Commit: `git add backend/app/api/routes/portraits.py backend/app/main.py backend/tests/test_npc_portrait_routes.py && git commit -m "feat(B3): add portrait API routes"`

**Context:** Standard FastAPI patterns. Regenerate should accept force=True query param. All endpoints return PortraitResponse with status, error fields.

---

## Task 6: Wire Eager Generation into Bootstrap

**Files:**
- Modify: `backend/app/services/bootstrap.py`
- Create: `backend/tests/test_bootstrap_portraits.py`

**Steps:**

- [ ] Write failing test that bootstrap creates portraits for all NPCs
- [ ] Add `_queue_npc_portraits(session, campaign)` function to bootstrap.py
- [ ] Call this function after NPC creation in bootstrap_campaign()
- [ ] Run bootstrap test to verify pass
- [ ] Commit: `git add backend/app/services/bootstrap.py backend/tests/test_bootstrap_portraits.py && git commit -m "feat(B3): queue portrait generation on bootstrap"`

**Context:** Should iterate over all characters where is_player_character=False, call ensure_portrait for each. Wrap in try/except to continue if one fails.

---

## Task 7: Update ParticipantStrip Component

**Files:**
- Modify: `frontend/src/components/ParticipantStrip.jsx`

**Steps:**

- [ ] Read current ParticipantStrip to understand structure
- [ ] Add portraitSrc computation: `character ? /portraits/${slugify(character.name)}.png : null`
- [ ] Add lazy-load trigger: fetch HEAD on portraitSrc, if 404 call `POST /api/v1/portraits/{id}/regenerate`
- [ ] Verify fallback to initials still works
- [ ] Test in browser at localhost:5180
- [ ] Commit: `git add frontend/src/components/ParticipantStrip.jsx && git commit -m "feat(B3): ParticipantStrip displays portrait URLs with lazy load"`

**Context:** Use same slug function as backend (lowercase, dashes). Lazy load should silently fail and let initials show. No breaking changes to existing props.

---

## Task 8: Full Stack Integration Test

**Files:**
- Create: `backend/tests/test_integration_portraits.py`

**Steps:**

- [ ] Write E2E test: bootstrap campaign → check portraits created → check PNG files exist
- [ ] Run test to verify pass
- [ ] Commit: `git add backend/tests/test_integration_portraits.py && git commit -m "test(B3): add E2E portrait integration test"`

**Context:** Should verify portrait records exist in DB and PNG files on disk. Use tmp_path fixture for cache_dir.

---

## Task 9: Run Full Test Suite

**Files:**
- No changes, verification only

**Steps:**

- [ ] Run `make backend-test` — expect 105+ tests PASS
- [ ] Run `make check` — expect TypeScript, ESLint pass, build success
- [ ] Start `make compose-up`, navigate to http://localhost:5180, seed intro, play turns
- [ ] Verify no console errors, portraits render
- [ ] Commit any fixes needed (if any)

**Context:** Verify all existing tests still pass and new tests don't break anything.

---

## Task 10: Playwright Screenshots

**Files:**
- Create: `assets/samples/ui-iteration/2026-05-06-B3-npc-portraits-desktop.png`
- Create: `assets/samples/ui-iteration/2026-05-06-B3-npc-portraits-mobile.png`

**Steps:**

- [ ] Start `make compose-up`
- [ ] Navigate to http://localhost:5180, seed intro, play until NPC appears
- [ ] Capture desktop screenshot (1366×1024) showing ParticipantStrip with portrait
- [ ] Resize to mobile (390×844), capture screenshot
- [ ] Verify portraits are visible in both
- [ ] Commit: `git add assets/samples/ui-iteration/2026-05-06-B3-npc-portraits-*.png && git commit -m "docs(B3): add Playwright screenshots"`

**Context:** Use browser's screenshot tool or Playwright CLI. Show both portrait + initials fallback if possible.

---

## Task 11: Update Documentation

**Files:**
- Create: `docs/development/workstreams/B3-npc-portrait-generation.md`
- Modify: `docs/development/master-plan.md`, `CLAUDE.md`

**Steps:**

- [ ] Create/update workstream doc with goal, implementation summary, files changed, hard constraints status
- [ ] Update master-plan.md: change B3 status to "finished", add to Recently Finished
- [ ] Update CLAUDE.md: mention B3 in implementation status section
- [ ] Commit: `git add docs/development/workstreams/B3-npc-portrait-generation.md docs/development/master-plan.md CLAUDE.md && git commit -m "docs(B3): update workstream and master plan"`

**Context:** Standard documentation updates following project conventions.

---

## Execution Notes

- All tasks use TDD (failing test → implementation → passing test → commit)
- Frequent commits after each task
- Backend tests should all pass by end (105+)
- Frontend changes minimal and non-breaking
- Screenshots provide visual proof of feature working
- Plan assumes stub provider for all testing (no API keys needed)

