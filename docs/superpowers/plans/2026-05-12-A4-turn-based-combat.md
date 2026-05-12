# A4 Turn-Based Combat Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add hybrid turn-based combat mode layered on the existing narrative GM flow — initiative tracker, round counter, HP bars, hit log — without disrupting free-form player input.

**Architecture:** One new JSON column `Campaign.combat_state`. Two new optional tool fields (`combat_state_change`, `damage_summary`). Turn engine manages combat lifecycle. Context builder injects live combat state into the hidden brief. New `CombatPanel.jsx` rendered when combat is active. Builds on existing dice (A1), conditions (A3), scene_participants, and the chat-quality slice.

**Tech Stack:** Python 3.12 / FastAPI / SQLAlchemy / Alembic / OpenAI + Anthropic SDKs / React + Vite / pytest. Spec: `docs/superpowers/specs/2026-05-12-A4-turn-based-combat-design.md`. Branch: `feat/a4-turn-based-combat`. Last migration head: `741c8686e3a3`.

---

## File Structure

**Backend create:**
- `backend/alembic/versions/<auto-rev>_add_combat_state_to_campaign.py`

**Backend modify:**
- `backend/app/models/campaign.py` — add `combat_state` JSON column.
- `backend/app/services/ai_provider.py` — extend `NarrationResponse`.
- `backend/app/services/anthropic_provider.py` — tool schema, prompt, parser.
- `backend/app/services/turn_engine.py` — combat lifecycle logic.
- `backend/app/services/context_builder.py` — combat-state injection into hidden brief.
- `backend/app/schemas/campaign.py` — expose `combat_state` on `CampaignState`.
- `backend/app/api/routes/campaigns.py` — populate `combat_state` in response.

**Backend tests (modify/append):**
- `backend/tests/test_anthropic_provider.py`
- `backend/tests/test_turn_engine.py`
- `backend/tests/test_context_builder.py`
- `backend/tests/test_campaigns_api.py` (or whichever campaigns route tests live in)

**Frontend create:**
- `frontend/src/components/CombatPanel.jsx`

**Frontend modify:**
- `frontend/src/App.jsx` — render `CombatPanel` + header badge when active.
- `frontend/src/styles.css` — minimal CSS for combat panel + badge.

No new modules. No new tables.

---

## Notes for engineers

- Run tests from `/home/lans/ares/backend` with venv `.venv` (the real one — `venv` is a stub). Activate: `cd backend && source .venv/bin/activate && pytest -q`.
- Test fixtures in `test_context_builder.py` and `test_turn_engine.py` use inline `_make_session()` / `_make_campaign()` / `_bootstrap_scenario()` helpers — NOT pytest fixtures. Match that pattern.
- The Anthropic provider exports `_TOOL_SCHEMA`, `_build_response`, `_format_user_message`, `build_system_prompt`, `build_tool_schema`. OpenAI provider re-imports those, so updating Anthropic covers both providers.
- Branch `feat/a4-turn-based-combat` is already checked out. Spec is already committed (`2cf876c`). New commits chain from there.
- The frontend dev URL for visual checks is `http://localhost:5180/` (Docker compose). Use `make compose-up` if not already running. Seed `localStorage.ares_intro_seen=1` to skip the intro.

---

## Task 1: Migration + Campaign.combat_state column

**Files:**
- Create: `backend/alembic/versions/<rev>_add_combat_state_to_campaign.py`
- Modify: `backend/app/models/campaign.py`

- [ ] **Step 1: Generate migration**

```bash
cd /home/lans/ares/backend && source .venv/bin/activate
alembic revision -m "add combat state to campaign"
```

Note the revision hex from the generated filename.

- [ ] **Step 2: Replace migration body**

```python
"""add combat state to campaign

Revision ID: <REV>
Revises: 741c8686e3a3
Create Date: <auto>

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "<REV>"
down_revision: Union[str, None] = "741c8686e3a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("campaigns", sa.Column("combat_state", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("campaigns", "combat_state")
```

- [ ] **Step 3: Apply**

```bash
alembic upgrade head
```

Expected: `Running upgrade 741c8686e3a3 -> <REV>, add combat state to campaign`.

- [ ] **Step 4: Add field to Campaign model**

In `backend/app/models/campaign.py`, immediately after the existing `narrative_summary: Mapped[str | None] = mapped_column(Text(), nullable=True)` line, add:

```python
    combat_state: Mapped[dict | None] = mapped_column(JSON, nullable=True)
```

`JSON` is already imported (used by `last_scene_state`). If somehow it's not, add to the import line.

- [ ] **Step 5: Verify**

```bash
python -c "from app.models.campaign import Campaign; print('combat_state' in Campaign.__table__.columns)"
```

Expected: `True`.

- [ ] **Step 6: Commit**

```bash
git add backend/alembic/versions/*_add_combat_state_to_campaign.py backend/app/models/campaign.py
git commit -m "feat: add combat_state column to campaigns"
```

---

## Task 2: Extend `NarrationResponse` and add tool schema + parser (TDD)

**Files:**
- Modify: `backend/app/services/ai_provider.py`
- Modify: `backend/app/services/anthropic_provider.py`
- Modify: `backend/tests/test_anthropic_provider.py`

- [ ] **Step 1: Extend `NarrationResponse`**

In `backend/app/services/ai_provider.py`, the `NarrationResponse` dataclass currently has `scene_state` and `narrative_summary_update`. Append two more fields at the end:

```python
    combat_state_change: dict | None = None
    damage_summary: str | None = None
```

- [ ] **Step 2: Write failing tests**

Append to `backend/tests/test_anthropic_provider.py`:

```python
def test_tool_schema_includes_combat_fields():
    from app.services.anthropic_provider import build_tool_schema

    schema = build_tool_schema()
    props = schema["input_schema"]["properties"]
    required = schema["input_schema"]["required"]

    assert "combat_state_change" in props
    assert "combat_state_change" not in required  # optional
    cs_props = props["combat_state_change"]["properties"]
    assert cs_props["action"]["enum"] == ["enter", "exit"]
    assert "initiative_rolls" in cs_props
    assert "reason" in cs_props

    assert "damage_summary" in props
    assert "damage_summary" not in required


def test_build_response_extracts_combat_fields():
    from app.services.anthropic_provider import _build_response

    tool_input = {
        "narrative": "n",
        "player_safe_summary": "s",
        "consequences": {},
        "suggested_actions": [],
        "scene_participants": [],
        "scene_state": {"tension_tier": 3, "key_holdings": "", "last_concrete_change": "c"},
        "combat_state_change": {
            "action": "enter",
            "initiative_rolls": [
                {"name": "Gray Sergeant", "is_player": False, "initiative_score": 8},
                {"name": "Mara", "is_player": True, "initiative_score": 5},
            ],
        },
        "damage_summary": "Mara took 6 from the slingblade",
    }
    response = _build_response(tool_input)

    assert response.combat_state_change == tool_input["combat_state_change"]
    assert response.damage_summary == "Mara took 6 from the slingblade"


def test_build_response_handles_missing_combat_fields():
    from app.services.anthropic_provider import _build_response

    tool_input = {
        "narrative": "n",
        "player_safe_summary": "s",
        "consequences": {},
        "suggested_actions": [],
        "scene_participants": [],
        "scene_state": {"tension_tier": 0, "key_holdings": "", "last_concrete_change": "x"},
    }
    response = _build_response(tool_input)
    assert response.combat_state_change is None
    assert response.damage_summary is None
```

Run:
```bash
pytest backend/tests/test_anthropic_provider.py -k "combat_fields" -v
```

Expected: FAIL (missing schema fields and unsupported kwargs on NarrationResponse if Step 1 wasn't done).

- [ ] **Step 3: Add tool schema fields**

In `backend/app/services/anthropic_provider.py`, inside `_TOOL_SCHEMA["input_schema"]["properties"]`, AFTER the existing `"narrative_summary_update"` entry (added in the chat-quality slice), add:

```python
            "combat_state_change": {
                "type": "object",
                "description": "Emit when combat status changes this turn. Omit when unchanged.",
                "properties": {
                    "action": {"type": "string", "enum": ["enter", "exit"]},
                    "initiative_rolls": {
                        "type": "array",
                        "description": "Required when action='enter'. Player + all combatant NPCs. Initiative score is d6 + Cunning modifier.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "is_player": {"type": "boolean"},
                                "initiative_score": {"type": "integer", "minimum": 1, "maximum": 20},
                            },
                            "required": ["name", "is_player", "initiative_score"],
                        },
                    },
                    "reason": {
                        "type": "string",
                        "description": "Required when action='exit'. One-line cause: defeated, retreated, surrendered, de-escalated, third-party intervention.",
                    },
                },
                "required": ["action"],
            },
            "damage_summary": {
                "type": "string",
                "description": "Optional one-line hit-log entry during combat. Example: 'Mara took 8 from the slingblade'. Emit only when damage actually landed.",
            },
```

`combat_state_change` and `damage_summary` are **not** added to the top-level `required` list — both remain optional.

- [ ] **Step 4: Extend `_build_response`**

In `backend/app/services/anthropic_provider.py`, locate `_build_response`. After the existing `narrative_summary_update = ...` extraction (added in chat-quality slice), and BEFORE the `return NarrationResponse(` call, add:

```python
    raw_combat = tool_input.get("combat_state_change")
    combat_state_change = raw_combat if isinstance(raw_combat, dict) else None

    raw_damage = tool_input.get("damage_summary")
    damage_summary = (
        raw_damage.strip() if isinstance(raw_damage, str) and raw_damage.strip() else None
    )
```

Inside the `return NarrationResponse(` call, after the `narrative_summary_update=narrative_summary_update,` line, insert:

```python
        combat_state_change=combat_state_change,
        damage_summary=damage_summary,
```

- [ ] **Step 5: Run tests**

```bash
pytest backend/tests/test_anthropic_provider.py -v
```

Expected: all pass (existing + 3 new).

- [ ] **Step 6: Commit**

```bash
git add backend/app/services/ai_provider.py backend/app/services/anthropic_provider.py backend/tests/test_anthropic_provider.py
git commit -m "feat: add combat_state_change and damage_summary to tool schema and response"
```

---

## Task 3: Turn engine — enter combat (TDD)

**Files:**
- Modify: `backend/app/services/turn_engine.py`
- Modify: `backend/tests/test_turn_engine.py`

- [ ] **Step 1: Add failing test**

Append to `backend/tests/test_turn_engine.py`:

```python
def test_resolve_turn_enters_combat() -> None:
    session = _make_session()
    campaign = _make_campaign(session)

    from app.services.ai_provider import NarrationResponse
    from app.services.consequence_applier import Consequences
    from app.services.turn_engine import resolve_turn

    class _Stub:
        def narrate(self, request):
            return NarrationResponse(
                narrative="The Gray draws his slingblade.",
                player_safe_summary="Combat erupts.",
                consequences=Consequences(),
                scene_state={"tension_tier": 4, "key_holdings": "Gray has blade", "last_concrete_change": "Combat began"},
                combat_state_change={
                    "action": "enter",
                    "initiative_rolls": [
                        {"name": "Mara", "is_player": True, "initiative_score": 5},
                        {"name": "Gray Sergeant", "is_player": False, "initiative_score": 8},
                        {"name": "Obsidian Guard", "is_player": False, "initiative_score": 3},
                    ],
                },
            )
        def clarify(self, request):
            return ""

    resolve_turn(session=session, campaign=campaign, player_input="brace", narration_provider=_Stub())

    session.refresh(campaign)
    assert campaign.combat_state is not None
    assert campaign.combat_state["active"] is True
    assert campaign.combat_state["round"] == 1
    order = campaign.combat_state["initiative_order"]
    assert [p["name"] for p in order] == ["Gray Sergeant", "Mara", "Obsidian Guard"]
    assert order[0]["initiative_score"] == 8
    assert order[0]["defeated"] is False
    assert order[1]["is_player"] is True
    assert campaign.combat_state["last_damage"] == ""
    assert "started_at_iso" in campaign.combat_state
```

Run:
```bash
pytest backend/tests/test_turn_engine.py::test_resolve_turn_enters_combat -v
```

Expected: FAIL — `campaign.combat_state` is None.

- [ ] **Step 2: Add helper and call site**

In `backend/app/services/turn_engine.py`, near the top of the file (after the existing imports), add:

```python
from datetime import datetime, timezone
```

Then, immediately after the existing block:

```python
    if narration.scene_state is not None:
        campaign.last_scene_state = narration.scene_state
    if narration.narrative_summary_update:
        campaign.narrative_summary = narration.narrative_summary_update
```

ADD:

```python
    _apply_combat_state_change(campaign, narration)
```

Then at the bottom of `turn_engine.py`, append the helper:

```python
def _apply_combat_state_change(campaign: Campaign, narration) -> None:
    """Apply combat lifecycle changes emitted by the GM this turn.

    Handles: enter (build state), progression (increment round, persist damage,
    mark defeated), and exit (clear state).
    """
    change = narration.combat_state_change

    if change and change.get("action") == "enter":
        rolls = change.get("initiative_rolls") or []
        sorted_rolls = sorted(
            rolls,
            key=lambda r: int(r.get("initiative_score", 0)),
            reverse=True,
        )
        campaign.combat_state = {
            "active": True,
            "round": 1,
            "initiative_order": [
                {
                    "name": r["name"],
                    "is_player": bool(r.get("is_player", False)),
                    "initiative_score": int(r["initiative_score"]),
                    "defeated": False,
                }
                for r in sorted_rolls
            ],
            "last_damage": "",
            "started_at_iso": datetime.now(timezone.utc).isoformat(),
        }
        return
```

(The progression and exit paths come in Tasks 4 and 5.)

- [ ] **Step 3: Run test**

```bash
pytest backend/tests/test_turn_engine.py::test_resolve_turn_enters_combat -v
```

Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add backend/app/services/turn_engine.py backend/tests/test_turn_engine.py
git commit -m "feat: turn engine handles combat entry"
```

---

## Task 4: Turn engine — round progression, damage, defeated (TDD)

**Files:**
- Modify: `backend/app/services/turn_engine.py`
- Modify: `backend/tests/test_turn_engine.py`

- [ ] **Step 1: Add failing tests**

Append to `backend/tests/test_turn_engine.py`:

```python
def test_resolve_turn_progresses_combat_round() -> None:
    session = _make_session()
    campaign = _make_campaign(session)
    campaign.combat_state = {
        "active": True,
        "round": 1,
        "initiative_order": [
            {"name": "Gray Sergeant", "is_player": False, "initiative_score": 8, "defeated": False},
            {"name": "Mara", "is_player": True, "initiative_score": 5, "defeated": False},
        ],
        "last_damage": "",
        "started_at_iso": "2026-05-12T00:00:00+00:00",
    }
    session.commit()

    from app.services.ai_provider import NarrationResponse
    from app.services.consequence_applier import Consequences
    from app.services.turn_engine import resolve_turn

    class _Stub:
        def narrate(self, request):
            return NarrationResponse(
                narrative="Mara dodges, Gray swings.",
                player_safe_summary="Trade blows.",
                consequences=Consequences(),
                scene_state={"tension_tier": 4, "key_holdings": "blade live", "last_concrete_change": "Mara hit"},
                damage_summary="Mara took 4 from the slingblade",
            )
        def clarify(self, request):
            return ""

    resolve_turn(session=session, campaign=campaign, player_input="dodge", narration_provider=_Stub())

    session.refresh(campaign)
    assert campaign.combat_state["round"] == 2
    assert campaign.combat_state["last_damage"] == "Mara took 4 from the slingblade"


def test_resolve_turn_marks_defeated_from_scene_participants() -> None:
    session = _make_session()
    campaign = _make_campaign(session)
    campaign.combat_state = {
        "active": True,
        "round": 2,
        "initiative_order": [
            {"name": "Gray Sergeant", "is_player": False, "initiative_score": 8, "defeated": False},
            {"name": "Mara", "is_player": True, "initiative_score": 5, "defeated": False},
            {"name": "Obsidian Guard", "is_player": False, "initiative_score": 3, "defeated": False},
        ],
        "last_damage": "",
        "started_at_iso": "2026-05-12T00:00:00+00:00",
    }
    session.commit()

    from app.services.ai_provider import NarrationResponse
    from app.services.consequence_applier import Consequences
    from app.services.turn_engine import resolve_turn

    class _Stub:
        def narrate(self, request):
            return NarrationResponse(
                narrative="Gray drops.",
                player_safe_summary="Gray defeated.",
                consequences=Consequences(),
                scene_state={"tension_tier": 3, "key_holdings": "Mara standing", "last_concrete_change": "Gray down"},
                scene_participants=[
                    {"name": "Gray Sergeant", "caste": "Gray", "role": "guard", "disposition": "hostile", "current_hp": 0, "max_hp": 12},
                    {"name": "Obsidian Guard", "caste": "Obsidian", "role": "muscle", "disposition": "hostile", "current_hp": 8, "max_hp": 14},
                ],
            )
        def clarify(self, request):
            return ""

    resolve_turn(session=session, campaign=campaign, player_input="attack", narration_provider=_Stub())

    session.refresh(campaign)
    order = {p["name"]: p for p in campaign.combat_state["initiative_order"]}
    assert order["Gray Sergeant"]["defeated"] is True
    assert order["Obsidian Guard"]["defeated"] is False
    assert order["Mara"]["defeated"] is False
```

Run:
```bash
pytest backend/tests/test_turn_engine.py::test_resolve_turn_progresses_combat_round backend/tests/test_turn_engine.py::test_resolve_turn_marks_defeated_from_scene_participants -v
```

Expected: FAIL — round stays at 1, defeated flag stays False.

- [ ] **Step 2: Extend the helper**

In `backend/app/services/turn_engine.py`, extend the `_apply_combat_state_change` helper. After the `if change and change.get("action") == "enter":` block, add:

```python
    if campaign.combat_state and campaign.combat_state.get("active"):
        # Round progression: each player input represents one full round.
        campaign.combat_state["round"] = int(campaign.combat_state.get("round", 1)) + 1

        if narration.damage_summary:
            campaign.combat_state["last_damage"] = narration.damage_summary

        # Mark defeated from scene_participants HP.
        defeated_names = {
            p["name"]
            for p in (narration.scene_participants or [])
            if isinstance(p, dict)
            and p.get("current_hp") is not None
            and int(p["current_hp"]) <= 0
        }
        if defeated_names:
            for entry in campaign.combat_state["initiative_order"]:
                if entry["name"] in defeated_names:
                    entry["defeated"] = True

        # SQLAlchemy JSON columns don't auto-detect in-place mutations.
        # Re-assign to trigger the change tracker.
        campaign.combat_state = dict(campaign.combat_state)
```

(The exit path comes in Task 5; this block currently runs even on enter turns, which is wrong — fix below.)

Wait: the entry path returns early, so this progression block only runs on turns that did NOT enter combat. That's correct. Keep the `return` in the entry branch.

But the entry turn itself should NOT also bump the round to 2. Confirm by re-reading: the entry branch sets `round=1` and returns. The progression branch only runs if entry didn't happen. Good.

- [ ] **Step 3: Run tests**

```bash
pytest backend/tests/test_turn_engine.py::test_resolve_turn_progresses_combat_round backend/tests/test_turn_engine.py::test_resolve_turn_marks_defeated_from_scene_participants backend/tests/test_turn_engine.py::test_resolve_turn_enters_combat -v
```

Expected: all PASS.

- [ ] **Step 4: Commit**

```bash
git add backend/app/services/turn_engine.py backend/tests/test_turn_engine.py
git commit -m "feat: progress combat round, persist damage, mark defeated"
```

---

## Task 5: Turn engine — exit combat (TDD)

**Files:**
- Modify: `backend/app/services/turn_engine.py`
- Modify: `backend/tests/test_turn_engine.py`

- [ ] **Step 1: Add failing test**

Append to `backend/tests/test_turn_engine.py`:

```python
def test_resolve_turn_exits_combat() -> None:
    session = _make_session()
    campaign = _make_campaign(session)
    campaign.combat_state = {
        "active": True,
        "round": 3,
        "initiative_order": [
            {"name": "Mara", "is_player": True, "initiative_score": 5, "defeated": False},
        ],
        "last_damage": "Final blow",
        "started_at_iso": "2026-05-12T00:00:00+00:00",
    }
    session.commit()

    from app.services.ai_provider import NarrationResponse
    from app.services.consequence_applier import Consequences
    from app.services.turn_engine import resolve_turn

    class _Stub:
        def narrate(self, request):
            return NarrationResponse(
                narrative="The Gray surrenders.",
                player_safe_summary="Combat over.",
                consequences=Consequences(),
                scene_state={"tension_tier": 1, "key_holdings": "", "last_concrete_change": "Gray surrendered"},
                combat_state_change={"action": "exit", "reason": "Gray surrendered"},
            )
        def clarify(self, request):
            return ""

    resolve_turn(session=session, campaign=campaign, player_input="hold blade to throat", narration_provider=_Stub())

    session.refresh(campaign)
    assert campaign.combat_state is None
```

Run:
```bash
pytest backend/tests/test_turn_engine.py::test_resolve_turn_exits_combat -v
```

Expected: FAIL — combat_state is not None.

- [ ] **Step 2: Add exit branch**

In `backend/app/services/turn_engine.py`, in `_apply_combat_state_change`, AFTER the progression block (and BEFORE the function's implicit end), add:

```python
    if change and change.get("action") == "exit":
        campaign.combat_state = None
```

Order matters: exit runs after progression so the final damage and defeated-marking from the exit turn are processed (visible in logs / scene_state) before clearing.

- [ ] **Step 3: Run test**

```bash
pytest backend/tests/test_turn_engine.py::test_resolve_turn_exits_combat -v
```

Expected: PASS.

- [ ] **Step 4: Run full turn engine test suite to confirm no regressions**

```bash
pytest backend/tests/test_turn_engine.py -v
```

Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/turn_engine.py backend/tests/test_turn_engine.py
git commit -m "feat: exit combat clears campaign state"
```

---

## Task 6: Context builder — inject Combat state (live) block (TDD)

**Files:**
- Modify: `backend/app/services/context_builder.py`
- Modify: `backend/tests/test_context_builder.py`

- [ ] **Step 1: Add failing tests**

Append to `backend/tests/test_context_builder.py`:

```python
def test_hidden_brief_includes_combat_state_when_active() -> None:
    session = _make_session()
    from app.models.campaign import Campaign

    campaign = Campaign(
        name="Test",
        current_date_pce=728,
        combat_state={
            "active": True,
            "round": 2,
            "initiative_order": [
                {"name": "Gray Sergeant", "is_player": False, "initiative_score": 8, "defeated": False},
                {"name": "Mara", "is_player": True, "initiative_score": 5, "defeated": False},
                {"name": "Obsidian", "is_player": False, "initiative_score": 3, "defeated": True},
            ],
            "last_damage": "Mara took 6 from the slingblade",
            "started_at_iso": "2026-05-12T00:00:00+00:00",
        },
    )
    session.add(campaign)
    session.commit()

    ctx = build_turn_context(session, campaign, "next action")

    assert "Combat state (live)" in ctx.hidden_gm_brief
    assert "Round: 2" in ctx.hidden_gm_brief
    assert "Gray Sergeant" in ctx.hidden_gm_brief
    assert "init 8" in ctx.hidden_gm_brief
    assert "[PLAYER]" in ctx.hidden_gm_brief
    assert "defeated" in ctx.hidden_gm_brief.lower()  # marker for Obsidian
    assert "Mara took 6 from the slingblade" in ctx.hidden_gm_brief
    assert "Combat state (live)" not in ctx.player_safe_brief


def test_hidden_brief_omits_combat_state_when_inactive() -> None:
    session = _make_session()
    from app.models.campaign import Campaign

    campaign = Campaign(name="Test", current_date_pce=728)
    session.add(campaign)
    session.commit()

    ctx = build_turn_context(session, campaign, "first turn")
    assert "Combat state (live)" not in ctx.hidden_gm_brief
```

Run:
```bash
pytest backend/tests/test_context_builder.py::test_hidden_brief_includes_combat_state_when_active backend/tests/test_context_builder.py::test_hidden_brief_omits_combat_state_when_inactive -v
```

Expected: FAIL — "Combat state (live)" not present.

- [ ] **Step 2: Pass combat_state through to renderer**

In `backend/app/services/context_builder.py`, inside `build_turn_context`, in the `_render_hidden_gm_brief(...)` keyword arguments, add:

```python
            combat_state=campaign.combat_state,
```

Then update the signature of `_render_hidden_gm_brief` to accept the new param (append after existing kwargs):

```python
    combat_state: dict | None = None,
```

- [ ] **Step 3: Render the block**

In `_render_hidden_gm_brief`, IMMEDIATELY AFTER the existing scene-state block (the `if last_scene_state:` block added in chat-quality), add:

```python
    if combat_state and combat_state.get("active"):
        lines.append("Combat state (live):")
        lines.append(f"  Round: {combat_state.get('round', 1)}")
        lines.append("  Initiative order:")
        for entry in combat_state.get("initiative_order", []):
            marker = " [PLAYER]" if entry.get("is_player") else ""
            defeated = " [defeated]" if entry.get("defeated") else ""
            lines.append(
                f"    - {entry['name']} (init {entry['initiative_score']}){marker}{defeated}"
            )
        last_damage = combat_state.get("last_damage")
        if last_damage:
            lines.append(f"  Last damage: {last_damage}")
        lines.append(
            "  Rules: narrate this round in initiative order; pause before the player's next turn; "
            "emit damage_summary if a hit lands; emit combat_state_change.action='exit' when the fight resolves."
        )
```

- [ ] **Step 4: Run tests**

```bash
pytest backend/tests/test_context_builder.py -v
```

Expected: all pass (existing + 2 new).

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/context_builder.py backend/tests/test_context_builder.py
git commit -m "feat: inject live combat state into hidden GM brief"
```

---

## Task 7: System prompt — Combat mode section

**Files:**
- Modify: `backend/app/services/anthropic_provider.py`

- [ ] **Step 1: Insert section**

In `backend/app/services/anthropic_provider.py`, locate `_SYSTEM_PROMPT`. Find the existing `Scene change discipline:` section. Immediately AFTER that section's last paragraph (the one referencing the `scene_state` tool block) and BEFORE the line `Stock phrase banlist (do not use these unmodified — they are dead from overuse):`, insert:

```
Combat mode:
- Enter combat (emit combat_state_change.action='enter' with initiative_rolls) when narrative tension crosses into open violence: a drawn weapon connects, an ambush triggers, a formal duel begins, an attack of opportunity lands. Initiative is d6 + Cunning modifier per combatant. Include the player and every named NPC who is fighting.
- While combat is active, every response narrates ONE COMPLETE ROUND in initiative order, pausing at the moment immediately before the player would act again. If NPCs have higher initiative than the player, narrate their next-round actions in the same response.
- The hidden brief contains a "Combat state (live)" block with the live initiative order, round, and last damage line. Narrate participants in that exact order. Do not skip turns. Do not reorder.
- When a hit lands, emit damage_summary as a single short line ("Mara took 8 from the slingblade"). Update scene_participants.current_hp on the affected participant to reflect the new HP. Apply mechanical conditions (bleeding, wounded, prone, etc.) via condition_updates as appropriate.
- Exit combat (emit combat_state_change.action='exit' with a one-line reason) when one side is defeated, retreats, surrenders, or a third party stops the fight. The player reaching 0 HP also exits combat — narrate the result (KO, capture, death) according to the fiction, but always exit the combat state.
- The "first sentence names what changed" rule applies doubly in combat: lead with the most consequential beat of the round (a hit, a fall, a turn of momentum), not the initiative ordering or a recap.
- Combat narration is not exempt from the stock-phrase banlist. Find fresh language for hits, misses, and physical positioning.
```

Match the indentation/blank-line style of the surrounding sections.

- [ ] **Step 2: Verify prompt builds**

```bash
cd /home/lans/ares/backend && source .venv/bin/activate
python -c "from app.services.anthropic_provider import build_system_prompt; p = build_system_prompt(); assert 'Combat mode:' in p; assert 'combat_state_change.action=' in p; assert 'damage_summary' in p; print('prompt OK, len=', len(p))"
```

Expected: prints `prompt OK, len=<integer>`.

- [ ] **Step 3: Run full backend test suite**

```bash
pytest -q
```

Expected: all pass.

- [ ] **Step 4: Commit**

```bash
git add backend/app/services/anthropic_provider.py
git commit -m "feat: add Combat mode section to GM system prompt"
```

---

## Task 8: Expose `combat_state` on the campaign API response

**Files:**
- Modify: `backend/app/schemas/campaign.py`
- Modify: `backend/app/api/routes/campaigns.py`
- Modify: a campaigns API test file (find or create per Step 1)

- [ ] **Step 1: Locate or create campaigns API test file**

```bash
ls backend/tests/ | grep -i campaign
```

If `test_campaigns_api.py` (or similar) exists, append to it. If not, create `backend/tests/test_campaigns_api.py` with a minimal FastAPI TestClient setup mirroring `tests/test_turn_api_contract.py` (existing in this repo).

- [ ] **Step 2: Add failing test**

Append (or write to the new file):

```python
def test_get_campaign_state_includes_combat_state(client, session_factory):
    # Adapt the fixture pattern from test_turn_api_contract.py — that file
    # already wires up a FastAPI TestClient against the SQLAlchemy session.
    from app.models.campaign import Campaign

    with session_factory() as session:
        campaign = Campaign(
            name="Combat Test",
            current_date_pce=728,
            combat_state={
                "active": True,
                "round": 1,
                "initiative_order": [
                    {"name": "Mara", "is_player": True, "initiative_score": 7, "defeated": False},
                ],
                "last_damage": "",
                "started_at_iso": "2026-05-12T00:00:00+00:00",
            },
        )
        session.add(campaign)
        session.commit()
        campaign_id = campaign.id

    response = client.get(f"/api/v1/campaigns/{campaign_id}/state")
    assert response.status_code == 200
    body = response.json()
    assert body["combat_state"] is not None
    assert body["combat_state"]["active"] is True
    assert body["combat_state"]["round"] == 1
```

If the existing test file uses a different fixture name or structure, adapt to match.

Run the test. Expected: FAIL — `combat_state` not in the response body.

- [ ] **Step 3: Add field to schema**

In `backend/app/schemas/campaign.py`, extend `CampaignState`:

```python
class CampaignState(BaseModel):
    campaign: CampaignRead
    current_location: str | None
    active_objective: str | None
    recent_turns: list[str]
    player_character: CharacterRead | None
    scene_art: SceneArtRead | None = None
    hidden_state_summary: str
    combat_state: dict | None = None
```

- [ ] **Step 4: Populate field in route**

In `backend/app/api/routes/campaigns.py`, in `get_campaign_state`, modify the return to include `combat_state=campaign.combat_state`:

```python
    return CampaignState(
        campaign=campaign,
        current_location=campaign.current_location_label,
        active_objective=active_objective,
        recent_turns=recent_turns,
        player_character=_player_facing_character(latest_character),
        scene_art=scene_art,
        hidden_state_summary="Hidden state remains server-only.",
        combat_state=campaign.combat_state,
    )
```

- [ ] **Step 5: Run test**

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/app/schemas/campaign.py backend/app/api/routes/campaigns.py backend/tests/
git commit -m "feat: expose combat_state on campaign state API"
```

---

## Task 9: Frontend — CombatPanel component

**Files:**
- Create: `frontend/src/components/CombatPanel.jsx`

- [ ] **Step 1: Write the component**

```jsx
import React from "react";

/**
 * Renders the live combat panel when campaign.combat_state.active is true.
 * Shows round counter, initiative order with HP bars (from scene_participants),
 * defeated state, and the most recent damage line.
 */
export function CombatPanel({ combatState, participants = [] }) {
  if (!combatState || !combatState.active) {
    return null;
  }

  const participantByName = new Map(participants.map((p) => [p.name, p]));

  return (
    <section className="combat-panel" aria-label="Combat panel">
      <header className="combat-panel-header">
        <span className="combat-panel-badge">⚔ COMBAT</span>
        <span className="combat-panel-round">Round {combatState.round ?? 1}</span>
      </header>

      <ol className="combat-initiative">
        {(combatState.initiative_order ?? []).map((entry) => {
          const live = participantByName.get(entry.name);
          const hp = live?.current_hp;
          const maxHp = live?.max_hp;
          const hpPct = hp != null && maxHp ? Math.max(0, Math.min(100, (hp / maxHp) * 100)) : null;
          return (
            <li
              key={entry.name}
              className={[
                "combat-initiative-row",
                entry.is_player ? "is-player" : "",
                entry.defeated ? "is-defeated" : "",
              ].filter(Boolean).join(" ")}
            >
              <span className="combat-initiative-name">{entry.name}</span>
              <span className="combat-initiative-score">init {entry.initiative_score}</span>
              {hpPct != null ? (
                <span className="combat-initiative-hp" aria-label={`HP ${hp} of ${maxHp}`}>
                  <span
                    className="combat-initiative-hp-fill"
                    style={{ width: `${hpPct}%` }}
                  />
                </span>
              ) : null}
              {entry.defeated ? <span className="combat-initiative-defeated">DOWN</span> : null}
            </li>
          );
        })}
      </ol>

      {combatState.last_damage ? (
        <p className="combat-last-damage">{combatState.last_damage}</p>
      ) : null}
    </section>
  );
}
```

- [ ] **Step 2: Add minimal CSS**

In `frontend/src/styles.css`, append:

```css
.combat-panel {
  border: 1px solid #5a2424;
  background: rgba(28, 8, 8, 0.85);
  padding: 0.75rem 1rem;
  margin: 0.5rem 0;
  font-family: "VT323", monospace;
  color: #f3e6d6;
}
.combat-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}
.combat-panel-badge {
  color: #ff6b4a;
  font-weight: bold;
  letter-spacing: 0.1em;
}
.combat-panel-round {
  font-size: 1.1rem;
}
.combat-initiative {
  list-style: none;
  padding: 0;
  margin: 0;
}
.combat-initiative-row {
  display: grid;
  grid-template-columns: 1fr auto 80px auto;
  gap: 0.5rem;
  align-items: center;
  padding: 0.2rem 0;
  border-bottom: 1px dashed rgba(243, 230, 214, 0.15);
}
.combat-initiative-row.is-player {
  background: rgba(255, 200, 80, 0.08);
  border-left: 3px solid #ffc850;
  padding-left: 0.4rem;
}
.combat-initiative-row.is-defeated {
  opacity: 0.4;
  text-decoration: line-through;
}
.combat-initiative-score {
  color: #b89876;
  font-size: 0.9rem;
}
.combat-initiative-hp {
  display: block;
  width: 80px;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}
.combat-initiative-hp-fill {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, #ff5252, #ff8a4a);
  transition: width 0.4s ease;
}
.combat-initiative-defeated {
  color: #ff6b4a;
  font-weight: bold;
  font-size: 0.8rem;
}
.combat-last-damage {
  margin: 0.5rem 0 0;
  font-style: italic;
  color: #ffb380;
}
.topbar-combat-badge {
  background: rgba(255, 80, 50, 0.2);
  color: #ff8a4a;
  padding: 0.15rem 0.5rem;
  border: 1px solid #5a2424;
  border-radius: 3px;
  font-family: "VT323", monospace;
  font-weight: bold;
  letter-spacing: 0.05em;
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/CombatPanel.jsx frontend/src/styles.css
git commit -m "feat: add CombatPanel component and combat CSS"
```

---

## Task 10: Frontend — integrate CombatPanel + header badge into App.jsx

**Files:**
- Modify: `frontend/src/App.jsx`

- [ ] **Step 1: Import CombatPanel**

Near the top of `frontend/src/App.jsx`, with the other component imports:

```jsx
import { CombatPanel } from "./components/CombatPanel";
```

- [ ] **Step 2: Render the panel**

In the JSX, locate the existing `<StatusPanel ... />` block inside `main-grid`. Immediately AFTER the closing `/>` of StatusPanel, add:

```jsx
          <CombatPanel
            combatState={campaignState?.combat_state}
            participants={participants}
          />
```

This places the combat panel in the same column area as StatusPanel, conditionally rendered.

- [ ] **Step 3: Add header badge**

In the JSX `<div className="topbar-stats">` block, immediately AFTER the existing `topbar-stat` divs (Time / Signal / Runtime), but BEFORE the Tone / clarify / asset buttons, add:

```jsx
          {campaignState?.combat_state?.active ? (
            <span className="topbar-combat-badge" title="Combat in progress">
              ⚔ COMBAT — R{campaignState.combat_state.round}
            </span>
          ) : null}
```

- [ ] **Step 4: Manual visual sanity check**

```bash
cd /home/lans/ares
docker compose up --build --no-deps -d frontend backend 2>&1 | tail -5
```

Open `http://localhost:5180/` in a browser. Confirm:
- App loads without errors.
- No combat panel visible by default (no active combat).
- Console shows no React errors.

Don't attempt to trigger combat here — that requires a live narrative session. Visual rendering will be validated in the playtest task.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/App.jsx
git commit -m "feat: wire CombatPanel and combat badge into App shell"
```

---

## Task 11: Full backend suite + push branch

**Files:** None (validation)

- [ ] **Step 1: Run full test suite**

```bash
cd /home/lans/ares/backend && source .venv/bin/activate && pytest -q
```

Expected: all pass. The slice should add roughly 10 new tests on top of the existing 237.

- [ ] **Step 2: Push branch**

```bash
cd /home/lans/ares
git push -u origin feat/a4-turn-based-combat
```

- [ ] **Step 3: Open draft PR**

```bash
gh pr create --base main --head feat/a4-turn-based-combat --draft \
  --title "feat: A4 turn-based combat mode" \
  --body "$(cat <<'EOF'
## Summary
Adds hybrid turn-based combat layered on the existing narrative GM flow:
- GM-decided combat entry/exit via new \`combat_state_change\` tool field.
- Roll-based initiative (d6 + Cunning modifier), persisted on Campaign as JSON.
- One player input = one full round of narration in initiative order.
- New \`CombatPanel.jsx\` shown in the right column when combat is active, plus a header badge.
- \`damage_summary\` hit-log line per turn during combat.

Spec: \`docs/superpowers/specs/2026-05-12-A4-turn-based-combat-design.md\`
Plan: \`docs/superpowers/plans/2026-05-12-A4-turn-based-combat.md\`

## Test plan
- [ ] Unit suite green (~247 tests).
- [ ] Playtest: trigger a hostile encounter, run several combat rounds, exit cleanly. Repetition + Flow stay ≥ 4.0 across combat turns.
- [ ] Manual UI check: combat panel renders, HP bars track scene_participants, badge appears in header.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Note the PR URL.

---

## Task 12: Playtest validation

**Files:** None (validation)

- [ ] **Step 1: Rebuild backend container with new code**

```bash
cd /home/lans/ares
docker compose up --build --no-deps -d backend 2>&1 | tail -3
```

Wait for `/api/v1/health` to return `{"status":"ok"}`.

- [ ] **Step 2: Run a combat-seeking playtest**

The seeded campaign opens at Surface Relay Tower 19 — a covert sabotage scene, NOT a combat scenario. The Mara of Cimmeria premise emphasizes stealth and tradecraft. To validate combat we either need to (a) wait for natural escalation, or (b) seed a hostile encounter prompt.

For this validation, run a 30-turn playtester session with both player + evaluator on Anthropic Haiku (more reliable than gpt-5.5 mid-session — see `tools/playtester/llm.py` retry logic from prior slice). Combat should trigger naturally if the player is aggressive, and the prompt change tells the GM to escalate into combat when violence becomes appropriate.

```bash
cd /home/lans/ares/tools/playtester
source .venv/bin/activate
ARES_PLAYTESTER_TURNS=30 \
  ARES_PLAYTESTER_PLAYER_PROVIDER=anthropic ARES_PLAYTESTER_PLAYER_MODEL=claude-haiku-4-5 \
  ARES_PLAYTESTER_EVALUATOR_PROVIDER=anthropic ARES_PLAYTESTER_EVALUATOR_MODEL=claude-haiku-4-5 \
  python run.py
```

- [ ] **Step 3: Inspect the resulting report**

Look in `tools/playtester/reports/` for the latest dated file. Search for:
- `combat_state_change` events in the per-turn logs (Implementation note: the playtester does not currently log the GM's tool-side fields, only narrative text. So check the database instead.)

```bash
sqlite3 /home/lans/ares/backend/ares.db "SELECT id, name, combat_state FROM campaigns WHERE combat_state IS NOT NULL;"
```

Confirm at least one campaign has a populated `combat_state` (or had one — if combat resolved cleanly the column may be back to NULL with logs in turns).

- [ ] **Step 4: If combat never triggered, dispatch a targeted retry**

If the 30-turn run never entered combat (the GM stayed in stealth/social mode throughout), repeat the playtester run but with a pre-seeded aggressive player intent. Edit the player agent's opening prompt in `tools/playtester/player.py` to bias toward confrontation, OR manually POST a turn that explicitly attacks an NPC and verify combat enters via the campaign state endpoint.

```bash
# Manual attack injection (replace <campaign_id>):
curl -s http://localhost:8000/api/v1/campaigns/<campaign_id>/turns \
  -H 'Content-Type: application/json' \
  -d '{"player_input": "I draw the slingblade hidden in my toolkit and lunge at the nearest Gray supervisor, striking for the throat."}' \
  | python -m json.tool

# Inspect campaign state:
curl -s http://localhost:8000/api/v1/campaigns/<campaign_id>/state | python -m json.tool | grep -A 10 combat_state
```

Confirm `combat_state.active=true`, `round>=1`, `initiative_order` populated with the player + at least one NPC.

- [ ] **Step 5: Confirm exit path**

Submit additional turns until combat resolves. Confirm `combat_state` returns to `null` once the GM emits an exit event.

- [ ] **Step 6: If anything is broken, iterate**

If a turn fails (e.g., GM emits a malformed `combat_state_change`, the schema rejects it, the panel doesn't render correctly), capture the failure, write a regression test, and fix forward in additional commits on the same branch.

- [ ] **Step 7: Mark PR ready**

```bash
gh pr ready <PR_NUMBER>
```

Comment the validation evidence on the PR (combat entry events, round progression, exit, any iteration commits).

---

## Self-Review

**1. Spec coverage check:**
- New Campaign.combat_state column → Task 1 ✅
- combat_state_change tool field → Task 2 ✅
- damage_summary tool field → Task 2 ✅
- Turn engine: enter combat (sort initiative, persist) → Task 3 ✅
- Turn engine: round increment + damage + defeated → Task 4 ✅
- Turn engine: exit combat → Task 5 ✅
- Context builder: live combat block in hidden brief → Task 6 ✅
- System prompt: Combat mode section → Task 7 ✅
- Campaign API exposes combat_state → Task 8 ✅
- CombatPanel.jsx component → Task 9 ✅
- App.jsx integration + header badge → Task 10 ✅
- Backend test suite green → Task 11 ✅
- Playtest validation → Task 12 ✅

**2. Placeholder scan:** No "TBD", "TODO", or hand-wave instructions. All code blocks contain the full code. All commands have expected outputs. Task 8 says "find or create" the campaigns API test file — that's pragmatic, not a placeholder, since the test layout is best discovered by the implementer.

**3. Type consistency:**
- `combat_state` is `dict | None` everywhere (model, schema, response, render param).
- `combat_state_change` is `dict | None` in NarrationResponse.
- `damage_summary` is `str | None` in NarrationResponse.
- `initiative_order` entry shape: `{name: str, is_player: bool, initiative_score: int, defeated: bool}` — consistent across enter (Task 3), progression (Task 4), exit (Task 5), context builder (Task 6), and component (Task 9).
- `last_damage` stored as `str`, displayed as `str`.

**4. Ambiguity check:** Initiative ties are resolved by emission order (the GM-supplied order before sort — Python's `sorted` is stable). The progression branch ignores the entry turn correctly because of the `return` in the entry block. Exit branch runs after progression so the exit turn's damage line is captured before clearing.
