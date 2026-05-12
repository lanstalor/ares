# A4: Turn-Based Combat Mode — Design Specification

**Date:** 2026-05-12
**Track:** A (Mechanical Depth)
**Goal:** Add a hybrid turn-based combat mode that layers structural initiative + HP tracking on top of the existing narrative GM flow, without disrupting free-form player input.

---

## Overview

Combat mode is a flagged state on the campaign. While active, the GM narrates encounters in initiative order: each player input represents one full round, with the GM resolving the player's action plus every NPC's action in initiative sequence, pausing at "now it is your turn." The player UI shows a structured combat panel (initiative order, round counter, HP bars, hit log) alongside the existing layout.

Combat builds on the existing foundation:

- **Dice (A1):** the GM already calls for attribute checks with d6+modifier outcomes. Combat reuses this.
- **Inventory (A2):** weapons are already structured Items with `is_equipped`. No changes.
- **Conditions (A3):** bleeding, wounded, exhausted, stunned, disarmed, prone, panicked already exist. Combat applies them through the existing condition_updates path.
- **Scene participants:** the GM already emits HP per participant each turn. Combat continues that pattern; no new damage schema.

What combat adds: explicit lifecycle (enter → rounds → exit), persisted initiative order, a hit-log line per turn, and a dedicated UI panel.

---

## Combat Lifecycle

### Entry

The GM emits `combat_state_change.action = "enter"` when narrative tension crosses into open violence — drawn weapon connects, ambush triggers, formal duel begins, attack of opportunity, etc. The decision is the GM's, same pattern as `objective_updates` and `location_change`.

On entry, the GM emits initiative rolls inline:

```json
"combat_state_change": {
  "action": "enter",
  "initiative_rolls": [
    {"name": "Gray Sergeant", "is_player": false, "initiative_score": 8},
    {"name": "Mara of Cimmeria", "is_player": true, "initiative_score": 5},
    {"name": "Obsidian Guard", "is_player": false, "initiative_score": 3}
  ]
}
```

The initiative score is `d6 + Cunning modifier`. The GM judges the modifier inline (same pattern as A1 dice rolls — no structured attribute storage yet; see Out of Scope).

The entry response itself narrates any NPC turns that come before the player's first turn. If the player has the highest initiative, the entry response just announces combat and waits for player input.

### Round progression

After entry, each subsequent player input represents one full round:

1. Player types an action.
2. GM response resolves the player's action.
3. GM narrates each subsequent NPC turn in initiative order.
4. GM narrates NPCs above the player in initiative for the *next* round.
5. Narration pauses at "it is your turn" — i.e., right before the player would act again.

The turn engine increments `combat_state.round` once per player input received during active combat.

### Exit

The GM emits `combat_state_change.action = "exit"` when:

- All non-player participants are defeated (HP ≤ 0 or fled).
- The player is defeated (HP ≤ 0 — the GM decides KO vs death vs captured narratively).
- One side surrenders or retreats.
- A third party intervenes and stops the fight.
- The fiction de-escalates (e.g., negotiation resumes).

```json
"combat_state_change": {
  "action": "exit",
  "reason": "Mara defeated all hostiles"
}
```

On exit, `campaign.combat_state` is cleared (set to null). The combat panel disappears from the UI.

---

## Architecture

### Data Model

One new column on `Campaign`:

```
combat_state: JSON (nullable)
```

When null, combat is inactive. When present:

```json
{
  "active": true,
  "round": 1,
  "initiative_order": [
    {"name": "Gray Sergeant", "is_player": false, "initiative_score": 8, "defeated": false},
    {"name": "Mara of Cimmeria", "is_player": true, "initiative_score": 5, "defeated": false},
    {"name": "Obsidian Guard", "is_player": false, "initiative_score": 3, "defeated": false}
  ],
  "last_damage": "Mara took 6 from the Gray's slingblade",
  "started_at_iso": "2026-05-12T08:30:00Z"
}
```

No new tables. No new models.

### Tool Schema Additions

Two new **optional** fields on `record_turn` input schema:

```json
"combat_state_change": {
  "type": "object",
  "description": "Emitted when combat status changes this turn. Omit when unchanged.",
  "properties": {
    "action": {"type": "string", "enum": ["enter", "exit"]},
    "initiative_rolls": {
      "type": "array",
      "description": "Required when action='enter'. Includes player and all combatant NPCs.",
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "is_player": {"type": "boolean"},
          "initiative_score": {"type": "integer", "minimum": 1, "maximum": 20}
        },
        "required": ["name", "is_player", "initiative_score"]
      }
    },
    "reason": {"type": "string", "description": "Required when action='exit'. One-line cause of exit."}
  },
  "required": ["action"]
},
"damage_summary": {
  "type": "string",
  "description": "Optional one-line hit-log entry summarizing damage this turn during combat. Example: 'Mara took 8 from the slingblade'. Emit only when damage actually occurred."
}
```

HP changes continue flowing through the existing `scene_participants` mechanism — no separate `damage_events` array.

### Turn Engine Logic

After the narrate call, before consequence application:

1. If `narration.combat_state_change` has `action == "enter"`:
   - Build `combat_state` with `active=true`, `round=1`, `initiative_order` from the emitted rolls (sorted high → low by `initiative_score`), `last_damage=""`, `started_at_iso=now`.
   - Persist to `campaign.combat_state`.

2. Else if combat is currently active:
   - Increment `campaign.combat_state["round"]` by 1.
   - If `narration.damage_summary` is non-empty, set `campaign.combat_state["last_damage"]`.
   - For each `scene_participants` entry where `current_hp <= 0`, mark the corresponding `initiative_order` entry as `defeated=true`.

3. If `narration.combat_state_change` has `action == "exit"`:
   - Set `campaign.combat_state = None`.

Order matters: the exit check runs **after** the round/damage updates, so an "exit" emitted on a turn where damage also lands still records that damage on the way out (visible in the GM context for the next non-combat turn). Actually, since combat_state is cleared on exit, the final damage_summary won't be visible after exit — that's fine, the GM's narrative already conveys it.

### Context Builder Additions

When `campaign.combat_state` is set and `active=true`, inject a new block in the hidden GM brief immediately after the "Scene state at start of this turn" block:

```
Combat state (live):
  Round: 3
  Initiative order:
    - Gray Sergeant (init 8) [HP visible via scene_participants]
    - Mara of Cimmeria (init 5) [PLAYER]
    - Obsidian Guard (init 3) [defeated]
  Last damage: Mara took 6 from the Gray's slingblade
  Rules: narrate this round in initiative order; pause before player's next turn; emit damage_summary if a hit lands; emit combat_state_change.action='exit' when resolved.
```

No change to the player-safe brief — the combat panel reads from `combat_state` directly via the existing campaign GET endpoint, not from the brief.

### NarrationResponse Updates

Add two fields to the dataclass in `app/services/ai_provider.py`:

```python
combat_state_change: dict | None = None
damage_summary: str | None = None
```

The response builder in `anthropic_provider.py::_build_response` extracts these the same way it extracts `scene_state`.

---

## Prompt Additions

A new "Combat mode" section in `_SYSTEM_PROMPT`, inserted between "Scene change discipline" and "Prose discipline":

```
Combat mode:
- Enter combat (emit combat_state_change.action='enter' with initiative_rolls) when narrative tension crosses into open violence: a drawn weapon connects, an ambush triggers, a formal duel begins, an attack of opportunity lands. Initiative is d6 + Cunning modifier per combatant. The player and every named NPC in the fight must appear in initiative_rolls.
- While combat is active, every response narrates ONE COMPLETE ROUND in initiative order, pausing at the moment immediately before the player would act again. If NPCs have higher initiative than the player, narrate their next-round actions in the same response.
- The hidden brief contains a "Combat state (live)" block with the live initiative order and round number. Narrate participants in that exact order. Do not skip turns, do not reorder.
- When a hit lands, emit damage_summary as a single short line ("Mara took 8 from the slingblade"). Update scene_participants.current_hp to reflect the new HP. Apply mechanical conditions (bleeding, wounded, prone, etc.) via condition_updates as appropriate.
- Exit combat (emit combat_state_change.action='exit' with a one-line reason) when one side is defeated, retreats, surrenders, or a third party stops the fight. The player reaching 0 HP also exits combat — narrate the result (KO, capture, death) according to the fiction, but always exit the combat state.
- The "first sentence names what changed" rule applies doubly in combat: lead with the most consequential beat of the round (a hit, a fall, a turn of momentum), not the initiative ordering or a recap.
- Combat narration is not exempt from the stock-phrase banlist. Find fresh language for hits, misses, and physical positioning.
```

---

## Frontend

### New Component: `CombatPanel.tsx`

Rendered in the right-hand utility column when `campaign.combat_state?.active === true`. Hidden otherwise.

Contents:

- **Header:** `Round {round}` + ⚔ COMBAT badge.
- **Initiative order list:**
  - One row per participant: name, initiative score, compact HP bar (driven by `scene_participants` for that name).
  - The player's row highlighted with a distinct border indicating "next up."
  - Defeated participants rendered with strikethrough and dimmed.
- **Hit log:** the most recent `last_damage` line (just the single most recent one — the campaign state only stores the latest; if we want history we can append client-side as React state since the user sees them as they arrive).
- **Compact:** target footprint ~280px wide column. Mobile-responsive collapsing to a drawer.

### Header badge

When combat is active, the existing header gains a `⚔ COMBAT — Round {n}` chip in the top-right region of the campaign tagline area.

### State source

The frontend reads `combat_state` from the existing `GET /api/v1/campaigns/{id}` response. No new endpoints. The turn submission response is the natural refresh trigger — the campaign payload is already fetched after each turn.

---

## Testing Strategy

### Backend Unit Tests

**`tests/test_anthropic_provider.py`:**
- Tool schema includes `combat_state_change` and `damage_summary` as optional.
- `_build_response` extracts `combat_state_change` and `damage_summary` into `NarrationResponse`.
- Both default to None when the GM omits them.

**`tests/test_turn_engine.py`:**
- `combat_state_change.action='enter'` builds the expected JSON on `campaign.combat_state` with initiative sorted high→low.
- When combat is active and no state change emitted, `round` increments by 1.
- `damage_summary` is persisted into `combat_state.last_damage`.
- `scene_participants` entries with `current_hp <= 0` mark the matching `initiative_order` entry as `defeated=true`.
- `combat_state_change.action='exit'` clears `campaign.combat_state`.
- Combat does not affect non-combat turns (regression check).

**`tests/test_context_builder.py`:**
- "Combat state (live)" block appears in hidden brief when `combat_state.active=true`.
- Block lists initiative order with defeated participants marked.
- Block is omitted when `combat_state` is null.
- Player-safe brief never contains the combat state block.

### Frontend Tests

- `CombatPanel` renders correctly for: no combat (hidden), active combat (visible with initiative), combat with defeated participants (strikethrough).
- Round number and last_damage update on campaign refetch.

### Playtest Validation

Run the existing playtester tool against a campaign seeded with a hostile scene (or rely on the GM to trigger combat naturally during a 30-turn run). Targets:

- At least one combat encounter enters cleanly with valid initiative rolls.
- Multi-round combat runs without state corruption.
- Combat exits cleanly on resolution (no zombie state).
- Repetition score ≥ 4.0, Flow score ≥ 4.0 across the combat turns specifically.

---

## Out of Scope

These are deferred to future slices and explicitly NOT part of A4:

- **Structured attributes on Character/NPC.** The GM continues to judge initiative modifiers and damage inline. A future slice (A5: Abilities/equipment registry) can add explicit Strength/Cunning/Will/Charm/Tech columns; combat will pick them up automatically when present.
- **Damage type system.** No kinetic/energy/poison resistances. The GM's narration carries damage type as flavor only.
- **Multi-combatant player party.** The player is always a single character.
- **Grid or map positioning.** Movement is narrative-only.
- **Reactions / opportunity attacks / readied actions.** Single free-form action per round.
- **Operator override.** The GM owns the trigger and exit. A future slice can add an operator-toggled override if needed.
- **Persistent hit log history.** Only the most recent `damage_summary` is stored server-side. The frontend may keep a session-local hit log in component state for the UI.

---

## Open Decisions

- **Initiative ties:** if two participants emit the same `initiative_score`, the order is the order the GM listed them in `initiative_rolls`. The turn engine preserves emission order on ties.
- **Mid-combat new arrivals:** if a third party enters mid-fight, the GM can emit a new `combat_state_change.action='enter'` with the updated `initiative_rolls` to re-roll initiative for the new lineup. Simple but sufficient; alternative is a separate `combat_state_add` action which feels over-designed for the current need.

---

## Rollout

Single branch, single PR. Components in dependency order:

1. Alembic migration for `Campaign.combat_state`.
2. Model + dataclass updates.
3. Tool schema additions.
4. Response parsing.
5. Turn engine combat lifecycle logic.
6. Context builder injection.
7. System prompt update.
8. Frontend CombatPanel + header badge.
9. Backend tests.
10. Frontend test (one happy-path component test).
11. Playtest run for validation.

Estimated touch: ~6 backend files, ~3 frontend files, 1 migration, ~10 new tests.
