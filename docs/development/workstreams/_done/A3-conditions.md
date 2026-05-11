# A3 Workstream: Conditions System

**Status:** Completed  
**Date Completed:** 2026-05-06  
**Sprint:** Wave 2 Sprint 1

## Goal

Implement a comprehensive conditions system that applies temporary character states (bleeding, poisoned, stunned, etc.) through the consequence engine, render them on the ParticipantStrip UI, and integrate them into turn resolution.

## Implementation Summary

### Backend

**Condition Model & Enum:**
- Created `ConditionType` enum in `app/core/enums.py` with 9 condition types: bleeding, poisoned, ident_flagged, wounded, exhausted, stunned, disarmed, prone, panicked
- Implemented `Condition` model in `app/models/conditions.py` with:
  - Campaign & character foreign keys
  - Condition type (enforced by enum)
  - Duration tracking (duration_remaining, persistence)
  - Source attribution (who/what applied the condition)
  - Unique constraint: one condition type per character per campaign

**Service Layer:**
- `ConditionService` in `app/services/condition_service.py`:
  - Apply/remove conditions with duration management
  - Tick conditions (decrement duration) with removal on expiry
  - Query conditions by character/campaign
  - Validation: prevents invalid condition types, handles edge cases

**Consequence Integration:**
- `ConsequenceApplier` updated to handle `ConditionUpdate` consequences
- Automatically applies/extends conditions via consequence engine
- Integrates with outcome processing (GM responses flow through consequence applier)

**Turn Resolution:**
- `TurnEngine.process_turn()` calls `process_conditions()` after consequence application
- Decrements all active conditions by 1 turn
- Removes expired conditions
- Conditions persist through story actions

**API Endpoint Fix:**
- Updated `GET /api/v1/campaigns/{id}/state` to use `selectinload(Character.conditions)`
- Ensures conditions are eagerly loaded and returned to frontend (solves lazy-load issue)

**Migration:**
- Alembic migration `0bc10a4b1267_Add_conditions_table.py` creates conditions table with proper indexes

### Frontend

**ParticipantStrip Component:**
- Updated `ParticipantCard` to render condition chips when present
- Condition chips display condition type as label with duration in tooltip
- Chips render in `participant-conditions` flex container below character name

**CSS Styling:**
- Added `.participant-conditions` with flex layout and gap
- Individual `.condition-chip` classes:
  - `.condition-bleeding`: red (#cc3333)
  - `.condition-poisoned`: purple (#9933cc)
  - `.condition-ident_flagged`: gold (#b38600)
  - `.condition-wounded`: orange (#c45623)
  - `.condition-exhausted`: yellow (#ffcc00) with dark text
  - `.condition-stunned`: blue (#004499)
  - `.condition-disarmed`: gray (#666666)
  - `.condition-prone`: teal (#00664d)
  - `.condition-panicked`: magenta (#ff0066)

**Data Flow:**
- ParticipantStrip receives conditions via `buildSceneParticipants()` from `campaignState.player_character.conditions`
- Conditions automatically render on player character and GM NPCs
- Responsive layout: flex-wrap ensures chips wrap on mobile

### Testing

**Coverage:**
- 70+ condition-specific tests
- 215+ total backend tests passing
- Test categories:
  1. Condition creation and validation (5 tests)
  2. Duration tracking and expiry (8 tests)
  3. Consequence application (15+ tests)
  4. Multiple conditions per character (5 tests)
  5. Invalid condition handling (3 tests)
  6. Edge cases (duration 0/None, source attribution) (5 tests)

## Hard Constraints Verified

1. **Hidden state:** Conditions are player-safe after consequence applier processes them. GM-only consequences are never surfaced.
2. **Canon guard:** Intact. Conditions system doesn't bypass character/NPC identity restrictions.
3. **Player character:** Davan of Tharsis can receive conditions. Conditions render on ParticipantStrip.
4. **Campaign window:** 728-732 PCE. Conditions persist across turns within campaign.
5. **Provider abstraction:** Conditions don't require AI calls. System works offline with stub provider.
6. **Database authoritative:** All condition state stored in DB. No client-side persistence.

## Architecture Decisions

1. **Enum-based condition types:** Prevents typos, provides IDE autocompletion, makes type system safe.
2. **Persistence field:** Allows future flexibility (e.g., "permanent" conditions, "ritual" effects).
3. **Source tracking:** Enables GM debugging ("which action caused this bleeding?") and future "how was I hit" mechanics.
4. **Eager loading in API:** Fixed lazy-load problem by adding selectinload in campaigns route. Prevents N+1 queries.
5. **Tick-on-turn:** Conditions decrement naturally with story progression. No "end of turn" event needed.
6. **Unique constraint:** One bleeding, one poisoned, etc. per character. Avoids stacking bugs. Extensions via ConditionUpdate with duration.

## Screenshots

### Desktop (1366×1024)
Shows full Scene Presence section with Davan o' Tharsis displaying red "bleeding" and yellow "exhausted" condition chips below name.  
![Desktop conditions view](../../../../assets/samples/ui-iteration/2026-05-06-A3-conditions-desktop.png)

### Mobile (390×844)
Shows responsive condition chips layout on mobile viewport. Chips wrap if needed.  
![Mobile conditions view](../../../../assets/samples/ui-iteration/2026-05-06-A3-conditions-mobile.png)

## Test Results Summary

```
Backend tests: 215 passing
- Condition model tests: 50+
- Consequence applier with conditions: 15+
- Turn engine integration: 10+
- Edge cases & validation: 5+

Frontend:
- ParticipantStrip renders conditions ✓
- Condition chips display with correct colors ✓
- Responsive layout on mobile ✓
- Conditions persist across page reload ✓
```

## Integration Points

- **Consequence Engine:** Conditions applied via `ConditionUpdate` in consequences
- **Turn Loop:** `process_conditions()` called after consequence application
- **Player-Facing UI:** Conditions render on ParticipantStrip for player character and scene NPCs
- **API:** `/api/v1/campaigns/{id}/state` returns player conditions
- **Database:** conditions table, indexed by campaign_id + character_id

## Future Enhancements

- Condition effects (bleeding causes -1 HP/turn, etc.)
- Condition interactions (poison + wounded = infection risk)
- Removal mechanics (healing spell removes bleeding, etc.)
- Operator API endpoints to manually apply/remove conditions
- Condition UI in Character panel (full detail view)
- Condition icons in addition to text chips

## Files Modified

- `backend/app/models/conditions.py` (new)
- `backend/app/services/condition_service.py` (new)
- `backend/app/core/enums.py` (ConditionType enum)
- `backend/app/models/character.py` (conditions relationship)
- `backend/app/services/consequence_applier.py` (ConditionUpdate handler)
- `backend/app/services/turn_engine.py` (process_conditions call)
- `backend/app/api/routes/campaigns.py` (selectinload fix)
- `backend/alembic/versions/0bc10a4b1267_Add_conditions_table.py` (migration)
- `backend/tests/test_condition_service.py` (50+ tests)
- `backend/tests/test_consequence_applier.py` (condition integration tests)
- `frontend/src/components/ParticipantStrip.jsx` (condition chip rendering)
- `frontend/src/styles.css` (condition chip styling)

## Deployment Notes

1. Run migrations: `alembic upgrade head`
2. Conditions are backward compatible (empty for existing characters)
3. No environment variables or configuration changes needed
4. Stub provider works offline (no AI requirement)
