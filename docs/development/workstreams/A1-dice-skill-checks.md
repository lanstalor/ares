# Slice A1 — Dice + Skill Check Primitive

| Field | Value |
|---|---|
| **Track** | A — Mechanical Depth |
| **Branch** | `track-a/A1-dice-skill-checks` |
| **Worktree** | `~/ares-track-a/A1` |
| **PR** | https://github.com/lanstalor/ares/pull/10 (draft) |
| **Status** | in-flight (5/12 tasks complete) |
| **Last agent** | Claude (2026-05-05) |
| **Next agent** | any |
| **Parent plan** | `~/.claude/plans/a-i-happy-matsumoto.md` |
| **Implementation plan** | `docs/superpowers/plans/2026-05-05-A1-dice-skill-checks.md` |

---

## Goal

Add a Red Rising-flavored skill-check primitive so the GM can call for and resolve attribute checks (Strength, Cunning, Will, Charm, Tech) and the player sees the dice in the turn feed. Gated behind `ARES_ENABLE_DICE` (default off).

## Last-known-good commit

`aaaf504` — `feat(A1): provider accepts enable_dice; registry and turn_engine plumb it through`

Test status at this commit:
- backend (`PYTHONPATH=. pytest tests/`): ✅ 81 passing (70 pre-existing + 11 new in `test_a1_dice.py`)
- frontend (`make check`): not-run (no frontend changes yet)
- playtester (offline, stub provider): not-run
- playwright screenshot at 5180: not-run (frontend tasks pending)

## In-flight WIP

`clean` — last commit is a `feat:`. Working tree is clean. 5 of 12 tasks complete; 7 remain.

## Files touched so far

- ✅ `backend/app/core/config.py` — `enable_dice: bool` setting added
- ✅ `backend/app/services/ai_provider.py` — `Roll` dataclass + `rolls` field on `NarrationResponse`
- ✅ `backend/app/services/anthropic_provider.py` — `build_tool_schema()` builder + `_ROLLS_PROPERTY_SCHEMA` constant; `_build_response` translates `tool_input["rolls"]` into typed `Roll` instances; `AnthropicNarrationProvider.__init__` accepts `enable_dice` and passes it to `build_tool_schema` in `narrate()`
- ✅ `backend/app/services/provider_registry.py` — `get_narration_provider(..., *, enable_dice=False)` plumbed to Anthropic provider
- ✅ `backend/app/services/turn_engine.py` — passes `settings.enable_dice` through to `get_narration_provider`
- ✅ `backend/tests/test_a1_dice.py` — 11 tests covering settings, dataclass, schema builder, response parsing, provider wiring

Not yet touched (Tasks 6–12):
- ⏳ `backend/app/services/anthropic_provider.py` — system-prompt addendum (`build_system_prompt`)
- ⏳ `backend/app/services/turn_engine.py` — `TurnEngineResult.rolls` field
- ⏳ `backend/app/api/routes/turns.py` — forward rolls in response
- ⏳ `backend/app/schemas/turn.py` — `rolls` on `TurnResolution`
- ⏳ `frontend/src/App.jsx` — `buildConsequenceEvents` emits `system-roll`
- ⏳ `frontend/src/components/TurnFeed.jsx` — `system-roll` avatar
- ⏳ `frontend/src/styles.css` — `.turn-system-roll` styling

## Next concrete step

**Task 6** — add `build_system_prompt(*, enable_dice=False)` in `backend/app/services/anthropic_provider.py` that appends the `_DICE_PROMPT_ADDENDUM` constant (skill-check guidance covering when to roll, attribute set, target calibration, outcome alignment) when the flag is on. Update `narrate()` to use `build_system_prompt(enable_dice=self._enable_dice)` instead of literal `_SYSTEM_PROMPT`. Test stubs are in the implementation plan.

After Task 6: continue sequentially through Tasks 7 → 12 in `docs/superpowers/plans/2026-05-05-A1-dice-skill-checks.md`. The plan has full code for every step.

## Open questions / blockers

- None. Architecture validated by 81 passing tests.

## Agent rotation log

- 2026-05-05 — Claude → bootstrap + plan + Tasks 1–5 (settings flag, Roll dataclass, conditional tool schema, response translation, provider wiring). 81 tests passing. Ended at commit `aaaf504` due to imminent quota exhaustion. Working tree clean. Next: Task 6 (system-prompt addendum).

## How to resume (any agent)

```bash
cd ~/ares-track-a/A1
cat docs/development/workstreams/A1-dice-skill-checks.md     # this file
cat docs/superpowers/plans/2026-05-05-A1-dice-skill-checks.md  # the plan
git log --oneline -10
PYTHONPATH=backend /home/lans/ares/backend/.venv/bin/pytest backend/tests/ -q   # confirm 81 pass
```

Then execute Task 6 from the plan. Each subsequent task has full code.

## Verification on completion

- [ ] All 12 plan tasks complete (5/12 done)
- [ ] `make backend-test` passes
- [ ] `make check` passes
- [ ] Playtester runs 30 turns clean with `ARES_ENABLE_DICE=false` (default) and `=true`
- [ ] Playwright screenshot at 5180 with dice enabled — save under `assets/samples/ui-iteration/2026-05-05-A1-dice-after.png`
- [ ] PR #10 marked ready for review (`gh pr ready 10`)

## Hard constraints checklist

- [ ] Hidden state does not leak — rolls expose nothing the player wouldn't already see
- [ ] Canon guard not bypassed — narration still passes through `evaluate_canon_guard`
- [ ] Player character remains Davan of Tharsis
- [ ] All AI calls go through `NarrationProvider` Protocol — confirmed
- [ ] Stub provider works offline — confirmed (new tests use fake `messages_create`, no live API calls)
- [ ] Default `ARES_ENABLE_DICE=false` keeps `main` behaviour identical — confirmed (full suite green with flag off)
