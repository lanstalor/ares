# A3: Conditions + Status Effects — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a conditions system where persistent and ephemeral status effects apply to characters, auto-tick during turn resolution, and render as UI chips on participant cards.

**Architecture:** Backend Condition SQLAlchemy model + ConditionType enum + condition_service utilities. Turn resolution processes conditions (tick, apply effects via consequences, cleanup). Frontend ParticipantStrip renders condition chips with colors and duration. Ephemeral conditions auto-cleared after turn; persistent conditions survive sessions.

**Tech Stack:** SQLAlchemy (models), Alembic (migrations), FastAPI (routes), pytest + TDD (tests), React (frontend), Playwright (screenshots).

---

## File Structure

### Backend (New)
- **`backend/app/core/enums.py`** (modified) — Add ConditionType enum + CONDITION_METADATA constant
- **`backend/app/models/conditions.py`** — Condition SQLAlchemy model
- **`backend/app/services/condition_service.py`** — Condition utilities (add_or_refresh, get_active, remove, get_display)
- **`backend/alembic/versions/{hash}_add_conditions.py`** — Migration: create conditions table
- **`backend/tests/test_condition_service.py`** — Unit + integration tests (50+)
- **`backend/tests/test_turn_resolution_conditions.py`** — Turn boundary processing tests

### Backend (Modified)
- **`backend/app/services/turn_resolution.py`** — Add process_conditions() call
- **`backend/app/services/consequence_applier.py`** — Add add_condition handler

### Frontend (Modified)
- **`frontend/src/components/ParticipantStrip.jsx`** — Render condition chips
- **`frontend/src/styles.css`** — Add condition chip styling

### Documentation
- **`docs/development/workstreams/A3-conditions.md`** — Workstream summary
- **`docs/development/master-plan.md`** — Update A3 status to "finished"
- **`CLAUDE.md`** — Update implementation status section

---

## Task 1: Create ConditionType Enum + Metadata

**Files:**
- Modify: `backend/app/core/enums.py`

**Steps:**

- [ ] Read current enums.py to understand existing patterns
- [ ] Add ConditionType enum with all values (BLEEDING, POISONED, IDENT_FLAGGED, WOUNDED, EXHAUSTED, STUNNED, DISARMED, PRONE, PANICKED)
- [ ] Create CONDITION_METADATA constant (dict mapping condition_type → {persistence, visibility, base_duration, effect, effect_value})
- [ ] Add unit tests for enum existence and metadata structure
- [ ] Commit: `git add backend/app/core/enums.py && git commit -m "feat(A3): add ConditionType enum and metadata"`

**Context:** This establishes the authoritative list of all possible conditions and their properties. Both the service layer and TurnResolution will reference this metadata.

---

## Task 2: Create Condition Model + Migration

**Files:**
- Create: `backend/app/models/conditions.py`
- Modify: `backend/app/models/campaign.py`
- Create: `backend/alembic/versions/{timestamp}_add_conditions.py`

**Steps:**

- [ ] Write failing test for Condition model creation
- [ ] Create Condition model with:
  - UUIDPrimaryKeyMixin, TimestampMixin
  - campaign_id FK to Campaign (cascade delete)
  - character_id FK to Character (cascade delete)
  - condition_type (String, ConditionType enum)
  - duration_remaining (Integer)
  - persistence (String: "persistent" or "ephemeral")
  - source (Text, nullable)
  - Unique constraint on (campaign_id, character_id, condition_type)
- [ ] Add relationship from Campaign to conditions
- [ ] Run test to verify passes
- [ ] Generate Alembic migration: `alembic revision -m "add conditions table"`
- [ ] Write upgrade() and downgrade() functions in migration
- [ ] Run migration: `alembic upgrade head`
- [ ] Verify table exists: `psql -c "\d conditions"`
- [ ] Commit both model and migration

**Context:** Mirrors the B2 SceneArt pattern. Unique constraint ensures one condition per character per type, preventing duplicates. Persistence field determines cleanup behavior in TurnResolution.

---

## Task 3: Implement Condition Service

**Files:**
- Create: `backend/app/services/condition_service.py`
- Create: `backend/tests/test_condition_service.py`

**Steps:**

- [ ] Write failing tests for add_or_refresh_condition (new creation, refresh existing)
- [ ] Implement add_or_refresh_condition(session, campaign, character, condition_type, duration, source, metadata):
  - Query for existing condition with unique constraint (campaign_id, character_id, condition_type)
  - If found: update duration_remaining to provided duration, log refresh
  - If new: create Condition with persistence from metadata, duration, source
  - Commit and return condition
- [ ] Run tests, verify pass
- [ ] Write failing tests for get_active_conditions(session, campaign_id, character_id)
- [ ] Implement query returning list of active conditions
- [ ] Write failing tests for remove_condition(session, campaign_id, character_id, condition_type)
- [ ] Implement delete + commit
- [ ] Write failing tests for get_condition_display(condition) returning {type, duration, color, icon}
- [ ] Implement display mapping (use CONDITION_METADATA for colors)
- [ ] Run all tests, verify pass
- [ ] Commit: `git add backend/app/services/condition_service.py backend/tests/test_condition_service.py && git commit -m "feat(A3): implement condition_service utilities"`

**Context:** TDD approach. All functions must work with stub provider (no API calls). get_condition_display drives frontend rendering colors.

---

## Task 4: Add Condition Handler to Consequence Applier

**Files:**
- Modify: `backend/app/services/consequence_applier.py`
- Modify: `backend/tests/test_consequence_applier.py`

**Steps:**

- [ ] Write failing test for add_condition consequence handler
- [ ] In consequence_applier.py, add handler for "add_condition" consequence type:
  ```python
  def _handle_add_condition(self, consequence, session, campaign, character):
      condition_type = consequence.get("condition_type")
      duration = consequence.get("duration")
      source = consequence.get("source", "system")
      metadata = CONDITION_METADATA.get(condition_type)
      
      if not metadata:
          self.logger.error(f"Unknown condition type: {condition_type}")
          return None
      
      return condition_service.add_or_refresh_condition(
          session, campaign, character, condition_type, duration, source, metadata
      )
  ```
- [ ] Register handler in consequence_applier's handler map
- [ ] Write test that consequence system can trigger add_condition consequences
- [ ] Run tests, verify pass
- [ ] Commit: `git add backend/app/services/consequence_applier.py backend/tests/test_consequence_applier.py && git commit -m "feat(A3): add condition handler to consequence applier"`

**Context:** Conditions are consequences. This wiring makes consequences the authority for applying conditions. No operator manual management.

---

## Task 5: Add process_conditions() to TurnResolution

**Files:**
- Modify: `backend/app/services/turn_resolution.py`
- Modify: `backend/tests/test_turn_resolution.py`

**Steps:**

- [ ] Write failing test for turn resolution with conditions:
  - Create character with bleeding condition (duration 2)
  - Run turn resolution
  - Verify condition duration decremented to 1
  - Verify damage applied
  - Verify ephemeral conditions removed
- [ ] In turn_resolution.py, implement process_conditions(session, campaign, scene_participants):
  ```python
  def process_conditions(session, campaign, scene_participants):
      """Auto-tick conditions, apply effects, remove expired."""
      for character in scene_participants:
          conditions = session.query(Condition).filter_by(
              campaign_id=campaign.id,
              character_id=character.id
          ).all()
          
          for condition in conditions:
              # 1. Apply effect via consequence
              metadata = CONDITION_METADATA[condition.condition_type]
              effect_consequence = {
                  "type": "damage" if condition.condition_type == "bleeding" else "penalty",
                  "value": metadata["effect_value"]
              }
              consequence_applier.apply(effect_consequence, session, campaign, character)
              
              # 2. Decrement duration
              condition.duration_remaining -= 1
              
              # 3. Remove if expired
              if condition.persistence == "ephemeral" or condition.duration_remaining <= 0:
                  session.delete(condition)
          
          session.commit()
  ```
- [ ] Call process_conditions() in resolve_turn() AFTER consequences are processed
- [ ] Run test, verify pass
- [ ] Write integration test: full turn with multiple conditions (persistent + ephemeral)
- [ ] Verify persistent survives, ephemeral clears
- [ ] Commit: `git add backend/app/services/turn_resolution.py backend/tests/test_turn_resolution.py && git commit -m "feat(A3): add condition ticking to turn resolution"`

**Context:** This is the core game loop integration. Order matters: consequences fire first (can set conditions), then conditions tick and apply their effects. Ephemeral conditions are deleted after ticking; persistent conditions persist.

---

## Task 6: Update ParticipantStrip to Render Condition Chips

**Files:**
- Modify: `frontend/src/components/ParticipantStrip.jsx`

**Steps:**

- [ ] Read current ParticipantStrip structure
- [ ] Add conditions prop (array of condition objects with id, condition_type, duration_remaining)
- [ ] Add rendering block after character name/header:
  ```jsx
  {conditions && conditions.length > 0 && (
    <div className="participant-conditions">
      {conditions.map(cond => (
        <div
          key={cond.id}
          className={`condition-chip condition-${cond.condition_type}`}
          title={`${cond.condition_type} (${cond.duration_remaining} turns)`}
        >
          {cond.condition_type}
        </div>
      ))}
    </div>
  )}
  ```
- [ ] Verify no breaking changes to existing props
- [ ] Test in browser: `make frontend-dev` on localhost:5173 with sample conditions data
- [ ] Commit: `git add frontend/src/components/ParticipantStrip.jsx && git commit -m "feat(A3): ParticipantStrip renders condition chips"`

**Context:** Condition chips should appear below character header, before HP bar. No API integration yet; just prop-driven rendering. Data flows from scene_participants response from backend.

---

## Task 7: Add Condition Chip Styling

**Files:**
- Modify: `frontend/src/styles.css`

**Steps:**

- [ ] Add CSS for .participant-conditions container:
  ```css
  .participant-conditions {
    display: flex;
    gap: 0.25rem;
    margin-top: 0.5rem;
    flex-wrap: wrap;
  }
  ```
- [ ] Add .condition-chip base styling:
  ```css
  .condition-chip {
    display: inline-block;
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
    border-radius: 3px;
    font-weight: bold;
    color: #fff;
  }
  ```
- [ ] Add color variants for each condition type:
  ```css
  .condition-bleeding { background-color: #cc3333; }
  .condition-poisoned { background-color: #9933cc; }
  .condition-ident_flagged { background-color: #ffaa00; }
  .condition-wounded { background-color: #ff6b35; }
  .condition-exhausted { background-color: #ffcc00; color: #000; }
  .condition-stunned { background-color: #0099ff; }
  .condition-disarmed { background-color: #666666; }
  .condition-prone { background-color: #00cc99; }
  .condition-panicked { background-color: #ff0066; }
  ```
- [ ] Test responsive at 390px (mobile) and 1366px (desktop) viewports
- [ ] Verify chips wrap on mobile, stay inline on desktop
- [ ] Commit: `git add frontend/src/styles.css && git commit -m "feat(A3): add condition chip styling and colors"`

**Context:** Colors should be distinctive and match the Red Rising aesthetic. Flex-wrap ensures mobile readability. Yellow text on light yellow is hard to read, so exhausted overrides color to black.

---

## Task 8: Write Backend Tests (50+)

**Files:**
- Create/Modify: `backend/tests/test_condition_service.py`, `backend/tests/test_condition_integration.py`

**Steps:**

- [ ] Unit tests for Condition model:
  - [ ] Test creation with all fields
  - [ ] Test unique constraint (campaign_id, character_id, condition_type)
  - [ ] Test cascade delete on campaign delete
  - [ ] Test default values (created_at, updated_at)

- [ ] Unit tests for condition_service:
  - [ ] add_or_refresh_condition: new condition creation
  - [ ] add_or_refresh_condition: refresh existing (duration update)
  - [ ] get_active_conditions: returns list
  - [ ] get_active_conditions: filters by campaign + character
  - [ ] remove_condition: deletes
  - [ ] get_condition_display: returns correct color/icon mapping

- [ ] Integration tests for consequence system:
  - [ ] Consequence applier triggers add_condition handler
  - [ ] add_condition consequence creates Condition record
  - [ ] Re-applying same condition refreshes duration
  - [ ] Invalid condition_type fails gracefully

- [ ] Integration tests for turn resolution:
  - [ ] Process conditions decrements duration
  - [ ] Ephemeral conditions removed after turn
  - [ ] Persistent conditions survive turn
  - [ ] Condition effects (damage, penalties) applied via consequences
  - [ ] Multiple conditions on same character all tick
  - [ ] Condition at duration 0 is removed

- [ ] Edge case tests:
  - [ ] Character with no conditions (query returns empty)
  - [ ] Duration 0 condition removed immediately
  - [ ] Session reload preserves persistent conditions
  - [ ] Stub provider works offline (no API calls)

- [ ] Run full test suite: `make backend-test`
- [ ] Target: 50+ new tests passing, 105+ total
- [ ] Commit: `git add backend/tests/test_condition_service.py backend/tests/test_condition_integration.py && git commit -m "test(A3): add 50+ condition tests"`

**Context:** Heavy test coverage ensures robustness. TDD approach: failing test → implementation → passing test. All tests must use stub provider (no real API calls).

---

## Task 9: Capture Screenshots + Update Documentation

**Files:**
- Create: `assets/samples/ui-iteration/2026-05-06-A3-conditions-desktop.png`, `2026-05-06-A3-conditions-mobile.png`
- Create: `docs/development/workstreams/A3-conditions.md`
- Modify: `docs/development/master-plan.md`, `CLAUDE.md`

**Steps:**

- [ ] Start full stack: `make compose-up`
- [ ] Navigate to http://localhost:5180, seed intro (localStorage.ares_intro_seen=1)
- [ ] Play turns until character acquires a condition (via consequence or combat)
- [ ] Capture desktop screenshot (1366×1024) showing ParticipantStrip with condition chips
- [ ] Resize viewport to mobile (390×844), capture screenshot
- [ ] Verify conditions visible, colors correct, responsive
- [ ] Save screenshots to assets/samples/ui-iteration/
- [ ] Create workstream doc `docs/development/workstreams/A3-conditions.md`:
  - [ ] Goal section
  - [ ] Implementation summary (files, LOC, key design decisions)
  - [ ] Hard constraints verification (ident-flagged gm_only, no manual management, stub offline)
  - [ ] Testing summary (50+ tests passing)
  - [ ] Screenshots embedded
- [ ] Update master-plan.md:
  - [ ] Change A3 status from "not-started" to "finished"
  - [ ] Add to Recently Finished section with date + notes
- [ ] Update CLAUDE.md:
  - [ ] Add A3 to Implementation Status section
  - [ ] Note turn-boundary auto-ticking, ParticipantStrip rendering, consequence integration
- [ ] Commit: `git add assets/samples/ui-iteration/ docs/development/workstreams/A3-conditions.md docs/development/master-plan.md CLAUDE.md && git commit -m "docs(A3): capture screenshots and update workstreams"`

**Context:** Documentation and visual proof that feature works end-to-end. Screenshots show both desktop and mobile responsiveness. Workstream doc becomes the authoritative reference for future maintenance.

---

## Execution Notes

- All tasks use TDD (failing test → implementation → passing test → commit)
- Frequent commits after each task (9 commits total)
- Backend tests should reach 105+ by end
- Frontend changes minimal and non-breaking (prop-driven)
- Screenshots provide visual proof of feature working
- Hard constraints verified: ident-flagged stays gm_only, conditions consequence-driven only, stub provider works offline
- Plan assumes clean git state on main branch
