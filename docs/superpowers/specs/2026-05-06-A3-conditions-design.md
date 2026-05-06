# A3: Conditions + Status Effects — Design Specification

**Date:** 2026-05-06  
**Track:** A (Mechanical Depth)  
**Goal:** Implement a conditions system where persistent and ephemeral status effects apply to characters, auto-tick during turn resolution, and render as UI chips on participant cards.

---

## Overview

Conditions represent temporary or persistent status effects applied to characters through the consequence system. Persistent conditions (bleeding, poisoned, ident-flagged, wounded, exhausted) survive across turns and carry between sessions; ephemeral conditions (stunned, disarmed, prone, panicked) last only the current turn and are cleared after turn resolution. On each turn boundary, active conditions auto-tick, apply damage or penalties via consequences, decrement their duration, and are removed when duration reaches zero.

---

## Architecture

### Data Model: Condition

A new SQLAlchemy model tracks active conditions per character.

```
Condition
├── id: UUID (primary key)
├── campaign_id: FK(Campaign) → cascade delete
├── character_id: FK(Character) → cascade delete
├── condition_type: String(40) — enum value (bleeding, poisoned, etc.)
├── duration_remaining: Integer — turns left (0 = remove after this turn)
├── persistence: String(20) — "persistent" or "ephemeral"
├── source: Text (nullable) — optional context (e.g., "combat_wound", "consequence_system")
├── created_at: DateTime
├── updated_at: DateTime
├── Unique Constraint: (campaign_id, character_id, condition_type)
```

### Condition Enum

New `ConditionType` in `backend/app/core/enums.py`:

```python
class ConditionType(StrEnum):
    # Persistent conditions (survive across turns, carry between sessions)
    BLEEDING = "bleeding"
    POISONED = "poisoned"
    IDENT_FLAGGED = "ident_flagged"
    WOUNDED = "wounded"
    EXHAUSTED = "exhausted"

    # Ephemeral conditions (last only current turn)
    STUNNED = "stunned"
    DISARMED = "disarmed"
    PRONE = "prone"
    PANICKED = "panicked"
```

### Condition Metadata

Each condition type has associated metadata (visibility, effects, base duration):

| Condition | Persistence | Visibility | Base Duration | Effect |
|-----------|-------------|------------|----------------|---------|
| Bleeding | persistent | player_facing | 3 turns | -1 hp/turn |
| Poisoned | persistent | player_facing | 3 turns | -1 hp/turn + disadvantage |
| Ident-flagged | persistent | gm_only | 5 turns | marked as Red (GM narrative) |
| Wounded | persistent | player_facing | 2 turns | disadvantage on physical checks |
| Exhausted | persistent | player_facing | 2 turns | half move speed |
| Stunned | ephemeral | player_facing | 1 turn | can't act |
| Disarmed | ephemeral | player_facing | 1 turn | lost weapon |
| Prone | ephemeral | player_facing | 1 turn | disadvantage on ranged attacks |
| Panicked | ephemeral | player_facing | 1 turn | must flee scene |

---

## Backend Flow

### 1. Condition Application (via Consequence System)

Consequences trigger condition creation through a new consequence handler:

```python
consequence_applier.apply("add_condition", {
    "character_id": "char-uuid",
    "condition_type": "bleeding",
    "duration": 3,
    "source": "combat_wound"
})
```

The applier:
- Looks up character in campaign
- Checks if condition already exists (unique constraint)
- If exists, updates duration (refresh mechanism)
- If new, creates Condition record with:
  - persistence = "persistent" or "ephemeral" (from metadata)
  - duration_remaining = duration (provided)
  - visibility = player_facing or gm_only (from metadata)
- Returns created/updated condition

### 2. Turn Boundary Processing (New Step in TurnResolution)

After consequences resolve each turn, a new method processes all active conditions:

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
            apply_condition_effect(session, character, condition)
            
            # 2. Decrement duration
            condition.duration_remaining -= 1
            
            # 3. Mark ephemeral as "should_remove" or persistent for cleanup
            if condition.persistence == "ephemeral":
                session.delete(condition)
            elif condition.duration_remaining <= 0:
                session.delete(condition)
        
        session.commit()
```

### 3. Condition Effects (Consequence Mapping)

Each condition type maps to one or more consequences:

| Condition | Consequence(s) |
|-----------|---|
| Bleeding | damage(character, 1) |
| Poisoned | damage(character, 1), apply_penalty(character, "disadvantage") |
| Ident-flagged | (narrative only; no mechanical effect) |
| Wounded | apply_penalty(character, "physical_disadvantage") |
| Exhausted | apply_penalty(character, "half_move_speed") |
| Stunned | apply_penalty(character, "cannot_act") |
| Disarmed | apply_penalty(character, "unarmed") |
| Prone | apply_penalty(character, "ranged_disadvantage") |
| Panicked | apply_penalty(character, "must_flee") |

### 4. Service Layer: `condition_service.py`

Utility functions for condition management:

```python
def add_or_refresh_condition(session, campaign, character, condition_type, duration, source):
    """Create or refresh a condition; returns Condition object."""

def get_active_conditions(session, campaign_id, character_id) -> list[Condition]:
    """Get all active conditions for a character."""

def remove_condition(session, campaign_id, character_id, condition_type):
    """Manually remove a condition (optional; not exposed to operators)."""

def get_condition_display(condition: Condition) -> dict:
    """Return UI-friendly representation: type, duration, color, icon."""
```

---

## Frontend Integration

### ParticipantStrip Rendering

Update `ParticipantStrip.jsx` to display active conditions as colored chips below character name:

```jsx
function ParticipantCard({ character, conditions }) {
  return (
    <div className="participant-card">
      <div className="participant-header">
        <h3>{character.name}</h3>
        {/* Existing: level badge, disposition, HP bar */}
      </div>
      
      {/* NEW: Condition chips */}
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
    </div>
  );
}
```

### CSS

Add condition chip styling to `frontend/src/styles.css`:

```css
.participant-conditions {
  display: flex;
  gap: 0.25rem;
  margin-top: 0.5rem;
  flex-wrap: wrap;
}

.condition-chip {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  border-radius: 3px;
  font-weight: bold;
  color: #fff;
}

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

### API Integration

Frontend fetches conditions from turn state:

```javascript
// In scene_participants or turn_resolution response
{
  character_id: "xyz",
  name: "Captain Jag",
  hp: { current: 8, max: 10 },
  conditions: [
    { id: "cond-1", condition_type: "bleeding", duration_remaining: 2 },
    { id: "cond-2", condition_type: "stunned", duration_remaining: 0 }  // Will be removed next turn
  ]
}
```

---

## Data Persistence

### Persistent Conditions

Stored in `Condition` table. Survive:
- Session reload (database persists)
- Campaign load (queries retrieve from DB)
- Between turns (auto-tick in TurnResolution)

Examples: bleeding, poisoned, ident-flagged

### Ephemeral Conditions

Stored in `Condition` table during the turn they're active. Auto-removed:
- After TurnResolution processes them (duration auto-decremented, effect applied, then deleted)
- Never persisted to next turn
- Player sees them on current turn display, gone on next turn start

Examples: stunned, disarmed, prone

---

## Hard Constraints Status

1. **✅ Hidden state never leaks to player**
   - `ident_flagged` is `gm_only` visibility; never surfaced to ParticipantStrip
   - Player-facing conditions are clearly marked in enum

2. **✅ Canon guard intact**
   - No condition mentions canon characters (Darrow, Eo, etc.)
   - Conditions are mechanical, not narrative

3. **✅ Player character remains Davan of Tharsis**
   - No change to character identity system
   - Conditions apply equally to all characters

4. **✅ Consequence system is authority**
   - All condition application goes through consequence system
   - Operators never manually manage conditions (A3 is auto-only)
   - Conditions are consequences, not primaries

5. **✅ Stub provider works offline**
   - Conditions apply synchronously in tests
   - No external API calls
   - All tests pass with stub provider

---

## Error Handling

### Duplicate Condition Application

If consequence tries to add bleeding when character already has bleeding:
- Query finds existing condition
- Update duration_remaining (refresh) instead of creating duplicate
- Log: "Refreshed bleeding duration to 3 turns"

### Character Not Found

If consequence references non-existent character:
- Query returns None
- Consequence applier logs error, continues
- Condition not created

### Invalid Condition Type

If consequence specifies unknown condition_type:
- Enum validation fails at insert time
- Database constraint error
- TurnResolution catches, logs, continues

---

## Testing Strategy

### Backend Tests (50+)

**Unit Tests:**
- Condition model creation, defaults, unique constraints
- `add_or_refresh_condition()` logic (new vs. refresh)
- `get_active_conditions()` filtering
- Effect mapping (bleeding → damage)

**Integration Tests:**
- Full turn resolution: conditions tick, effects apply, removed at 0
- Ephemeral conditions cleared after turn
- Persistent conditions survive session reload
- Consequence system integration (consequences trigger conditions)

**Stub Provider Tests:**
- All tests pass with no external API calls

### Frontend Tests

- ParticipantStrip renders condition chips when present
- Correct colors per condition type
- Hover shows duration
- Responsive at 390px and 1366px viewports

---

## Success Criteria

- ✅ Condition enum + model created with correct fields
- ✅ Alembic migration creates conditions table
- ✅ Consequence system can apply conditions
- ✅ TurnResolution processes conditions (tick, effect, cleanup)
- ✅ Ephemeral conditions auto-cleared after turn
- ✅ Persistent conditions survive session reload
- ✅ ParticipantStrip renders condition chips with correct colors
- ✅ Backend tests: 50+ tests, all passing
- ✅ Frontend: condition chips visible, responsive, styled
- ✅ Hard constraints respected (no hidden state leaks, canon guard)
- ✅ Playwright screenshots: conditions visible on ParticipantStrip

---

## Files to Create/Modify

### Backend (New)
- `backend/app/models/conditions.py` — Condition model
- `backend/app/services/condition_service.py` — Condition utilities
- `backend/alembic/versions/{hash}_add_conditions.py` — Migration
- `backend/tests/test_condition_service.py` — Unit tests
- `backend/tests/test_condition_integration.py` — Integration tests

### Backend (Modified)
- `backend/app/core/enums.py` — Add ConditionType enum
- `backend/app/services/turn_resolution.py` — Add process_conditions() call
- `backend/app/services/consequence_applier.py` — Add add_condition handler

### Frontend (Modified)
- `frontend/src/components/ParticipantStrip.jsx` — Render condition chips
- `frontend/src/styles.css` — Add condition chip styling

### Documentation
- `docs/superpowers/specs/2026-05-06-A3-conditions-design.md` (this file)
- `docs/superpowers/plans/2026-05-06-A3-conditions.md` (after approval)

---

## Notes for Implementation

1. **Condition Metadata:** Create a constant dict mapping condition_type → (visibility, base_duration, effect). Use in both applier and TurnResolution.
2. **Unique Constraint Semantics:** Only one "bleeding" per character. Re-application = refresh duration to provided value (or default from metadata).
3. **Effect Timing:** Condition effects fire AFTER consequences resolve, so consequences can set up conditions that take effect the same turn.
4. **Ephemeral Cleanup:** Delete ephemeral conditions in TurnResolution, not in a background job. Synchronous, deterministic.
5. **Testing:** Use stub provider for all tests. Conditions apply instantly, no async.
6. **Mobile Rendering:** Condition chips should wrap and not overflow at 390px viewport.
