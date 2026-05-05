# A1 — Dice + Skill Check Primitive Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Red Rising-flavored skill-check primitive so the GM can call for and resolve attribute checks (Strength, Cunning, Will, Charm, Tech) and the player sees the dice in the turn feed.

**Architecture:** The LLM emits a full structured roll (attribute, target, dice_total, outcome, narration) on each turn that calls for one, alongside its existing tool-call output. We add `rolls` as a new top-level field on `NarrationResponse` (parallel to `scene_participants` and `suggested_actions`) — **not** inside `Consequences`, because rolls describe events rather than mutate persisted state. The new field flows through `TurnEngineResult` → `TurnResolution` → frontend `buildConsequenceEvents`, surfacing as `system-roll` events in the turn feed.

The whole feature is gated behind a new `ARES_ENABLE_DICE` setting. With the flag off (default), nothing changes: the tool schema does not include `rolls`, the system prompt does not mention dice, and the frontend never receives roll events. With the flag on, the GM is taught to call for checks and the UI renders them.

Server-authoritative dice rolling (where the backend rolls and the LLM reads the result) is **deferred to A4 (combat mode)**. Slice A1 is the surface contract: rolls are visible, structured, and persisted in the turn payload. Per parent plan `~/.claude/plans/a-i-happy-matsumoto.md`.

**Tech Stack:** Python 3 (FastAPI, SQLAlchemy, Pydantic, pydantic-settings), pytest, React (Vite), CSS modules.

---

## File Structure

| File | Responsibility | Status |
|---|---|---|
| `backend/app/core/config.py` | Add `enable_dice` setting | Modify |
| `backend/app/services/ai_provider.py` | Define `Roll` dataclass + add `rolls` field on `NarrationResponse` | Modify |
| `backend/app/services/anthropic_provider.py` | Conditionally extend `_TOOL_SCHEMA` and `_SYSTEM_PROMPT`; translate `tool_input["rolls"]` in `_build_response` | Modify |
| `backend/app/services/turn_engine.py` | Pass `rolls` through `TurnEngineResult` | Modify |
| `backend/app/api/routes/turns.py` | Forward `rolls` in `TurnResolution` response | Modify |
| `backend/app/schemas/turn.py` | Add `rolls: list[dict]` to `TurnResolution` | Modify |
| `backend/tests/test_a1_dice.py` | New focused test module for slice A1 | Create |
| `frontend/src/App.jsx` | Extend `buildConsequenceEvents` to emit `system-roll` events | Modify |
| `frontend/src/components/TurnFeed.jsx` | Handle `system-roll` speaker in `getTurnAvatar` | Modify |
| `frontend/src/styles.css` | Add `.turn-system-roll` styling | Modify |
| `docs/development/workstreams/A1-dice-skill-checks.md` | Update slice doc with status / next-step / agent log | Modify |

---

## Roll Data Contract

A `Roll` is one structured record. Frozen for slice A1:

```python
@dataclass
class Roll:
    attribute: str        # "strength" | "cunning" | "will" | "charm" | "tech"
    target: int           # difficulty class, typically 8–18
    dice_total: int       # final number after modifier (LLM-authored for slice A1)
    outcome: str          # "critical_success" | "success" | "failure" | "critical_failure"
    narration: str        # one short sentence the GM authored to flavor the roll
```

The frontend renders this as a system-roll event with the form:
`{attribute}  {dice_total} vs {target}  →  {outcome}` followed by `{narration}` on a second line.

---

## Task 1: Add `enable_dice` setting

**Files:**
- Modify: `backend/app/core/config.py`
- Test: `backend/tests/test_a1_dice.py` (create)

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_a1_dice.py` with:

```python
"""Tests for slice A1 — dice + skill check primitive."""
from __future__ import annotations

import os
from unittest.mock import patch

from app.core.config import Settings


def test_enable_dice_defaults_off() -> None:
    settings = Settings(_env_file=None)
    assert settings.enable_dice is False


def test_enable_dice_reads_env() -> None:
    with patch.dict(os.environ, {"ARES_ENABLE_DICE": "true"}, clear=False):
        settings = Settings(_env_file=None)
        assert settings.enable_dice is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .venv/bin/pytest tests/test_a1_dice.py -v`
Expected: FAIL with `AttributeError: 'Settings' object has no attribute 'enable_dice'`

- [ ] **Step 3: Add the setting**

In `backend/app/core/config.py`, add inside the `Settings` class (after `world_bible_path_raw`):

```python
    enable_dice: bool = Field(default=False, alias="ARES_ENABLE_DICE")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && .venv/bin/pytest tests/test_a1_dice.py -v`
Expected: both tests PASS.

- [ ] **Step 5: Commit**

```bash
cd /home/lans/ares-track-a/A1
git add backend/app/core/config.py backend/tests/test_a1_dice.py
git commit -m "feat(A1): add ARES_ENABLE_DICE setting (default off)

Slice A1 step 1 — feature flag for the dice/skill-check primitive.
Default off so main stays unaffected until the slice is complete."
```

---

## Task 2: Add `Roll` dataclass + `rolls` field on `NarrationResponse`

**Files:**
- Modify: `backend/app/services/ai_provider.py`
- Test: `backend/tests/test_a1_dice.py`

- [ ] **Step 1: Append failing test**

Append to `backend/tests/test_a1_dice.py`:

```python
from app.services.ai_provider import NarrationResponse, Roll


def test_roll_dataclass_instantiates() -> None:
    roll = Roll(
        attribute="cunning",
        target=14,
        dice_total=17,
        outcome="success",
        narration="Davan reads the Copper's tell before the question lands.",
    )
    assert roll.attribute == "cunning"
    assert roll.target == 14
    assert roll.dice_total == 17
    assert roll.outcome == "success"


def test_narration_response_has_empty_rolls_by_default() -> None:
    resp = NarrationResponse(narrative="x", player_safe_summary="x")
    assert resp.rolls == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .venv/bin/pytest tests/test_a1_dice.py -v`
Expected: FAIL with `ImportError: cannot import name 'Roll'`.

- [ ] **Step 3: Add `Roll` dataclass and field**

In `backend/app/services/ai_provider.py`, add `Roll` after `NarrationRequest` and a `rolls` field on `NarrationResponse`:

```python
@dataclass
class Roll:
    attribute: str
    target: int
    dice_total: int
    outcome: str
    narration: str


@dataclass
class NarrationResponse:
    narrative: str
    player_safe_summary: str
    consequences: Consequences = field(default_factory=Consequences)
    suggested_actions: list[dict] = field(default_factory=list)
    scene_participants: list[dict] = field(default_factory=list)
    rolls: list[Roll] = field(default_factory=list)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && .venv/bin/pytest tests/test_a1_dice.py -v`
Expected: all four tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/ai_provider.py backend/tests/test_a1_dice.py
git commit -m "feat(A1): Roll dataclass + rolls field on NarrationResponse

Adds the structured roll record used by the GM tool call. Lives on
NarrationResponse alongside suggested_actions/scene_participants
because rolls describe events rather than mutate persisted state."
```

---

## Task 3: Conditionally extend the tool schema with `rolls`

**Files:**
- Modify: `backend/app/services/anthropic_provider.py`
- Test: `backend/tests/test_a1_dice.py`

- [ ] **Step 1: Append failing test**

Append to `backend/tests/test_a1_dice.py`:

```python
from app.services.anthropic_provider import build_tool_schema


def test_tool_schema_omits_rolls_when_disabled() -> None:
    schema = build_tool_schema(enable_dice=False)
    properties = schema["input_schema"]["properties"]
    assert "rolls" not in properties


def test_tool_schema_includes_rolls_when_enabled() -> None:
    schema = build_tool_schema(enable_dice=True)
    properties = schema["input_schema"]["properties"]
    assert "rolls" in properties
    rolls_schema = properties["rolls"]
    assert rolls_schema["type"] == "array"
    item_props = rolls_schema["items"]["properties"]
    assert set(item_props.keys()) == {"attribute", "target", "dice_total", "outcome", "narration"}
    assert item_props["attribute"]["enum"] == ["strength", "cunning", "will", "charm", "tech"]
    assert item_props["outcome"]["enum"] == [
        "critical_success",
        "success",
        "failure",
        "critical_failure",
    ]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .venv/bin/pytest tests/test_a1_dice.py -v`
Expected: FAIL with `ImportError: cannot import name 'build_tool_schema'`.

- [ ] **Step 3: Refactor `_TOOL_SCHEMA` into a builder function**

In `backend/app/services/anthropic_provider.py`, replace the module-level `_TOOL_SCHEMA = { ... }` dict with a `build_tool_schema(*, enable_dice: bool = False)` function that returns the same structure, then conditionally adds `rolls`. Apply this sequence inside the file:

1. Wrap the existing schema dict in a function:

```python
def build_tool_schema(*, enable_dice: bool = False) -> dict:
    schema = {
        "name": _TOOL_NAME,
        "description": "Record the GM's narrative response and any structured consequences for this turn.",
        "input_schema": {
            "type": "object",
            "properties": {
                # ... all existing properties unchanged ...
            },
            "required": ["narrative", "player_safe_summary", "consequences", "suggested_actions", "scene_participants"],
        },
    }
    if enable_dice:
        schema["input_schema"]["properties"]["rolls"] = {
            "type": "array",
            "description": (
                "Skill checks the GM called for this turn. Emit only when the player's "
                "action genuinely warrants a check (uncertainty, pressure, opposed will). "
                "Routine narration does not need a roll."
            ),
            "items": {
                "type": "object",
                "properties": {
                    "attribute": {
                        "type": "string",
                        "enum": ["strength", "cunning", "will", "charm", "tech"],
                        "description": "Red Rising attribute being tested.",
                    },
                    "target": {
                        "type": "integer",
                        "minimum": 5,
                        "maximum": 25,
                        "description": "Difficulty class. 8 trivial, 12 average, 15 hard, 18+ heroic.",
                    },
                    "dice_total": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 30,
                        "description": "Final roll total after modifier.",
                    },
                    "outcome": {
                        "type": "string",
                        "enum": ["critical_success", "success", "failure", "critical_failure"],
                    },
                    "narration": {
                        "type": "string",
                        "description": "One short sentence flavoring the roll. No more than ~20 words.",
                    },
                },
                "required": ["attribute", "target", "dice_total", "outcome", "narration"],
            },
            "maxItems": 3,
        }
    return schema
```

2. Keep `_TOOL_SCHEMA` as a default for backward compat — replace it with `_TOOL_SCHEMA = build_tool_schema(enable_dice=False)` so existing tests that import it keep working.

3. In `narrate()`, replace the literal `tools=[_TOOL_SCHEMA]` with `tools=[build_tool_schema(enable_dice=self._enable_dice)]` (we'll add `self._enable_dice` in Task 5).

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && .venv/bin/pytest tests/test_a1_dice.py -v`
Expected: all six tests PASS. Existing `backend/tests/test_turn_engine.py` and the rest of the suite must still pass — run `make backend-test` from repo root and confirm 70+ green.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/anthropic_provider.py backend/tests/test_a1_dice.py
git commit -m "feat(A1): tool schema gains conditional rolls property

build_tool_schema(enable_dice=...) adds an additive rolls array when
the flag is on. Default off keeps existing behaviour and tests."
```

---

## Task 4: Translate `tool_input["rolls"]` in `_build_response`

**Files:**
- Modify: `backend/app/services/anthropic_provider.py`
- Test: `backend/tests/test_a1_dice.py`

- [ ] **Step 1: Append failing test**

Append to `backend/tests/test_a1_dice.py`:

```python
from app.services.anthropic_provider import _build_response


def test_build_response_extracts_rolls() -> None:
    tool_input = {
        "narrative": "n",
        "player_safe_summary": "s",
        "consequences": {},
        "suggested_actions": [
            {"label": "A", "prompt": "do A"},
            {"label": "B", "prompt": "do B"},
            {"label": "C", "prompt": "do C"},
        ],
        "scene_participants": [],
        "rolls": [
            {
                "attribute": "cunning",
                "target": 14,
                "dice_total": 17,
                "outcome": "success",
                "narration": "Davan reads the tell before it lands.",
            }
        ],
    }
    response = _build_response(tool_input)
    assert len(response.rolls) == 1
    roll = response.rolls[0]
    assert roll.attribute == "cunning"
    assert roll.target == 14
    assert roll.outcome == "success"


def test_build_response_handles_missing_rolls() -> None:
    tool_input = {
        "narrative": "n",
        "player_safe_summary": "s",
        "consequences": {},
        "suggested_actions": [
            {"label": "A", "prompt": "do A"},
            {"label": "B", "prompt": "do B"},
            {"label": "C", "prompt": "do C"},
        ],
        "scene_participants": [],
    }
    response = _build_response(tool_input)
    assert response.rolls == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .venv/bin/pytest tests/test_a1_dice.py::test_build_response_extracts_rolls -v`
Expected: FAIL — rolls field on response is empty.

- [ ] **Step 3: Translate rolls in `_build_response`**

Add `Roll` to the import block at the top of `anthropic_provider.py`:

```python
from app.services.ai_provider import NarrationProvider, NarrationRequest, NarrationResponse, Roll
```

In `_build_response()` (just before the final `return NarrationResponse(...)`), parse rolls:

```python
    raw_rolls = tool_input.get("rolls") or []
    rolls = []
    for item in raw_rolls:
        if not isinstance(item, dict):
            continue
        try:
            rolls.append(
                Roll(
                    attribute=item["attribute"],
                    target=int(item["target"]),
                    dice_total=int(item["dice_total"]),
                    outcome=item["outcome"],
                    narration=item["narration"],
                )
            )
        except (KeyError, TypeError, ValueError):
            continue
```

Then add `rolls=rolls` to the `NarrationResponse(...)` constructor call.

- [ ] **Step 4: Run tests to verify**

Run: `cd backend && .venv/bin/pytest tests/test_a1_dice.py -v && .venv/bin/pytest tests/ -q`
Expected: full backend suite green.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/anthropic_provider.py backend/tests/test_a1_dice.py
git commit -m "feat(A1): _build_response translates tool_input rolls -> Roll

Parses the rolls array out of the LLM tool call into typed Roll
dataclass instances. Malformed entries are skipped; missing list
yields an empty rolls list (existing behaviour preserved)."
```

---

## Task 5: Wire `enable_dice` into `AnthropicNarrationProvider` and `narrate()`

**Files:**
- Modify: `backend/app/services/anthropic_provider.py`
- Modify: `backend/app/services/provider_registry.py` (read first to confirm signature)
- Test: `backend/tests/test_a1_dice.py`

- [ ] **Step 1: Read provider_registry**

Read `backend/app/services/provider_registry.py` to confirm how `AnthropicNarrationProvider` is constructed. Note the call site for the flag wiring.

- [ ] **Step 2: Append failing test**

Append to `backend/tests/test_a1_dice.py`:

```python
from app.services.anthropic_provider import AnthropicNarrationProvider


def test_provider_passes_enable_dice_to_schema() -> None:
    captured = {}

    def fake_messages_create(**kwargs):
        captured.update(kwargs)

        class _Block:
            type = "tool_use"
            name = "record_turn"
            input = {
                "narrative": "n",
                "player_safe_summary": "s",
                "consequences": {},
                "suggested_actions": [
                    {"label": "A", "prompt": "do A"},
                    {"label": "B", "prompt": "do B"},
                    {"label": "C", "prompt": "do C"},
                ],
                "scene_participants": [],
            }

        class _Message:
            content = [_Block()]

        return _Message()

    provider = AnthropicNarrationProvider(
        messages_create=fake_messages_create,
        enable_dice=True,
    )
    from app.services.ai_provider import NarrationRequest

    provider.narrate(
        NarrationRequest(
            campaign_name="x",
            current_date_pce=728,
            player_input="probe",
            player_safe_brief="b",
            hidden_gm_brief="h",
        )
    )
    tool_schema = captured["tools"][0]
    assert "rolls" in tool_schema["input_schema"]["properties"]
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd backend && .venv/bin/pytest tests/test_a1_dice.py::test_provider_passes_enable_dice_to_schema -v`
Expected: FAIL — `__init__` does not accept `enable_dice`.

- [ ] **Step 4: Add `enable_dice` to provider**

In `AnthropicNarrationProvider.__init__`, accept `enable_dice` and store it:

```python
    def __init__(
        self,
        *,
        messages_create: Callable[..., Any] | None = None,
        model: str = "claude-haiku-4-5",
        max_tokens: int = 4096,
        enable_dice: bool = False,
    ) -> None:
        if not model:
            raise ValueError("AnthropicNarrationProvider requires a non-empty model.")
        self._messages_create = messages_create
        self._model = model
        self._max_tokens = max_tokens
        self._enable_dice = enable_dice
```

In `narrate()`, replace the `tools=[_TOOL_SCHEMA]` line with:

```python
            tools=[build_tool_schema(enable_dice=self._enable_dice)],
```

In `provider_registry.py`, where `AnthropicNarrationProvider(...)` is constructed, read settings via `get_settings().enable_dice` and pass it through.

- [ ] **Step 5: Run tests**

Run: `cd backend && .venv/bin/pytest tests/ -q`
Expected: full suite green.

- [ ] **Step 6: Commit**

```bash
git add backend/app/services/anthropic_provider.py backend/app/services/provider_registry.py backend/tests/test_a1_dice.py
git commit -m "feat(A1): provider accepts enable_dice; registry plumbs it through"
```

---

## Task 6: Extend system prompt with dice guidance (when enabled)

**Files:**
- Modify: `backend/app/services/anthropic_provider.py`
- Test: `backend/tests/test_a1_dice.py`

- [ ] **Step 1: Append failing test**

Append to `backend/tests/test_a1_dice.py`:

```python
from app.services.anthropic_provider import build_system_prompt


def test_system_prompt_omits_dice_guidance_when_disabled() -> None:
    prompt = build_system_prompt(enable_dice=False)
    assert "skill check" not in prompt.lower()
    assert "rolls:" not in prompt


def test_system_prompt_includes_dice_guidance_when_enabled() -> None:
    prompt = build_system_prompt(enable_dice=True)
    lowered = prompt.lower()
    assert "skill check" in lowered or "attribute check" in lowered
    assert "cunning" in lowered
    assert "do not call for a roll" in lowered or "do not roll" in lowered
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .venv/bin/pytest tests/test_a1_dice.py -v -k system_prompt`
Expected: FAIL — `build_system_prompt` does not exist.

- [ ] **Step 3: Add `build_system_prompt`**

In `backend/app/services/anthropic_provider.py`, define:

```python
_DICE_PROMPT_ADDENDUM = """

Skill checks (dice):
- Some player actions warrant a Red Rising attribute check. Call for one ONLY when the outcome is genuinely uncertain or under pressure: opposed will, deception, infiltration, lifting under load, threading a dataspike, etc. Do not call for a roll on routine narration, dialogue, or movement.
- Available attributes: strength, cunning, will, charm, tech.
- For each check, emit one entry in the rolls array with attribute, target (8 trivial / 12 average / 15 hard / 18+ heroic), dice_total (the resolved total — be honest, do not always favour the player), outcome (critical_success / success / failure / critical_failure), and narration (one short sentence flavouring the result).
- The narrative you produce must align with the roll outcome — failed rolls land as cost, complication, or partial success. Do not narrate success when the roll failed.
- Never explain dice mechanics in the narrative. The roll record is structural; the narrative is fiction.
- Maximum 3 rolls per turn. Most turns should have zero.
"""


def build_system_prompt(*, enable_dice: bool = False) -> str:
    if enable_dice:
        return _SYSTEM_PROMPT + _DICE_PROMPT_ADDENDUM
    return _SYSTEM_PROMPT
```

In `narrate()`, replace the literal `_SYSTEM_PROMPT` with `build_system_prompt(enable_dice=self._enable_dice)`.

- [ ] **Step 4: Run tests**

Run: `cd backend && .venv/bin/pytest tests/ -q`
Expected: full suite green.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/anthropic_provider.py backend/tests/test_a1_dice.py
git commit -m "feat(A1): conditional dice-prompt addendum

build_system_prompt(enable_dice=True) appends Red Rising-flavored
skill-check guidance covering when to roll, attribute set, target
calibration, and outcome alignment with narrative."
```

---

## Task 7: Carry `rolls` through `TurnEngineResult`

**Files:**
- Modify: `backend/app/services/turn_engine.py`
- Test: `backend/tests/test_a1_dice.py`

- [ ] **Step 1: Append failing test**

Append to `backend/tests/test_a1_dice.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.models.base import Base
from app.models.campaign import Campaign
from app.services.ai_provider import NarrationRequest, NarrationResponse
from app.services.consequence_applier import Consequences
from app.services.turn_engine import resolve_turn


class _RollProvider:
    def __init__(self, rolls):
        self._rolls = rolls

    def narrate(self, request):
        return NarrationResponse(
            narrative="n",
            player_safe_summary="s",
            consequences=Consequences(),
            rolls=self._rolls,
        )


def _bare_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)
    return SessionLocal()


def test_resolve_turn_returns_rolls() -> None:
    from app.services.ai_provider import Roll

    session = _bare_session()
    campaign = Campaign(
        name="t",
        tagline="t",
        current_date_pce=728,
        current_location_label="Crescent Block",
    )
    session.add(campaign)
    session.flush()

    provider = _RollProvider(
        [Roll(attribute="cunning", target=14, dice_total=17, outcome="success", narration="x.")]
    )
    result = resolve_turn(
        session=session,
        campaign=campaign,
        player_input="lie to the Copper",
        narration_provider=provider,
    )
    assert len(result.rolls) == 1
    assert result.rolls[0].attribute == "cunning"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .venv/bin/pytest tests/test_a1_dice.py::test_resolve_turn_returns_rolls -v`
Expected: FAIL — `TurnEngineResult` has no `rolls`.

- [ ] **Step 3: Add `rolls` to TurnEngineResult**

In `backend/app/services/turn_engine.py`:

1. Import `Roll`:

```python
from app.services.ai_provider import NarrationProvider, NarrationRequest, Roll
```

2. Add field on `TurnEngineResult`:

```python
    rolls: list[Roll] = field(default_factory=list)
```

3. In `resolve_turn`, return:

```python
    return TurnEngineResult(
        # ... existing fields ...
        rolls=narration.rolls,
    )
```

- [ ] **Step 4: Run tests**

Run: `cd backend && .venv/bin/pytest tests/ -q`
Expected: full suite green.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/turn_engine.py backend/tests/test_a1_dice.py
git commit -m "feat(A1): TurnEngineResult carries rolls"
```

---

## Task 8: Forward `rolls` through API `TurnResolution`

**Files:**
- Modify: `backend/app/schemas/turn.py`
- Modify: `backend/app/api/routes/turns.py`
- Test: `backend/tests/test_a1_dice.py`

- [ ] **Step 1: Append failing test**

Append to `backend/tests/test_a1_dice.py`:

```python
from fastapi.testclient import TestClient


def test_turns_endpoint_returns_rolls(monkeypatch) -> None:
    from app.main import app
    from app.services.ai_provider import NarrationResponse, Roll
    from app.services.consequence_applier import Consequences
    from app.services import turn_engine as turn_engine_module

    captured_provider = _RollProvider(
        [Roll(attribute="will", target=12, dice_total=15, outcome="success", narration="ok.")]
    )

    original_resolve = turn_engine_module.resolve_turn

    def fake_resolve(*, session, campaign, player_input, narration_provider=None):
        return original_resolve(
            session=session,
            campaign=campaign,
            player_input=player_input,
            narration_provider=captured_provider,
        )

    monkeypatch.setattr(
        "app.api.routes.turns.resolve_turn",
        fake_resolve,
    )

    client = TestClient(app)
    # Use the existing seed pipeline to create a campaign.
    seed_response = client.post("/api/v1/seed/world-bible")
    assert seed_response.status_code in (200, 201)
    campaign_id = seed_response.json()["campaign_id"]

    response = client.post(
        f"/api/v1/campaigns/{campaign_id}/turns",
        json={"player_input": "hold the line"},
    )
    assert response.status_code == 201
    body = response.json()
    assert "rolls" in body
    assert body["rolls"][0]["attribute"] == "will"
    assert body["rolls"][0]["outcome"] == "success"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .venv/bin/pytest tests/test_a1_dice.py::test_turns_endpoint_returns_rolls -v`
Expected: FAIL — `rolls` not in response body.

- [ ] **Step 3: Add field to `TurnResolution` schema**

In `backend/app/schemas/turn.py`, add to `TurnResolution`:

```python
    rolls: list[dict] = Field(default_factory=list)
```

- [ ] **Step 4: Forward in route**

In `backend/app/api/routes/turns.py`, in the `create_turn` route, add to the `TurnResolution(...)` construction:

```python
        rolls=[
            {
                "attribute": r.attribute,
                "target": r.target,
                "dice_total": r.dice_total,
                "outcome": r.outcome,
                "narration": r.narration,
            }
            for r in result.rolls
        ],
```

- [ ] **Step 5: Run test**

Run: `cd backend && .venv/bin/pytest tests/ -q`
Expected: full suite green.

- [ ] **Step 6: Commit**

```bash
git add backend/app/schemas/turn.py backend/app/api/routes/turns.py backend/tests/test_a1_dice.py
git commit -m "feat(A1): TurnResolution forwards rolls to API client"
```

---

## Task 9: Frontend — emit `system-roll` events from resolution

**Files:**
- Modify: `frontend/src/App.jsx`

- [ ] **Step 1: Extend `buildConsequenceEvents`**

In `frontend/src/App.jsx`, locate `buildConsequenceEvents(resolution)` and append before the return:

```javascript
  for (const roll of resolution.rolls ?? []) {
    events.push({
      id: `${id}-roll-${roll.attribute}-${events.length}`,
      speaker: "system-roll",
      label: "Roll",
      meta: `${roll.attribute} vs ${roll.target}`,
      text: `${roll.dice_total} → ${roll.outcome.replace("_", " ")} — ${roll.narration}`,
      timestamp: null,
      roll,
    });
  }
```

- [ ] **Step 2: Sanity-check the file**

Run: `cd frontend && node --check src/App.jsx 2>&1 || true`
Note: JSX cannot be syntax-checked with bare node, but `make check` will catch obvious breakage. Move on.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/App.jsx
git commit -m "feat(A1): App emits system-roll events from turn resolution"
```

---

## Task 10: Frontend — render `system-roll` in TurnFeed

**Files:**
- Modify: `frontend/src/components/TurnFeed.jsx`

- [ ] **Step 1: Add avatar mapping**

In `frontend/src/components/TurnFeed.jsx`, in `getTurnAvatar`, after the `system-clock` block and before the fallback, add:

```javascript
  if (turn.speaker === "system-roll") {
    return {
      initials: "RL",
      name: "Skill Check",
      caste: "Copper",
    };
  }
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/TurnFeed.jsx
git commit -m "feat(A1): TurnFeed handles system-roll speaker avatar"
```

---

## Task 11: Frontend — style `.turn-system-roll`

**Files:**
- Modify: `frontend/src/styles.css`

- [ ] **Step 1: Find the existing system-* turn block**

Open `frontend/src/styles.css` and locate the rules for `.turn-system-location`, `.turn-system-clock`, `.turn-system-secret`. Identify the visual pattern (top stripe colour + meta layout).

- [ ] **Step 2: Add the parallel `.turn-system-roll` rule**

Append after the existing system-* rules:

```css
.turn-system-roll {
  border-left: 2px solid var(--accent-tac-amber);
}

.turn-system-roll .turn-meta span:first-child {
  color: var(--accent-tac-amber);
}

.turn-system-roll .turn-body {
  font-family: "VT323", monospace;
  letter-spacing: 0.04em;
  font-size: 1.05rem;
  color: var(--accent-tac-amber);
}
```

(If the existing system-* rules use different selectors or token names, mirror them — the goal is a Copper/amber stripe distinct from Location/Clock/Secret.)

- [ ] **Step 3: Commit**

```bash
git add frontend/src/styles.css
git commit -m "feat(A1): style system-roll turn events with amber/copper accent"
```

---

## Task 12: Update slice doc + run final verification

**Files:**
- Modify: `docs/development/workstreams/A1-dice-skill-checks.md`

- [ ] **Step 1: Run full backend suite**

Run from `/home/lans/ares-track-a/A1`: `make backend-test`
Expected: all tests pass (70+ existing plus ~10 new in `test_a1_dice.py`).

- [ ] **Step 2: Run frontend syntax check**

Run: `make check`
Expected: passes.

- [ ] **Step 3: Update workstream doc**

Edit `docs/development/workstreams/A1-dice-skill-checks.md` to record:

- Status: review (or in-flight if tasks remain)
- Last-known-good commit: latest sha + test results
- Files touched so far: full list with ✅
- Next concrete step: "open PR for review; flip ARES_ENABLE_DICE=true and smoke-test against full stack at 5180"
- Agent rotation log entry for this session

- [ ] **Step 4: Final commit + push**

```bash
git add docs/development/workstreams/A1-dice-skill-checks.md
git commit -m "docs(A1): mark slice ready for review

All 12 tasks complete. Backend suite green, frontend check green.
Next: smoke-test with ARES_ENABLE_DICE=true at localhost:5180 and
open the draft PR for review."
git push
```

- [ ] **Step 5: Mark draft PR ready (manual)**

Operator step. Run from any worktree:

```bash
gh pr ready 10
```

(Optional — leave as draft if smoke-test pending.)

---

## Verification on completion

End-to-end smoke test (operator-led, NOT a task step):

1. Set `ARES_ENABLE_DICE=true` in `.env`.
2. `make compose-up`
3. Open `http://localhost:5180/`, seed campaign if needed.
4. Issue a player action that should warrant a check (e.g. "I lie to the Copper about my ident-papers").
5. Confirm: turn feed shows an amber `system-roll` event with attribute, total vs target, outcome, and narration.
6. Take Playwright screenshot, save under `assets/samples/ui-iteration/2026-05-05-A1-dice-after.png`.
7. Confirm `ARES_ENABLE_DICE=false` (default) leaves the feed unchanged.

## Hard constraints checklist

- [ ] Hidden state does not leak — rolls expose nothing the player wouldn't already see.
- [ ] Canon guard not bypassed — narration still passes through `evaluate_canon_guard`.
- [ ] Player character remains Davan of Tharsis.
- [ ] All AI calls go through `NarrationProvider`.
- [ ] Stub provider works offline — `make backend-test` passes without API key (the new tests use fake `messages_create`, no live calls).
- [ ] Default `ARES_ENABLE_DICE=false` keeps `main` behaviour identical.
