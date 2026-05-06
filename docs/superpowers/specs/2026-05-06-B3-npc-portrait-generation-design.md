# B3: NPC Portrait Generation — Design Specification

**Date:** 2026-05-06  
**Track:** B (Sensory Polish)  
**Goal:** Generate and cache portraits for NPCs on creation and first appearance, with operator control for regeneration.

---

## Overview

When an NPC (non-player character) is created in a campaign or first appears in a scene, the system automatically generates a portrait image using the MediaProvider abstraction (B1 pattern). Portraits are cached to the frontend static directory and rendered in ParticipantStrip cards and modals. Operators can manually regenerate portraits if needed via an API endpoint.

---

## Architecture

### Data Model: NpcPortrait

A new persistent model tracks portrait generation metadata, separate from the Character/NPC definition (mirrors B2 SceneArt pattern).

```
NpcPortrait
├── id: UUID (primary key)
├── campaign_id: FK(Campaign) → cascade delete
├── npc_id: FK(Character) → cascade delete
├── slug: String(120) — derived from character name (lowercase, alphanumeric + dash)
├── prompt: Text — player-facing generation prompt
├── image_url: String(500) — local path: /portraits/{slug}.png
├── provider: String(80) — "openai", "replicate", "stub"
├── status: String(40) — "generating" | "ready" | "failed"
├── error: Text (nullable) — error message if status="failed"
├── model: String(200, nullable) — e.g., "dall-e-3", provider-specific
├── revised_prompt: Text (nullable) — used by provider (e.g., OpenAI's revised_prompt)
├── created_at: DateTime
├── updated_at: DateTime
├── Unique Constraint: (campaign_id, npc_id)
```

### Service Layer: `npc_portrait_service.py`

Mirrors `scene_art_service.py`. Provides:

- `slugify_npc_name(character_name: str) -> str` — converts "Captain Jag Delmar" → "captain-jag-delmar"
- `get_cached_portrait(session, campaign_id, npc_id) -> NpcPortrait | None` — lookup by campaign + NPC
- `build_portrait_prompt(session, character) -> str` — generates player-facing prompt
  - Includes: character name, caste (if visible), role/title, visible disposition
  - Excludes: secrets, hidden state, gm_instructions
- `ensure_portrait(session, campaign, character, force=False, media_provider=None, cache_dir=None) -> NpcPortrait`
  - Checks cache; if missing or `force=True`, calls MediaProvider
  - Writes b64 PNG to `frontend/public/portraits/{slug}.png`
  - Returns NpcPortrait with status="ready" or status="failed" + error
- `cache_portrait_response(response, slug, cache_dir)` — writes PNG to disk

### Backend API Routes

New routes in `backend/app/api/routes/portraits.py`:

- `GET /api/v1/portraits` — list all portraits for campaign (for operator debugging)
- `GET /api/v1/portraits/{npc_slug}` — metadata for single portrait
- `POST /api/v1/portraits/{npc_slug}/regenerate` — trigger regeneration (queues async task or waits synchronously)

All routes return NpcPortrait schema with status + error fields.

### Trigger Points

**1. Eager Generation (On NPC Creation)**

When an NPC is created (seeded at bootstrap or created via C1 PATCH):
- Queues async task: `queue_portrait_generation(campaign_id, npc_id)`
- If running synchronously (tests, stub provider): calls `ensure_portrait()` immediately
- NpcPortrait.status starts as "generating", transitions to "ready" or "failed"

**2. Lazy Generation (On First Appearance)**

When NPC first appears in `scene_participants`:
- Frontend checks if portrait file exists at `/portraits/{slug}.png`
- If 404 or missing: calls `POST /portraits/{slug}/regenerate` to queue generation
- Shows "generating..." placeholder while waiting
- Polls or waits for response with final status

**3. Operator Regenerate**

Operator can manually trigger via C2 admin interface (future enhancement) or direct API call:
- `POST /portraits/{slug}/regenerate` with `force=True`
- Regenerates regardless of current status
- Useful for fixing failed generations or refreshing stale portraits

---

## Prompt Building

### Player-Facing Content Only

The portrait prompt includes only what the player would realistically know or observe:
- Character name
- Caste (if visible in world)
- Role / title / occupation (e.g., "Obsidian enforcer", "Gold politician")
- Visible demeanor / disposition (e.g., "hostile", "guarded", "calculating")
- Visible scars, physical traits, attire (if already in NPC definition)

### Excluded (Hidden State)

- Secrets and sealed knowledge
- Hidden motivations or relationships
- gm_instructions or internal plot notes
- Anything marked `visibility="gm_only"` or `visibility="sealed"`

### Example Prompt

```
Generate a portrait of Captain Jag Delmar, a Gold military commander.
He is hostile and distrustful. Appear commanding, authoritative, scarred.
Red Rising universe, 728 PCE. Photorealistic, high-resolution.
```

---

## Frontend Integration

### ParticipantStrip & ParticipantModal

**Current State:**
- Already accept `portraitSrc` prop
- Render `<img src={portraitSrc} />` if present
- Fall back to character initials (e.g., "JD" for Jag Delmar)

**Changes:**
- Compute `portraitSrc` from character: `portraitSrc = character ? `/portraits/${slugify(character.name)}.png` : null`
- If file returns 404: keep fallback (initials), optionally log warning
- Add optional `onPortraitMissing(character)` callback to trigger lazy generation

### Lazy Load Trigger

When a NPC first appears in scene:
1. ParticipantStrip renders portrait with static path
2. If image fails to load (404), fire event to request generation
3. API call: `POST /api/v1/portraits/{slug}/regenerate`
4. On success: reload image or trigger refetch
5. Show "generating..." state during wait

---

## Error Handling

### Generation Failures

If MediaProvider call fails or image generation times out:
1. NpcPortrait.status = "failed"
2. NpcPortrait.error = error message (e.g., "OpenAI API timeout")
3. Frontend shows initials fallback gracefully
4. Operator can see error in `/admin` via full-state (future: dedicated portraits page)
5. Operator calls `/regenerate` to retry

### Missing Files

If `frontend/public/portraits/{slug}.png` doesn't exist but NpcPortrait.status="ready":
- Frontend falls back to initials
- Logs warning
- Next time scene loads, lazy trigger can regenerate if needed

### Stub Provider (Tests)

For offline testing:
- Stub provider generates solid-color 256×256 PNG with initials centered
- No API calls needed
- `ensure_portrait()` completes synchronously in tests

---

## Caching Strategy

**Disk Cache:** `frontend/public/portraits/{slug}.png`
- One file per NPC per campaign (slug is globally unique via campaign constraint)
- Base64 PNG written directly
- Frontend serves as static asset (no API call)
- Pre-deployment: can be checked into git or generated on-demand

**Database Cache:** NpcPortrait metadata
- Tracks generation status, error, provider, prompt
- Allows operator to see which portraits need attention
- Enables regenerate endpoint (force=True)

---

## Success Criteria

### Backend

- ✅ NpcPortrait model created with correct schema
- ✅ `npc_portrait_service.py` implements all functions
- ✅ API routes return correct payloads
- ✅ Eager generation queued on NPC creation (or sync in tests)
- ✅ Lazy generation API works (returns status, triggers if needed)
- ✅ Operator regenerate endpoint works
- ✅ Tests: portrait generation logic, caching, error cases (105+ tests passing)
- ✅ Stub provider works offline

### Frontend

- ✅ ParticipantStrip computes and uses `portraitSrc` from character
- ✅ Portraits render in cards and modals (when files exist)
- ✅ Initials fallback works smoothly if portrait missing
- ✅ Lazy load trigger fires on 404, calls regenerate API
- ✅ `make check` passes (TS, ESLint)
- ✅ `npm run build` succeeds

### Integration

- ✅ Full stack at `localhost:5180`: create NPC → portrait generated → visible in scene
- ✅ Manual test: regenerate portrait via API → file updates on disk
- ✅ Playwright screenshots: portrait in ParticipantStrip (desktop 1366×1024, mobile 390×844)
- ✅ Error case: failed generation → fallback visible, operator sees error in admin

### Hard Constraints

- ✅ Portraits are player-facing only (no hidden state in prompts)
- ✅ Canon guard not bypassed (prompts don't mention Darrow, Eo, etc.)
- ✅ MediaProvider abstraction maintained (all image calls via B1)
- ✅ Stub provider works offline (no API keys required for tests)

---

## Files to Create/Modify

### Backend (New)
- `backend/app/models/portraits.py` — NpcPortrait model
- `backend/app/services/npc_portrait_service.py` — generation logic
- `backend/app/api/routes/portraits.py` — API endpoints
- `backend/app/alembic/versions/{hash}_add_npc_portraits.py` — migration

### Backend (Modified)
- `backend/app/core/enums.py` — portrait status enum (optional)
- `backend/app/services/bootstrap.py` — queue eager generation on NPC creation
- `backend/tests/test_npc_portrait_service.py` — unit tests

### Frontend (Modified)
- `frontend/src/components/ParticipantStrip.jsx` — compute portraitSrc, add lazy load
- `frontend/public/portraits/` — directory for portrait PNGs (gitignored or committed)

### Documentation
- `docs/superpowers/specs/2026-05-06-B3-npc-portrait-generation-design.md` (this file)
- `docs/superpowers/plans/2026-05-06-B3-npc-portrait-generation.md` (after approval)

---

## Constraints & Trade-offs

### Why Separate Model (vs. portrait fields on Character)?
- **Chosen:** Separate `NpcPortrait` model (B2 pattern)
- **Benefit:** Clean separation — Character is NPC definition, NpcPortrait is generated media
- **Benefit:** Easier to extend (multiple styles, regeneration history)
- **Trade-off:** One more table, one more FK join

### Why Disk Cache (vs. Database)?
- **Chosen:** Write PNG to `frontend/public/portraits/{slug}.png`
- **Benefit:** Fast (no API call), static serving, no database blob overhead
- **Benefit:** Works offline, survives frontend rebuilds
- **Trade-off:** Ties frontend and backend tightly; deployment must sync files

### Why Eager + Lazy (vs. One or the Other)?
- **Chosen:** Eager at creation, lazy on first appearance, operator regenerate
- **Benefit:** Portraits ready when campaign starts, but also generated on-demand for edge cases
- **Benefit:** Operator has control to fix or refresh
- **Trade-off:** More complex logic, potential async/race conditions

---

## Notes for Implementation

1. **Async Queueing:** Eager generation should be async if possible (use Celery, APScheduler, or sync for now). Tests can force synchronous.
2. **Slug Uniqueness:** Within a campaign, NPC slugs must be unique. Use character name as source, ensure no collisions.
3. **Provider Config:** Portrait generation should respect `VITE_MEDIA_PROVIDER` env var (same as scene art).
4. **Frontend Path:** Portrait static path is `/portraits/{slug}.png`. Ensure `frontend/public/portraits/` is served correctly in both dev and production.
5. **Testing:** Use stub provider for all tests. No real API calls in test suite.
6. **Mobile:** Ensure portraits scale well at 390px viewport (ParticipantStrip is already responsive).
